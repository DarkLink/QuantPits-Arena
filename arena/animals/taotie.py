"""
arena/animals/taotie.py
=======================
Taotie (饕餮) — 全池吞噬纯被动指数化动物 (100% Full-Market Passive Handler)
"""

from typing import Optional, Dict, Any
import pandas as pd
from arena.animals.base import Animal


class Taotie(Animal):
    """
    Taotie (饕餮) 行为：
    - 信号直通：不做任何信号变换，原样使用模型打分。
    - 策略参数：
      * TopK: 固定为全池的 100%（全量买入并持有当期整个 Universe）；
      * DropN: 设为 0（无主动换出需求）；
      * 调仓机制：纯被动调仓，严格根据出池与入池操作（若有标的出池则被动卖出，若有新标的入池则被动买入）。
    """

    def __init__(self):
        super().__init__(
            animal_id="taotie",
            display_name="Taotie-All",
            family="All-Market"
        )
        self.topk = 0  # 0 表示全池 100% 动态匹配
        self.n_drop = 0

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
            "passive_pool": True
        }
