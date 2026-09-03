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
    _cached_authoritative_store: Optional[Dict[str, Any]] = None

    def __init__(self, manifest: ContestantManifest, snapshot_path: Optional[Path] = None):
        super().__init__(manifest)
        self.auth_store_path = Path(__file__).resolve().parent.parent.parent.parent / "artifacts" / "predictions" / "all_contestants_oos.pkl"
        self.snapshot_path = snapshot_path or (Path.home() / "src/QLIB-TEST-RUN/ARCHAEOLOGY/raw_preds.pkl")
        self.role_key = "static" if "static" in manifest.contestant_id.lower() or "static" in manifest.training_mode.lower() else "cpcv"
        self._fused_cache: Dict[str, pd.Series] = {}

    def load_models(self) -> None:
        # 1. 优先载入权威全量预测库
        if HistoricalReplayAdapter._cached_authoritative_store is None and self.auth_store_path.exists():
            with open(self.auth_store_path, "rb") as f:
                HistoricalReplayAdapter._cached_authoritative_store = pickle.load(f)

        # 2. 兜底载入历史原始快照
        if HistoricalReplayAdapter._cached_raw_preds is None and self.snapshot_path.exists():
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

        # 优先从权威预测库提取
        if HistoricalReplayAdapter._cached_authoritative_store is not None:
            c_store = HistoricalReplayAdapter._cached_authoritative_store.get(self.manifest.contestant_id)
            if c_store and start_date in c_store:
                res = c_store[start_date]
                if instruments is not None:
                    res = res.reindex(instruments).fillna(0.5)
                self._fused_cache[start_date] = res
                return res

        # 兜底从 raw_preds.pkl 提取并融合
        if HistoricalReplayAdapter._cached_raw_preds is not None:
            raw_dict = HistoricalReplayAdapter._cached_raw_preds.get(self.role_key, {})
            dt = pd.to_datetime(start_date)

            sub_preds = []
            for model_name, series in raw_dict.items():
                if dt in series.index.levels[0]:
                    sub_preds.append(series.loc[dt])

            if sub_preds:
                fused = rank_norm_equal_fusion(sub_preds, fillna_value=0.5)
                if instruments is not None:
                    fused = fused.reindex(instruments).fillna(0.5)
                self._fused_cache[start_date] = fused
                return fused

        raise ValueError(f"选手 {self.manifest.contestant_id} 在日期 {start_date} 未找到有效打分")
