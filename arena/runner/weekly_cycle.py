"""
arena/runner/weekly_cycle.py
============================
周频同步执行主运行器 (Weekly Cycle Runner)
支持全量巡回回测、参数化猴子群落、饕餮独立基准与按周增量滚动推进 (State Checkpoint)
"""

from typing import List, Dict, Optional, Callable, Any, Tuple
from pathlib import Path
import pickle
import datetime
import pandas as pd
import numpy as np

from arena.config import (
    DEFAULT_ANCHOR_DATE,
    DEFAULT_END_DATE,
    DEFAULT_TOPK,
    DEFAULT_INITIAL_CASH,
    DEFAULT_DEAL_PRICE,
    RUNS_DIR,
)
from arena.calendar import TradingCalendar, WeeklyCycle
from arena.contestants.manifest import ContestantManifest
from arena.contestants.registry import ContestantRegistry
from arena.contestants.adapters import create_adapter, BaseInferenceAdapter
from arena.animals import get_all_animals, Animal
from arena.portfolio import PortfolioEngine, PortfolioPath
from arena.controls import (
    MonkeyColony,
    RockBenchmark,
    TaotieBenchmark,
    CANONICAL_STRATEGY_SPECS,
    StrategySpec,
    map_animal_to_spec_id,
)
from arena.data.market import MarketDataProvider


