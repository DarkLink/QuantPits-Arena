"""
arena/animals/turtle.py
=======================
Turtle (乌龟) — 极低换手执行动物 (Minimal Turnover Handler)
"""

from typing import Optional, Dict, Any
import pandas as pd
from arena.animals.base import Animal
from arena.config import DEFAULT_TOPK


class Turtle(Animal):
    """
    Turtle 行为：
    - 不做信号变换，直通信号
    - 极低换手：每次周频调仓仅换出 1 只股票 (n_drop = 1)
    """

    def __init__(self, topk: int = DEFAULT_TOPK):
        super().__init__(animal_id="turtle", display_name="Turtle (Drop-1)", family="Low-Turnover")
        self.topk = topk
        self.n_drop = 1

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
