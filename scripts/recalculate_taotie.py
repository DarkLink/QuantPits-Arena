#!/usr/bin/env python3
"""
scripts/recalculate_taotie.py
==============================
根据 season_config.yaml 中配置的 Taotie 资金规模 (例如 CSI 500 为 1M, CSI 800 为 1.6M, CSI 1000 为 2M)，
重新计算各宽基赛季的物理饕餮 (Taotie Benchmark) 绩效，并无损回写至各赛季的数据产物与 Web 前端 Payload。
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import pandas as pd
from arena.seasons.manager import SeasonManager
from arena.calendar import TradingCalendar
from arena.data.market import MarketDataProvider
from arena.benchmarks.taotie import TaotieBenchmark
from arena.reports.sanitizer import DualTierExporter

def recalculate_season_taotie(season_id: str):
    print(f"\n========================================================")
    print(f"[*] 重新评估赛季物理饕餮: {season_id}")
    print(f"========================================================")
    
    cfg = SeasonManager.get_season_config(season_id)
    taotie_cash = cfg.get_benchmark_initial_cash("taotie", default=500_000.0)
    taotie_name = cfg.get_benchmark_display_name("taotie", default="Taotie")
    print(f"[+] 赛季: {cfg.title}")
    print(f"[+] 物理饕餮配置本金: CNY {taotie_cash:,.2f} ({taotie_cash/1e6:.1f}M)")
    
    # 1. 加载预测文件获取每周Universe
    pred_path = REPO_ROOT / "artifacts" / "predictions" / f"{season_id}_contestants_oos.pkl"
    if not pred_path.exists():
        raw_univ = season_id.replace("season_", "").lower()
        pred_path = REPO_ROOT / "artifacts" / "predictions" / f"{raw_univ}_contestants_oos.pkl"
    
    raw_data = pd.read_pickle(pred_path)
    first_cid = next(iter(raw_data.keys()))
    date_dict = raw_data[first_cid]
    
    all_instruments = set()
    for s in date_dict.values():
        if isinstance(s, pd.Series):
            all_instruments.update(s.index)
    all_instruments = sorted(list(all_instruments))
    
    cal = TradingCalendar()
    cycles = cal.build_weekly_cycles(cfg.anchor_date, cfg.end_date)
    
    # 2. 准备行情数据提供者
    mp = MarketDataProvider(use_real_qlib=True)
    mp.load_qlib_data(all_instruments, cycles[0].decision_date, cycles[-1].settle_date)
    
    price_lookup = mp.get_real_price
    tradability_filter = mp.is_tradable
        
    # 3. 运行 Taotie 回测
    taotie = TaotieBenchmark(
        initial_cash=taotie_cash,
        deal_price_mode=cfg.deal_price_mode,
        display_name=taotie_name
    )
    
    for c_idx, cycle in enumerate(cycles):
        d_date = cycle.decision_date
        if d_date in date_dict:
            universe = list(date_dict[d_date].index)
        else:
            available_dates = sorted(date_dict.keys())
            d_prev = [dt for dt in available_dates if dt <= d_date]
            closest = d_prev[-1] if d_prev else available_dates[0]
            universe = list(date_dict[closest].index)
            
        mock_score = pd.Series(1.0, index=universe)
        is_first = (c_idx == 0)
        order = taotie.engine.generate_order(
            score=mock_score,
            topk=0,
            n_drop=0,
            trade_date=cycle.trade_date,
            is_first_entry=is_first,
            tradability_filter=tradability_filter,
            price_lookup=price_lookup,
            passive_pool=True
        )
        taotie.engine.execute_weekly_cycle(cycle, order, price_lookup)
        
    path = taotie.engine.to_portfolio_path()
    diag = path.diagnostics
    
    print(f"[+] 回测完成:")
    print(f"    - 总收益率 (Total Return): {path.total_return*100:.2f}% (最终净值: {path.nav_series.iloc[-1]:.4f})")
    print(f"    - 最大回撤 (Max Drawdown): {path.max_drawdown*100:.2f}%")
    print(f"    - 平均持仓股票数: {diag.get('actual_holdings_mean', 0):.1f} / {len(universe)} 只")
    print(f"    - 买不起拒单率 (Skip Ratio): {diag.get('unaffordable_buy_ratio', 0)*100:.2f}%")
    print(f"    - 平均现金比例 (Mean Cash Ratio): {diag.get('mean_cash_ratio', 0)*100:.2f}%")
    print(f"    - 期末现金比例 (Final Cash Ratio): {diag.get('final_cash_ratio', 0)*100:.2f}%")
    
    # 4. 更新 runs/<run_id>/public/ 下的 CSV 产物
    run_id = f"{season_id}_run"
    pub_dir = REPO_ROOT / "runs" / run_id / "public"
    if pub_dir.exists():
        # 4.1 更新 daily_nav_curves.csv
        nav_file = pub_dir / "daily_nav_curves.csv"
        if nav_file.exists():
            df_nav = pd.read_csv(nav_file, index_col="datetime")
            df_nav["BENCHMARK_taotie"] = path.nav_series.values
            df_nav.to_csv(nav_file)
            print(f"[+] 已更新 {nav_file.name}")
            
        # 4.2 更新 summary_metrics.csv
        summary_file = pub_dir / "summary_metrics.csv"
        if summary_file.exists():
            df_summary = pd.read_csv(summary_file)
            mask = (df_summary["contestant_id"] == "BENCHMARK") & (df_summary["animal_id"] == "taotie")
            if mask.any():
                df_summary.loc[mask, "total_return_pct"] = f"{path.total_return * 100:.2f}%"
                df_summary.loc[mask, "max_drawdown_pct"] = f"{path.max_drawdown * 100:.2f}%"
                df_summary.loc[mask, "final_nav"] = f"{path.nav_series.iloc[-1]:.4f}"
                df_summary.loc[mask, "target_holdings_mean"] = diag.get("target_holdings_mean", 0)
                df_summary.loc[mask, "actual_holdings_mean"] = diag.get("actual_holdings_mean", 0)
                df_summary.loc[mask, "unaffordable_buy_count"] = diag.get("unaffordable_buy_count", 0)
                df_summary.loc[mask, "unaffordable_buy_ratio"] = f"{diag.get('unaffordable_buy_ratio', 0.0) * 100:.2f}%"
                df_summary.loc[mask, "mean_cash_ratio"] = f"{diag.get('mean_cash_ratio', 0.0) * 100:.2f}%"
                df_summary.loc[mask, "max_cash_ratio"] = f"{diag.get('max_cash_ratio', 0.0) * 100:.2f}%"
                df_summary.loc[mask, "final_cash_ratio"] = f"{diag.get('final_cash_ratio', 0.0) * 100:.2f}%"
                df_summary.to_csv(summary_file, index=False)
                print(f"[+] 已更新 {summary_file.name}")

        # 4.3 更新 capital_constraint_diagnostics.csv
        diag_file = pub_dir / "capital_constraint_diagnostics.csv"
        if diag_file.exists():
            df_diag = pd.read_csv(diag_file)
            mask = (df_diag["contestant_id"] == "BENCHMARK") & (df_diag["animal_id"] == "taotie")
            if mask.any():
                for col in ["target_holdings_mean", "actual_holdings_mean", "actual_holdings_min", "actual_holdings_max",
                            "buy_attempt_count", "unaffordable_buy_count", "unaffordable_event_days"]:
                    df_diag.loc[mask, col] = diag.get(col, 0)
                df_diag.loc[mask, "unaffordable_buy_ratio"] = f"{diag.get('unaffordable_buy_ratio', 0.0) * 100:.2f}%"
                df_diag.loc[mask, "unaffordable_event_day_ratio"] = f"{diag.get('unaffordable_event_day_ratio', 0.0) * 100:.2f}%"
                df_diag.loc[mask, "mean_cash_ratio"] = f"{diag.get('mean_cash_ratio', 0.0) * 100:.2f}%"
                df_diag.loc[mask, "max_cash_ratio"] = f"{diag.get('max_cash_ratio', 0.0) * 100:.2f}%"
                df_diag.loc[mask, "final_cash_ratio"] = f"{diag.get('final_cash_ratio', 0.0) * 100:.2f}%"
                df_diag.loc[mask, "mean_invested_ratio"] = f"{diag.get('mean_invested_ratio', 0.0) * 100:.2f}%"
                df_diag.to_csv(diag_file, index=False)
                print(f"[+] 已更新 {diag_file.name}")
                
        # 5. 重新生成 web/js/data/<season_id>.js
        exporter = DualTierExporter(run_id=run_id, base_dir=REPO_ROOT / "runs")
        web_target = REPO_ROOT / "web" / "js" / "data" / f"{season_id}.js"
        exporter.export_web_payload(season_cfg=cfg, web_output_path=web_target)
        print(f"[+] 已成功重写 Web 数据载荷: {web_target.name}")

if __name__ == "__main__":
    seasons = sys.argv[1:] if len(sys.argv) > 1 else ["season_csi500", "season_csi800", "season_csi1000"]
    for s in seasons:
        recalculate_season_taotie(s)
    print("\n[SUCCESS] 全部宽基物理饕餮重算完成！")
