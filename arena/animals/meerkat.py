"""
arena/animals/meerkat.py
========================
Meerkat (狐獴群) — 截面打分百分位切片站位动物 (Percentile Slice Handler)
"""

from typing import Optional, Dict, Any
import pandas as pd
from arena.animals.base import Animal
from arena.config import DEFAULT_TOPK, DEFAULT_CANONICAL_DROP_N


class Meerkat(Animal):
    """
    Meerkat (狐獴群 10%~90%) 行为：
    - 按截面预测得分的百分位站位进行标的选择 (0% 对应 Robot，100% 对应 Koala)。
    - 计算各标的在横截面上的归一化排位 r_i in [0, 1] (0 为最高分，1 为最低分)。
    - 标的变换得分为 -|r_i - P|，使得距离目标百分位 P 最近的标的获得最高分并被优先选入。
    - 策略参数与其他动物保持一致的标准 canonical policy (TopK=22, DropN=3)。
    """

    def __init__(
        self,
        percentile: int,
        topk: int = DEFAULT_TOPK,
        n_drop: int = DEFAULT_CANONICAL_DROP_N
    ):
        if not (0 <= percentile <= 100):
            raise ValueError(f"percentile 必须在 [0, 100] 之间，当前为 {percentile}")
        super().__init__(
            animal_id=f"meerkat-{percentile}",
            display_name=f"Meerkat-{percentile}%",
            family="Percentile"
        )
        self.percentile = percentile
        self.topk = topk
        self.n_drop = n_drop

    def transform_signal(
        self,
        current_score: pd.Series,
        history_scores: Dict[int, pd.Series],
        cycle_idx: int
    ) -> Optional[pd.Series]:
        n = len(current_score)
        if n <= 1:
            return current_score.copy()

        # 计算归一化排位 (0: 最高分, 1: 最低分)
        ranks = current_score.rank(ascending=False, method="average") - 1
        norm_rank = ranks / (n - 1)

        target_p = self.percentile / 100.0
        dist = (norm_rank - target_p).abs()
        # 距离越近，得分越高
        return -dist

    def get_portfolio_policy(self) -> Dict[str, Any]:
        return {
            "topk": self.topk,
            "n_drop": self.n_drop,
            "rebalance_freq": "weekly",
            "percentile": self.percentile
        }
