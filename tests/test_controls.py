"""
tests/test_controls.py
======================
Monkey Colony 与 Rock 基准控制组测试
"""

import pandas as pd
import numpy as np
import pytest

from arena.controls import MonkeyColony, RockBenchmark


def test_monkey_colony_deterministic_generation():
    """验证猴子群落分数生成的确定性与可复现性"""
    colony = MonkeyColony(colony_size=100)
    instruments = [f"STOCK_{i:02d}" for i in range(20)]

    s1 = colony.generate_monkey_score(monkey_idx=0, cycle_idx=0, instruments=instruments)
    s2 = colony.generate_monkey_score(monkey_idx=0, cycle_idx=0, instruments=instruments)
    s_diff_cycle = colony.generate_monkey_score(monkey_idx=0, cycle_idx=1, instruments=instruments)
    s_diff_monkey = colony.generate_monkey_score(monkey_idx=1, cycle_idx=0, instruments=instruments)

    # 同一猴子同一周期生成结果完全一致
    assert s1.equals(s2)
    # 不同周期不同
    assert not s1.equals(s_diff_cycle)
    # 不同猴子不同
    assert not s1.equals(s_diff_monkey)


def test_monkey_colony_distribution_summary():
    """验证猴子统计指标计算 (min, 5%, median, 95%, max)"""
    colony = MonkeyColony()
    values = list(np.linspace(0.0, 100.0, 101))
    summary = colony.summarize_distribution(values)

    assert summary["min"] == 0.0
    assert summary["max"] == 100.0
    assert summary["median"] == 50.0
    assert np.isclose(summary["p05"], 5.0)
    assert np.isclose(summary["p95"], 95.0)

    # 分位数排名
    assert np.isclose(colony.compute_percentile_rank(50.0, values), 50.0 / 101.0)


def test_rock_benchmark_fallback_mode(tmp_path):
    """验证 Rock 在无数据文件时的优雅降级"""
    non_existent = tmp_path / "non_existent_rock.csv"
    rock = RockBenchmark(non_existent)
    assert rock.is_active is False
    assert rock.get_nav_at("2026-07-06") == 1.0
