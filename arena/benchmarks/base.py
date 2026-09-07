"""
arena/benchmarks/base.py
========================
Arena 基准统一抽象基类契约与分类定义 (First-Class Benchmark Protocol)
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Callable, Dict, Any, List
import pandas as pd

from arena.calendar import WeeklyCycle
from arena.portfolio.types import PortfolioPath


class BenchmarkCategory(str, Enum):
    """基准分类枚举"""
    INDEX = "INDEX"                  # 宏观市场公开指数 (如 CSI300)
    EXECUTABLE = "EXECUTABLE"        # 物理受限真实执行组合 (如 50万本金/100股一手 Taotie)
    THEORETICAL = "THEORETICAL"      # 理论全池等权无摩擦基准 (如 Ghost Taotie)
    STATISTICAL = "STATISTICAL"      # 零假设统计控制组 (如 Monkey Colony)


class Benchmark(ABC):
    """
    所有 Arena 基准的一等公民抽象契约。
    """

    def __init__(
        self,
        benchmark_id: str,
        display_name: str,
        category: BenchmarkCategory,
        description: str = ""
    ):
        self.benchmark_id = benchmark_id
        self.display_name = display_name
        self.category = category
        self.description = description

    @abstractmethod
    def step(
        self,
        cycle: WeeklyCycle,
        universe: Optional[List[str]] = None,
        price_lookup_fn: Optional[Callable[[str, str, str], float]] = None,
        tradability_filter_fn: Optional[Callable[[str, str], bool]] = None,
        **kwargs
    ) -> None:
        """
        向前推进一个周频周期 (增量步进)。
        """
        pass

    @abstractmethod
    def to_portfolio_path(self) -> PortfolioPath:
        """
        导出标准化组合回测路径，包含 daily_nav_series、trades_history、holdings_history 等。
        """
        pass

    def get_summary_metrics(self) -> Dict[str, Any]:
        """
        获取基准的风险收益摘要指标。
        """
        path = self.to_portfolio_path()
        final_nav = path.daily_valuations[-1].nav if path.daily_valuations else 1.0
        return {
            "benchmark_id": self.benchmark_id,
            "display_name": self.display_name,
            "category": self.category.value,
            "total_return": path.total_return,
            "max_drawdown": path.max_drawdown,
            "final_nav": final_nav,
        }
