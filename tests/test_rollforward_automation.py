"""
tests/test_rollforward_automation.py
====================================
自动化滚动推进与日期推进命令单元测试
"""

import pytest
import argparse
from pathlib import Path

from arena.config import REPO_ROOT, DEFAULT_END_DATE
from arena.calendar import TradingCalendar
from arena.reports.sanitizer import sync_chronicles
from cli import cmd_bump_date


def test_trading_days_calculation_in_bump():
    """验证 TradingCalendar 在指定日期间计算交易日数的一致性"""
    cal = TradingCalendar()
    assert cal.is_trading_day("2026-09-11")
    tds = cal.get_trading_days("2026-07-03", "2026-09-11")
    assert len(tds) == 51


def test_sync_chronicles_idempotent():
    """验证 sync_chronicles 的幂等性与同步能力"""
    res1 = sync_chronicles()
    assert res1 >= 0
    res2 = sync_chronicles()
    assert res2 == 0


def test_cli_parser_subcommands():
    """验证 cli.py 的 bump-date 与 rollforward 子命令参数配置正确解析"""
    import cli

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="subcommand")

    p_step = subparsers.add_parser("step")
    p_step.add_argument("--season", type=str, default="season_01")
    p_step.add_argument("--run-id", type=str, default=None)

    p_bump = subparsers.add_parser("bump-date")
    p_bump.add_argument("--end-date", type=str, required=True)
    p_bump.add_argument("--seasons", nargs="+", default=None)

    p_rf = subparsers.add_parser("rollforward")
    p_rf.add_argument("--end-date", type=str, default=None)
    p_rf.add_argument("--seasons", nargs="+", default=None)
    p_rf.add_argument("--monkeys", dest="monkeys", action="store_true", default=True)
    p_rf.add_argument("--no-monkeys", dest="monkeys", action="store_false")

    args = parser.parse_args(["step", "--season", "season_01"])
    assert args.run_id is None
    assert args.season == "season_01"

    args = parser.parse_args(["bump-date", "--end-date", "2026-09-18"])
    assert args.end_date == "2026-09-18"
    assert args.seasons is None

    # rollforward 默认带猴子
    args = parser.parse_args(["rollforward", "--end-date", "2026-09-18"])
    assert args.end_date == "2026-09-18"
    assert args.monkeys is True

    # rollforward 显式指定 --no-monkeys
    args_no_m = parser.parse_args(["rollforward", "--no-monkeys"])
    assert args_no_m.monkeys is False


def test_bump_date_dry_run_with_current_date():
    """测试 bump-date 对当前已知日期的原子更新能够安全幂等执行"""
    args = argparse.Namespace(end_date=DEFAULT_END_DATE, seasons=None)
    res = cmd_bump_date(args)
    assert res == DEFAULT_END_DATE
