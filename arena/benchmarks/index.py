"""
arena/benchmarks/index.py
=========================
IndexBenchmark: 公开市场指数基准 (如 CSI300 沪深300)
"""

from typing import Optional, Callable, Dict, Any, List
import pandas as pd
import numpy as np

from arena.benchmarks.base import Benchmark, BenchmarkCategory
from arena.portfolio.types import PortfolioPath, DailyValuation
from arena.calendar import WeeklyCycle


def read_feature_slice(path, start, end):
    """Qlib feature files store the starting calendar offset as float32."""
    with open(path, 'rb') as stream:
        header=np.fromfile(stream,dtype='<f4',count=1)
        data=np.fromfile(stream,dtype='<f4')
    if len(header)!=1 or not np.isfinite(header[0]) or header[0]<0 or int(header[0])!=header[0]:
        raise ValueError('Invalid feature start offset')
    offset=int(header[0])
    if start<offset or end<start or end-offset>=len(data):
        raise ValueError('Index feature does not cover the evaluation window')
    result=data[start-offset:end-offset+1].astype(float)
    if not np.isfinite(result).all() or (result<=0).any():
        raise ValueError('Index feature contains an invalid quote')
    return result


class IndexBenchmark(Benchmark):
    """
    公开市场指数被动基准：
    - 直接跟踪指数本身的价格序列 (以锚定基准日归一化为 1.0000)；
    - 衡量宽基宏观 Beta，为所有主动策略提供最根本的选股有效性基线。
    """

    def __init__(
        self,
        index_symbol: str = "SH000300",
        benchmark_id: str = "csi300",
        display_name: str = "CSI 300 (沪深300)"
    ):
        super().__init__(
            benchmark_id=benchmark_id,
            display_name=display_name,
            category=BenchmarkCategory.INDEX,
            description=f"公开市场大盘基准指数 ({index_symbol})"
        )
        self.index_symbol = index_symbol
        self.daily_nav: Dict[str, float] = {}
        self.base_price: Optional[float] = None

    def step(
        self,
        cycle: WeeklyCycle,
        universe: Optional[List[str]] = None,
        price_lookup_fn: Optional[Callable[[str, str, str], float]] = None,
        tradability_filter_fn: Optional[Callable[[str, str], bool]] = None,
        **kwargs
    ) -> None:
        if price_lookup_fn is None:
            raise ValueError("指数基准推进必须提供 price_lookup_fn")

        # 对周期内的每一个交易日提取指数收盘价并归一化
        for day in cycle.trading_days:
            price = price_lookup_fn(self.index_symbol, day, "close")
            if self.base_price is None:
                # 以周期首日开盘价或前一收盘价为基准
                open_p = price_lookup_fn(self.index_symbol, day, "open")
                self.base_price = open_p if open_p > 0 else price

            nav = price / self.base_price if self.base_price > 0 else 1.0
            self.daily_nav[day] = nav

    def to_portfolio_path(self) -> PortfolioPath:
        vals = []
        prev_nav = 1.0
        for d in sorted(self.daily_nav.keys()):
            cur_nav = self.daily_nav[d]
            ret = (cur_nav / prev_nav) - 1.0 if prev_nav > 0 else 0.0
            vals.append(DailyValuation(
                date=d,
                cash=0.0,
                holdings_value=cur_nav,
                total_asset=cur_nav,
                nav=cur_nav,
                daily_return=ret,
                num_holdings=1
            ))
            prev_nav = cur_nav

        return PortfolioPath(
            contestant_id="BENCHMARK",
            animal_id=self.benchmark_id,
            daily_valuations=vals,
            weekly_settlements=[],
            trades=[],
            final_holdings={},
            diagnostics={}
        )
