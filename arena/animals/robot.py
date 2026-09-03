"""
arena/animals/robot.py
======================
Robot — 标准基准执行动物 (Canonical Benchmark Handler)
"""

from typing import Optional, Dict, Any
import pandas as pd
from arena.animals.base import Animal
from arena.config import DEFAULT_TOPK, DEFAULT_CANONICAL_DROP_N


class Robot(Animal):
    """
    Robot 行为：
    - 不做任何信号变换，原样直通模型预测分
    - 采用标准周频调仓策略 (TopK=22, DropN=3)
    """

    def __init__(self, topk: int = DEFAULT_TOPK, n_drop: int = DEFAULT_CANONICAL_DROP_N):
        super().__init__(animal_id="robot", display_name="Robot", family="Benchmark")
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
