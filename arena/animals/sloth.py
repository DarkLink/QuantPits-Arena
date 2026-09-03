"""
arena/animals/sloth.py
======================
Sloth (树懒) — 信号延迟执行动物 (Signal Latency Handler)
"""

from typing import Optional, Dict, Any
import pandas as pd
from arena.animals.base import Animal
from arena.config import DEFAULT_TOPK, DEFAULT_CANONICAL_DROP_N


class Sloth(Animal):
    """
    Sloth (树懒 1~4 周延迟) 行为：
    - 方案 B（冷启动）：在 cycle_idx < delay_weeks 的前置周期内返回 None，组合保持 100% 空仓现金。
    - 到达 cycle_idx == delay_weeks 时，返回 cycle 0 的信号进行首次满额建仓。
    - 后续周期 (cycle_idx > delay_weeks) 使用 cycle_idx - delay_weeks 的历史信号进行周频调仓。
    - 策略参数采用标准 canonical policy (TopK=22, DropN=3)。
    """

    def __init__(
        self,
        delay_weeks: int,
        topk: int = DEFAULT_TOPK,
        n_drop: int = DEFAULT_CANONICAL_DROP_N
    ):
        if delay_weeks < 1:
            raise ValueError("delay_weeks 必须 >= 1")
        super().__init__(
            animal_id=f"sloth-{delay_weeks}",
            display_name=f"Sloth-{delay_weeks}w",
            family="Latency"
        )
        self.delay_weeks = delay_weeks
        self.topk = topk
        self.n_drop = n_drop

    def transform_signal(
        self,
        current_score: pd.Series,
        history_scores: Dict[int, pd.Series],
        cycle_idx: int
    ) -> Optional[pd.Series]:
        # 冷启动判断：如果当前周期数小于延迟周数，尚未观察到符合延迟条件的信号，保持空仓现金
        if cycle_idx < self.delay_weeks:
            return None

        delayed_idx = cycle_idx - self.delay_weeks
        if delayed_idx not in history_scores:
            raise KeyError(f"缺少周期 {delayed_idx} 的历史得分快照")

        return history_scores[delayed_idx].copy()

    def get_portfolio_policy(self) -> Dict[str, Any]:
        return {
            "topk": self.topk,
            "n_drop": self.n_drop,
            "rebalance_freq": "weekly",
            "delay_weeks": self.delay_weeks
        }
