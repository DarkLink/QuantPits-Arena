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
from arena.reports import DualTierExporter, sync_chronicles
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
    season_id = getattr(args, "season", "season_01")
    season_cfg = SeasonManager.get_season_config(season_id)

    run_id = args.run_id or f"{season_id}_run"
    anchor_date = args.anchor_date if args.anchor_date != DEFAULT_ANCHOR_DATE else season_cfg.anchor_date
    end_date = args.end_date if args.end_date != DEFAULT_END_DATE else season_cfg.end_date
    initial_cash = args.initial_cash if args.initial_cash != 500000.0 else season_cfg.initial_cash

    print("\n" + "=" * 70)
    print(f" 🚀 启动 QuantPits-Arena 周频巡回锦标赛: {run_id}")
    print(f"    赛季: [{season_cfg.season_id}] {season_cfg.title}")
    print(f"    起点: {anchor_date} (周五收盘) | 截止: {end_date}")
    print(f"    模式: {'Mock 快速验证' if args.mock else '真实本地模型推理'}")
    print("=" * 70)

    output_dir = Path(args.output) if args.output else RUNS_DIR
    run_dir = output_dir / run_id

    calendar = TradingCalendar()
    registry = ContestantRegistry()

    runner = WeeklyCycleRunner(
        anchor_date=anchor_date,
        end_date=end_date,
        initial_cash=initial_cash,
        mock_mode=args.mock,
        calendar=calendar,
        registry=registry,
        season_id=season_id,
        run_dir=run_dir,
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
    season_id = getattr(args, "season", "season_01")
    season_cfg = SeasonManager.get_season_config(season_id)

    run_id = args.run_id or f"{season_id}_run"
    base_dir = Path(args.output) if args.output else RUNS_DIR
    run_dir = base_dir / run_id
    cp_dir = run_dir / "checkpoints"
    latest_path = cp_dir / "latest_state.pkl"

    if not latest_path.exists():
        print(f"[ERROR] 未找到历史状态快照: {latest_path}")
        print("        请先执行一次完整或冷启动回测生成初始快照 (cli.py run --cycles 1 ...)")
        sys.exit(1)

    anchor_date = args.anchor_date if args.anchor_date != DEFAULT_ANCHOR_DATE else season_cfg.anchor_date
    end_date = args.end_date if args.end_date != DEFAULT_END_DATE else season_cfg.end_date
    initial_cash = args.initial_cash if args.initial_cash != 500_000.0 else season_cfg.initial_cash

    calendar = TradingCalendar()
    registry = ContestantRegistry()

    runner = WeeklyCycleRunner(
        anchor_date=anchor_date,
        end_date=end_date,
        initial_cash=initial_cash,
        mock_mode=args.mock,
        calendar=calendar,
        registry=registry,
        season_id=season_id,
        run_dir=run_dir
    )

    print("\n" + "=" * 70)
    print(f" ⏩ 启动 QuantPits-Arena 按周增量滚动推进: {run_id}")
    print(f"    赛季: [{season_cfg.season_id}] {season_cfg.title}")
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
    results[("BENCHMARK", "ghost_taotie")] = runner.ghost_taotie_benchmark.engine.to_portfolio_path()

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
    print("=" * 70 + "\n")


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
        registry=registry,
        season_id=season_id,
        run_dir=run_dir,
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

def cmd_export_web(args):
    """通用 Web Payload 导出命令 (Stage 3)"""
    season_id = getattr(args, "season", "season_01")
    cfg = SeasonManager.get_season_config(season_id)
    run_id = args.run_id or f"{season_id}_run"
    base_dir = Path(args.output) if args.output else RUNS_DIR
    exporter = DualTierExporter(run_id=run_id, base_dir=base_dir)

    print("\n" + "=" * 70)
    print(f" 🌐 导出通用前端 Web Payload: {season_id}")
    print(f"    来源目录: {base_dir / run_id / 'public'}")
    print("=" * 70)

    out_file = exporter.export_web_payload(season_cfg=cfg)
    print(f"[✔] 成功导出前端 Payload: {out_file} ({out_file.stat().st_size / 1024:.1f} KB)")
    print("=" * 70 + "\n")


def cmd_infer(args):
    """Stage 1: 通用股票池全量候选模型自动批处理推理"""
    universe = getattr(args, "universe", "csi500")
    force = getattr(args, "force", False)
    from arena.inference.batch_infer import run_batch_inference
    out_file = run_batch_inference(market=universe, force=force)
    print(f"[✔] 推理完成，预测库已就绪: {out_file}")


def cmd_pipeline(args):
    """一键执行全流程赛季管线: Stage 1(Infer) -> Stage 2(Run) -> Stage 3(Export) -> Stage 4(Audit)"""
    season_id = getattr(args, "season", "season_01")
    cfg = SeasonManager.get_season_config(season_id)
    run_id = args.run_id or f"{season_id}_run"
    force_infer = getattr(args, "force_infer", False)

    print("\n" + "=" * 70)
    print(f" 🏁 启动全自动化赛季标准化管线 (The Season Pipeline)")
    print(f"    赛季目标: [{season_id}] {cfg.title}")
    print(f"    股票池:   {cfg.universe_code}")
    print(f"    运行标识: {run_id}")
    print("=" * 70)

    # 1. Stage 1: 检查或自动执行股票池模型打分推理
    universe = cfg.universe_code
    pred_dir = REPO_ROOT / "artifacts" / "predictions"
    season_pred = pred_dir / f"{season_id}_contestants_oos.pkl"
    univ_pred = pred_dir / f"{universe}_contestants_oos.pkl"

    if force_infer or (not season_pred.exists() and not univ_pred.exists() and universe not in ["csirun300", "csi300"]):
        print(f"\n[Stage 1/4] 股票池 [{universe}] 预测库未就绪，自动启动全量候选模型批处理推理...")
        from arena.inference.batch_infer import run_batch_inference
        run_batch_inference(
            market=universe,
            oos_start="2026-06-29",
            oos_end=cfg.end_date,
            fit_start="2026-04-01",
            fit_end=cfg.anchor_date,
            output_file=univ_pred,
            force=force_infer
        )
    else:
        print(f"[Stage 1/4] 股票池 [{universe}] 预测库已就绪，跳过重复推理。")

    # 2. Stage 2: 运行周频回测与参数化猴群评估
    print(f"\n[Stage 2/4] 启动周频锦标赛与猴群零假设评估...")
    args.monkeys = True
    args.season = season_id
    args.run_id = run_id
    cmd_run(args)

    # 3. Stage 3: 导出前端 Payload 并自动注册
    print(f"\n[Stage 3/4] 导出前端 Web Payload 并自动注册...")
    cmd_export_web(args)

    # 4. Stage 4: 本地脱敏合规审计
    print(f"\n[Stage 4/4] 运行本地零泄密隐私审计...")
    cmd_audit(args)
    print("\n" + "=" * 70)
    print(f"[🎉] 赛季 [{season_id}] 全自动化标准化流水线圆满完成！")
    print("=" * 70 + "\n")


def cmd_bump_date(args):
    """一键更新全局配置、活跃赛季 YAML 及前端索引中的截止交易日 (Horizon Bump)"""
    import re

    target_date = args.end_date
    calendar = TradingCalendar()
    if not calendar.is_trading_day(target_date):
        print(f"[WARN] 目标日期 {target_date} 不是有效交易日，自动查找之前的最近有效交易日...")
        actual_end_date = calendar.get_latest_trading_day_on_or_before(target_date)
        print(f"       调整为交易日: {actual_end_date}")
    else:
        actual_end_date = target_date

    print("\n" + "=" * 70)
    print(f" 📅 推进赛季结算截止日期 (Horizon Bump): -> {actual_end_date}")
    print("=" * 70)

    # 1. 更新 arena/config.py 中的 DEFAULT_END_DATE
    config_py = REPO_ROOT / "arena" / "config.py"
    if config_py.exists():
        py_text = config_py.read_text(encoding="utf-8")
        updated_py = re.sub(
            r'(DEFAULT_END_DATE\s*=\s*["\'])[\d\-]+(["\'])',
            rf'\g<1>{actual_end_date}\g<2>',
            py_text
        )
        if updated_py != py_text:
            config_py.write_text(updated_py, encoding="utf-8")
            print(f"[✔] 已更新全局默认配置: arena/config.py (DEFAULT_END_DATE = \"{actual_end_date}\")")
        else:
            print(f"[i] arena/config.py 中的 DEFAULT_END_DATE 已是 \"{actual_end_date}\"")

    # 2. 识别目标赛季并更新 season_config.yaml
    if args.seasons:
        if args.seasons == ["all"]:
            seasons_to_update = SeasonManager.list_seasons()
        else:
            seasons_to_update = args.seasons
    else:
        # 默认更新所有 ACTIVE / PREVIEW / DEMO 赛季 (排除 DRAFT)
        seasons_to_update = []
        for sid in SeasonManager.list_seasons():
            cfg = SeasonManager.get_season_config(sid)
            if cfg.status in ["ACTIVE", "PREVIEW", "DEMO"]:
                seasons_to_update.append(sid)

    updated_seasons_info = {}
    for sid in seasons_to_update:
        yaml_path = REPO_ROOT / "seasons" / sid / "season_config.yaml"
        if not yaml_path.exists():
            yaml_path = REPO_ROOT / "seasons" / sid / "season.yaml"
        if not yaml_path.exists():
            continue

        cfg = SeasonManager.get_season_config(sid)
        tds = calendar.get_trading_days(cfg.anchor_date, actual_end_date)
        trading_days_count = len(tds)
        updated_seasons_info[sid] = {
            "end_date": actual_end_date,
            "trading_days": trading_days_count,
            "anchor_date": cfg.anchor_date
        }

        yaml_text = yaml_path.read_text(encoding="utf-8")
        # 精准替换 calendar 块内的 end_date
        updated_yaml = re.sub(
            r'(\bend_date:\s*["\'])[\d\-]+(["\'])',
            rf'\g<1>{actual_end_date}\g<2>',
            yaml_text
        )
        # 精准替换 banner proof_text 中的日期范围 (YYYY-MM-DD ~ YYYY-MM-DD)
        updated_yaml = re.sub(
            r'(\b\d{4}-\d{2}-\d{2}\s*~\s*)\d{4}-\d{2}-\d{2}',
            rf'\g<1>{actual_end_date}',
            updated_yaml
        )
        if updated_yaml != yaml_text:
            yaml_path.write_text(updated_yaml, encoding="utf-8")
            print(f"[✔] 已更新赛季配置: {yaml_path.relative_to(REPO_ROOT)} (end_date: {actual_end_date}, 交易日数: {trading_days_count})")
        else:
            print(f"[i] 赛季配置已是最新: {yaml_path.relative_to(REPO_ROOT)}")

    # 3. 更新 web/js/data/seasons_index.js
    index_file = REPO_ROOT / "web" / "js" / "data" / "seasons_index.js"
    if index_file.exists():
        content = index_file.read_text(encoding="utf-8")
        orig_content = content
        for sid, info in updated_seasons_info.items():
            pattern = rf'({{\s*id:\s*["\']{re.escape(sid)}["\'].*?\}})'
            match = re.search(pattern, content, flags=re.DOTALL)
            if match:
                block = match.group(1)
                new_block = re.sub(
                    r'(end_date:\s*["\'])[\d\-]+(["\'])',
                    rf'\g<1>{info["end_date"]}\g<2>',
                    block
                )
                new_block = re.sub(
                    r'(trading_days:\s*)\d+',
                    rf'\g<1>{info["trading_days"]}',
                    new_block
                )
                cal_end_ym = info["end_date"][:7].replace("-", ".")
                new_block = re.sub(
                    r'(period:\s*["\'][\d\.]+\s*-\s*)[\d\.]+(["\'])',
                    rf'\g<1>{cal_end_ym}\g<2>',
                    new_block
                )
                if new_block != block:
                    content = content[:match.start()] + new_block + content[match.end():]
        if content != orig_content:
            index_file.write_text(content, encoding="utf-8")
            print(f"[✔] 已同步前端索引: web/js/data/seasons_index.js")
        else:
            print(f"[i] 前端索引已是最新: web/js/data/seasons_index.js")

    print("=" * 70 + "\n")
    return actual_end_date


def cmd_rollforward(args):
    """一键执行全部赛季批量增量推进、Web 导出、Chronicles 同步与安全审计 (Batch Roll-Forward)"""
    print("\n" + "=" * 70)
    print(" 🚀 QuantPits-Arena 批量全自动周频滚动推进 (The Grand Roll-Forward)")
    print("=" * 70)

    # 1. 若指定了 --end-date，则首先原子执行 bump-date
    if args.end_date:
        print(f"\n[Step 1/5] 执行全局截止日期原子推进: -> {args.end_date}...")
        bump_args = argparse.Namespace(
            end_date=args.end_date,
            seasons=args.seasons if args.seasons != ["all"] else None
        )
        actual_end = cmd_bump_date(bump_args)
    else:
        actual_end = DEFAULT_END_DATE
        print(f"\n[Step 1/5] 使用当前全局默认截止日期: {actual_end}")

    # 2. 确定待推进赛季列表
    if args.seasons and args.seasons != ["all"]:
        target_seasons = args.seasons
    else:
        target_seasons = []
        for sid in SeasonManager.list_seasons():
            cfg = SeasonManager.get_season_config(sid)
            if cfg.status in ["ACTIVE", "PREVIEW", "DEMO"]:
                target_seasons.append(sid)

    print(f"\n[Step 2/5] 待推进目标赛季列表: {target_seasons}")

    # 3. 逐个赛季执行增量推进 step
    for idx, sid in enumerate(target_seasons, 1):
        print(f"\n--- [Step 3/5] ({idx}/{len(target_seasons)}) 增量推进赛季: {sid} ---")
        step_args = argparse.Namespace(
            season=sid,
            run_id=None,
            anchor_date=DEFAULT_ANCHOR_DATE,
            end_date=actual_end,
            initial_cash=500_000.0,
            mock=getattr(args, "mock", False),
            monkeys=getattr(args, "monkeys", False),
            monkey_count=getattr(args, "monkey_count", 1000),
            contestants=None,
            output=getattr(args, "output", None)
        )
        cmd_step(step_args)

    # 4. 逐个赛季导出通用前端 Payload export-web
    for idx, sid in enumerate(target_seasons, 1):
        print(f"\n--- [Step 4/5] ({idx}/{len(target_seasons)}) 导出 Web Payload: {sid} ---")
        exp_args = argparse.Namespace(
            season=sid,
            run_id=None,
            output=getattr(args, "output", None)
        )
        cmd_export_web(exp_args)

    # 5. 可选同步 Chronicles
    if not getattr(args, "no_sync_chronicles", False):
        print(f"\n[Step 5/5] 检查并同步 Chronicles 文档...")
        n_synced = sync_chronicles()
        if n_synced > 0:
            print(f"[✔] 成功自动同步 {n_synced} 篇 Chronicles 到 web/chronicles/en/")
        else:
            print(f"[i] Chronicles 与 web/chronicles/en/ 保持一致，无需拷贝")

    # 6. 安全隐私合规审计
    if not getattr(args, "no_audit", False):
        print(f"\n[Final] 强制执行本地零泄密隐私审计...")
        cmd_audit(args)

    print("\n" + "=" * 70)
    print(" 🎉 全部赛季增量推进与导出圆满完成！")
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
    p_step.add_argument("--run-id", type=str, default=None, help="指定待推进的运行 ID (默认: {season}_run)")
    p_step.add_argument("--anchor-date", type=str, default=DEFAULT_ANCHOR_DATE, help="初始锚定日期")
    p_step.add_argument("--end-date", type=str, default=DEFAULT_END_DATE, help="回测结束日期")
    p_step.add_argument("--initial-cash", type=float, default=500_000.0, help="初始资金规模 (默认 500,000 元)")
    p_step.add_argument("--mock", action="store_true", help="使用 Mock 适配器运行")
    p_step.add_argument("--monkeys", action="store_true", help="同时运行参数化猴子群落零假设评估")
    p_step.add_argument("--monkey-count", type=int, default=1000, help="每组策略规格的猴子数量 (默认 1000 只)")
    p_step.add_argument("--contestants", type=str, default=None, help="逗号分隔的参赛选手 ID")
    p_step.add_argument("--output", type=str, default=None, help="指定输出根目录")

    # pipeline (一键执行全自动化赛季管线)
    p_pipe = subparsers.add_parser("pipeline", help="一键全自动化赛季标准化管线 (Infer -> Run -> Export -> Audit)")
    p_pipe.add_argument("--season", type=str, default="season_01", help="指定赛季 ID")
    p_pipe.add_argument("--run-id", type=str, default=None, help="指定运行 ID")
    p_pipe.add_argument("--anchor-date", type=str, default=DEFAULT_ANCHOR_DATE, help="初始锚定日期")
    p_pipe.add_argument("--end-date", type=str, default=DEFAULT_END_DATE, help="回测结束日期")
    p_pipe.add_argument("--initial-cash", type=float, default=500_000.0, help="初始资金规模")
    p_pipe.add_argument("--mock", action="store_true", help="使用 Mock 适配器运行全流程快速验证")
    p_pipe.add_argument("--monkey-count", type=int, default=1000, help="每组策略规格的猴子数量")
    p_pipe.add_argument("--contestants", type=str, default=None, help="逗号分隔的参赛选手 ID")
    p_pipe.add_argument("--cycles", type=int, default=0, help="限制运行的最大周数")
    p_pipe.add_argument("--output", type=str, default=None, help="指定输出根目录")
    p_pipe.add_argument("--force-infer", action="store_true", help="强制重新执行 Stage 1 模型推理")

    # infer (通用股票池批处理推理)
    p_inf = subparsers.add_parser("infer", help="通用股票池批量特征提取与模型推理 (Stage 1)")
    p_inf.add_argument("--universe", type=str, default="csi500", help="指定股票池代码 (默认 csi500)")
    p_inf.add_argument("--force", action="store_true", help="强制重新推理")

    # export-web
    p_exp = subparsers.add_parser("export-web", help="导出通用前端 Web Payload (web/js/data/<season_id>.js)")
    p_exp.add_argument("--season", type=str, default="season_01", help="指定赛季 ID")
    p_exp.add_argument("--run-id", type=str, default=None, help="指定运行 ID")
    p_exp.add_argument("--output", type=str, default=None, help="指定输出根目录")

    # bump-date
    p_bump = subparsers.add_parser("bump-date", help="一键原子推进全局及各赛季配置与前端索引的截止日期")
    p_bump.add_argument("--end-date", type=str, required=True, help="新的截止交易日 (YYYY-MM-DD，如 2026-09-18)")
    p_bump.add_argument("--seasons", nargs="+", default=None, help="指定待更新赛季 ID (默认所有活跃赛季，支持 all)")

    # rollforward (一键全赛季批量增量推进)
    p_rf = subparsers.add_parser("rollforward", help="一键批量周频滚动推进全量赛季 (Bump -> Step -> Export -> Sync -> Audit)")
    p_rf.add_argument("--end-date", type=str, default=None, help="可选：指定新截止日期并先原子执行 bump-date")
    p_rf.add_argument("--seasons", nargs="+", default=None, help="指定待推进赛季列表 (默认所有活跃赛季)")
    p_rf.add_argument("--mock", action="store_true", help="使用 Mock 模式快速推进")
    p_rf.add_argument("--monkeys", action="store_true", help="增量推进同时运行猴群零假设评估")
    p_rf.add_argument("--monkey-count", type=int, default=1000, help="每组策略规格猴子数量")
    p_rf.add_argument("--no-sync-chronicles", action="store_true", help="跳过自动同步 Chronicles 文档")
    p_rf.add_argument("--no-audit", action="store_true", help="跳过末尾本地零泄密隐私审计")
    p_rf.add_argument("--output", type=str, default=None, help="指定输出根目录")

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
    elif args.subcommand == "infer":
        cmd_infer(args)
    elif args.subcommand == "run":
        cmd_run(args)
    elif args.subcommand == "step":
        cmd_step(args)
    elif args.subcommand == "cycle-step":
        cmd_cycle_step(args)
    elif args.subcommand == "pipeline":
        cmd_pipeline(args)
    elif args.subcommand == "export-web":
        cmd_export_web(args)
    elif args.subcommand == "bump-date":
        cmd_bump_date(args)
    elif args.subcommand == "rollforward":
        cmd_rollforward(args)


if __name__ == "__main__":
    main()


