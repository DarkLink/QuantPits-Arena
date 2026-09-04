#!/usr/bin/env python3
"""
cli.py
======
QuantPits Graveyard Arena (Zoo) 命令行入口工具
"""

import argparse
import sys
import datetime
from pathlib import Path

from arena.config import REPO_ROOT, RUNS_DIR, DEFAULT_ANCHOR_DATE, DEFAULT_END_DATE
from arena.calendar import TradingCalendar
from arena.contestants import ContestantRegistry
from arena.animals import get_all_animals
from arena.runner import WeeklyCycleRunner
from arena.reports import DualTierExporter


def cmd_list_contestants(args):
    """列出当前注册的所有参赛选手"""
    registry = ContestantRegistry()
    contestants = registry.list_contestants()

    print("\n" + "=" * 70)
    print(" 🏆 QuantPits-Arena 参赛选手清单 (Contestants)")
    print("=" * 70)

    for c in contestants:
        anon_id = registry.get_anonymous_id(c.contestant_id)
        role = c.historical_role or "None"
        print(f" • [{anon_id}] {c.display_name}")
        print(f"     Family: {c.family} | Cutoff: {c.train_cutoff} | Integrity: {c.integrity_class}")
        print(f"     Role: {role}")
    print("=" * 70 + "\n")


def cmd_list_animals(args):
    """列出 9 种标准执行动物"""
    animals = get_all_animals()

    print("\n" + "=" * 70)
    print(" 🐾 QuantPits-Arena 动物园清单 (Animal Handlers)")
    print("=" * 70)

    for a in animals:
        policy = a.get_portfolio_policy()
        topk = policy.get("topk", 22)
        n_drop = policy.get("n_drop", 3)
        print(f" • [{a.animal_id}] {a.display_name} ({a.family})")
        print(f"     Policy: TopK={topk}, DropN={n_drop}")
    print("=" * 70 + "\n")


def cmd_audit(args):
    """执行本地零泄密合规隐私审计"""
    import subprocess
    script = REPO_ROOT / "scripts" / "audit_privacy.py"
    ret = subprocess.run([sys.executable, str(script)])
    sys.exit(ret.returncode)


def cmd_run(args):
    """执行周频同步 Arena 回测"""
    run_id = args.run_id or f"run_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print("\n" + "=" * 70)
    print(f" 🚀 启动 QuantPits-Arena 周频巡回锦标赛: {run_id}")
    print(f"    起点: {args.anchor_date} (周五收盘) | 截止: {args.end_date}")
    print(f"    模式: {'Mock 快速验证' if args.mock else '真实本地模型推理'}")
    print("=" * 70)

    calendar = TradingCalendar()
    registry = ContestantRegistry()

    runner = WeeklyCycleRunner(
        anchor_date=args.anchor_date,
        end_date=args.end_date,
        initial_cash=args.initial_cash,
        mock_mode=args.mock,
        calendar=calendar,
        registry=registry
    )

    print(f"[1/3] 已划分 {len(runner.cycles)} 个周频执行周期...")
    max_c = args.cycles if args.cycles > 0 else None

    active_contestants = None
    if args.contestants:
        chosen = [c.strip() for c in args.contestants.split(",")]
        active_contestants = [c for c in registry.list_contestants() if c.contestant_id in chosen]
        print(f"    指定参赛选手: {[c.contestant_id for c in active_contestants]}")

    results = runner.run(contestants=active_contestants, max_cycles=max_c)
    print(f"[2/3] 完成回测计算，涵盖 {len(results)} 个 (Contestant, Animal) 组合路径。")

    output_dir = Path(args.output) if args.output else RUNS_DIR
    exporter = DualTierExporter(run_id=run_id, base_dir=output_dir)
    artifacts = exporter.export(results, registry)

    print("[3/3] 产物已完成双层隔离与自动化脱敏导出：")
    print(f"    🟢 脱敏公开 NAV:     {artifacts['public_nav']}")
    print(f"    🟢 脱敏指标汇总:     {artifacts['public_metrics']}")
    print(f"    🟢 资本粒度诊断:     {artifacts['public_diagnostics']}")
    print(f"    🟢 收益率衰减矩阵:   {artifacts['public_matrix']}")
    print(f"    🔴 本地私有交易明细: {artifacts['private_trades']}")
    print("=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(description="QuantPits-Arena CLI")
    subparsers = parser.add_subparsers(dest="subcommand", help="子命令")

    # list-contestants
    subparsers.add_parser("list-contestants", help="查看所有参赛选手")

    # list-animals
    subparsers.add_parser("list-animals", help="查看所有执行动物")

    # audit
    subparsers.add_parser("audit", help="执行本地零泄密隐私审计")

    # run
    p_run = subparsers.add_parser("run", help="启动周频回测")
    p_run.add_argument("--run-id", type=str, default=None, help="指定运行 ID")
    p_run.add_argument("--anchor-date", type=str, default=DEFAULT_ANCHOR_DATE, help="初始锚定日期")
    p_run.add_argument("--end-date", type=str, default=DEFAULT_END_DATE, help="回测结束日期")
    p_run.add_argument("--cycles", type=int, default=0, help="限制运行的最大周数 (0 表示全部)")
    p_run.add_argument("--initial-cash", type=float, default=500_000.0, help="初始资金规模 (默认 500,000 元)")
    p_run.add_argument("--mock", action="store_true", help="使用 Mock 适配器运行全流程快速验证")
    p_run.add_argument("--contestants", type=str, default=None, help="逗号分隔的参赛选手 ID (如 QP-20260626-STATIC,QP-20260626-CPCV)")
    p_run.add_argument("--output", type=str, default=None, help="指定输出根目录")

    args = parser.parse_args()
    if not args.subcommand:
        parser.print_help()
        sys.exit(0)

    if args.subcommand == "list-contestants":
        cmd_list_contestants(args)
    elif args.subcommand == "list-animals":
        cmd_list_animals(args)
    elif args.subcommand == "audit":
        cmd_audit(args)
    elif args.subcommand == "run":
        cmd_run(args)


if __name__ == "__main__":
    main()
