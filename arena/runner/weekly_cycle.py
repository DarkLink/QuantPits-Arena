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
    REPO_ROOT,
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
from arena.benchmarks import GhostTaotieBenchmark
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
        season_id: Optional[str] = None,
        auth_store_path: Optional[Path] = None,
        run_dir: Optional[Path] = None,
    ):
        self.anchor_date = anchor_date
        self.end_date = end_date
        self.topk = topk
        self.initial_cash = initial_cash
        self.deal_price_mode = deal_price_mode
        self.mock_mode = mock_mode
        self.season_id = season_id
        self.run_dir = run_dir

        if auth_store_path is not None:
            self.auth_store_path = auth_store_path
        elif season_id:
            raw_univ = season_id.replace("season_", "").lower()
            candidates = [
                REPO_ROOT / "artifacts" / "predictions" / f"{season_id}_contestants_oos.pkl",
                REPO_ROOT / "artifacts" / "predictions" / f"{raw_univ}_contestants_oos.pkl",
            ]
            for p in candidates:
                if p.exists():
                    self.auth_store_path = p
                    break
            else:
                fallback = REPO_ROOT / "artifacts" / "predictions" / "all_contestants_oos.pkl"
                self.auth_store_path = fallback if fallback.exists() else candidates[1]
        else:
            self.auth_store_path = REPO_ROOT / "artifacts" / "predictions" / "all_contestants_oos.pkl"

        self.calendar = calendar or TradingCalendar()
        self.registry = registry or ContestantRegistry()
        self.animals = animals or get_all_animals()
        self.market_provider = market_provider

        self.cycles = self.calendar.build_weekly_cycles(anchor_date, end_date)
        self.monkey_colony = MonkeyColony(colony_size=1000)
        self.rock_benchmark = RockBenchmark()
        self._create_benchmarks()

        # 运行实例映射: {(contestant_id, animal_id): PortfolioEngine}
        self.engines: Dict[tuple, PortfolioEngine] = {}
        # 各选手的历史信号记录: {contestant_id: {cycle_idx: score_series}}
        self.signal_history: Dict[str, Dict[int, pd.Series]] = {}
        # 适配器缓存: {contestant_id: adapter}
        self.adapters: Dict[str, BaseInferenceAdapter] = {}
        # 当前已完成的最新周期索引
        self.last_completed_cycle_idx: int = -1

    def _create_benchmarks(self) -> None:
        """根据赛季配置声明或动态估算初始化物理与理论全池基准 (支持可配置初始资金)"""
        taotie_cash = self.initial_cash
        ghost_cash = 100_000_000.0
        taotie_name = "Taotie (全池物理被动)"
        ghost_name = "Ghost Taotie (全池理论等权)"

        if self.season_id:
            try:
                from arena.seasons.manager import SeasonManager
                scfg = SeasonManager.get_season_config(self.season_id)
                taotie_cash = scfg.get_benchmark_initial_cash("taotie", default=self.initial_cash)
                ghost_cash = scfg.get_benchmark_initial_cash("ghost_taotie", default=100_000_000.0)
                taotie_name = scfg.get_benchmark_display_name("taotie", default=taotie_name)
                ghost_name = scfg.get_benchmark_display_name("ghost_taotie", default=ghost_name)
            except Exception:
                pass

        self.taotie_benchmark = TaotieBenchmark(
            initial_cash=taotie_cash,
            deal_price_mode=self.deal_price_mode,
            display_name=taotie_name
        )
        self.ghost_taotie_benchmark = GhostTaotieBenchmark(
            initial_cash=ghost_cash,
            deal_price_mode=self.deal_price_mode,
            display_name=ghost_name
        )

    def _init_engines(self, contestants: List[ContestantManifest]):
        """初始化所有 (Contestant, Animal) 组合的回测引擎"""
        self.engines = {}
        self.signal_history = {}
        self.adapters = {}

        for c in contestants:
            cid = c.contestant_id
            self.signal_history[cid] = {}
            self.adapters[cid] = create_adapter(
                c,
                mock=self.mock_mode,
                use_replay=not self.mock_mode,
                auth_store_path=self.auth_store_path
            )

            for a in self.animals:
                key = (cid, a.animal_id)
                self.engines[key] = PortfolioEngine(
                    contestant_id=cid,
                    animal_id=a.animal_id,
                    topk=self.topk,
                    initial_cash=self.initial_cash,
                    deal_price_mode=self.deal_price_mode
                )

        self._create_benchmarks()
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
                    if not self.adapters and active_contestants:
                        for c in active_contestants:
                            self.adapters[c.contestant_id] = create_adapter(
                                c,
                                mock=self.mock_mode,
                                use_replay=not self.mock_mode,
                                auth_store_path=self.auth_store_path
                            )
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

    def commit_orders(
        self,
        cycle: WeeklyCycle,
        active_contestants: List[ContestantManifest],
        tradability_filter_fn: Optional[Callable[[str, str], bool]] = None,
        price_lookup_fn: Optional[Callable[[str, str, str], float]] = None,
    ) -> Dict[tuple, Any]:
        """
        【阶段一：周五决策日 (Decision Phase)】
        - 严格仅使用 <= decision_date 的信息；
        - 模型生成原始打分截面；
        - 各动物执行信号转换；
        - 生成各策略组合与基准在下周一的目标调仓订单 (Orders)；
        - 可在此阶段将订单哈希写入存证，杜绝事后窥探与过拟合。
        """
        c_idx = cycle.cycle_idx

        # 1. 决策日（周五收盘）：各模型产出本周期的原始预测分数
        for c in active_contestants:
            cid = c.contestant_id
            if cid not in self.adapters:
                self.adapters[cid] = create_adapter(
                    c,
                    mock=self.mock_mode,
                    use_replay=not self.mock_mode,
                    auth_store_path=self.auth_store_path
                )
            adapter = self.adapters[cid]

            raw_score = adapter.predict(
                start_date=cycle.decision_date,
                end_date=cycle.decision_date
            )
            if cid not in self.signal_history:
                self.signal_history[cid] = {}
            self.signal_history[cid][c_idx] = raw_score

        orders: Dict[tuple, Any] = {}

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
                orders[key] = order

        # 3. 生成独立基准 (Taotie & Ghost Taotie) 的目标订单
        first_raw = next(iter(self.signal_history.values()))[c_idx]
        universe = list(first_raw.index)
        is_first_taotie = (c_idx == 0)
        mock_score = pd.Series(1.0, index=universe)
        taotie_order = self.taotie_benchmark.engine.generate_order(
            score=mock_score,
            topk=0,
            n_drop=0,
            trade_date=cycle.trade_date,
            is_first_entry=is_first_taotie,
            tradability_filter=tradability_filter_fn,
            price_lookup=price_lookup_fn,
            passive_pool=True
        )
        orders[("BENCHMARK", "taotie")] = taotie_order

        ghost_order = self.ghost_taotie_benchmark.engine.generate_order(
            score=mock_score,
            topk=0,
            n_drop=0,
            trade_date=cycle.trade_date,
            is_first_entry=is_first_taotie,
            tradability_filter=tradability_filter_fn,
            price_lookup=price_lookup_fn,
            passive_pool=True
        )
        orders[("BENCHMARK", "ghost_taotie")] = ghost_order

        return orders

    def execute_orders(
        self,
        cycle: WeeklyCycle,
        orders: Dict[tuple, Any],
        price_lookup_fn: Callable[[str, str, str], float],
        tradability_filter_fn: Optional[Callable[[str, str], bool]] = None,
    ) -> None:
        """
        【阶段二：周一开盘执行与周内日频估值 (Execution & Valuation Phase)】
        - 接收周五已锁定的订单字典；
        - 按周一实际集合竞价价格和停牌状态撮合成交（严格拦截停牌标的，不可交易标的烂在持仓中）；
        - 记录周内每一个交易日的 Daily Marked-to-Market 市值与 NAV。
        """
        c_idx = cycle.cycle_idx

        # 执行各选手参赛动物组合与独立基准
        for key, order in orders.items():
            if key == ("BENCHMARK", "taotie"):
                self.taotie_benchmark.engine.execute_weekly_cycle(
                    cycle=cycle,
                    order=order,
                    price_lookup=price_lookup_fn,
                    tradability_filter=tradability_filter_fn
                )
            elif key == ("BENCHMARK", "ghost_taotie"):
                self.ghost_taotie_benchmark.engine.execute_weekly_cycle(
                    cycle=cycle,
                    order=order,
                    price_lookup=price_lookup_fn,
                    tradability_filter=tradability_filter_fn
                )
            else:
                engine = self.engines[key]
                engine.execute_weekly_cycle(
                    cycle=cycle,
                    order=order,
                    price_lookup=price_lookup_fn,
                    tradability_filter=tradability_filter_fn
                )

        self.last_completed_cycle_idx = c_idx

    def step_cycle(
        self,
        cycle: WeeklyCycle,
        active_contestants: List[ContestantManifest],
        price_lookup_fn: Callable[[str, str, str], float],
        tradability_filter_fn: Optional[Callable[[str, str], bool]] = None,
    ):
        """
        单周推进核心逻辑（无论是全量批量还是增量滚动，统一编排两阶段流水线保证绝对一致性）。
        """
        orders = self.commit_orders(
            cycle=cycle,
            active_contestants=active_contestants,
            tradability_filter_fn=tradability_filter_fn,
            price_lookup_fn=price_lookup_fn
        )
        if self.run_dir is not None:
            self.export_isolated_orders(cycle, orders, self.run_dir)
        self.execute_orders(
            cycle=cycle,
            orders=orders,
            price_lookup_fn=price_lookup_fn,
            tradability_filter_fn=tradability_filter_fn
        )

    def step_friday_cycle(
        self,
        cycle: WeeklyCycle,
        active_contestants: List[ContestantManifest],
        price_lookup_fn: Callable[[str, str, str], float],
        pending_orders: Optional[Dict[tuple, Any]] = None,
        tradability_filter_fn: Optional[Callable[[str, str], bool]] = None,
    ) -> Tuple[Dict[tuple, Any], Optional[Dict[tuple, Any]]]:
        """
        周五闭环原子执行流 (Friday All-in-One Cycle):
        1. 若提供了 pending_orders (上周五已冻结的下周一调仓订单)，
           则以本周一实际开盘价与周内行情进行撮合成交与盯市估值 (execute_orders)；
        2. 接着读取本周五收盘最新截面特征，为下周一生成全新目标订单 (commit_orders)；
        3. 返回 (settled_orders, next_orders)。
        """
        # 1. 撮合与结算已冻结的订单 (若首周无 pending_orders，则先 commit 再 execute 首周建仓)
        if pending_orders is not None:
            self.execute_orders(
                cycle=cycle,
                orders=pending_orders,
                price_lookup_fn=price_lookup_fn,
                tradability_filter_fn=tradability_filter_fn
            )
            settled_orders = pending_orders
        else:
            settled_orders = self.commit_orders(
                cycle=cycle,
                active_contestants=active_contestants,
                tradability_filter_fn=tradability_filter_fn,
                price_lookup_fn=price_lookup_fn
            )
            if self.run_dir is not None:
                self.export_isolated_orders(cycle, settled_orders, self.run_dir)
            self.execute_orders(
                cycle=cycle,
                orders=settled_orders,
                price_lookup_fn=price_lookup_fn,
                tradability_filter_fn=tradability_filter_fn
            )

        # 2. 为下周一预生成调仓订单并锁定
        next_cycle_idx = cycle.cycle_idx + 1
        next_orders = None
        if next_cycle_idx < len(self.cycles):
            next_cycle = self.cycles[next_cycle_idx]
            next_orders = self.commit_orders(
                cycle=next_cycle,
                active_contestants=active_contestants,
                tradability_filter_fn=tradability_filter_fn,
                price_lookup_fn=price_lookup_fn
            )
            if self.run_dir is not None:
                self.export_isolated_orders(next_cycle, next_orders, self.run_dir)

        return settled_orders, next_orders

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

        # 导出所有组合的完整回测路径，包含统一控制基准 BENCHMARK_taotie 与 BENCHMARK_ghost_taotie
        results = {
            key: engine.to_portfolio_path()
            for key, engine in self.engines.items()
        }
        results[("BENCHMARK", "taotie")] = self.taotie_benchmark.engine.to_portfolio_path()
        results[("BENCHMARK", "ghost_taotie")] = self.ghost_taotie_benchmark.engine.to_portfolio_path()
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
                self.adapters[first_c.contestant_id] = create_adapter(
                    first_c,
                    mock=self.mock_mode,
                    use_replay=not self.mock_mode,
                    auth_store_path=self.auth_store_path
                )
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
            "ghost_taotie_engine": self.ghost_taotie_benchmark.engine.export_checkpoint(),
        }

    def load_checkpoint(self, state: Dict[str, Any]):
        """从状态快照字典恢复运行器状态"""
        self.last_completed_cycle_idx = state["last_completed_cycle_idx"]
        self.signal_history = state.get("signal_history", {})

        self.engines = {}
        for key, cp in state.get("engines", {}).items():
            self.engines[key] = PortfolioEngine.from_checkpoint(cp)

        if "taotie_engine" in state or "ghost_taotie_engine" in state:
            self._create_benchmarks()
            if "taotie_engine" in state:
                self.taotie_benchmark.engine = PortfolioEngine.from_checkpoint(state["taotie_engine"])
            if "ghost_taotie_engine" in state:
                self.ghost_taotie_benchmark.engine = PortfolioEngine.from_checkpoint(state["ghost_taotie_engine"])

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

    def export_isolated_orders(
        self,
        cycle: WeeklyCycle,
        orders: Dict[tuple, Any],
        run_dir: Path,
        secret_salt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        严格分层隔离导出本周期的所有实体 orders.csv (不含猴群)。
        命名空间:
          - 参赛选手: runs/<season_id>/private/cycles/cycle_{idx}_{date}/contestants/<cid>/animal_<aid>.csv
          - 独立基准: runs/<season_id>/private/cycles/cycle_{idx}_{date}/benchmarks/taotie_500k.csv 等
        并生成加盐哈希存证清单 (分项 SHA-256 + 周期根哈希 Merkle Root)。
        """
        import hashlib
        import json
        import secrets

        c_idx = cycle.cycle_idx
        c_date = cycle.decision_date.replace("-", "")
        cycle_folder_name = f"cycle_{c_idx:02d}_{c_date}"
        priv_cycle_dir = run_dir / "private" / "cycles" / cycle_folder_name
        priv_cycle_dir.mkdir(parents=True, exist_ok=True)

        salt = secret_salt or secrets.token_hex(16)
        salt_file = priv_cycle_dir / "salt.key"
        with open(salt_file, "w", encoding="utf-8") as f:
            f.write(salt)

        items_manifest = []

        for key, order_obj in orders.items():
            if order_obj is None:
                continue

            entity_type, entity_name = key
            if entity_type == "BENCHMARK":
                target_dir = priv_cycle_dir / "benchmarks"
                target_dir.mkdir(parents=True, exist_ok=True)
                file_name = f"{entity_name}.csv"
                file_path = target_dir / file_name
                item_id = f"benchmark_{entity_name}"
            else:
                cid, aid = key
                target_dir = priv_cycle_dir / "contestants" / cid
                target_dir.mkdir(parents=True, exist_ok=True)
                file_name = f"animal_{aid}.csv"
                file_path = target_dir / file_name
                item_id = f"{cid}_{aid}"

            # 导出标准化 CSV
            order_rows = []
            for inst in order_obj.buy_instruments:
                order_rows.append({
                    "trade_date": order_obj.trade_date,
                    "direction": "BUY",
                    "instrument": inst,
                    "is_first_entry": order_obj.is_first_entry
                })
            for inst in order_obj.sell_instruments:
                order_rows.append({
                    "trade_date": order_obj.trade_date,
                    "direction": "SELL",
                    "instrument": inst,
                    "is_first_entry": order_obj.is_first_entry
                })

            df_order = pd.DataFrame(order_rows)
            df_order.to_csv(file_path, index=False)

            # 计算该文件的加盐 SHA-256
            content_bytes = file_path.read_bytes()
            salted_payload = content_bytes + salt.encode("utf-8") + cycle.decision_date.encode("utf-8")
            file_hash = hashlib.sha256(salted_payload).hexdigest()

            items_manifest.append({
                "item_id": item_id,
                "relative_path": str(file_path.relative_to(run_dir)),
                "num_buys": len(order_obj.buy_instruments),
                "num_sells": len(order_obj.sell_instruments),
                "sha256": file_hash
            })

        # 排序后计算周期的聚合根哈希
        items_manifest.sort(key=lambda x: x["item_id"])
        concat_hashes = "".join([item["sha256"] for item in items_manifest])
        cycle_root_hash = hashlib.sha256((concat_hashes + salt).encode("utf-8")).hexdigest()

        manifest_data = {
            "cycle_idx": c_idx,
            "decision_date": cycle.decision_date,
            "trade_date": cycle.trade_date,
            "cycle_root_hash": cycle_root_hash,
            "total_entities": len(items_manifest),
            "items": items_manifest
        }

        manifest_file = priv_cycle_dir / "manifest.json"
        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, ensure_ascii=False, indent=2)

        return {
            "cycle_folder": priv_cycle_dir,
            "cycle_root_hash": cycle_root_hash,
            "manifest_file": manifest_file,
            "salt": salt,
            "total_orders": len(items_manifest)
        }

