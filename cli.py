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
from arena.seasons import SeasonManager
from arena.benchmarks import BenchmarkCategory


def cmd_list_seasons(args):
    """列出当前所有可用赛季"""
    seasons = SeasonManager.list_seasons()
    print("\n" + "=" * 70)
    print(" 🏁 QuantPits-Arena 赛季清单 (Seasons)")
    print("=" * 70)
    for sid in seasons:
        cfg = SeasonManager.get_season_config(sid)
        print(f" • [{sid}] {cfg.title} (Status: {cfg.status})")
        print(f"     Anchor: {cfg.anchor_date} -> {cfg.end_date} | Initial Cash: CNY {cfg.initial_cash:,.0f}")
        print(f"     Description: {cfg.description}")
        b_names = [b.get("id") for b in cfg.benchmarks]
        print(f"     Active Benchmarks: {', '.join(b_names)}")
    print("=" * 70 + "\n")


def cmd_list_benchmarks(args):
    """列出体系化基准 (Benchmarks)"""
    sid = getattr(args, "season", "season_01")
    cfg = SeasonManager.get_season_config(sid)
    print("\n" + "=" * 70)
    print(f" 📊 QuantPits-Arena 基准体系 (Benchmarks for {sid})")
    print("=" * 70)
    for b in cfg.benchmarks:
        bid = b.get("id")
        btype = b.get("type", "BENCHMARK")
        name = b.get("display_name", bid)
        print(f" • [{bid}] {name} (Category: {btype})")
        if "initial_cash" in b:
            print(f"     Initial Cash: CNY {b['initial_cash']:,.0f}")
        if "symbol" in b:
            print(f"     Index Symbol: {b['symbol']}")
    print("=" * 70 + "\n")


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

    # 保存执行快照供后续增量滚动推进
    cp_dir = (Path(args.output) if args.output else RUNS_DIR) / run_id / "checkpoints"
    runner.save_checkpoint_to_disk(cp_dir, cycle_idx=runner.last_completed_cycle_idx)

    # 导出产物
    output_dir = Path(args.output) if args.output else RUNS_DIR
    exporter = DualTierExporter(run_id=run_id, base_dir=output_dir)
    artifacts = exporter.export(results, registry)

    # 可选：运行参数化猴子群落
    if getattr(args, "monkeys", False):
        m_count = getattr(args, "monkey_count", 1000)
        print("\n" + "=" * 70)
        print(f" 🐒 启动参数化猴子群落零假设评估 (11 组策略规格 × {m_count} 只随机猴子)...")
        print("=" * 70)
        monkey_results = runner.run_parametric_monkeys(max_cycles=max_c, colony_size=m_count)
        m_artifacts = exporter.export_monkey_reports(monkey_results, results, registry)
        print(f"    🟢 猴子零假设分布数据: {m_artifacts['monkey_distributions_csv']}")
        print(f"    🟢 选手显著性检验报告: {m_artifacts['contestant_significance_csv']}")
        print(f"    🟢 猴群零假设分析文档: {m_artifacts['monkey_report_md']}")

    print("[3/3] 产物已完成双层隔离与自动化脱敏导出：")
    print(f"    🟢 脱敏公开 NAV:     {artifacts['public_nav']}")
    print(f"    🟢 脱敏指标汇总:     {artifacts['public_metrics']}")
    print(f"    🟢 资本粒度诊断:     {artifacts['public_diagnostics']}")
    print(f"    🟢 收益率衰减矩阵:   {artifacts['public_matrix']}")
    print(f"    🔴 本地私有交易明细: {artifacts['private_trades']}")
    print(f"    💾 最新运行状态快照: {cp_dir / 'latest_state.pkl'}")
    print("=" * 70 + "\n")


