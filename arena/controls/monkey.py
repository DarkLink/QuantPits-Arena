"""
arena/controls/monkey.py
========================
Monkey Colony (猴子群落 1000 只) 零假设基准控制组
"""

from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from arena.portfolio.types import DailyValuation, WeeklySettlement


class MonkeyColony:
    """
    1000 只猴子零假设控制组：
    - 每只猴子使用确定性伪随机数发生器 (Seed = base_seed + monkey_idx * 1000 + cycle_idx)
    - 针对给定可交易股票池生成纯随机截面打分
    - 运行相同的标准周频组合策略 (Canonical Policy: TopK=22, DropN=3)
    - 产出零假设分布统计量 (min, 5%, median, 95%, max)
    """

    def __init__(self, colony_size: int = 1000, base_seed: int = 2026):
        self.colony_size = colony_size
        self.base_seed = base_seed

    def generate_monkey_score(
        self,
        monkey_idx: int,
        cycle_idx: int,
        instruments: List[str]
    ) -> pd.Series:
        """
        生成指定猴子在指定周期的确定性随机截面得分。
        """
        seed = (self.base_seed + monkey_idx * 10007 + cycle_idx * 37) % (2**31 - 1)
        rng = np.random.RandomState(seed)
        scores = rng.uniform(0.0, 1.0, size=len(instruments))
        return pd.Series(scores, index=instruments)

    def summarize_distribution(self, values: List[float]) -> Dict[str, float]:
        """计算零假设分布的核心百分位数 (min, 5%, median, 95%, max)"""
        arr = np.array(values)
        if len(arr) == 0:
            return {"min": 0.0, "p05": 0.0, "median": 0.0, "p95": 0.0, "max": 0.0}

        return {
            "min": float(np.min(arr)),
            "p05": float(np.percentile(arr, 5)),
            "median": float(np.median(arr)),
            "p95": float(np.percentile(arr, 95)),
            "max": float(np.max(arr)),
            "mean": float(np.mean(arr)),
            "std": float(np.std(arr)),
        }

    def compute_percentile_rank(self, target_value: float, monkey_values: List[float]) -> float:
        """计算目标模型在猴子群落中的分位数排名 (0.0 ~ 1.0, 越大越好)"""
        arr = np.array(monkey_values)
        if len(arr) == 0:
            return 0.5
        # 计算有多少比例的猴子表现劣于该模型
        return float(np.mean(arr < target_value))
