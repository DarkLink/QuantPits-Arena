"""
tests/test_portfolio_weekly_engine.py
=====================================
周频组合执行引擎的前置与实现测试
"""

import pandas as pd
import numpy as np
import pytest

from arena.portfolio import PortfolioEngine, Order
from arena.calendar import WeeklyCycle


def test_first_week_full_entry():
    """验证首周满额建仓契约：买入恰好 TopK 只，卖出为空"""
    stocks = [f"STOCK_{i:02d}" for i in range(50)]
    score = pd.Series(np.linspace(0.1, 0.9, 50), index=stocks)

    engine = PortfolioEngine(contestant_id="CONTESTANT_A", animal_id="robot", topk=22)
    order = engine.generate_order(score, topk=22, n_drop=3, trade_date="2026-07-06", is_first_entry=True)

    assert order is not None
    assert len(order.buy_instruments) == 22, "首周应一次性买入 22 只股票"
    assert len(order.sell_instruments) == 0, "首周不应有任何卖出订单"
    assert order.is_first_entry is True


def test_subsequent_weekly_rebalance():
    """验证后续调仓契约：卖出最低 n_drop，买入最高 n_drop，总持仓数保持 TopK"""
    stocks = [f"STOCK_{i:02d}" for i in range(50)]
    score_w1 = pd.Series(np.linspace(0.1, 0.9, 50), index=stocks)

    engine = PortfolioEngine(contestant_id="CONTESTANT_A", animal_id="robot", topk=22)
    # 模拟首周已持有 22 只
    top22 = list(score_w1.nlargest(22).index)
    for s in top22:
        engine.holdings[s] = 1000.0

    # Week 2 得分变化：把持仓中的 3 只分数打到极低
    score_w2 = score_w1.copy()
    for s in top22[:3]:
        score_w2[s] = 0.001

    order = engine.generate_order(score_w2, topk=22, n_drop=3, trade_date="2026-07-13", is_first_entry=False)

    assert order is not None
    assert len(order.sell_instruments) == 3, "调仓应卖出 3 只"
    assert len(order.buy_instruments) == 3, "调仓应买入 3 只"
    for s in top22[:3]:
        assert s in order.sell_instruments, "分数垫底的持仓标的必须被卖出"


def test_tradability_buffer_fallback():
    """
    验证可交易性顺延缓冲 (Tradability Buffer)：
    若 Top 22 只中有 2 只停牌，自动顺延选入第 23、24 只补足，确保刚好买入 22 只。
    """
    stocks = [f"STOCK_{i:02d}" for i in range(50)]
    # 得分从高到低排列
    score = pd.Series(np.linspace(0.9, 0.1, 50), index=stocks)

    # 假定排在第 1 名和第 2 名的股票停牌
    suspended_stocks = {stocks[0], stocks[1]}

    def mock_tradability_filter(inst: str, date: str) -> bool:
        return inst not in suspended_stocks

    engine = PortfolioEngine(contestant_id="CONTESTANT_A", animal_id="robot", topk=22)
    order = engine.generate_order(
        score,
        topk=22,
        n_drop=3,
        trade_date="2026-07-06",
        is_first_entry=True,
        tradability_filter=mock_tradability_filter
    )

    assert order is not None
    assert len(order.buy_instruments) == 22, "通过顺延缓冲机制，最终买入标的严格等于 22 只"
    assert stocks[0] not in order.buy_instruments, "停牌股票不应被买入"
    assert stocks[1] not in order.buy_instruments, "停牌股票不应被买入"
    # 顺延选入了第 22 和第 23 索引位的股票（即第 23、24 名）
    assert stocks[22] in order.buy_instruments
    assert stocks[23] in order.buy_instruments


def test_execute_weekly_cycle_flow_and_daily_valuation():
    """验证周频撮合、日频估值与周结算完整流程"""
    stocks = [f"STOCK_{i:02d}" for i in range(25)]
    score = pd.Series(np.linspace(0.1, 0.9, 25), index=stocks)

    cycle = WeeklyCycle(
        cycle_idx=0,
        decision_date="2026-07-03",
        trade_date="2026-07-06",
        settle_date="2026-07-10",
        trading_days=["2026-07-06", "2026-07-07", "2026-07-08", "2026-07-09", "2026-07-10"]
    )

    engine = PortfolioEngine(
        contestant_id="CONTESTANT_A",
        animal_id="robot",
        initial_cash=100_000_000.0,
        deal_price_mode="open"
    )

    order = engine.generate_order(score, topk=22, n_drop=3, trade_date=cycle.trade_date, is_first_entry=True)

    # 模拟价格函数: 股价恒定为 10.0 元
    def mock_price_lookup(inst: str, date: str, field: str) -> float:
        return 10.0

    settlement = engine.execute_weekly_cycle(cycle, order, mock_price_lookup)

    assert settlement.week_idx == 0
    assert settlement.num_holdings == 22
    assert len(engine.daily_valuations) == 5, "周内 5 个交易日必须每日核算 NAV"
    # 首周扣除手续费后，净值略低于 1.0 (约 0.9995)
    assert 0.9990 < settlement.end_nav < 1.0000
    assert settlement.weekly_cost > 0
