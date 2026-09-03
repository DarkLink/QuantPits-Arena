"""
tests/test_p9_invariants.py
===========================
P9 理论必然成立的不变式自动化测试套件 (Invariants Tests)

包含 8 个必然成立测试：
1. Test 1: Transaction cost = 0 时，Rabbit-2 净收益等于毛收益
2. Test 2: 所有模型输入相同 ranking 时，同一种动物的 NAV 曲线完全相同
3. Test 3: Robot (DropN=1) 必须与 Turtle (DropN=1) 表现完全相同
4. Test 4: Sloth (delay_weeks=0) 必须与 Robot 完全相同
5. Test 5: Rabbit-2 调仓时，若 target Top-22 完全不变，换手应为 0（无无效买卖）
6. Test 6: Koala 两次反转 rank(rank(signal)) 必须严格恢复原始排名
7. Test 7: 价格全部固定不变且 cost=0 时，所有策略最终 NAV 恒等于 1.000000
8. Test 8: 价格固定不变且 cost>0 时，净值亏损必须恰好等于累计扣除的手续费
"""

import pytest
import pandas as pd
import numpy as np

from arena.portfolio import PortfolioEngine, Order
from arena.portfolio.costs import CostModel
from arena.calendar import WeeklyCycle
from arena.animals import Robot, Sloth, Turtle, Koala, Rabbit


def test_invariant_1_cost_zero():
    """Test 1: 费用为 0 时，净收益恒等于毛收益"""
    stocks = [f"STOCK_{i:02d}" for i in range(25)]
    score = pd.Series(np.linspace(0.1, 0.9, 25), index=stocks)

    free_cost_model = CostModel(open_cost=0.0, close_cost=0.0, min_cost=0.0)
    engine = PortfolioEngine(
        contestant_id="CONTESTANT_A",
        animal_id="rabbit-2",
        initial_cash=500_000.0,
        cost_model=free_cost_model
    )

    cycle = WeeklyCycle(
        cycle_idx=0,
        decision_date="2026-07-03",
        trade_date="2026-07-06",
        settle_date="2026-07-10",
        trading_days=["2026-07-06", "2026-07-10"]
    )

    order = engine.generate_order(score, topk=22, n_drop=22, trade_date=cycle.trade_date, is_first_entry=True)
    # 模拟价格恒定 10.0 元
    engine.execute_weekly_cycle(cycle, order, lambda inst, d, f: 10.0)

    assert engine.trades, "应当有交易发生"
    total_trade_cost = sum(t.cost for t in engine.trades)
    assert total_trade_cost == 0.0, "零费率下累计手续费必须严格为 0"
    assert np.isclose(engine.daily_valuations[-1].nav, 1.0), "价格不变且零费率下 NAV 必须严格为 1.000000"


def test_invariant_2_same_ranking_same_nav():
    """Test 2: 输入相同 ranking 时，同种动物的 NAV 必须完全重合，不得受模型 ID 干扰"""
    stocks = [f"STOCK_{i:02d}" for i in range(25)]
    score = pd.Series(np.linspace(0.1, 0.9, 25), index=stocks)

    engine_A = PortfolioEngine("MODEL_X", "robot", initial_cash=500_000.0)
    engine_B = PortfolioEngine("MODEL_Y", "robot", initial_cash=500_000.0)

    cycle = WeeklyCycle(
        cycle_idx=0,
        decision_date="2026-07-03",
        trade_date="2026-07-06",
        settle_date="2026-07-10",
        trading_days=["2026-07-06", "2026-07-10"]
    )

    order_A = engine_A.generate_order(score, topk=22, n_drop=3, trade_date=cycle.trade_date, is_first_entry=True)
    order_B = engine_B.generate_order(score, topk=22, n_drop=3, trade_date=cycle.trade_date, is_first_entry=True)

    engine_A.execute_weekly_cycle(cycle, order_A, lambda inst, d, f: 10.0)
    engine_B.execute_weekly_cycle(cycle, order_B, lambda inst, d, f: 10.0)

    navs_A = [v.nav for v in engine_A.daily_valuations]
    navs_B = [v.nav for v in engine_B.daily_valuations]

    assert np.allclose(navs_A, navs_B), "相同打分下不同模型名称的 NAV 必须完全一致"


def test_invariant_3_robot_drop1_equals_turtle():
    """Test 3: Robot (DropN=1) 与 Turtle 的策略行为与生成订单必须完全相同"""
    robot_drop1 = Robot(topk=22, n_drop=1)
    turtle = Turtle(topk=22)

    stocks = [f"STOCK_{i:02d}" for i in range(30)]
    score = pd.Series(np.linspace(0.1, 0.9, 30), index=stocks)

    engine_r = PortfolioEngine("TEST", "robot", topk=22)
    engine_t = PortfolioEngine("TEST", "turtle", topk=22)

    # 预设相同初始持仓
    for s in stocks[:22]:
        engine_r.holdings[s] = 1000.0
        engine_t.holdings[s] = 1000.0

    order_r = engine_r.generate_order(score, topk=22, n_drop=robot_drop1.n_drop, trade_date="2026-07-13")
    order_t = engine_t.generate_order(score, topk=22, n_drop=turtle.n_drop, trade_date="2026-07-13")

    assert order_r.sell_instruments == order_t.sell_instruments
    assert order_r.buy_instruments == order_t.buy_instruments


