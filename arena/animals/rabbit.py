"""
arena/animals/rabbit.py
=======================
Rabbit (兔子) — 高换手部署带宽执行动物 (High-Bandwidth Deployment Handler)
"""

from typing import Optional, Dict, Any
import pandas as pd
from arena.animals.base import Animal
from arena.config import DEFAULT_TOPK


class Rabbit(Animal):
    """
    Rabbit 行为：
    - 不做信号变换，直通信号
    - 提升调仓换手带宽：
      - Rabbit-1 (variant=1): 半仓调仓，n_drop = topk // 2 (22 // 2 = 11)
      - Rabbit-2 (variant=2): 全仓调仓，n_drop = topk (22，完全切换最新 target)
    """

    def __init__(self, variant: int = 1, topk: int = DEFAULT_TOPK):
        if variant not in (1, 2):
            raise ValueError("Rabbit variant 必须为 1 (半仓) 或 2 (全仓)")

        super().__init__(
            animal_id=f"rabbit-{variant}",
            display_name=f"Rabbit-{variant} ({'50%' if variant == 1 else '100%'})",
            family="Bandwidth"
        )
        self.variant = variant
        self.topk = topk
        self.n_drop = (topk // 2) if variant == 1 else topk

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
            "rebalance_freq": "weekly",
            "variant": self.variant
        }
