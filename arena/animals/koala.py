"""
arena/animals/koala.py
======================
Koala (考拉) — 反向信号执行动物 (Anti-Alpha Inversion Handler)
"""

from typing import Optional, Dict, Any
import pandas as pd
from arena.animals.base import Animal
from arena.config import DEFAULT_TOPK, DEFAULT_CANONICAL_DROP_N


class Koala(Animal):
    """
    Koala 行为：
    - 截面排名反转：rank_inversion: 1.0 - (rank - 1)/(n - 1)
    - 保证反转的确定性与对称性
    - 调仓策略采用 canonical policy (TopK=22, DropN=3)
    """

    def __init__(self, topk: int = DEFAULT_TOPK, n_drop: int = DEFAULT_CANONICAL_DROP_N):
        super().__init__(animal_id="koala", display_name="Koala (Reverse)", family="Inversion")
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
            return pd.Series(0.5, index=current_score.index)

        # 截面排名，归一化到 [0, 1] 后反转
        ranked = current_score.rank(method="average", ascending=True)
        norm_rank = (ranked - 1.0) / (n - 1.0)
        return 1.0 - norm_rank

    def get_portfolio_policy(self) -> Dict[str, Any]:
        return {
            "topk": self.topk,
            "n_drop": self.n_drop,
            "rebalance_freq": "weekly"
        }
