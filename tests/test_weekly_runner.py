"""
tests/test_weekly_runner.py
===========================
周频同步执行主运行器与双层脱敏导出集成测试
"""

from pathlib import Path
import pandas as pd
import numpy as np
import pytest

from arena.runner import WeeklyCycleRunner
from arena.reports import DualTierExporter
from arena.contestants import ContestantRegistry


def test_weekly_cycle_runner_mock_execution(tmp_path):
    """
    集成测试：
    在 Mock 模式下执行 2 个周期的周频回测，
    验证所有 (Contestant, Animal) 组合正常产生日频估值与周结算，
    特别校验 Sloth 方案 B 冷启动：Cycle 0 空仓净值恒等于 1.0，Cycle 1 激活建仓。
    """
    runner = WeeklyCycleRunner(mock_mode=True)
    # 取前两个周期进行快速验证
    results = runner.run(max_cycles=2)

    assert len(results) > 0
    # 验证每一个组合都输出了有效的回测路径
    for (cid, aid), path in results.items():
        assert len(path.daily_valuations) == 11, f"{cid}_{aid} 期望 1 个 T0 锚定日 + 2 周共 10 个交易日估值"
        assert len(path.weekly_settlements) == 2, f"{cid}_{aid} 期望 2 个周结算"

    # 特别检查 Sloth-1 方案 B 冷启动
    sloth1_key = ("QP-20260626-STATIC", "sloth-1")
    if sloth1_key in results:
        s1_path = results[sloth1_key]
        # Cycle 0 (T0 + 前 5 个交易日): 保持空仓现金，无买卖，NAV 恒为 1.0000
        for v in s1_path.daily_valuations[:6]:
            assert np.isclose(v.nav, 1.0)
            assert v.holdings_value == 0.0

        # Cycle 1 (第 7~11 个交易日，索引 6 起): 激活建仓，持仓市值大于 0
        v_c1 = s1_path.daily_valuations[6]
        assert v_c1.holdings_value > 0.0


def test_dual_tier_exporter(tmp_path):
    """验证双层脱敏导出器输出合规性"""
    runner = WeeklyCycleRunner(mock_mode=True)
    registry = ContestantRegistry()
    results = runner.run(max_cycles=1)

    exporter = DualTierExporter(run_id="test_run_001", base_dir=tmp_path)
    artifacts = exporter.export(results, registry)

    # 1. 验证公开层文件存在
    pub_nav = artifacts["public_nav"]
    pub_metrics = artifacts["public_metrics"]
    pub_matrix = artifacts["public_matrix"]

    assert pub_nav.exists()
    assert pub_metrics.exists()
    assert pub_matrix.exists()

    # 2. 检查公开 NAV 文件的列名完全匿名化
    df_nav = pd.read_csv(pub_nav)
    for col in df_nav.columns:
        if col != "datetime":
            assert col.startswith("CONTESTANT_") or col.startswith("BENCHMARK_"), f"公开列名必须以匿名代号或基准代号开头: {col}"
            # 首日净值接近 1.0
            assert 0.99 <= df_nav[col].iloc[0] <= 1.01

    # 3. 检查私有层文件隔离在 private/ 目录
    priv_trades = artifacts["private_trades"]
    assert "private" in str(priv_trades)
