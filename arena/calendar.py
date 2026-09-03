"""
arena/calendar.py
=================
A 股交易日历与周频同步执行周期管理模块
"""

from dataclasses import dataclass
from typing import List, Optional
import datetime
from pathlib import Path
from arena.config import CALENDAR_PATH, DEFAULT_ANCHOR_DATE, DEFAULT_END_DATE


@dataclass
class WeeklyCycle:
    """一个标准周频周期的结构化定义"""
    cycle_idx: int                  # 周期序号 (0: 初始建仓周, 1: 第一次调仓周...)
    decision_date: str              # 决策截断日 (周五收盘，产生下一周订单)
    trade_date: str                 # 订单执行日 (周一开盘)
    settle_date: str                # 当周结算日 (周五收盘)
    trading_days: List[str]         # 当周内所有交易日列表 (用于 Daily Marked-to-Market 估值)

    @property
    def is_first_week(self) -> bool:
        return self.cycle_idx == 0


class TradingCalendar:
    """A 股真实交易日历管理器"""

    def __init__(self, calendar_path: Optional[Path] = None):
        self.path = calendar_path or CALENDAR_PATH
        if not self.path.exists():
            raise FileNotFoundError(f"未找到 Qlib 交易日历文件: {self.path}")

        with open(self.path, "r", encoding="utf-8") as f:
            self.all_days = [line.strip() for line in f if line.strip()]
        self.days_set = set(self.all_days)
        self.day_to_idx = {d: i for i, d in enumerate(self.all_days)}

    def is_trading_day(self, date_str: str) -> bool:
        """判断是否为有效 A 股交易日"""
        return date_str in self.days_set

    def get_latest_trading_day_on_or_before(self, date_str: str) -> str:
        """获取指定日期或之前的最近一个有效交易日（例如 7/4 周六 -> 7/3 周五）"""
        if date_str in self.days_set:
            return date_str
        # 向前倒推寻找
        dt = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        for _ in range(14):
            dt -= datetime.timedelta(days=1)
            s = dt.strftime("%Y-%m-%d")
            if s in self.days_set:
                return s
        raise ValueError(f"无法找到 {date_str} 之前的有效交易日")

    def get_next_trading_day(self, date_str: str) -> str:
        """获取指定日期之后的下一个有效交易日（例如 7/3 周五 -> 7/6 周一）"""
        if date_str in self.day_to_idx:
            idx = self.day_to_idx[date_str]
            if idx + 1 < len(self.all_days):
                return self.all_days[idx + 1]
            raise IndexError("已到达日历末尾")

        dt = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        for _ in range(14):
            dt += datetime.timedelta(days=1)
            s = dt.strftime("%Y-%m-%d")
            if s in self.days_set:
                return s
        raise ValueError(f"无法找到 {date_str} 之后的有效交易日")

    def get_trading_days(self, start_date: str, end_date: str) -> List[str]:
        """获取 [start_date, end_date] 区间内的所有有效交易日"""
        return [d for d in self.all_days if start_date <= d <= end_date]

    def build_weekly_cycles(
        self,
        anchor_date: str = DEFAULT_ANCHOR_DATE,
        end_date: str = DEFAULT_END_DATE
    ) -> List[WeeklyCycle]:
        """
        构建周频执行周期序列。

        规则：
        - Cycle 0:
          - decision_date: 截至 anchor_date 的最新交易日 (如 2026-07-03 周五收盘)
          - trade_date: 下一交易日 (2026-07-06 周一开盘)
          - settle_date: 当周最后一个交易日 (2026-07-10 周五收盘)
          - trading_days: [07-06, 07-07, 07-08, 07-09, 07-10]
        - Cycle 1:
          - decision_date: 2026-07-10 周五收盘
          - trade_date: 2026-07-13 周一开盘
          - settle_date: 2026-07-17 周五收盘
          - trading_days: [07-13, 07-14, 07-15, 07-16, 07-17]
        ... 一直到 end_date
        """
        actual_anchor = self.get_latest_trading_day_on_or_before(anchor_date)
        actual_end = self.get_latest_trading_day_on_or_before(end_date)

        cycles = []
        cycle_idx = 0
        current_decision = actual_anchor

        while True:
            # 订单执行日：下周第一个交易日
            try:
                trade_date = self.get_next_trading_day(current_decision)
            except (IndexError, ValueError):
                break

            if trade_date > actual_end:
                break

            # 寻找该周的结算日（本周五，或遇到节假日为当周最后交易日）
            # 策略：沿着交易日走，只要下一个交易日还在同一周（周一至周五内），就纳入本周
            week_days = [trade_date]
            curr_d = trade_date
            while True:
                try:
                    next_d = self.get_next_trading_day(curr_d)
                except Exception:
                    break

                # 检查是否属于同一个日历周
                dt_curr = datetime.datetime.strptime(curr_d, "%Y-%m-%d").date()
                dt_next = datetime.datetime.strptime(next_d, "%Y-%m-%d").date()

                # 如果下一个交易日已跨到下一周（例如当前是周五，下一交易日是下周一），跳出
                if dt_next.weekday() <= dt_curr.weekday() or (dt_next - dt_curr).days > 4:
                    break

                if next_d > actual_end:
                    week_days.append(next_d)
                    curr_d = next_d
                    break

                week_days.append(next_d)
                curr_d = next_d

            settle_date = week_days[-1]

            cycles.append(
                WeeklyCycle(
                    cycle_idx=cycle_idx,
                    decision_date=current_decision,
                    trade_date=trade_date,
                    settle_date=settle_date,
                    trading_days=week_days
                )
            )

            # 下一周期的决策日即为当周结算日（周五收盘）
            current_decision = settle_date
            cycle_idx += 1

            if current_decision >= actual_end:
                break

        return cycles
