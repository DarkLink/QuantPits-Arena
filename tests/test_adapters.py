"""
tests/test_adapters.py
======================
模型适配器与截面打分融合契约测试
"""

import pandas as pd
import numpy as np
import pytest

from arena.contestants import ContestantRegistry
from arena.contestants.adapters import (
    rank_norm_score,
    rank_norm_equal_fusion,
    create_adapter,
    MockInferenceAdapter,
    StaticEnsembleAdapter,
    CPCVEnsembleAdapter,
)


def test_rank_norm_score():
    """验证单截面打分 Rank-Normalization 行为"""
    stocks = [f"STOCK_{i:02d}" for i in range(10)]
    raw = pd.Series(np.linspace(10.0, 100.0, 10), index=stocks)

    norm = rank_norm_score(raw, fillna_val=0.5)

    assert norm.idxmin() == stocks[0]
    assert norm.idxmax() == stocks[-1]
    assert np.isclose(norm.min(), 0.0)
    assert np.isclose(norm.max(), 1.0)


def test_rank_norm_equal_fusion():
    """验证多子模型融合契约：各子模型截面 rank_norm 后等权平均"""
    stocks = [f"STOCK_{i:02d}" for i in range(10)]

    # 模型 1：正序
    p1 = pd.Series(np.linspace(1.0, 10.0, 10), index=stocks)
    # 模型 2：倒序
    p2 = pd.Series(np.linspace(10.0, 1.0, 10), index=stocks)

    fused = rank_norm_equal_fusion([p1, p2], fillna_value=0.5)

    # 正序 + 倒序等权融合，所有标的得分应该完全相等 (0.5)
    assert np.allclose(fused.values, 0.5)


def test_create_adapter_factory():
    """验证适配器工厂函数依据选手清单类型正确实例化"""
    registry = ContestantRegistry()

    # Contestant A (Static)
    cA = registry.get_contestant("CONTESTANT_A")
    adapter_A = create_adapter(cA, mock=False)
    assert isinstance(adapter_A, StaticEnsembleAdapter)

    # Contestant B (CPCV)
    cB = registry.get_contestant("CONTESTANT_B")
    adapter_B = create_adapter(cB, mock=False)
    assert isinstance(adapter_B, CPCVEnsembleAdapter)

    # Mock 模式
    adapter_mock = create_adapter(cA, mock=True)
    assert isinstance(adapter_mock, MockInferenceAdapter)

    # 验证 Mock 推理输出格式
    pred = adapter_mock.predict("2026-07-03", "2026-07-03")
    assert isinstance(pred, pd.Series)
    assert len(pred) == 100
    assert 0.0 <= pred.min() and pred.max() <= 1.0
