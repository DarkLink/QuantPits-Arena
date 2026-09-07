"""
arena/benchmarks/ghost_taotie.py
================================
Ghost Taotie (幽灵饕餮) — 理论全池等权基准 (Theoretical Unconstrained Universe Benchmark)
"""

from typing import Optional, Callable, Dict, Any, List
import pandas as pd

from arena.benchmarks.base import Benchmark, BenchmarkCategory
from arena.portfolio.engine import PortfolioEngine
from arena.portfolio.types import PortfolioPath
from arena.calendar import WeeklyCycle


class GhostTaotieBenchmark(Benchmark):
    """
    幽灵饕餮基准：
    - 定位为“全市场理论等权无偏 Beta 基准”；
    - 采用机构大资金规模 (默认 1 亿元: 100,000,000.0)，单标的配额超 40 万元；
    - 彻底消解 100 股整手约束导致的高价股系统性拒单失真，买单受阻率接近 0；
    - 调仓周频、估值日频，依然计入买卖印花税与佣金，精准刻画理论全池等权潜能。
    """

    def __init__(
        self,
        initial_cash: float = 100_000_000.0,
        deal_price_mode: str = "open",
        benchmark_id: str = "ghost_taotie",
        display_name: str = "Ghost Taotie (全池理论等权)"
    ):
        super().__init__(
            benchmark_id=benchmark_id,
            display_name=display_name,
            category=BenchmarkCategory.THEORETICAL,
            description="大资金规模(1亿元)消解整手摩擦的全池理论等权基准"
        )
        self.contestant_id = "BENCHMARK"
        self.animal_id = benchmark_id
        self.initial_cash = initial_cash
        self.deal_price_mode = deal_price_mode
        self.engine = PortfolioEngine(
            contestant_id=self.contestant_id,
            animal_id=self.animal_id,
            topk=0,  # 全池等权
            initial_cash=initial_cash,
            deal_price_mode=deal_price_mode
        )

    def step(
        self,
        cycle: WeeklyCycle,
        universe: Optional[List[str]] = None,
        price_lookup_fn: Optional[Callable[[str, str, str], float]] = None,
        tradability_filter_fn: Optional[Callable[[str, str], bool]] = None,
        **kwargs
    ) -> None:
        if universe is None:
            raise ValueError("幽灵饕餮推进必须提供当前周期的 universe 列表")
        if price_lookup_fn is None:
            raise ValueError("幽灵饕餮推进必须提供 price_lookup_fn")

        is_first = (cycle.cycle_idx == 0)
        mock_score = pd.Series(1.0, index=universe)

        order = self.engine.generate_order(
            score=mock_score,
            topk=0,
            n_drop=0,
            trade_date=cycle.trade_date,
            is_first_entry=is_first,
            tradability_filter=tradability_filter_fn,
            price_lookup=price_lookup_fn,
            passive_pool=True
        )

        self.engine.execute_weekly_cycle(
            cycle=cycle,
            order=order,
            price_lookup=price_lookup_fn
        )

    def to_portfolio_path(self) -> PortfolioPath:
        return self.engine.to_portfolio_path()
