"""
arena/portfolio/costs.py
========================
交易成本模型
"""

from arena.config import (
    DEFAULT_OPEN_COST,
    DEFAULT_CLOSE_COST,
    DEFAULT_MIN_COST
)


class CostModel:
    """A 股标准交易费率模型"""

    def __init__(
        self,
        open_cost: float = DEFAULT_OPEN_COST,
        close_cost: float = DEFAULT_CLOSE_COST,
        min_cost: float = DEFAULT_MIN_COST
    ):
        self.open_cost = open_cost
        self.close_cost = close_cost
        self.min_cost = min_cost

    def calculate_buy_cost(self, trade_value: float) -> float:
        """计算买入佣金成本（最低 5 元）"""
        if trade_value <= 0:
            return 0.0
        return max(trade_value * self.open_cost, self.min_cost)

    def calculate_sell_cost(self, trade_value: float) -> float:
        """计算卖出成本（含佣金及印花税）"""
        if trade_value <= 0:
            return 0.0
        return max(trade_value * self.close_cost, self.min_cost)
