"""
arena/contestants/adapters/base.py
==================================
参赛模型推理适配器抽象基类与截面打分融合工具
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
import pandas as pd
import numpy as np

from arena.contestants.manifest import ContestantManifest


def rank_norm_score(score: pd.Series, fillna_val: float = 0.5) -> pd.Series:
    """
    对单日或单截面打分执行 Rank-Normalization:
    norm_rank = (rank - 1) / (n - 1) 映射到 [0, 1] 区间，缺失值填入 fillna_val。
    """
    n = len(score)
    if n <= 1:
        return pd.Series(fillna_val, index=score.index)

    ranked = score.rank(method="average", ascending=True)
    norm = (ranked - 1.0) / (n - 1.0)
    return norm.fillna(fillna_val)


def rank_norm_equal_fusion(
    predictions: List[pd.Series],
    fillna_value: float = 0.5
) -> pd.Series:
    """
    Contestant 核心融合契约：
    1. 各子模型分别在每日截面上进行 Rank-Normalization
    2. 缺失打分标的填充 0.5
    3. 各子模型等权平均 (Equal Weighting)
    """
    if not predictions:
        raise ValueError("predictions 列表不能为空")

    if len(predictions) == 1:
        return rank_norm_score(predictions[0], fillna_value)

    # 统一索引合并
    all_indices = predictions[0].index
    for p in predictions[1:]:
        all_indices = all_indices.union(p.index)

    normalized_list = []
    for p in predictions:
        reindexed = p.reindex(all_indices)
        norm = rank_norm_score(reindexed, fillna_value)
        normalized_list.append(norm)

    combined_df = pd.concat(normalized_list, axis=1)
    fused = combined_df.mean(axis=1)
    return fused


class BaseInferenceAdapter(ABC):
    """
    模型推理适配器基类。
    负责将特定的模型 artifact（如 static pkl, cpcv folds, GAT trained_model）
    桥接到 Arena 统一的周频截面预测接口。
    """

    def __init__(self, manifest: ContestantManifest):
        self.manifest = manifest
        self.is_loaded = False

    @abstractmethod
    def load_models(self) -> None:
        """加载底层权重二进制资产至内存或显存"""
        pass

    @abstractmethod
    def predict(
        self,
        start_date: str,
        end_date: str,
        market: str = "csirun300"
    ) -> pd.Series:
        """
        在 [start_date, end_date] 区间内执行推理。

        Returns:
            pd.Series (MultiIndex: [datetime, instrument] 或 Series with instrument index for single date)
        """
        pass
