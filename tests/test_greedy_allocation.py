import pytest
import pandas as pd
from arena.portfolio import PortfolioEngine, Order
from arena.calendar import WeeklyCycle


def test_greedy_allocation_improves_capital_utilization():
    # 模拟 10 只股票，价格差异较大 (从 5 元到 50 元)
    prices = {
        "S1": 5.0,    # 1手 = 500
        "S2": 8.0,    # 1手 = 800
        "S3": 12.0,   # 1手 = 1200
        "S4": 18.0,   # 1手 = 1800
        "S5": 25.0,   # 1手 = 2500
        "S6": 30.0,   # 1手 = 3000
        "S7": 40.0,   # 1手 = 4000
        "S8": 50.0,   # 1手 = 5000
    }
    instruments = list(prices.keys())

    def price_lookup(inst: str, date: str, field: str) -> float:
        return prices[inst]

    cycle = WeeklyCycle(
        cycle_idx=0,
        decision_date="2026-07-03",
        trade_date="2026-07-06",
        settle_date="2026-07-10",
        trading_days=["2026-07-06", "2026-07-07", "2026-07-08", "2026-07-09", "2026-07-10"]
    )

    order = Order(
        trade_date="2026-07-06",
        buy_instruments=instruments,
        sell_instruments=[],
        is_first_entry=True
    )

    # 1. 普通模式 (Non-greedy): 资金 10,000 元，分给 8 只股票，每只约 1,240 元
    # 此时 S3 (1200) 刚好可买 1 手，而 S4~S8 (>=1800) 全部买不起
    engine_normal = PortfolioEngine(
        contestant_id="TEST",
        animal_id="normal",
        topk=len(instruments),
        initial_cash=10000.0,
        greedy_allocation=False
    )
    engine_normal.execute_weekly_cycle(cycle, order, price_lookup)
    
    # 普通模式下买入标的较少，剩余大量现金
    assert len(engine_normal.holdings) <= 3
    assert engine_normal.cash_balance > 5000.0  # 超过 50% 现金闲置

    # 2. 贪心瀑布流模式 (Greedy): 相同资金 10,000 元
    engine_greedy = PortfolioEngine(
        contestant_id="TEST",
        animal_id="greedy",
        topk=len(instruments),
        initial_cash=10000.0,
        greedy_allocation=True
    )
    engine_greedy.execute_weekly_cycle(cycle, order, price_lookup)

    # 贪心模式下闲置现金大幅压缩，标的覆盖或资金利用率显著提升
    # 剩余现金应不足以买下当前候选池中最便宜的标的 1 手 (500元)
    assert engine_greedy.cash_balance < 550.0
    assert len(engine_greedy.holdings) >= len(engine_normal.holdings)
    invested_ratio = (10000.0 - engine_greedy.cash_balance) / 10000.0
    assert invested_ratio > 0.94  # 投资仓位超过 94%


def test_greedy_allocation_checkpoint_persistence():
    engine = PortfolioEngine(
        contestant_id="TEST",
        animal_id="taotie",
        topk=0,
        initial_cash=500000.0,
        greedy_allocation=True
    )
    cp = engine.export_checkpoint()
    assert cp.greedy_allocation is True

    restored = PortfolioEngine.from_checkpoint(cp)
    assert restored.greedy_allocation is True
