"""
arena/contestants/adapters/cpcv.py
=================================
Combinatorial Purged Cross-Validation (CPCV) 多折集成模型推理适配器
"""

import pickle
import glob
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np

from arena.config import REPO_ROOT
from arena.contestants.manifest import ContestantManifest
from arena.contestants.adapters.base import BaseInferenceAdapter, rank_norm_equal_fusion


class CPCVEnsembleAdapter(BaseInferenceAdapter):
    """
    CPCV 集成模型推理适配器：
    - 加载各 member 的多折模型权重 (model_fold_0.pkl ~ model_fold_7.pkl)
    - 单 member 内多折预测值取简单均值 (fold_aggregation="mean")
    - 多个 member 之间采用 rank_norm_equal 进行融合
    """

    def __init__(self, manifest: ContestantManifest):
        super().__init__(manifest)
        # member_models: List[List[fold_model]]
        self.member_models: List[List[Any]] = []

    def load_models(self) -> None:
        self.member_models = []
        for member in self.manifest.members:
            if not member.artifact_pattern:
                continue

            full_pattern = str(REPO_ROOT / member.artifact_pattern)
            fold_files = sorted(glob.glob(full_pattern))

            expected_folds = member.expected_folds or 8
            if len(fold_files) != expected_folds:
                raise ValueError(
                    f"CPCV 成员 {member.name} 期望 {expected_folds} 折权重，实际找到 {len(fold_files)} 个: {full_pattern}"
                )

            folds = []
            for fpath in fold_files:
                with open(fpath, "rb") as f:
                    model = pickle.load(f)

                if hasattr(model, "flatten_parameters"):
                    try:
                        model.flatten_parameters()
                    except Exception:
                        pass
                elif hasattr(model, "rnn") and hasattr(model.rnn, "flatten_parameters"):
                    try:
                        model.rnn.flatten_parameters()
                    except Exception:
                        pass

                folds.append(model)

            self.member_models.append(folds)

        self.is_loaded = len(self.member_models) > 0

    def predict(
        self,
        start_date: str,
        end_date: str,
        market: str = "csirun300",
        dataset_provider: Optional[Any] = None
    ) -> pd.Series:
        if not self.is_loaded:
            self.load_models()

        if dataset_provider is None:
            raise ValueError("真实预测需要提供 dataset_provider")

        member_preds = []
        for folds in self.member_models:
            # 单 member 内 8 折取平均
            fold_preds = []
            for model in folds:
                p = model.predict(dataset_provider)
                if isinstance(p, pd.DataFrame):
                    p = p.iloc[:, 0]
                fold_preds.append(p)

            # 8 折求均值
            fold_mean = pd.concat(fold_preds, axis=1).mean(axis=1)
            member_preds.append(fold_mean)

        # 多个 member 之间 rank_norm 等权融合
        fused = rank_norm_equal_fusion(member_preds, fillna_value=0.5)
        return fused
