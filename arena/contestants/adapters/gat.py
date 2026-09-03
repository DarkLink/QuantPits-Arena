"""
arena/contestants/adapters/gat.py
================================
Graph Attention Network (GAT) 模型推理适配器
"""

from pathlib import Path
from typing import Any, Optional
import pandas as pd
import numpy as np

from arena.config import REPO_ROOT
from arena.contestants.manifest import ContestantManifest
from arena.contestants.adapters.base import BaseInferenceAdapter, rank_norm_score


class GATAdapter(BaseInferenceAdapter):
    """
    GAT 模型推理适配器：
    - 加载 trained_model 权重文件
    - 支持 20 特征 (baseline) 与 52 特征 (expansion) 两套架构配置
    - 统一设定 step_len = 20
    """

    def __init__(self, manifest: ContestantManifest):
        super().__init__(manifest)
        self.d_feat = self.manifest.adapter_config.get("d_feat", 20)
        self.step_len = self.manifest.adapter_config.get("step_len", 20)
        self.model = None

    def load_models(self) -> None:
        if not self.manifest.members or not self.manifest.members[0].artifact_path:
            raise ValueError("GAT Manifest 缺失 artifact_path")

        artifact_file = REPO_ROOT / self.manifest.members[0].artifact_path
        if not artifact_file.exists():
            raise FileNotFoundError(f"未找到 GAT 权重文件: {artifact_file}")

        try:
            import torch
            # 使用 torch.load 加载权重
            self.model = torch.load(artifact_file, map_location="cpu", weights_only=False)
            if hasattr(self.model, "eval"):
                self.model.eval()
            self.is_loaded = True
        except Exception as e:
            # 若环境暂未初始化 torch 或存在依赖冲突，记录异常
            self.is_loaded = False
            raise RuntimeError(f"加载 GAT 模型权重失败: {e}")

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

        # 调用模型预测
        pred = self.model.predict(dataset_provider)
        if isinstance(pred, pd.DataFrame):
            pred = pred.iloc[:, 0]

        return rank_norm_score(pred, fillna_val=0.5)
