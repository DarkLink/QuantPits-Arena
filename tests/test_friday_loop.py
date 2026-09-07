"""
tests/test_friday_loop.py
=========================
验证周五一键闭环执行流 (Friday Loop: step_friday_cycle)
"""

import pytest
from arena.calendar import WeeklyCycle
from arena.runner.weekly_cycle import WeeklyCycleRunner
from arena.contestants import ContestantRegistry


def test_step_friday_cycle_execution():
    """验证周五闭环：执行上周订单 + 生成下周订单"""
    manifests = ContestantRegistry().list_contestants()[:1]
    cid = manifests[0].contestant_id

    runner = WeeklyCycleRunner(mock_mode=True)
    runner._init_engines(manifests)

    def dummy_price(inst: str, date: str, field: str) -> float:
        return 25.0 if field == "open" else 26.0

    # 1. 第一周周五：首周启动 (无 pending_orders)，执行首周建仓并产出第二周订单
    cycle_0 = runner.cycles[0]
    settled_0, next_orders_1 = runner.step_friday_cycle(
        cycle=cycle_0,
        active_contestants=manifests,
        price_lookup_fn=dummy_price,
        pending_orders=None
    )
    assert settled_0 is not None
    assert next_orders_1 is not None
    assert (cid, "robot") in next_orders_1
    assert runner.last_completed_cycle_idx == 0

    # 2. 第二周周五：传入上一周锁定的 next_orders_1 作为 pending_orders 进行结算，并预生成第三周订单
    cycle_1 = runner.cycles[1]
    settled_1, next_orders_2 = runner.step_friday_cycle(
        cycle=cycle_1,
        active_contestants=manifests,
        price_lookup_fn=dummy_price,
        pending_orders=next_orders_1
    )
    assert settled_1 is next_orders_1
    assert next_orders_2 is not None
    assert runner.last_completed_cycle_idx == 1

    path = runner.engines[(cid, "robot")].to_portfolio_path()
    assert len(path.weekly_settlements) == 2
    assert path.total_return != 0.0
