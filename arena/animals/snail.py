"""
arena/animals/snail.py
======================
Snail (蜗牛) — 初始建仓预热 + 信号延迟执行动物 (Warm-start Signal Latency Handler)
"""

from typing import Optional, Dict, Any
import pandas as pd
from arena.animals.base import Animal
from arena.config import DEFAULT_TOPK, DEFAULT_CANONICAL_DROP_N


class Snail(Animal):
    """
    Snail (蜗牛 1~4 周延迟) 行为：
    - 方案 C（预热平稳建仓）：在 cycle_idx == 0 时，与同模型的 Robot 保持一致，使用当前最新信号进行首次满额建仓。
    - 在 0 < cycle_idx < delay_weeks 的过渡周期内，延迟信号尚未到达，复用 cycle 0 信号保持现有持仓不动 (hold)，
      避免树懒 (Sloth) 因空仓现金导致的入场延迟与敞口截断 (exposure-length) 偏差。
    - 到达 cycle_idx >= delay_weeks 时，与树懒保持一致，使用 cycle_idx - delay_weeks 的历史信号进行周频调仓。
    - 策略参数采用标准 canonical policy (TopK=22, DropN=3)。
    """

    def __init__(
        self,
        delay_weeks: int,
        topk: int = DEFAULT_TOPK,
        n_drop: int = DEFAULT_CANONICAL_DROP_N
    ):
        if delay_weeks < 0:
            raise ValueError("delay_weeks 必须 >= 0")
        super().__init__(
            animal_id=f"snail-{delay_weeks}" if delay_weeks > 0 else "snail-0",
            display_name=f"Snail-{delay_weeks}w" if delay_weeks > 0 else "Snail-0w",
            family="Latency-Warm"
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
        # 首次建仓 (cycle 0)：与 Robot 完全一致，使用当前期截面打分满额买入
        if cycle_idx == 0:
            return current_score.copy()

        # 后续周期：当 cycle_idx < delay_weeks 时，复用 cycle 0 信号 (维持持仓不换手)；
        # 当 cycle_idx >= delay_weeks 时，与树懒一致，严格使用延迟 delay_weeks 周的历史信号。
        delayed_idx = max(0, cycle_idx - self.delay_weeks)
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