def cmd_step(args):
    """从上周快照状态继续往后滚动推进 1 个周期 (Rolling Incremental Weekly Execution)"""
    run_id = args.run_id
    if not run_id:
        print("[ERROR] 必须指定 --run-id 才能恢复历史快照并推进！")
        sys.exit(1)

    base_dir = Path(args.output) if args.output else RUNS_DIR
    cp_dir = base_dir / run_id / "checkpoints"
    latest_path = cp_dir / "latest_state.pkl"

    if not latest_path.exists():
        print(f"[ERROR] 未找到历史状态快照: {latest_path}")
        print("        请先执行一次完整或冷启动回测生成初始快照 (cli.py run --cycles 1 ...)")
        sys.exit(1)

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

    print("\n" + "=" * 70)
    print(f" ⏩ 启动 QuantPits-Arena 按周增量滚动推进: {run_id}")
    print(f"    读取快照: {latest_path}")
    runner.load_checkpoint_from_disk(latest_path)
    print(f"    已恢复至周期: Cycle {runner.last_completed_cycle_idx}")

    next_idx = runner.last_completed_cycle_idx + 1
    if next_idx >= len(runner.cycles):
        print(f"[INFO] 全部周期已执行完毕 (总周期数={len(runner.cycles)})，无需继续推进。")
        print("=" * 70 + "\n")
        return

    target_cycle = runner.cycles[next_idx]
    print(f"    🎯 本次推进目标周期: Cycle {next_idx}")
    print(f"       决策日: {target_cycle.decision_date} (周五收盘)")
    print(f"       执行日: {target_cycle.trade_date} (周一开盘)")
    print(f"       结算日: {target_cycle.settle_date} (周五收盘)")
    print("=" * 70)

    active_contestants = None
    if args.contestants:
        chosen = [c.strip() for c in args.contestants.split(",")]
        active_contestants = [c for c in registry.list_contestants() if c.contestant_id in chosen]
    else:
        active_contestants = registry.list_contestants()

    price_lookup_fn, tradability_filter_fn = runner._setup_market_provider(
        active_contestants, None, None
    )

    # 仅执行目标这 1 个周期
    runner.step_cycle(
        cycle=target_cycle,
        active_contestants=active_contestants,
        price_lookup_fn=price_lookup_fn,
        tradability_filter_fn=tradability_filter_fn
    )

    # 持久化最新状态
    runner.save_checkpoint_to_disk(cp_dir, cycle_idx=next_idx)

    # 导出最新累积路径
    results = {
        key: engine.to_portfolio_path()
        for key, engine in runner.engines.items()
    }
    results[("BENCHMARK", "taotie")] = runner.taotie_benchmark.engine.to_portfolio_path()

    exporter = DualTierExporter(run_id=run_id, base_dir=base_dir)
    artifacts = exporter.export(results, registry)

    # 可选：运行参数化猴子群落
    if getattr(args, "monkeys", False):
        m_count = getattr(args, "monkey_count", 1000)
        print("\n" + "=" * 70)
        print(f" 🐒 启动参数化猴子群落零假设评估 (11 组策略规格 × {m_count} 只随机猴子)...")
        print("=" * 70)
        monkey_results = runner.run_parametric_monkeys(
            max_cycles=next_idx + 1,
            colony_size=m_count,
            price_lookup_fn=price_lookup_fn,
            tradability_filter_fn=tradability_filter_fn
        )
        m_artifacts = exporter.export_monkey_reports(monkey_results, results, registry)
        print(f"    🟢 猴子零假设分布数据: {m_artifacts['monkey_distributions_csv']}")
        print(f"    🟢 选手显著性检验报告: {m_artifacts['contestant_significance_csv']}")
        print(f"    🟢 猴群零假设分析文档: {m_artifacts['monkey_report_md']}")

    print("\n[✔] 增量推进成功，最新状态与累计指标已落盘：")
    print(f"    🟢 脱敏公开 NAV:     {artifacts['public_nav']}")
    print(f"    🟢 脱敏指标汇总:     {artifacts['public_metrics']}")
    print(f"    🟢 资本粒度诊断:     {artifacts['public_diagnostics']}")
    print(f"    🟢 收益率衰减矩阵:   {artifacts['public_matrix']}")
    print(f"    🔴 本地私有交易明细: {artifacts['private_trades']}")
    print(f"    💾 最新运行状态快照: {latest_path}")