class WeeklyCycleRunner:
    """
    周频同步执行运行器：
    - 按真实交易日历循环推进周期 (Cycle 0, 1, 2, ... 7)
    - 统一协调 Contestant 预测 -> Animal 信号变换 -> PortfolioEngine 调仓执行与日频盯市估值
    - 独立运行全池饕餮基准 (Taotie Benchmark)
    - 支持参数化猴子群落 (Parametric Monkey Colony: 11 组策略 × 100 只)
    - 支持按周增量滚动更新 (Checkpoint State Serialization & Step Advance)
    """

    def __init__(
        self,
        anchor_date: str = DEFAULT_ANCHOR_DATE,
        end_date: str = DEFAULT_END_DATE,
        topk: int = DEFAULT_TOPK,
        initial_cash: float = DEFAULT_INITIAL_CASH,
        deal_price_mode: str = DEFAULT_DEAL_PRICE,
        mock_mode: bool = False,
        calendar: Optional[TradingCalendar] = None,
        registry: Optional[ContestantRegistry] = None,
        animals: Optional[List[Animal]] = None,
        market_provider: Optional[MarketDataProvider] = None,
    ):
        self.anchor_date = anchor_date
        self.end_date = end_date
        self.topk = topk
        self.initial_cash = initial_cash
        self.deal_price_mode = deal_price_mode
        self.mock_mode = mock_mode

        self.calendar = calendar or TradingCalendar()
        self.registry = registry or ContestantRegistry()
        self.animals = animals or get_all_animals()
        self.market_provider = market_provider

        self.cycles = self.calendar.build_weekly_cycles(anchor_date, end_date)
        self.monkey_colony = MonkeyColony(colony_size=1000)
        self.rock_benchmark = RockBenchmark()
        self.taotie_benchmark = TaotieBenchmark(
            initial_cash=self.initial_cash,
            deal_price_mode=self.deal_price_mode
        )

        # 运行实例映射: {(contestant_id, animal_id): PortfolioEngine}
        self.engines: Dict[tuple, PortfolioEngine] = {}
        # 各选手的历史信号记录: {contestant_id: {cycle_idx: score_series}}
        self.signal_history: Dict[str, Dict[int, pd.Series]] = {}
        # 适配器缓存: {contestant_id: adapter}
        self.adapters: Dict[str, BaseInferenceAdapter] = {}
        # 当前已完成的最新周期索引
        self.last_completed_cycle_idx: int = -1

    def _init_engines(self, contestants: List[ContestantManifest]):
        """初始化所有 (Contestant, Animal) 组合的回测引擎"""
        self.engines = {}
        self.signal_history = {}
        self.adapters = {}

        for c in contestants:
            cid = c.contestant_id
            self.signal_history[cid] = {}
            self.adapters[cid] = create_adapter(c, mock=self.mock_mode, use_replay=not self.mock_mode)

            for a in self.animals:
                key = (cid, a.animal_id)
                self.engines[key] = PortfolioEngine(
                    contestant_id=cid,
                    animal_id=a.animal_id,
                    topk=self.topk,
                    initial_cash=self.initial_cash,
                    deal_price_mode=self.deal_price_mode
                )

        self.taotie_benchmark = TaotieBenchmark(
            initial_cash=self.initial_cash,
            deal_price_mode=self.deal_price_mode
        )
        self.last_completed_cycle_idx = -1

    def _setup_market_provider(
        self,
        active_contestants: List[ContestantManifest],
        price_lookup_fn: Optional[Callable[[str, str, str], float]],
        tradability_filter_fn: Optional[Callable[[str, str], bool]]
    ) -> Tuple[Callable[[str, str, str], float], Optional[Callable[[str, str], bool]]]:
        if price_lookup_fn is None:
            if not self.mock_mode:
                if self.market_provider is None:
                    self.market_provider = MarketDataProvider(use_real_qlib=True)
                # 获取首个预测标的池并预加载真实 Qlib 价格
                try:
                    first_adapter = next(iter(self.adapters.values()))
                    sample_score = first_adapter.predict(start_date=self.anchor_date, end_date=self.anchor_date)
                    insts = list(sample_score.index)
                    self.market_provider.load_qlib_data(insts, self.anchor_date, self.end_date)
                except Exception as e:
                    print(f"[WARN] 真实 Qlib 价格批量加载异常，降级为模拟价格: {e}")
                price_lookup_fn = self.market_provider.get_real_price
                if tradability_filter_fn is None:
                    tradability_filter_fn = self.market_provider.is_tradable
            else:
                def default_price_lookup(inst: str, date: str, field: str) -> float:
                    base = (abs(hash(inst)) % 3000 + 1000) / 100.0
                    day_offset = ((abs(hash(f"{inst}_{date}")) % 20) - 10) / 1000.0
                    if field == "open":
                        return base
                    return base * (1.0 + day_offset)
                price_lookup_fn = default_price_lookup
        return price_lookup_fn, tradability_filter_fn

    def step_cycle(
        self,
        cycle: WeeklyCycle,
        active_contestants: List[ContestantManifest],
        price_lookup_fn: Callable[[str, str, str], float],
        tradability_filter_fn: Optional[Callable[[str, str], bool]] = None,
    ):
        """
        单周推进核心逻辑（无论是全量批量还是增量滚动，统一调用此方法保证绝对幂等与一致性）。
        """
        c_idx = cycle.cycle_idx

        # 1. 决策日（周五收盘）：各模型产出本周期的原始预测分数
        for c in active_contestants:
            cid = c.contestant_id
            if cid not in self.adapters:
                self.adapters[cid] = create_adapter(c, mock=self.mock_mode, use_replay=not self.mock_mode)
            adapter = self.adapters[cid]

            raw_score = adapter.predict(
                start_date=cycle.decision_date,
                end_date=cycle.decision_date
            )
            if cid not in self.signal_history:
                self.signal_history[cid] = {}
            self.signal_history[cid][c_idx] = raw_score

        # 2. 各 Animal 进行信号变换并生成下周一的订单
        for c in active_contestants:
            cid = c.contestant_id
            history = self.signal_history[cid]
            current_raw = history[c_idx]

            for a in self.animals:
                key = (cid, a.animal_id)
                if key not in self.engines:
                    self.engines[key] = PortfolioEngine(
                        contestant_id=cid,
                        animal_id=a.animal_id,
                        topk=self.topk,
                        initial_cash=self.initial_cash,
                        deal_price_mode=self.deal_price_mode
                    )
                engine = self.engines[key]

                transformed_score = a.transform_signal(
                    current_score=current_raw,
                    history_scores=history,
                    cycle_idx=c_idx
                )

                policy = a.get_portfolio_policy()
                n_drop = policy.get("n_drop", 3)
                topk = policy.get("topk", self.topk)
                passive_pool = policy.get("passive_pool", False)

                is_first = (c_idx == 0)
                order = engine.generate_order(
                    score=transformed_score,
                    topk=topk,
                    n_drop=n_drop,
                    trade_date=cycle.trade_date,
                    is_first_entry=is_first,
                    tradability_filter=tradability_filter_fn,
                    price_lookup=price_lookup_fn,
                    passive_pool=passive_pool
                )

                # 3. 撮合成交与周内日频估值
                engine.execute_weekly_cycle(
                    cycle=cycle,
                    order=order,
                    price_lookup=price_lookup_fn
                )

        # 4. 推进独立基准：饕餮 (Taotie Benchmark)
        first_raw = next(iter(self.signal_history.values()))[c_idx]
        universe = list(first_raw.index)
        self.taotie_benchmark.step(
            cycle=cycle,
            universe=universe,
            price_lookup_fn=price_lookup_fn,
            tradability_filter_fn=tradability_filter_fn,
        )

        self.last_completed_cycle_idx = c_idx

    def run(
        self,
        contestants: Optional[List[ContestantManifest]] = None,
        price_lookup_fn: Optional[Callable[[str, str, str], float]] = None,
        tradability_filter_fn: Optional[Callable[[str, str], bool]] = None,
        max_cycles: Optional[int] = None
    ) -> Dict[tuple, PortfolioPath]:
        """
        全量批处理回测运行。
        """
        active_contestants = contestants or self.registry.list_contestants()
        self._init_engines(active_contestants)
        price_lookup_fn, tradability_filter_fn = self._setup_market_provider(
            active_contestants, price_lookup_fn, tradability_filter_fn
        )

        cycles_to_run = self.cycles[:max_cycles] if max_cycles else self.cycles

        for cycle in cycles_to_run:
            self.step_cycle(
                cycle=cycle,
                active_contestants=active_contestants,
                price_lookup_fn=price_lookup_fn,
                tradability_filter_fn=tradability_filter_fn
            )

        # 导出所有组合的完整回测路径，包含统一控制基准 BENCHMARK_taotie
        results = {
            key: engine.to_portfolio_path()
            for key, engine in self.engines.items()
        }
        results[("BENCHMARK", "taotie")] = self.taotie_benchmark.engine.to_portfolio_path()
        return results

    def run_parametric_monkeys(
        self,
        specs: Optional[List[StrategySpec]] = None,
        colony_size: Optional[int] = None,
        price_lookup_fn: Optional[Callable[[str, str, str], float]] = None,
        tradability_filter_fn: Optional[Callable[[str, str], bool]] = None,
        max_cycles: Optional[int] = None
    ) -> Dict[str, List[PortfolioPath]]:
        """
        为指定的策略规格组运行参数化猴子群落。
        默认覆盖全部 11 种策略规格。
        """
        if colony_size is not None:
            self.monkey_colony.colony_size = colony_size

        target_specs = specs or list(CANONICAL_STRATEGY_SPECS.values())
        cycles_to_run = self.cycles[:max_cycles] if max_cycles else self.cycles

        if price_lookup_fn is None:
            price_lookup_fn, tradability_filter_fn = self._setup_market_provider(
                self.registry.list_contestants(), None, None
            )

        def universe_provider(decision_date: str) -> List[str]:
            if self.signal_history:
                first_history = next(iter(self.signal_history.values()))
                for c_idx, s in first_history.items():
                    if c_idx < len(self.cycles) and self.cycles[c_idx].decision_date == decision_date:
                        return list(s.index)
            # 兜底从适配器采样
            first_c = self.registry.list_contestants()[0]
            if first_c.contestant_id not in self.adapters:
                self.adapters[first_c.contestant_id] = create_adapter(first_c, mock=self.mock_mode, use_replay=not self.mock_mode)
            ad = self.adapters[first_c.contestant_id]
            sc = ad.predict(decision_date, decision_date)
            return list(sc.index)

        monkey_results = {}
        for spec in target_specs:
            paths = self.monkey_colony.run_group(
                spec=spec,
                cycles=cycles_to_run,
                universe_provider_fn=universe_provider,
                price_lookup_fn=price_lookup_fn,
                tradability_filter_fn=tradability_filter_fn,
                initial_cash=self.initial_cash,
                deal_price_mode=self.deal_price_mode
            )
            monkey_results[spec.spec_id] = paths
        return monkey_results

    # =========================================================================
    # 按周增量滚动更新机制 (Rolling Incremental Checkpointing)
    # =========================================================================

    def export_checkpoint(self) -> Dict[str, Any]:
        """导出整个 Arena 运行器的完整状态快照字典"""
        return {
            "last_completed_cycle_idx": self.last_completed_cycle_idx,
            "anchor_date": self.anchor_date,
            "end_date": self.end_date,
            "signal_history": self.signal_history,
            "engines": {
                key: engine.export_checkpoint()
                for key, engine in self.engines.items()
            },
            "taotie_engine": self.taotie_benchmark.engine.export_checkpoint(),
        }

    def load_checkpoint(self, state: Dict[str, Any]):
        """从状态快照字典恢复运行器状态"""
        self.last_completed_cycle_idx = state["last_completed_cycle_idx"]
        self.signal_history = state.get("signal_history", {})

        self.engines = {}
        for key, cp in state.get("engines", {}).items():
            self.engines[key] = PortfolioEngine.from_checkpoint(cp)

        if "taotie_engine" in state:
            self.taotie_benchmark = TaotieBenchmark(
                initial_cash=self.initial_cash,
                deal_price_mode=self.deal_price_mode
            )
            self.taotie_benchmark.engine = PortfolioEngine.from_checkpoint(state["taotie_engine"])

    def save_checkpoint_to_disk(self, checkpoint_dir: Path, cycle_idx: int):
        """将状态快照持久化落盘至 runs/<run_id>/checkpoints/"""
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        state = self.export_checkpoint()

        latest_path = checkpoint_dir / "latest_state.pkl"
        cycle_path = checkpoint_dir / f"cycle_{cycle_idx}.pkl"

        with open(latest_path, "wb") as f:
            pickle.dump(state, f)
        with open(cycle_path, "wb") as f:
            pickle.dump(state, f)

    def load_checkpoint_from_disk(self, checkpoint_path: Path):
        """从指定文件加载状态快照"""
        with open(checkpoint_path, "rb") as f:
            state = pickle.load(f)
        self.load_checkpoint(state)
