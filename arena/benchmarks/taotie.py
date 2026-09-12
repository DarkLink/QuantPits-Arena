"""
arena/benchmarks/taotie.py
==========================
Taotie (饕餮) 物理可执行全池基准 (Capital-Constrained Full-Universe Executable Benchmark)
"""

from typing import Optional, Callable, Dict, Any, List
import pandas as pd

from arena.benchmarks.base import Benchmark, BenchmarkCategory
from arena.portfolio.engine import PortfolioEngine
from arena.portfolio.types import PortfolioPath
from arena.calendar import WeeklyCycle


class TaotieBenchmark(Benchmark):
    """
    全池吞噬物理独立基准：
    - 与模型信号完全无关（纯被动全池复制）；
    - 在初始资金（默认 50 万）、100 股最小交易单位约束下，尝试买入并持有整个有效股票池；
    - DropN=0，仅依据股票的出池与入池进行被动换仓；
    - 作为全场统一的物理可执行全市场基准 (BENCHMARK_taotie)。
    """

    def __init__(
        self,
        initial_cash: float = 500_000.0,
        deal_price_mode: str = "open",
        benchmark_id: str = "taotie",
        display_name: str = "Taotie (全池物理被动)"
    ):
        super().__init__(
            benchmark_id=benchmark_id,
            display_name=display_name,
            category=BenchmarkCategory.EXECUTABLE,
            description="50万初始资金与100股整手约束下的全池被动执行基准"
        )
        self.contestant_id = "BENCHMARK"
        self.animal_id = benchmark_id
        self.initial_cash = initial_cash
        self.deal_price_mode = deal_price_mode
        self.engine = PortfolioEngine(
            contestant_id=self.contestant_id,
            animal_id=self.animal_id,
            topk=0,  # 0 表示动态匹配全部有效池
            initial_cash=initial_cash,
            deal_price_mode=deal_price_mode,
            greedy_allocation=True  # 启用贪心瀑布流再分配，消除全池大容量一手约束导致的死现金沉淀
        )

    def step(
        self,
        cycle: WeeklyCycle,
        universe: Optional[List[str]] = None,
        price_lookup_fn: Optional[Callable[[str, str, str], float]] = None,
        tradability_filter_fn: Optional[Callable[[str, str], bool]] = None,
        **kwargs
    ) -> None:
        """
        单周增量推进饕餮基准。
        """
        if universe is None:
            raise ValueError("饕餮基准推进必须提供当前周期的 universe 列表")
        if price_lookup_fn is None:
            raise ValueError("饕餮基准推进必须提供 price_lookup_fn")

        is_first = (cycle.cycle_idx == 0)
        # 饕餮使用 mock 均匀打分，所有池内标的同等优先级
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

    def run(
        self,
        cycles: List[WeeklyCycle],
        universe_provider_fn: Callable[[str], List[str]],
        price_lookup_fn: Callable[[str, str, str], float],
        tradability_filter_fn: Optional[Callable[[str, str], bool]] = None,
    ) -> PortfolioPath:
        """
        全量批量运行饕餮基准。
        """
        for cycle in cycles:
            universe = universe_provider_fn(cycle.decision_date)
            self.step(cycle, universe, price_lookup_fn, tradability_filter_fn)
        return self.to_portfolio_path()
