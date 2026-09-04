"""
arena/animals/whale_shark.py
============================
WhaleShark (鲸鲨) — 半池大容量动物 (50% Broad-Market Pool Handler)
"""

from typing import Optional, Dict, Any
import pandas as pd
from arena.animals.base import Animal


class WhaleShark(Animal):
    """
    WhaleShark (鲸鲨) 行为：
    - 信号直通：不做任何信号变换，原样使用模型打分。
    - 策略参数：
      * TopK 固定为全池的 50%（当前 Universe 约 246 只标的，TopK 固定为 123 只）；
      * DropN 比例与其他动物保持接近的 13.8% 左右，DropN 固定为 17 只。
    """

    def __init__(self, topk: int = 123, n_drop: int = 17):
        super().__init__(
            animal_id="whale-shark",
            display_name="WhaleShark-50%",
            family="Broad-Market"
        )
        self.topk = topk
        self.n_drop = n_drop

    def transform_signal(
        self,
        current_score: pd.Series,
        history_scores: Dict[int, pd.Series],
        cycle_idx: int
    ) -> Optional[pd.Series]:
        return current_score.copy()

    def get_portfolio_policy(self) -> Dict[str, Any]:
        return {
            "topk": self.topk,
            "n_drop": self.n_drop,
            "rebalance_freq": "weekly"
        }