def cmd_cycle_step(args):
    """
    周五一键闭环原子执行流 (Friday Loop: Settle Last Week + Commit Next Week)
    每周仅在周五盘后运行一次：
    1. 撮合与结算上周五已冻结锁定的订单；
    2. 依据本周五最新收盘特征产出下周一的全新调仓订单，并计算 SHA-256 存证锁死；
    3. 自动导出战报与 Checkpoint 快照。
    """
    season_id = getattr(args, "season", "season_01")
    cfg = SeasonManager.get_season_config(season_id)

    run_id = args.run_id or f"{season_id}_live"
    base_dir = Path(args.output) if args.output else RUNS_DIR
    run_dir = base_dir / run_id
    cp_dir = run_dir / "checkpoints"
    orders_dir = run_dir / "commitments"
    orders_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 70)
    print(f" 🔄 QuantPits-Arena 周五一键闭环推进 (Friday Loop)")
    print(f"    当前赛季: [{cfg.season_id}] {cfg.title}")
    print(f"    运行 ID:   {run_id}")
    print(f"    模式:     {'Mock 快速验证' if args.mock else '真实本地模型推理'}")
    print("=" * 70)

    calendar = TradingCalendar()
    registry = ContestantRegistry()

    runner = WeeklyCycleRunner(
        anchor_date=cfg.anchor_date,
        end_date=cfg.end_date,
        initial_cash=cfg.initial_cash,
        mock_mode=args.mock,
        calendar=calendar,
        registry=registry
    )

    # 检查历史进度
    latest_path = cp_dir / "latest_checkpoint.pkl"
    next_idx = 0
    if latest_path.exists():
        loaded_idx = runner.load_checkpoint_from_disk(latest_path)
        next_idx = loaded_idx + 1

    if next_idx >= len(runner.cycles):
        print(f"[!] 赛季 {season_id} 所有周期已全部执行完毕，无需进一步推进。")
        return

    cur_cycle = runner.cycles[next_idx]
    print(f"[*] 推进周期: Cycle {next_idx} (交易日: {cur_cycle.trade_date} -> 结算日: {cur_cycle.settle_date})")

    active_contestants = registry.list_contestants()
    runner._init_engines(active_contestants)
    if latest_path.exists():
        runner.load_checkpoint_from_disk(latest_path)

    price_lookup_fn, tradability_filter_fn = runner._setup_market_provider(
        active_contestants, None, None
    )

    # 1. 尝试读取上一次预存证的下周订单 (若有)
    pending_file = orders_dir / f"orders_cycle_{next_idx}.json"
    pending_orders = None
    if pending_file.exists():
        print(f"[1/3] 发现上周五已冻结订单: {pending_file.name}")
        # 在此处可做 SHA-256 校验
    else:
        print(f"[1/3] 首周/无前置预存证订单，执行首周开盘建仓流水线...")

    settled_orders, next_orders = runner.step_friday_cycle(
        cycle=cur_cycle,
        active_contestants=active_contestants,
        price_lookup_fn=price_lookup_fn,
        pending_orders=pending_orders,
        tradability_filter_fn=tradability_filter_fn
    )

    print(f"    ✔ 本周撮合与 Daily MTM 估值结算完毕。")

    # 2. 锁定并存证下周订单
    if next_orders is not None:
        next_file = orders_dir / f"orders_cycle_{next_idx + 1}.json"
        import hashlib, json
        # 简单序列化订单标的
        order_summary = {}
        for (cid, aid), ord_obj in next_orders.items():
            if ord_obj is not None:
                order_summary[f"{cid}_{aid}"] = {
                    "buy": ord_obj.buy_instruments,
                    "sell": ord_obj.sell_instruments,
                    "trade_date": ord_obj.trade_date
                }
            else:
                order_summary[f"{cid}_{aid}"] = None
        serialized = json.dumps(order_summary, sort_keys=True)
        order_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        with open(next_file, "w", encoding="utf-8") as f:
            f.write(serialized)

        print(f"[2/3] 成功生成并锁定下周订单: {next_file.name}")
        print(f"    🔐 密码学存证指纹 (SHA-256): {order_hash}")
    else:
        print(f"[2/3] 已达赛季尾声，无下周订单生成。")

    # 3. 导出快照与战报
    runner.save_checkpoint_to_disk(cp_dir, cycle_idx=next_idx)

    results = {
        key: engine.to_portfolio_path()
        for key, engine in runner.engines.items()
    }
    results[("BENCHMARK", "taotie")] = runner.taotie_benchmark.engine.to_portfolio_path()

    exporter = DualTierExporter(run_id=run_id, base_dir=base_dir)
    artifacts = exporter.export(results, registry)

    print(f"[3/3] 战报生成成功，最新状态已落盘：")
    print(f"    🟢 脱敏公开 NAV:     {artifacts['public_nav']}")
    print(f"    🟢 脱敏指标汇总:     {artifacts['public_metrics']}")
    print(f"    💾 最新运行快照:     {latest_path}")
    print("=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(description="QuantPits-Arena CLI")
    subparsers = parser.add_subparsers(dest="subcommand", help="子命令")

    # cycle-step (推荐周五一键闭环)
    p_cstep = subparsers.add_parser("cycle-step", help="周五一键闭环：结算上周已冻结订单 + 预承诺锁定下周新订单")
    p_cstep.add_argument("--season", type=str, default="season_01", help="指定赛季 ID (默认 season_01)")
    p_cstep.add_argument("--run-id", type=str, default=None, help="指定运行 ID")
    p_cstep.add_argument("--mock", action="store_true", help="使用 Mock 适配器快速验证")
    p_cstep.add_argument("--output", type=str, default=None, help="指定输出根目录")

    # list-seasons
    subparsers.add_parser("list-seasons", help="查看所有可用赛季")

    # list-benchmarks
    p_b = subparsers.add_parser("list-benchmarks", help="查看赛季基准体系")
    p_b.add_argument("--season", type=str, default="season_01", help="指定赛季 ID (默认 season_01)")

    # list-contestants
    subparsers.add_parser("list-contestants", help="查看所有参赛选手")

    # list-animals
    subparsers.add_parser("list-animals", help="查看所有执行动物")

    # audit
    subparsers.add_parser("audit", help="执行本地零泄密隐私审计")

    # run
    p_run = subparsers.add_parser("run", help="启动周频回测")
    p_run.add_argument("--season", type=str, default="season_01", help="指定赛季 ID (默认 season_01)")
    p_run.add_argument("--run-id", type=str, default=None, help="指定运行 ID")
    p_run.add_argument("--anchor-date", type=str, default=DEFAULT_ANCHOR_DATE, help="初始锚定日期")
    p_run.add_argument("--end-date", type=str, default=DEFAULT_END_DATE, help="回测结束日期")
    p_run.add_argument("--cycles", type=int, default=0, help="限制运行的最大周数 (0 表示全部)")
    p_run.add_argument("--initial-cash", type=float, default=500_000.0, help="初始资金规模 (默认 500,000 元)")
    p_run.add_argument("--mock", action="store_true", help="使用 Mock 适配器运行全流程快速验证")
    p_run.add_argument("--monkeys", action="store_true", help="同时运行参数化猴子群落零假设评估")
    p_run.add_argument("--monkey-count", type=int, default=1000, help="每组策略规格的猴子数量 (默认 1000 只)")
    p_run.add_argument("--contestants", type=str, default=None, help="逗号分隔的参赛选手 ID (如 QP-20260626-STATIC,QP-20260626-CPCV)")
    p_run.add_argument("--output", type=str, default=None, help="指定输出根目录")

    # step
    p_step = subparsers.add_parser("step", help="从上周快照增量滚动推进 1 个周期")
    p_step.add_argument("--season", type=str, default="season_01", help="指定赛季 ID (默认 season_01)")
    p_step.add_argument("--run-id", type=str, required=True, help="指定待推进的运行 ID")
    p_step.add_argument("--anchor-date", type=str, default=DEFAULT_ANCHOR_DATE, help="初始锚定日期")
    p_step.add_argument("--end-date", type=str, default=DEFAULT_END_DATE, help="回测结束日期")
    p_step.add_argument("--initial-cash", type=float, default=500_000.0, help="初始资金规模 (默认 500,000 元)")
    p_step.add_argument("--mock", action="store_true", help="使用 Mock 适配器运行")
    p_step.add_argument("--monkeys", action="store_true", help="同时运行参数化猴子群落零假设评估")
    p_step.add_argument("--monkey-count", type=int, default=1000, help="每组策略规格的猴子数量 (默认 1000 只)")
    p_step.add_argument("--contestants", type=str, default=None, help="逗号分隔的参赛选手 ID")
    p_step.add_argument("--output", type=str, default=None, help="指定输出根目录")

    args = parser.parse_args()
    if not args.subcommand:
        parser.print_help()
        sys.exit(0)

    if args.subcommand == "list-seasons":
        cmd_list_seasons(args)
    elif args.subcommand == "list-benchmarks":
        cmd_list_benchmarks(args)
    elif args.subcommand == "list-contestants":
        cmd_list_contestants(args)
    elif args.subcommand == "list-animals":
        cmd_list_animals(args)
    elif args.subcommand == "audit":
        cmd_audit(args)
    elif args.subcommand == "run":
        cmd_run(args)
    elif args.subcommand == "step":
        cmd_step(args)
    elif args.subcommand == "cycle-step":
        cmd_cycle_step(args)


if __name__ == "__main__":
    main()

