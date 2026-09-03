"""
arena/contestants/adapters/historical.py
========================================
历史生产快照推理适配器 (HistoricalReplayAdapter)

直接对接 ARCHAEOLOGY 真实历史生产预测，
保证 100% 生产同源，复现 CONTESTANT_A 与 CONTESTANT_B 的真实样本外信号。
"""

import pickle
from pathlib import Path
from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np

from arena.contestants.manifest import ContestantManifest
from arena.contestants.adapters.base import BaseInferenceAdapter, rank_norm_score, rank_norm_equal_fusion


class HistoricalReplayAdapter(BaseInferenceAdapter):
    """
    历史生产预测回放适配器：
    从 ARCHAEOLOGY/raw_preds.pkl 中提取历史生产时点各子模型的真实预测并执行生产融合规则。
    """

    _cached_raw_preds: Optional[Dict[str, Any]] = None

    def __init__(self, manifest: ContestantManifest, snapshot_path: Optional[Path] = None):
        super().__init__(manifest)
        self.snapshot_path = snapshot_path or (Path.home() / "src/QLIB-TEST-RUN/ARCHAEOLOGY/raw_preds.pkl")
        self.role_key = "static" if "static" in manifest.contestant_id.lower() or "static" in manifest.training_mode.lower() else "cpcv"
        self._fused_cache: Dict[str, pd.Series] = {}

    def load_models(self) -> None:
        if HistoricalReplayAdapter._cached_raw_preds is None:
            if not self.snapshot_path.exists():
                raise FileNotFoundError(f"未找到历史预测快照: {self.snapshot_path}")
            with open(self.snapshot_path, "rb") as f:
                HistoricalReplayAdapter._cached_raw_preds = pickle.load(f)

        self.is_loaded = True

    def predict(
        self,
        start_date: str,
        end_date: str,
        market: str = "csirun300",
        instruments: Optional[List[str]] = None
    ) -> pd.Series:
        if not self.is_loaded:
            self.load_models()

        if start_date in self._fused_cache:
            return self._fused_cache[start_date]

        raw_dict = HistoricalReplayAdapter._cached_raw_preds.get(self.role_key, {})
        dt = pd.to_datetime(start_date)

        sub_preds = []
        for model_name, series in raw_dict.items():
            if dt in series.index.levels[0]:
                sub_preds.append(series.loc[dt])

        if not sub_preds:
            raise ValueError(f"日期 {start_date} 在历史预测快照中不存在")

        # 生产同源 rank_norm_equal 融合
        fused = rank_norm_equal_fusion(sub_preds, fillna_value=0.5)

        if instruments is not None:
            fused = fused.reindex(instruments).fillna(0.5)

        self._fused_cache[start_date] = fused
        return fused
