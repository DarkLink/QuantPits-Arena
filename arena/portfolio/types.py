"""
arena/portfolio/types.py
========================
组合引擎数据类型与数据类定义
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
import pandas as pd


@dataclass
class Order:
    """周频调仓订单"""
    trade_date: str                         # 期望执行日 (如 2026-07-06)
    buy_instruments: List[str]              # 拟买入标的清单
    sell_instruments: List[str]             # 拟卖出标的清单
    is_first_entry: bool = False            # 是否为首次冷启动满额建仓


@dataclass
class TradeRecord:
    """单笔成交记录"""
    date: str                               # 成交日期
    instrument: str                         # 证券标的
    direction: str                          # "BUY" 或 "SELL"
    price: float                            # 成交均价 (Open 或 Close)
    shares: float                           # 成交股数
    value: float                            # 成交金额
    cost: float                             # 交易佣金与印花税成本


@dataclass
class DailyValuation:
    """日频盯市估值点 (Daily Marked-to-Market)"""
    date: str                               # 交易日
    cash: float                             # 账户现金余额
    holdings_value: float                   # 持仓股票市值总额
    total_asset: float                      # 资产总值 = cash + holdings_value
    nav: float                              # 归一化净值 (以初始资金为 1.0000)
    daily_return: float                     # 当日相对前一交易日的收益率


@dataclass
class WeeklySettlement:
    """周频结算点"""
    week_idx: int                           # 周期序号
    settle_date: str                        # 周五结算日
    start_nav: float                        # 周初净值
    end_nav: float                          # 周末净值
    weekly_return: float                    # 当周区间收益率
    turnover: float                         # 当周单边换手率
    weekly_cost: float                      # 当周累计交易成本
    num_holdings: int                       # 期末持股数量


@dataclass
class PortfolioPath:
    """一个 (Contestant, Animal) 组合在整个 Arena 区间的完整回测路径"""
    contestant_id: str
    animal_id: str
    daily_valuations: List[DailyValuation] = field(default_factory=list)
    weekly_settlements: List[WeeklySettlement] = field(default_factory=list)
    trades: List[TradeRecord] = field(default_factory=list)
    final_holdings: Dict[str, float] = field(default_factory=dict)  # {instrument: shares}

    @property
    def nav_series(self) -> pd.Series:
        """返回日频 NAV 时序 (index=datetime)"""
        if not self.daily_valuations:
            return pd.Series(dtype=float)
        dates = [v.date for v in self.daily_valuations]
        navs = [v.nav for v in self.daily_valuations]
        return pd.Series(navs, index=pd.to_datetime(dates), name="nav")

    @property
    def total_return(self) -> float:
        """区间累计总收益率"""
        if not self.daily_valuations:
            return 0.0
        return (self.daily_valuations[-1].nav / self.daily_valuations[0].nav) - 1.0

    @property
    def max_drawdown(self) -> float:
        """日频最大回撤 (MDD)"""
        s = self.nav_series
        if len(s) == 0:
            return 0.0
        cummax = s.cummax()
        dd = (s - cummax) / cummax
        return abs(float(dd.min()))
