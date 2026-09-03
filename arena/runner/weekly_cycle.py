"""
arena/runner/weekly_cycle.py
============================
周频同步执行主运行器 (Weekly Cycle Runner)
"""

from typing import List, Dict, Optional, Callable, Any
from pathlib import Path
import datetime
import pandas as pd
import numpy as np

from arena.config import (
    DEFAULT_ANCHOR_DATE,
    DEFAULT_END_DATE,
    DEFAULT_TOPK,
    DEFAULT_DEAL_PRICE,
    RUNS_DIR,
)
from arena.calendar import TradingCalendar, WeeklyCycle
from arena.contestants.manifest import ContestantManifest
from arena.contestants.registry import ContestantRegistry
from arena.contestants.adapters import create_adapter, BaseInferenceAdapter
from arena.animals import get_all_animals, Animal
from arena.portfolio import PortfolioEngine, PortfolioPath
from arena.controls import MonkeyColony, RockBenchmark


class WeeklyCycleRunner:
    """
    周频同步执行运行器：
    - 按真实交易日历循环推进周期 (Cycle 0, 1, 2, ... 7)
    - 统一协调 Contestant 预测 -> Animal 信号变换 -> PortfolioEngine 调仓执行与日频盯市估值
    - 同步推进 Monkey Colony 零假设对照组与 Rock 基准
    """

    def __init__(
        self,
        anchor_date: str = DEFAULT_ANCHOR_DATE,
        end_date: str = DEFAULT_END_DATE,
        topk: int = DEFAULT_TOPK,
        deal_price_mode: str = DEFAULT_DEAL_PRICE,
        mock_mode: bool = False,
        calendar: Optional[TradingCalendar] = None,
        registry: Optional[ContestantRegistry] = None,
        animals: Optional[List[Animal]] = None,
    ):
        self.anchor_date = anchor_date
        self.end_date = end_date
        self.topk = topk
        self.deal_price_mode = deal_price_mode
        self.mock_mode = mock_mode

        self.calendar = calendar or TradingCalendar()
        self.registry = registry or ContestantRegistry()
        self.animals = animals or get_all_animals()

        self.cycles = self.calendar.build_weekly_cycles(anchor_date, end_date)
        self.monkey_colony = MonkeyColony(colony_size=100)  # 默认 100 只用于快速执行，支持配置 1000
        self.rock_benchmark = RockBenchmark()

        # 运行实例映射: {(contestant_id, animal_id): PortfolioEngine}
        self.engines: Dict[tuple, PortfolioEngine] = {}
        # 各选手的历史信号记录: {contestant_id: {cycle_idx: score_series}}
        self.signal_history: Dict[str, Dict[int, pd.Series]] = {}

        # 适配器缓存: {contestant_id: adapter}
        self.adapters: Dict[str, BaseInferenceAdapter] = {}

    def _init_engines(self, contestants: List[ContestantManifest]):
        """初始化所有 (Contestant, Animal) 组合的回测引擎"""
        self.engines = {}
        self.signal_history = {}
        self.adapters = {}

        for c in contestants:
            cid = c.contestant_id
            self.signal_history[cid] = {}
            self.adapters[cid] = create_adapter(c, mock=self.mock_mode)

            for a in self.animals:
                key = (cid, a.animal_id)
                self.engines[key] = PortfolioEngine(
                    contestant_id=cid,
                    animal_id=a.animal_id,
                    topk=self.topk,
                    deal_price_mode=self.deal_price_mode
                )

    def run(
        self,
        contestants: Optional[List[ContestantManifest]] = None,
        price_lookup_fn: Optional[Callable[[str, str, str], float]] = None,
        tradability_filter_fn: Optional[Callable[[str, str], bool]] = None,
        max_cycles: Optional[int] = None
    ) -> Dict[tuple, PortfolioPath]:
        """
        执行周频同步推进回测。

        Args:
            contestants: 参赛选手列表（默认全部注册选手）
            price_lookup_fn: 价格查询函数 (instrument, date, field) -> float
            tradability_filter_fn: 可交易性过滤函数 (instrument, date) -> bool
            max_cycles: 最大运行周期数（用于快速验证，None 表示跑完全部周期）
        """
        active_contestants = contestants or self.registry.list_contestants()
        self._init_engines(active_contestants)

        # 默认 Mock 价格生成器（以标的基准价为底，叠加小幅微量波动）
        if price_lookup_fn is None:
            def default_price_lookup(inst: str, date: str, field: str) -> float:
                base = (abs(hash(inst)) % 3000 + 1000) / 100.0  # 10.0 ~ 40.0 元
                day_offset = ((abs(hash(f"{inst}_{date}")) % 20) - 10) / 1000.0  # -1% ~ +1% 波动
                if field == "open":
                    return base
                return base * (1.0 + day_offset)
            price_lookup_fn = default_price_lookup

        cycles_to_run = self.cycles[:max_cycles] if max_cycles else self.cycles

        for cycle in cycles_to_run:
            c_idx = cycle.cycle_idx

            # 1. 决策日（周五收盘）：各模型产出本周期的原始预测分数
            for c in active_contestants:
                cid = c.contestant_id
                adapter = self.adapters[cid]

                raw_score = adapter.predict(
                    start_date=cycle.decision_date,
                    end_date=cycle.decision_date
                )
                self.signal_history[cid][c_idx] = raw_score

            # 2. 各 Animal 进行信号变换并生成下周一的订单
            for c in active_contestants:
                cid = c.contestant_id
                history = self.signal_history[cid]
                current_raw = history[c_idx]

                for a in self.animals:
                    key = (cid, a.animal_id)
                    engine = self.engines[key]

                    # 动物信号变换（处理 Sloth 方案 B 空仓延迟、Koala 排名反转等）
                    transformed_score = a.transform_signal(
                        current_score=current_raw,
                        history_scores=history,
                        cycle_idx=c_idx
                    )

                    policy = a.get_portfolio_policy()
                    n_drop = policy.get("n_drop", 3)
                    topk = policy.get("topk", self.topk)

                    is_first = (c_idx == 0)
                    order = engine.generate_order(
                        score=transformed_score,
                        topk=topk,
                        n_drop=n_drop,
                        trade_date=cycle.trade_date,
                        is_first_entry=is_first,
                        tradability_filter=tradability_filter_fn
                    )

                    # 3. 撮合成交与周内日频估值
                    engine.execute_weekly_cycle(
                        cycle=cycle,
                        order=order,
                        price_lookup=price_lookup_fn
                    )

        # 导出所有组合的完整回测路径
        results = {
            key: engine.to_portfolio_path()
            for key, engine in self.engines.items()
        }
        return results
