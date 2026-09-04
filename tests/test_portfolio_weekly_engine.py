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
        initial_cash=500_000.0,
        deal_price_mode="open"
    )

    order = engine.generate_order(score, topk=22, n_drop=3, trade_date=cycle.trade_date, is_first_entry=True)

    # 模拟价格函数: 股价恒定为 10.0 元
    def mock_price_lookup(inst: str, date: str, field: str) -> float:
        return 10.0

    settlement = engine.execute_weekly_cycle(cycle, order, mock_price_lookup)

    assert settlement.week_idx == 0
    assert settlement.num_holdings == 22
    assert len(engine.daily_valuations) == 6, "T0 锚定日 + 周内 5 个交易日共 6 次估值"
    # 首周扣除手续费后，净值略低于 1.0 (约 0.9995)
    assert 0.9990 < settlement.end_nav < 1.0000
    assert settlement.weekly_cost > 0


def test_skip_unaffordable_stock_and_no_fractional_shares():
    """
    验证不买碎股与资金门槛顺延契约：
    - 初始资金 50,000 元，目标买入 2 只，单只预算约 25,000 元
    - STOCK_0 (得分最高 0.99)，但股价 300 元，一手需 30,000 元 -> 买不起，必须跳过顺延！
    - STOCK_1 (得分 0.88)，股价 20 元，一手 2,000 元 -> 买得起
    - STOCK_2 (得分 0.77)，股价 10 元，一手 1,000 元 -> 买得起
    - 验证最终订单买入 STOCK_1 和 STOCK_2，且股数均为 100 的整数倍
    """
    score = pd.Series([0.99, 0.88, 0.77], index=["STOCK_HIGH", "STOCK_MID", "STOCK_LOW"])
    prices = {
        "STOCK_HIGH": 300.0,
        "STOCK_MID": 20.0,
        "STOCK_LOW": 10.0,
    }

    def price_lookup(inst: str, date: str, field: str) -> float:
        return prices[inst]

    engine = PortfolioEngine(
        contestant_id="CONTESTANT_A",
        animal_id="robot",
        topk=2,
        initial_cash=50_000.0,
        allow_fractional_shares=False,
        lot_size=100
    )

    order = engine.generate_order(
        score=score,
        topk=2,
        trade_date="2026-07-06",
        is_first_entry=True,
        price_lookup=price_lookup
    )

    assert order is not None
    assert "STOCK_HIGH" not in order.buy_instruments, "买不起一手 (300元*100=30000 > 25000) 的标的必须跳过"
    assert order.buy_instruments == ["STOCK_MID", "STOCK_LOW"], "应自动顺延选入后续买得起的标的"

    # 执行买入，验证股数无碎股（全部是 100 的整数倍）
    cycle = WeeklyCycle(
        cycle_idx=0,
        decision_date="2026-07-03",
        trade_date="2026-07-06",
        settle_date="2026-07-10",
        trading_days=["2026-07-06"]
    )
    engine.execute_weekly_cycle(cycle, order, price_lookup)

    for inst, shares in engine.holdings.items():
        assert shares > 0
        assert shares % 100 == 0, f"{inst} 持仓股数 {shares} 必须是一手 (100股) 的整数倍，严禁碎股！"


