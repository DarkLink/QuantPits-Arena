"""
tests/test_two_phase_pipeline.py
================================
验证周频两阶段防前瞻执行流水线 (Two-Phase Timeline Pipeline: commit_orders -> execute_orders)
"""

import pytest
from arena.calendar import WeeklyCycle
from arena.runner.weekly_cycle import WeeklyCycleRunner
from arena.contestants import ContestantRegistry


def test_two_phase_commit_and_execute_equivalence():
    """验证 commit_orders + execute_orders 两阶段分步执行与原 step_cycle 完全等价"""
    manifests = ContestantRegistry().list_contestants()[:1]

    cycle = WeeklyCycle(
        cycle_idx=0,
        decision_date="2026-07-03",
        trade_date="2026-07-06",
        settle_date="2026-07-10",
        trading_days=["2026-07-06", "2026-07-07", "2026-07-08", "2026-07-09", "2026-07-10"]
    )

    runner_a = WeeklyCycleRunner(mock_mode=True)
    runner_a._init_engines(manifests)

    runner_b = WeeklyCycleRunner(mock_mode=True)
    runner_b._init_engines(manifests)

    def dummy_price(inst: str, date: str, field: str) -> float:
        return 20.0 if field == "open" else 20.5

    # 方式 1: 直接 step_cycle
    runner_a.step_cycle(
        cycle=cycle,
        active_contestants=manifests,
        price_lookup_fn=dummy_price
    )

    cid = manifests[0].contestant_id

    # 方式 2: 两阶段显式解耦 commit -> execute
    orders = runner_b.commit_orders(
        cycle=cycle,
        active_contestants=manifests,
        price_lookup_fn=dummy_price
    )
    # 验证订单字典结构
    assert (cid, "robot") in orders
    assert ("BENCHMARK", "taotie") in orders

    runner_b.execute_orders(
        cycle=cycle,
        orders=orders,
        price_lookup_fn=dummy_price
    )

    # 验证两者的净值完全相等
    path_a = runner_a.engines[(cid, "robot")].to_portfolio_path()
    path_b = runner_b.engines[(cid, "robot")].to_portfolio_path()
    assert path_a.total_return == pytest.approx(path_b.total_return)
    assert len(path_a.daily_valuations) == len(path_b.daily_valuations)

    # 验证 Taotie 净值完全一致
    taotie_a = runner_a.taotie_benchmark.to_portfolio_path()
    taotie_b = runner_b.taotie_benchmark.to_portfolio_path()
    assert taotie_a.total_return == pytest.approx(taotie_b.total_return)
