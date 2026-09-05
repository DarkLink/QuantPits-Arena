"""
tests/test_rolling_and_controls.py
==================================
测试独立饕餮基准、参数化猴子群落与按周增量滚动快照机制
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path

from arena.controls import (
    TaotieBenchmark,
    MonkeyColony,
    CANONICAL_STRATEGY_SPECS,
    map_animal_to_spec_id,
    StrategySpec
)
from arena.portfolio import PortfolioEngine, Order
from arena.portfolio.types import DailyValuation, WeeklySettlement, TradeRecord
from arena.calendar import TradingCalendar, WeeklyCycle
from arena.runner import WeeklyCycleRunner
from arena.contestants.manifest import ContestantManifest


def test_taotie_benchmark_standalone():
    """验证独立饕餮基准 (TaotieBenchmark) 的全池被动执行逻辑"""
    benchmark = TaotieBenchmark(initial_cash=500_000.0)
    assert benchmark.contestant_id == "BENCHMARK"
    assert benchmark.animal_id == "taotie"
    assert benchmark.engine.topk == 0

    cycle = WeeklyCycle(
        cycle_idx=0,
        decision_date="2026-07-03",
        trade_date="2026-07-06",
        settle_date="2026-07-10",
        trading_days=["2026-07-06", "2026-07-07", "2026-07-08", "2026-07-09", "2026-07-10"]
    )
    universe = [f"STOCK_{i:03d}" for i in range(50)]

    def price_lookup(inst: str, date: str, field: str) -> float:
        return 20.0

    # 推进 1 个周期
    benchmark.step(cycle, universe, price_lookup)
    path = benchmark.engine.to_portfolio_path()

    assert len(path.daily_valuations) == 6  # T0 初始点 + 5 交易日
    assert len(path.weekly_settlements) == 1
    assert path.contestant_id == "BENCHMARK"
    assert path.animal_id == "taotie"


def test_parametric_monkey_specs_and_mapping():
    """验证参数化猴群覆盖全部 11 种策略规格（包含饕餮全池）"""
    assert len(CANONICAL_STRATEGY_SPECS) == 11
    expected_specs = [
        "P_22_3", "P_22_11", "P_22_22", "P_22_1",
        "P_5_1", "P_11_2", "P_44_6", "P_66_9", "P_88_12",
        "P_123_17", "P_ALL_0"
    ]
    for s in expected_specs:
        assert s in CANONICAL_STRATEGY_SPECS

    # 映射验证
    assert map_animal_to_spec_id("robot") == "P_22_3"
    assert map_animal_to_spec_id("sloth-2") == "P_22_3"
    assert map_animal_to_spec_id("snail-4") == "P_22_3"
    assert map_animal_to_spec_id("meerkat-50") == "P_22_3"
    assert map_animal_to_spec_id("rabbit-1") == "P_22_11"
    assert map_animal_to_spec_id("rabbit-2") == "P_22_22"
    assert map_animal_to_spec_id("turtle") == "P_22_1"
    assert map_animal_to_spec_id("eagle-5-1") == "P_5_1"
    assert map_animal_to_spec_id("eagle-88-12") == "P_88_12"
    assert map_animal_to_spec_id("whale-shark") == "P_123_17"
    assert map_animal_to_spec_id("taotie") == "P_ALL_0"


def test_monkey_empirical_pvalue():
    """验证单侧经验 p-value 计算 (含 plus-one 校正)"""
    colony = MonkeyColony()
    # 假设 100 只猴子的收益率
    monkey_rets = [0.01 * i for i in range(100)]  # 0.00 ~ 0.99

    # 目标实际收益为 0.95 (只有 5 只猴子 >= 0.95: 95, 96, 97, 98, 99)
    # plus-one: (5 + 1) / (100 + 1) = 6 / 101
    p_val = colony.compute_empirical_pvalue(0.95, monkey_rets, higher_is_better=True)
    assert np.isclose(p_val, 6.0 / 101.0)

    # 目标实际收益为 1.05 (0 只猴子 >= 1.05)
    # plus-one: (0 + 1) / (100 + 1) = 1 / 101, 绝不为 0.0
    p_val_top = colony.compute_empirical_pvalue(1.05, monkey_rets, higher_is_better=True)
    assert np.isclose(p_val_top, 1.0 / 101.0)


def test_portfolio_engine_checkpoint_roundtrip():
    """验证 PortfolioEngine 状态导出与反序列化恢复的无损一致性"""
    engine = PortfolioEngine(
        contestant_id="CONTESTANT_TEST",
        animal_id="robot",
        topk=22,
        initial_cash=500_000.0,
        deal_price_mode="open"
    )

    cycle = WeeklyCycle(
        cycle_idx=0,
        decision_date="2026-07-03",
        trade_date="2026-07-06",
        settle_date="2026-07-10",
        trading_days=["2026-07-06", "2026-07-07", "2026-07-08", "2026-07-09", "2026-07-10"]
    )
    score = pd.Series(np.linspace(0.9, 0.1, 30), index=[f"STOCK_{i:02d}" for i in range(30)])

    def price_lookup(inst: str, date: str, field: str) -> float:
        return 15.0

    order = engine.generate_order(
        score=score,
        topk=22,
        n_drop=3,
        trade_date="2026-07-06",
        is_first_entry=True,
        price_lookup=price_lookup
    )
    engine.execute_weekly_cycle(cycle, order, price_lookup)

    # 导出快照
    checkpoint = engine.export_checkpoint()
    assert checkpoint.last_cycle_idx == 0
    assert checkpoint.last_settle_date == "2026-07-10"
    assert checkpoint.cash_balance == engine.cash_balance
    assert checkpoint.holdings == engine.holdings
    assert len(checkpoint.daily_valuations) == len(engine.daily_valuations)

    # 从快照恢复
    restored_engine = PortfolioEngine.from_checkpoint(checkpoint)
    assert restored_engine.contestant_id == engine.contestant_id
    assert restored_engine.animal_id == engine.animal_id
    assert restored_engine.topk == engine.topk
    assert restored_engine.cash_balance == engine.cash_balance
    assert restored_engine.holdings == engine.holdings
    assert len(restored_engine.daily_valuations) == len(engine.daily_valuations)
    assert len(restored_engine.weekly_settlements) == len(engine.weekly_settlements)
    assert len(restored_engine.trades) == len(engine.trades)


def test_weekly_runner_incremental_step_identity(tmp_path):
    """
    验证按周增量滚动推进 (step) 与一次性全量运行 (run) 产出结果严格 bit-for-bit 一致
    """
    # 1. 一次性批量跑 2 个周期
    runner_batch = WeeklyCycleRunner(mock_mode=True)
    results_batch = runner_batch.run(max_cycles=2)

    # 2. 增量滚动跑：第 0 周期运行并保存快照
    runner_step1 = WeeklyCycleRunner(mock_mode=True)
    active = runner_step1.registry.list_contestants()
    price_fn, trade_fn = runner_step1._setup_market_provider(active, None, None)

    runner_step1._init_engines(active)
    # Step cycle 0
    runner_step1.step_cycle(runner_step1.cycles[0], active, price_fn, trade_fn)

    cp_dir = tmp_path / "checkpoints"
    runner_step1.save_checkpoint_to_disk(cp_dir, cycle_idx=0)
    assert (cp_dir / "latest_state.pkl").exists()
    assert (cp_dir / "cycle_0.pkl").exists()

    # 从磁盘恢复 runner_step2，并推进第 1 周期
    runner_step2 = WeeklyCycleRunner(mock_mode=True)
    runner_step2.load_checkpoint_from_disk(cp_dir / "latest_state.pkl")
    assert runner_step2.last_completed_cycle_idx == 0

    price_fn2, trade_fn2 = runner_step2._setup_market_provider(active, None, None)
    runner_step2.step_cycle(runner_step2.cycles[1], active, price_fn2, trade_fn2)
    assert runner_step2.last_completed_cycle_idx == 1

    results_incremental = {
        key: engine.to_portfolio_path()
        for key, engine in runner_step2.engines.items()
    }
    results_incremental[("BENCHMARK", "taotie")] = runner_step2.taotie_benchmark.engine.to_portfolio_path()

    # 3. 比对 Batch 与 Incremental 结果的完全一致性
    assert set(results_batch.keys()) == set(results_incremental.keys())

    # 抽样比对任意若干路径的 NAV 时序
    sample_key = next(iter(results_batch.keys()))
    path_batch = results_batch[sample_key]
    path_inc = results_incremental[sample_key]

    assert len(path_batch.daily_valuations) == len(path_inc.daily_valuations)
    for v_b, v_i in zip(path_batch.daily_valuations, path_inc.daily_valuations):
        assert v_b.date == v_i.date
        assert np.isclose(v_b.nav, v_i.nav, atol=1e-10)
        assert np.isclose(v_b.cash, v_i.cash, atol=1e-10)
        assert v_b.num_holdings == v_i.num_holdings

    # 比对 BENCHMARK_taotie
    tt_b = results_batch[("BENCHMARK", "taotie")]
    tt_i = results_incremental[("BENCHMARK", "taotie")]
    assert np.isclose(tt_b.total_return, tt_i.total_return, atol=1e-10)
