"""
arena/controls/taotie.py
=======================
Taotie (饕餮) 独立基准控制组 (Capital-Constrained Full-Universe Executable Benchmark)
"""

from typing import Optional, Callable, Dict, Any, List
import pandas as pd

from arena.portfolio.engine import PortfolioEngine
from arena.portfolio.types import PortfolioPath
from arena.calendar import WeeklyCycle


class TaotieBenchmark:
    """
    全池吞噬独立基准控制组：
    - 与模型信号完全无关（纯被动全池复制）；
    - 在 50 万初始资金、100 股最小交易单位约束下，尝试买入并持有整个有效股票池；
    - DropN=0，仅依据股票的出池与入池进行被动换仓；
    - 作为全场统一的物理可执行全市场基准 (BENCHMARK_TAOTIE)。
    """

    def __init__(self, initial_cash: float = 500_000.0, deal_price_mode: str = "open"):
        self.contestant_id = "BENCHMARK"
        self.animal_id = "taotie"
        self.engine = PortfolioEngine(
            contestant_id=self.contestant_id,
            animal_id=self.animal_id,
            topk=0,  # 0 表示动态匹配全部有效池
            initial_cash=initial_cash,
            deal_price_mode=deal_price_mode
        )

    def step(
        self,
        cycle: WeeklyCycle,
        universe: List[str],
        price_lookup_fn: Callable[[str, str, str], float],
        tradability_filter_fn: Optional[Callable[[str, str], bool]] = None,
    ):
        """
        单周增量推进饕餮基准。
        """
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
        return self.engine.to_portfolio_path()
