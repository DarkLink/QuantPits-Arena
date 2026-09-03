"""
arena/contestants/adapters/mock.py
==================================
用于公开演示与单元测试的 Mock 推理适配器
"""

from typing import List, Optional
import numpy as np
import pandas as pd

from arena.contestants.manifest import ContestantManifest
from arena.contestants.adapters.base import BaseInferenceAdapter, rank_norm_score


class MockInferenceAdapter(BaseInferenceAdapter):
    """
    Mock 推理适配器：
    - 在无本地私有模型权重时使用
    - 基于参赛选手 ID 生成确定性、具有可预测特性的截面得分
    - 支持快速运行全流程与回归测试
    """

    def __init__(self, manifest: ContestantManifest, seed_offset: int = 0):
        super().__init__(manifest)
        self.seed_offset = seed_offset
        # 基于 contestant_id 生成固定的 base seed
        self.base_seed = abs(hash(manifest.contestant_id)) % 100000 + seed_offset

    def load_models(self) -> None:
        self.is_loaded = True

    def predict(
        self,
        start_date: str,
        end_date: str,
        market: str = "csirun300",
        instruments: Optional[List[str]] = None
    ) -> pd.Series:
        if instruments is None:
            # 默认使用 100 只虚拟标的
            instruments = [f"STOCK_{i:03d}" for i in range(100)]

        # 单日截面打分生成（包含日期种子，保证打分随每周时间推进动态演化）
        date_seed = (self.base_seed + abs(hash(str(start_date)))) % 1000000
        rng = np.random.RandomState(date_seed)
        # 生成有一定排名的得分
        raw_scores = rng.normal(loc=0.0, scale=1.0, size=len(instruments))
        series = pd.Series(raw_scores, index=instruments)
        return rank_norm_score(series, fillna_val=0.5)
