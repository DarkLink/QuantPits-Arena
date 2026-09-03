"""
arena/contestants/adapters/static.py
===================================
Static Ensemble 成员模型加载与推理适配器
"""

import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np

from arena.config import REPO_ROOT
from arena.contestants.manifest import ContestantManifest
from arena.contestants.adapters.base import BaseInferenceAdapter, rank_norm_equal_fusion


class StaticEnsembleAdapter(BaseInferenceAdapter):
    """
    静态集成模型推理适配器：
    - 加载各 member 的单个 model.pkl 权重
    - 处理 RNN 权重的 flatten_parameters
    - 分别预测并执行 rank_norm_equal 融合
    """

    def __init__(self, manifest: ContestantManifest):
        super().__init__(manifest)
        self.models: List[Any] = []

    def load_models(self) -> None:
        self.models = []
        for member in self.manifest.members:
            if not member.artifact_path:
                continue

            artifact_file = REPO_ROOT / member.artifact_path
            if not artifact_file.exists():
                raise FileNotFoundError(f"未找到模型权重文件: {artifact_file}")

            with open(artifact_file, "rb") as f:
                model = pickle.load(f)

            # RNN 参数展平处理
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

            self.models.append(model)

        self.is_loaded = len(self.models) > 0

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

        sub_preds = []
        for model in self.models:
            pred = model.predict(dataset_provider)
            if isinstance(pred, pd.DataFrame):
                pred = pred.iloc[:, 0]
            sub_preds.append(pred)

        fused = rank_norm_equal_fusion(sub_preds, fillna_value=0.5)
        return fused