def test_invariant_4_sloth_0_equals_robot():
    """Test 4: Sloth (delay_weeks=0) 变换后的信号必须与原信号 (Robot) 完全相同"""
    sloth0 = Sloth(delay_weeks=0)
    robot = Robot()

    score = pd.Series([0.1, 0.5, 0.9], index=["A", "B", "C"])
    history = {0: score}

    s_signal = sloth0.transform_signal(score, history, cycle_idx=0)
    r_signal = robot.transform_signal(score, history, cycle_idx=0)

    assert (s_signal == r_signal).all()


def test_invariant_5_rabbit2_target_unchanged_zero_turnover():
    """Test 5: Rabbit-2 在调仓时，若目标 Top22 完全不变，卖出与买入应为空（零换手），不收双边费用"""
    stocks = [f"STOCK_{i:02d}" for i in range(30)]
    score = pd.Series(np.linspace(0.1, 0.9, 30), index=stocks)

    engine = PortfolioEngine("TEST", "rabbit-2", topk=22)
    # 持仓刚好就是得分最高的 22 只
    top22 = list(score.nlargest(22).index)
    for s in top22:
        engine.holdings[s] = 1000.0

    order = engine.generate_order(score, topk=22, n_drop=22, trade_date="2026-07-13", is_first_entry=False)

    # 目标无变化时，不产生不必要的先卖后买
    assert len(order.sell_instruments) == 0
    assert len(order.buy_instruments) == 0


def test_invariant_6_koala_double_reverse():
    """Test 6: Koala 两次反转必须恢复原信号的相对序 (Rank Monotonicity)"""
    koala = Koala()
    stocks = [f"STOCK_{i:02d}" for i in range(50)]
    raw = pd.Series(np.linspace(10.0, 100.0, 50), index=stocks)

    rev1 = koala.transform_signal(raw, {}, 0)
    rev2 = koala.transform_signal(rev1, {}, 0)

    # 两次反转后，排序顺序应与 raw 完全一致
    assert list(rev2.sort_values(ascending=False).index) == list(raw.sort_values(ascending=False).index)


def test_invariant_7_fixed_price_zero_cost_nav_one():
    """Test 7: 股价恒定且费用为 0 时，最终 NAV 恒等于 1.000000"""
    stocks = [f"STOCK_{i:02d}" for i in range(25)]
    score = pd.Series(np.linspace(0.1, 0.9, 25), index=stocks)

    free_cost_model = CostModel(open_cost=0.0, close_cost=0.0, min_cost=0.0)
    engine = PortfolioEngine("TEST", "robot", initial_cash=500_000.0, cost_model=free_cost_model)

    cycle = WeeklyCycle(
        cycle_idx=0,
        decision_date="2026-07-03",
        trade_date="2026-07-06",
        settle_date="2026-07-10",
        trading_days=["2026-07-06", "2026-07-07", "2026-07-08", "2026-07-09", "2026-07-10"]
    )

    order = engine.generate_order(score, topk=22, n_drop=3, trade_date=cycle.trade_date, is_first_entry=True)
    engine.execute_weekly_cycle(cycle, order, lambda inst, d, f: 10.0)

    for v in engine.daily_valuations:
        assert np.isclose(v.nav, 1.000000)


def test_invariant_8_fixed_price_cost_equals_loss():
    """Test 8: 股价固定不变时，净值亏损必须严格等于扣除的手续费"""
    stocks = [f"STOCK_{i:02d}" for i in range(25)]
    score = pd.Series(np.linspace(0.1, 0.9, 25), index=stocks)

    engine = PortfolioEngine("TEST", "robot", initial_cash=500_000.0)

    cycle = WeeklyCycle(
        cycle_idx=0,
        decision_date="2026-07-03",
        trade_date="2026-07-06",
        settle_date="2026-07-10",
        trading_days=["2026-07-06", "2026-07-10"]
    )

    order = engine.generate_order(score, topk=22, n_drop=3, trade_date=cycle.trade_date, is_first_entry=True)
    engine.execute_weekly_cycle(cycle, order, lambda inst, d, f: 10.0)

    total_fees = sum(t.cost for t in engine.trades)
    final_total_asset = engine.daily_valuations[-1].total_asset
    loss = engine.initial_cash - final_total_asset

    # 股价未变，资金减少量必须严格等于累计交易成本
    assert np.isclose(loss, total_fees), f"资产缩水 {loss} 应恰好等于累计手续费 {total_fees}"
