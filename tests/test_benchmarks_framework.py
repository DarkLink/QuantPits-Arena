"""
tests/test_benchmarks_framework.py
==================================
验证统一基准体系 (arena.benchmarks) 契约、Taotie 兼容性、Ghost Taotie 与 IndexBenchmark
"""

import pytest
import pandas as pd
from arena.calendar import WeeklyCycle
from arena.benchmarks import (
    Benchmark,
    BenchmarkCategory,
    TaotieBenchmark,
    GhostTaotieBenchmark,
    IndexBenchmark,
)
from arena.controls import TaotieBenchmark as LegacyTaotieBenchmark


def test_benchmark_backward_compatibility():
    """验证从 arena.controls 导入的 TaotieBenchmark 与新模块保持同源"""
    assert LegacyTaotieBenchmark is TaotieBenchmark
    tb = TaotieBenchmark(initial_cash=500_000.0)
    assert isinstance(tb, Benchmark)
    assert tb.category == BenchmarkCategory.EXECUTABLE
    assert tb.contestant_id == "BENCHMARK"
    assert tb.animal_id == "taotie"


def test_taotie_benchmark_step():
    """验证 Taotie 增量单步推进与 PortfolioPath 输出"""
    tb = TaotieBenchmark(initial_cash=500_000.0)
    cycle = WeeklyCycle(
        cycle_idx=0,
        decision_date="2026-07-03",
        trade_date="2026-07-06",
        settle_date="2026-07-10",
        trading_days=["2026-07-06", "2026-07-07", "2026-07-08", "2026-07-09", "2026-07-10"]
    )
    universe = ["STOCK_001", "STOCK_002", "STOCK_003"]

    def dummy_price(inst: str, date: str, field: str) -> float:
        return 10.0 if field == "open" else 10.5

    tb.step(cycle, universe=universe, price_lookup_fn=dummy_price)
    path = tb.to_portfolio_path()
    assert path is not None
    assert path.daily_valuations[-1].nav > 1.0
    # 首周包含锚定日 (2026-07-03) 初始点 + 5 个交易日 = 6 个点
    assert len(path.nav_series) == 6

    metrics = tb.get_summary_metrics()
    assert metrics["benchmark_id"] == "taotie"
    assert metrics["category"] == "EXECUTABLE"


def test_ghost_taotie_unconstrained_property():
    """验证 Ghost Taotie (1亿资金) 面对多标的时的高持有率与无拒单特性"""
    gtb = GhostTaotieBenchmark(initial_cash=100_000_000.0)
    assert gtb.category == BenchmarkCategory.THEORETICAL
    assert gtb.benchmark_id == "ghost_taotie"

    cycle = WeeklyCycle(
        cycle_idx=0,
        decision_date="2026-07-03",
        trade_date="2026-07-06",
        settle_date="2026-07-10",
        trading_days=["2026-07-06", "2026-07-10"]
    )
    # 模拟 50 只高价股票 (每股 100 元)
    large_universe = [f"EXPENSIVE_STOCK_{i:03d}" for i in range(50)]

    def dummy_expensive_price(inst: str, date: str, field: str) -> float:
        return 100.0

    gtb.step(cycle, universe=large_universe, price_lookup_fn=dummy_expensive_price)
    path = gtb.to_portfolio_path()
    assert path is not None
    # 验证 50 只标的全额买入成功
    assert len(gtb.engine.holdings) == 50
    assert path.diagnostics["unaffordable_buy_count"] == 0


def test_index_benchmark():
    """验证 IndexBenchmark 市场指数提取与每日归一化 NAV"""
    ib = IndexBenchmark(index_symbol="SH000300", benchmark_id="csi300")
    assert ib.category == BenchmarkCategory.INDEX

    cycle = WeeklyCycle(
        cycle_idx=0,
        decision_date="2026-07-03",
        trade_date="2026-07-06",
        settle_date="2026-07-10",
        trading_days=["2026-07-06", "2026-07-07", "2026-07-08", "2026-07-09", "2026-07-10"]
    )

    prices = {
        "2026-07-06": 4000.0,
        "2026-07-07": 4040.0,
        "2026-07-08": 4080.0,
        "2026-07-09": 4020.0,
        "2026-07-10": 4100.0,
    }

    def dummy_index_price(inst: str, date: str, field: str) -> float:
        if field == "open" and date == "2026-07-06":
            return 4000.0
        return prices.get(date, 4000.0)

    ib.step(cycle, price_lookup_fn=dummy_index_price)
    path = ib.to_portfolio_path()
    assert len(path.nav_series) == 5
    assert path.nav_series.iloc[0] == 1.0
    assert path.nav_series.iloc[-1] == 4100.0 / 4000.0
    assert path.total_return == pytest.approx(0.025)