def test_out_of_pool_priority_and_dropn_cap():
    """
    验证出池被动调仓核心规则：
    1. 出池优先于 DROP；
    2. 调仓卖出上限不超过 DropN；
    3. 若出池数 < DropN，出池先卖，剩余额度继续主动 Drop；若出池数 >= DropN，出池卖至上限，多余留待下期。
    """
    stocks_w1 = [f"STOCK_{i:02d}" for i in range(30)]
    score_w1 = pd.Series(np.linspace(0.9, 0.1, 30), index=stocks_w1)

    engine = PortfolioEngine(contestant_id="CONTESTANT_A", animal_id="robot", topk=10)
    # 模拟持仓 STOCK_00 ~ STOCK_09 共 10 只
    for s in stocks_w1[:10]:
        engine.holdings[s] = 1000.0

    # Week 2 出现出池情况：
    # 假设 STOCK_00, STOCK_01, STOCK_02, STOCK_03 共 4 只股票出池（不在 score_w2 中）
    in_pool_stocks = [s for s in stocks_w1 if s not in {"STOCK_00", "STOCK_01", "STOCK_02", "STOCK_03"}]
    score_w2 = pd.Series(np.linspace(0.9, 0.1, len(in_pool_stocks)), index=in_pool_stocks)

    # 场景 A: DropN = 2 (出池 4 只 > DropN 2)
    # 规则：卖出上限不超过 DropN (2)，必须优先卖出 2 只出池标的，多余 2 只出池标的保留至下期
    order_cap2 = engine.generate_order(score_w2, topk=10, n_drop=2, trade_date="2026-07-13", is_first_entry=False)
    assert order_cap2 is not None
    assert len(order_cap2.sell_instruments) == 2, "总卖出数量上限严格不超过 DropN=2"
    assert len(order_cap2.buy_instruments) == 2, "补足卖出数量以维持目标持仓"
    assert all(s in {"STOCK_00", "STOCK_01", "STOCK_02", "STOCK_03"} for s in order_cap2.sell_instruments), "卖出必须优先从出池标的中选取"

    # 场景 B: DropN = 5 (出池 4 只 < DropN 5)
    # 规则：4 只出池先卖，剩余 1 个名额进行主动得分 Drop
    order_cap5 = engine.generate_order(score_w2, topk=10, n_drop=5, trade_date="2026-07-13", is_first_entry=False)
    assert order_cap5 is not None
    assert len(order_cap5.sell_instruments) == 5, "总卖出正好达到 DropN=5"
    assert len(order_cap5.buy_instruments) == 5
    # 前 4 只必须包含所有出池标的
    for s in ["STOCK_00", "STOCK_01", "STOCK_02", "STOCK_03"]:
        assert s in order_cap5.sell_instruments
    # 第 5 只是在池标的中得分最低的标的
    in_pool_sells = [s for s in order_cap5.sell_instruments if s not in {"STOCK_00", "STOCK_01", "STOCK_02", "STOCK_03"}]
    assert len(in_pool_sells) == 1


def test_taotie_passive_pool_rebalance():
    """
    验证饕餮 (Taotie) 全池纯被动出入池调仓：
    1. 首周全池买入所有标的；
    2. 后续周期若有标的出池，全量被动卖出；若有标的入池，全量被动买入；不受 DropN=0 限制。
    """
    universe_w1 = [f"STOCK_{i:02d}" for i in range(20)]
    score_w1 = pd.Series(np.linspace(0.9, 0.1, 20), index=universe_w1)

    engine = PortfolioEngine(contestant_id="CONTESTANT_A", animal_id="taotie", topk=0)
    order_w1 = engine.generate_order(score_w1, topk=0, n_drop=0, trade_date="2026-07-06", is_first_entry=True, passive_pool=True)

    assert len(order_w1.buy_instruments) == 20, "首周应买入全池 20 只标的"
    assert len(order_w1.sell_instruments) == 0

    # 模拟持仓
    for s in universe_w1:
        engine.holdings[s] = 500.0

    # Week 2: STOCK_00, STOCK_01 出池；同时新增 STOCK_98, STOCK_99 入池
    universe_w2 = [s for s in universe_w1 if s not in {"STOCK_00", "STOCK_01"}] + ["STOCK_98", "STOCK_99"]
    score_w2 = pd.Series(np.linspace(0.9, 0.1, len(universe_w2)), index=universe_w2)

    order_w2 = engine.generate_order(score_w2, topk=0, n_drop=0, trade_date="2026-07-13", is_first_entry=False, passive_pool=True)

    assert order_w2 is not None
    assert set(order_w2.sell_instruments) == {"STOCK_00", "STOCK_01"}, "出池标的应全部被动卖出"
    assert set(order_w2.buy_instruments) == {"STOCK_98", "STOCK_99"}, "新入池标的应全部被动买入"

