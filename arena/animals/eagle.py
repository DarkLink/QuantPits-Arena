"""
arena/animals/eagle.py
======================
Eagle (鹰群) — 持仓容量与换手带宽变化动物 (Capacity & Bandwidth Matrix)
"""

from typing import Optional, Dict, Any
import pandas as pd
from arena.animals.base import Animal


class Eagle(Animal):
    """
    Eagle (鹰群 5/1, 11/2, 44/6, 66/9, 88/12) 行为：
    - 信号直通：不做任何信号变换，原样使用模型打分 (与 Robot 一致)。
    - 策略参数测试不同持仓集中度与容量带宽 (TopK / DropN)：
      * 5 / 1: 极端集中组合
      * 11 / 2: 紧凑半数组合
      * 44 / 6: 2 倍标准容量
      * 66 / 9: 3 倍标准容量
      * 88 / 12: 4 倍标准容量
    """

    def __init__(self, topk: int, n_drop: int):
        if topk <= 0 or n_drop <= 0:
            raise ValueError(f"topk 和 n_drop 必须大于 0，当前为 topk={topk}, n_drop={n_drop}")
        super().__init__(
            animal_id=f"eagle-{topk}-{n_drop}",
            display_name=f"Eagle-{topk}/{n_drop}",
            family="Capacity"
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
