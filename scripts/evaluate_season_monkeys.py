#!/usr/bin/env python3
"""
scripts/evaluate_season_monkeys.py
===================================
计算赛季参数化猴子群落（11 组策略规格 × 1,000 只随机猴子 = 11,000 只猴子）零假设基准，
生成 monkey_null_distributions.csv 与 contestant_monkey_significance.csv，
并将真实的经验分位数 (Percentile Rank)、猴子超额 (Excess over Monkey) 及经验 p 值 (Empirical p-value)
无损写回赛季 Web 前端数据载荷 (season_01.js & arena_data.js)。
"""

import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import pandas as pd
from arena.config import RUNS_DIR
from arena.seasons.manager import SeasonManager
from arena.runner.weekly_cycle import WeeklyCycleRunner
from arena.contestants import ContestantRegistry
from arena.reports.sanitizer import DualTierExporter

def evaluate_monkeys(season_id: str = "season_01", colony_size: int = 1000):
    print("\n" + "=" * 70)
    print(f" 🐒 启动参数化猴子群落评估: {season_id} (规格数=11, 每组={colony_size} 只, 总计={11 * colony_size:,} 只)")
    print("=" * 70)

    cfg = SeasonManager.get_season_config(season_id)
    registry = ContestantRegistry()

    run_id = f"{season_id}_run"
    run_dir = RUNS_DIR / run_id
    cp_dir = run_dir / "checkpoints"
    latest_path = cp_dir / "latest_state.pkl"

    if not latest_path.exists():
        print(f"[ERROR] 未找到快照文件: {latest_path}")
        sys.exit(1)

    runner = WeeklyCycleRunner(
        anchor_date=cfg.anchor_date,
        end_date=cfg.end_date,
        initial_cash=cfg.initial_cash,
        season_id=season_id,
        run_dir=run_dir
    )
    runner.load_checkpoint_from_disk(latest_path)
    print(f"[+] 成功读取快照: {latest_path.name} (已完成周期 Cycle {runner.last_completed_cycle_idx}, 共 {len(runner.cycles)} 周)")

    price_lookup_fn, tradability_filter_fn = runner._setup_market_provider(
        registry.list_contestants(), None, None
    )

    t0 = time.time()
    print(f"[+] 正在模拟 11 组策略规格 × {colony_size} 只随机猴子完整生命周期...")
    monkey_results = runner.run_parametric_monkeys(
        colony_size=colony_size,
        price_lookup_fn=price_lookup_fn,
        tradability_filter_fn=tradability_filter_fn
    )
    elapsed = time.time() - t0
    print(f"[✔] 猴群回测模拟完成，耗时: {elapsed:.2f} 秒")

    # 构建选手路径字典
    results = {
        key: engine.to_portfolio_path()
        for key, engine in runner.engines.items()
    }

    # 载入或更新物理饕餮与理论饕餮
    results[("BENCHMARK", "taotie")] = runner.taotie_benchmark.engine.to_portfolio_path()
    results[("BENCHMARK", "ghost_taotie")] = runner.ghost_taotie_benchmark.engine.to_portfolio_path()

    # 导出猴群零假设报告与显著性检验表格
    exporter = DualTierExporter(run_id=run_id, base_dir=RUNS_DIR)
    m_artifacts = exporter.export_monkey_reports(monkey_results, results, registry)
    print(f"[+] 已写出零假设分布: {m_artifacts['monkey_distributions_csv']}")
    print(f"[+] 已写出显著性检验: {m_artifacts['contestant_significance_csv']}")
    print(f"[+] 已写出诊断 Markdown: {m_artifacts['monkey_report_md']}")

    # 重新导出 Web 数据载荷 (season_01.js + arena_data.js)
    web_target = REPO_ROOT / "web" / "js" / "data" / f"{season_id}.js"
    exporter.export_web_payload(season_cfg=cfg, web_output_path=web_target)
    print(f"[+] Web 数据载荷已成功同步重写: {web_target.name}")

    # 检查检验结果样本
    df_sig = pd.read_csv(m_artifacts['contestant_significance_csv'])
    print("\n[+] 显著性检验结果样本 (前 10 行):")
    print(df_sig[["contestant_id", "animal_id", "actual_return_pct", "monkey_median_pct", "percentile_rank", "empirical_p_value", "significant_95pct"]].head(10).to_string(index=False))

    pct_ranks = df_sig["percentile_rank"].str.rstrip("%").astype(float)
    print(f"\n[+] 分位数统计:")
    print(f"    - 最小值: {pct_ranks.min():.1f}%")
    print(f"    - 中位数: {pct_ranks.median():.1f}%")
    print(f"    - 最大值: {pct_ranks.max():.1f}%")
    print(f"    - 显著选手数量 (p < 0.05): {(df_sig['significant_95pct'].str.startswith('YES')).sum()} / {len(df_sig)}")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    sid = sys.argv[1] if len(sys.argv) > 1 else "season_01"
    evaluate_monkeys(sid)
