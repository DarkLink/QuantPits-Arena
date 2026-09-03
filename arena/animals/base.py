"""
arena/animals/base.py
====================
Animal 执行动物基类定义
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import pandas as pd


class Animal(ABC):
    """
    Animal 抽象基类。

    职责：
    1. 接收参赛模型生成的原始 score，按固定规则进行时序延迟或截面反转等变换。
    2. 提供对应的调仓策略参数 (TopK, DropN 等)。
    """

    def __init__(self, animal_id: str, display_name: str, family: str):
        self.animal_id = animal_id
        self.display_name = display_name
        self.family = family

    @abstractmethod
    def transform_signal(
        self,
        current_score: pd.Series,
        history_scores: Dict[int, pd.Series],
        cycle_idx: int
    ) -> Optional[pd.Series]:
        """
        对给定的截面得分进行动物特有的信号变换。

        Args:
            current_score: 当前周期周五收盘产生的新截面得分 (Series, index=instrument)
            history_scores: 历史周期得分字典 {cycle_idx: score_series}
            cycle_idx: 当前周期的序号 (0 表示首周 Anchor 周)

        Returns:
            变换后的截面得分 Series；若返回 None，表示处于冷启动延迟等待期（保持 100% 空仓现金）。
        """
        pass

    @abstractmethod
    def get_portfolio_policy(self) -> Dict[str, Any]:
        """返回该动物所遵循的组合与调仓策略"""
        pass
