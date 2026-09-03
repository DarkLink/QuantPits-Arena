"""
tests/test_trading_calendar.py
==============================
交易日历与周频周期状态机的前置验证测试 (Verification First)

验证目标：
1. 真实 Qlib A 股交易日历读取与连续性验证 (~/.qlib/qlib_data/cn_data/calendars/day.txt)
2. 2026 年 7 月关键锚定日期的真实星期与交易日属性核验：
   - 2026-07-03 为周五交易日
   - 2026-07-04 为周六（非交易日，无收盘数据）
   - 2026-07-06 为周一交易日
   - 2026-07-07 为周二交易日（核查用户指定 7/7 建仓还是 7/6 周一建仓）
   - 2026-07-10 为周五交易日
   - 2026-07-13 为周一交易日
   - 2026-08-28 为当前数据最终截止日
3. 周期切分逻辑：自动识别每周五收盘截断点与下周一调仓点，自适应节假日
"""

import os
from pathlib import Path
import datetime
import pytest

CALENDAR_PATH = Path.home() / ".qlib" / "qlib_data" / "cn_data" / "calendars" / "day.txt"


def load_qlib_trading_days():
    """从本地 Qlib 数据加载所有有效 A 股交易日字符串集合及有序列表"""
    assert CALENDAR_PATH.exists(), f"Qlib 交易日历文件不存在: {CALENDAR_PATH}"
    with open(CALENDAR_PATH, "r", encoding="utf-8") as f:
        days = [line.strip() for line in f if line.strip()]
    return days


def test_calendar_existence_and_range():
    """验证日历文件的有效性及最新可用数据覆盖"""
    days = load_qlib_trading_days()
    assert len(days) > 1000
    assert "2026-07-03" in days
    assert "2026-08-28" in days
    assert days[-1] >= "2026-08-28", f"当前数据最新日期为 {days[-1]}，期望至少覆盖至 2026-08-28"


def test_july_2026_anchor_dates_day_of_week():
    """
    【关键核对】验证 2026 年 7 月各关键日期的真实星期与交易日状态
    发现潜在不对劲：
    - 2026-07-04 是周六，非交易日！周五是 2026-07-03。
    - 2026-07-07 是周二！下一周的周一是 2026-07-06。
    """
    days_set = set(load_qlib_trading_days())

    # 7/3 (周五) 是有效交易日
    d_703 = datetime.date(2026, 7, 3)
    assert d_703.weekday() == 4, "2026-07-03 应为星期五"
    assert "2026-07-03" in days_set

    # 7/4 (周六) 是非交易日
    d_704 = datetime.date(2026, 7, 4)
    assert d_704.weekday() == 5, "2026-07-04 真实日历为星期六"
    assert "2026-07-04" not in days_set, "2026-07-04 周六不应在交易日历中"

    # 7/6 (周一) 是有效交易日
    d_706 = datetime.date(2026, 7, 6)
    assert d_706.weekday() == 0, "2026-07-06 应为星期一"
    assert "2026-07-06" in days_set

    # 7/7 (周二) 是有效交易日
    d_707 = datetime.date(2026, 7, 7)
    assert d_707.weekday() == 1, "2026-07-07 应为星期二"
    assert "2026-07-07" in days_set

    # 7/10 (周五) 是有效交易日
    d_710 = datetime.date(2026, 7, 10)
    assert d_710.weekday() == 4, "2026-07-10 应为星期五"
    assert "2026-07-10" in days_set

    # 7/13 (周一) 是有效交易日
    d_713 = datetime.date(2026, 7, 13)
    assert d_713.weekday() == 0, "2026-07-13 应为星期一"
    assert "2026-07-13" in days_set


def build_weekly_cycles(start_date: str, end_date: str, trading_days: list):
    """
    周频状态机周期划分工具函数（用于验证周频推进行为）
    规则：
    - 每个周期：周五收盘产生 signal（或当周最后一个交易日）
    - 下一个交易周首日（通常是周一）执行买卖/调仓
    - 周五收盘结算当周净值
    """
    days_subset = [d for d in trading_days if start_date <= d <= end_date]
    assert len(days_subset) > 0

    # 找到所有周五或当周最后交易日
    cycles = []
    # 模拟周频推进
    return cycles
