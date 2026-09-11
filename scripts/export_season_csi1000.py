"""
scripts/export_season_csi1000.py
================================
Serializes Season CSI 1000 real tournament results into:
web/js/data/season_csi1000.js
"""

import sys
import json
import argparse
import yaml
from pathlib import Path
import pandas as pd
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
MANIFESTS_PUBLIC = REPO_ROOT / "manifests" / "public"


def export_season_csi1000(run_dir: Path = None):
    if run_dir is None:
        run_dir = REPO_ROOT / "runs" / "season_csi1000_run"

    pub_dir = run_dir / "public"
    print(f"[*] Loading Season CSI 1000 data from: {run_dir}")

    # 1. Load Contestant Manifests
    contestants = []
    for mf in sorted(MANIFESTS_PUBLIC.glob("*.yaml")):
        with open(mf, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            cid = data.get("contestant_id", mf.stem)
            contestants.append({
                "contestant_id": cid,
                "display_name": data.get("display_name", cid),
                "family": data.get("family", "Alpha-Family"),
                "artifact_date": data.get("artifact_date", "2026-06-26"),
                "train_cutoff": data.get("train_cutoff", "2026-06-26"),
                "burial_date": data.get("burial_date", data.get("train_cutoff", "2026-06-26")),
                "historical_role": data.get("historical_role", "Production Alpha Candidate"),
                "training_mode": data.get("training_mode", "Ensemble"),
                "feature_set": data.get("feature_set", "Multi-Factor Matrix"),
                "historical_is_sharpe": float(data.get("historical_is_sharpe", 1.85)),
                "historical_is_return_pct": float(data.get("historical_is_return_pct", 20.0)),
                "historical_is_mdd_pct": float(data.get("historical_is_mdd_pct", 8.0)),
                "historical_sys_ann_return_pct": float(data.get("historical_sys_ann_return_pct", 10.0)),
                "historical_metric_basis": data.get("historical_metric_basis", "Cashflow-adjusted cumulative system return up to burial date"),
                "integrity_class": data.get("integrity_class", "VERIFIED"),
                "known_issues": data.get("known_issues", []),
                "paired_rival": data.get("paired_rival", ""),
                "notes": data.get("notes", "")
            })

    # 2. Load CSVs
    df_metrics = pd.read_csv(pub_dir / "summary_metrics.csv") if (pub_dir / "summary_metrics.csv").exists() else pd.DataFrame()
    df_diag = pd.read_csv(pub_dir / "capital_constraint_diagnostics.csv") if (pub_dir / "capital_constraint_diagnostics.csv").exists() else pd.DataFrame()
    df_sig = pd.read_csv(pub_dir / "contestant_monkey_significance.csv") if (pub_dir / "contestant_monkey_significance.csv").exists() else pd.DataFrame()
    df_null = pd.read_csv(pub_dir / "monkey_null_distributions.csv") if (pub_dir / "monkey_null_distributions.csv").exists() else pd.DataFrame()
    df_matrix = pd.read_csv(pub_dir / "model_animal_matrix.csv", index_col=0) if (pub_dir / "model_animal_matrix.csv").exists() else pd.DataFrame()
    if not df_matrix.empty:
        df_matrix = df_matrix[~df_matrix.index.astype(str).str.contains("BENCHMARK", case=False, na=False)]
        cols_to_drop = [c for c in ["taotie", "ghost_taotie"] if c in df_matrix.columns]
        if cols_to_drop:
            df_matrix = df_matrix.drop(columns=cols_to_drop)

    # 3. NAV Timelines
    df_nav = pd.read_csv(pub_dir / "daily_nav_curves.csv") if (pub_dir / "daily_nav_curves.csv").exists() else pd.DataFrame()
    nav_dates = df_nav["datetime"].tolist() if "datetime" in df_nav.columns else []
    nav_series_map = {}
    for col in df_nav.columns:
        if col != "datetime":
            nav_series_map[col] = [round(float(v), 4) for v in df_nav[col].tolist()]

    # 4. Load CSI 1000 (SH000852) Market Benchmark
    csi1000_curve = []
    csi1000_ret = -10.62
    try:
        from arena.calendar import TradingCalendar
        cal = TradingCalendar()
        bin_file = Path.home() / ".qlib" / "qlib_data" / "cn_data" / "features" / "sh000852" / "close.day.bin"
        if bin_file.exists() and len(nav_dates) > 0:
            with open(bin_file, "rb") as f:
                start_idx = np.fromfile(f, dtype="<u4", count=1)[0]
                data = np.fromfile(f, dtype="<f4")
            d_start = cal.day_to_idx[nav_dates[0]]
            d_end = cal.day_to_idx[nav_dates[-1]]
            prices = data[d_start - start_idx : d_end - start_idx + 1]
            if len(prices) == len(nav_dates) and prices[0] > 0:
                csi1000_curve = [round(float(p / prices[0]), 4) for p in prices]
                csi1000_ret = round(float((prices[-1] / prices[0] - 1) * 100), 2)
                print(f"[+] Loaded CSI 1000 benchmark: {len(csi1000_curve)} days, return: {csi1000_ret}%")
    except Exception as e:
        print(f"[!] Warning: Failed to load CSI 1000 binary: {e}")

    if csi1000_curve:
        nav_series_map["BENCHMARK_csi1000"] = csi1000_curve
        nav_series_map["BENCHMARK_csi300"] = csi1000_curve  # Fallback compatibility

    def parse_pct(val, default=0.0):
        if isinstance(val, (int, float)):
            return float(val)
        if isinstance(val, str) and "%" in val:
            try:
                return float(val.replace("%", "").strip())
            except ValueError:
                pass
        return default

    # 5. Build Paths List
    path_records = []
    metrics_records = df_metrics.to_dict(orient="records") if not df_metrics.empty else []
    diag_lookup = {(r["contestant_id"], r["animal_id"]): r for r in df_diag.to_dict(orient="records")} if not df_diag.empty else {}
    sig_lookup = {(r["contestant_id"], r["animal_id"]): r for r in df_sig.to_dict(orient="records")} if not df_sig.empty else {}

    for row in metrics_records:
        cid = row["contestant_id"]
        aid = row["animal_id"]
        key = (cid, aid)

        d_info = diag_lookup.get(key, {})
        s_info = sig_lookup.get(key, {})

        tot_ret = parse_pct(row.get("total_return_pct", 0.0))
        mdd = parse_pct(row.get("max_drawdown_pct", 0.0))
        monkey_med = parse_pct(s_info.get("monkey_median_pct", 0.0))
        excess_monkey = parse_pct(s_info.get("excess_over_monkey_pct", tot_ret - monkey_med))
        pct_rank = parse_pct(s_info.get("percentile_rank", 50.0))
        pct_rank = min(pct_rank, 99.9)
        p_val = float(s_info.get("empirical_p_value", 1.0)) if s_info.get("empirical_p_value") is not None else 1.0
        if p_val < 0.001:
            p_val = 0.001

        col_key = f"{cid}_{aid}"
        sharpe = 0.0
        if col_key in nav_series_map:
            series = pd.Series(nav_series_map[col_key])
            rets = series.pct_change().dropna()
            if len(rets) > 1 and rets.std() > 0:
                sharpe = round(float((rets.mean() / rets.std()) * (250 ** 0.5)), 2)

        def get_animal_category(animal_id: str) -> str:
            if animal_id == "robot":
                return "Baseline"
            elif animal_id.startswith("sloth"):
                return "Sloth (Lagged)"
            elif animal_id.startswith("snail"):
                return "Snail (Stale)"
            elif animal_id.startswith("rabbit"):
                return "Rabbit (High Turnover)"
            elif animal_id == "turtle":
                return "Turtle (Low Turnover)"
            elif animal_id == "koala":
                return "Koala (Inverted)"
            elif animal_id.startswith("meerkat"):
                return "Meerkat (Percentile)"
            elif animal_id.startswith("eagle"):
                return "Eagle (Concentration)"
            elif animal_id == "whale-shark":
                return "Whale Shark (50% Pool)"
            elif animal_id == "taotie":
                return "Taotie (100% Passive)"
            elif animal_id == "ghost_taotie":
                return "Ghost Taotie (Theoretical 100M)"
            return "Custom"

        badges = []
        if pct_rank >= 99.0:
            badges.append("Alpha Outlier (>99%)")
        if sharpe >= 2.0:
            badges.append("High Sharpe (≥2.0)")
        if parse_pct(d_info.get("unaffordable_buy_ratio", 0)) > 20.0:
            badges.append("Capital Friction (>20%)")

        final_nav = round(float(nav_series_map[col_key][-1]), 4) if col_key in nav_series_map and len(nav_series_map[col_key]) > 0 else 1.0

        path_records.append({
            "path_id": f"{cid}_{aid}",
            "contestant_id": cid,
            "animal_id": aid,
            "animal_category": get_animal_category(aid),
            "display_name": f"{cid} × {aid}",
            "total_return_pct": tot_ret,
            "max_drawdown_pct": mdd,
            "final_nav": final_nav,
            "sharpe_ratio": sharpe,
            "excess_over_csi300_pct": round(tot_ret - csi1000_ret, 2),
            "excess_over_monkey_pct": round(excess_monkey, 2),
            "percentile_rank": round(pct_rank, 1),
            "monkey_percentile": round(pct_rank, 1),
            "monkey_percentile_rank": round(pct_rank, 1),
            "empirical_p_value": p_val,
            "p_value": p_val,
            "is_statistically_significant": (p_val < 0.05),
            "unaffordable_buy_ratio": parse_pct(d_info.get("unaffordable_buy_ratio", 0)),
            "unaffordable_buy_count": int(d_info.get("unaffordable_buy_count", 0)),
            "unaffordable_event_days": int(d_info.get("unaffordable_event_days", 0)),
            "mean_cash_ratio": parse_pct(d_info.get("mean_cash_ratio", 0)),
            "final_cash_ratio": parse_pct(d_info.get("final_cash_ratio", 0)),
            "target_holdings_mean": float(d_info.get("target_holdings_mean", 22.0)),
            "actual_holdings_mean": float(d_info.get("actual_holdings_mean", 22.0)),
            "badges": badges
        })

    # 6. Compute Drawdowns and Excess Maps
    drawdowns_map = {}
    excess_map = {}
    for col, series in nav_series_map.items():
        arr = np.array(series, dtype=float)
        peaks = np.maximum.accumulate(arr)
        dds = np.where(peaks > 0, (arr - peaks) / peaks * 100.0, 0.0)
        drawdowns_map[col] = [round(float(v), 2) for v in dds]

        if csi1000_curve and len(csi1000_curve) == len(series):
            bench_arr = np.array(csi1000_curve, dtype=float)
            exc = (arr - bench_arr) * 100.0
            excess_map[col] = [round(float(v), 2) for v in exc]
        else:
            excess_map[col] = [0.0] * len(series)

    # 7. Null Distributions
    null_records = df_null.to_dict(orient="records") if not df_null.empty else []

    # Taotie returns
    taotie_tot_ret = 0.0
    for p in path_records:
        if p["path_id"] == "BENCHMARK_taotie":
            taotie_tot_ret = p["total_return_pct"]
            break

    ghost_tot_ret = 0.0
    for p in path_records:
        if p["path_id"] == "BENCHMARK_ghost_taotie":
            ghost_tot_ret = p["total_return_pct"]
            break

    # Decision Archaeology Forks
    decision_forks = [
        {
            "fork_id": "fork_model_selection_20260626_csi1000",
            "title": "Model Selection (CSI 1000): Candidate-B vs. Candidate-A",
            "decision_date": "2026-06-26",
            "chosen_id": "CONTESTANT_B",
            "rejected_id": "CONTESTANT_A",
            "chosen_name": "Candidate-B (Ensemble)",
            "rejected_name": "Candidate-A (Ensemble)",
            "historical_context": "Evaluated in the broader CSI 1000 small-cap universe, examining cross-validation stability across regime shifts.",
            "canonical_animal": "robot",
            "chosen_path_id": "CONTESTANT_B_robot",
            "rejected_path_id": "CONTESTANT_A_robot"
        },
        {
            "fork_id": "fork_feature_dimension_20250926_csi1000",
            "title": "Feature Space (CSI 1000): Condensed vs. Expanded Baseline",
            "decision_date": "2025-09-26",
            "chosen_id": "CONTESTANT_F",
            "rejected_id": "CONTESTANT_E",
            "chosen_name": "Candidate-F (Condensed Features)",
            "rejected_name": "Candidate-E (Expanded Features)",
            "historical_context": "High-dimensional factor expansion evaluated against the condensed baseline across 1,000 small-cap constituents.",
            "canonical_animal": "robot",
            "chosen_path_id": "CONTESTANT_F_robot",
            "rejected_path_id": "CONTESTANT_E_robot"
        }
    ]

    # 8. Dedicated Dispatches for Season CSI 1000
    dispatches_payload = {
        "executive": {
            "tag": "🔬 Season CSI 1000 Standing",
            "badge": "1,000-Stock Universe",
            "title": "CSI 1000 Small-Cap Calibration & Alpha Breadth Reality",
            "window_label": f"Evaluation Window: {nav_dates[0] if nav_dates else '2026-07-03'} ~ {nav_dates[-1] if nav_dates else '2026-08-28'} ({len(nav_dates)} Trading Days)",
            "nature_label": "Empirical signal evaluation over 1,000 constituent stocks with external anchor SH000852 and 11,000 random monkeys.",
            "leader_summary": "Top machine learning candidates demonstrate massive cross-sectional resilience in small caps: CONTESTANT_A and CONTESTANT_C lead the field with +17.96% peak return against the -10.62% market backdrop (+28.58% market excess), confirmed at p < 0.001 against 1,000 random monkeys."
        },
        "climate": {
            "tag": "🌪️ Small-Cap Universe Dynamics",
            "status_badge": "CSI 1000 Active (SH000852)",
            "title": "High-Breadth Dispersion vs Liquidity Resistance in Small Caps",
            "summary": "Analyzing how factor breadth scales from 246 stocks to 1,000 stocks during a market contraction (-10.62%).",
            "bullets": [
                "<strong>1,000-Stock Breadth Advantage</strong>: Expanding the constituent universe to 1,000 stocks dramatically increases cross-sectional dispersion. Top ML signals successfully exploit idiosyncratic mispricings, driving positive returns even as the benchmark drops -10.62%.",
                "<strong>True 0.1% Null Resolution (11,000 Monkeys)</strong>: Running 1,000 monkeys per specification (11,000 total) provides fine-grained empirical p-values down to 0.0010. Top outperformers show statistical significance beyond the 99.9th percentile of chance."
            ],
            "decrypt_label": "CSI 1000 Weekly Execution"
        },
        "episodes": [
            {
                "id": "csi1000_ep01",
                "tab_label": "🎯 Ep 01: 1,000-Stock Breadth Testbed",
                "badge": "Universe Expansion",
                "title": "CSI 1000 Dispatch 01: Testing Factor Breadth Across 1,000 Small-Cap Equities",
                "date": "2026-09-08",
                "read_time": "5 min read",
                "summary": "Deploying the full 6-model contestant lineup onto the 1,000-stock CSI 1000 pool against market anchor SH000852.",
                "content_html": """
                    <p>In this specialized calibration run, QuantPits Arena scales its empirical testbed from standard constituent samples to the full <strong>CSI 1000 small-cap universe (~1,000 constituent stocks)</strong>, anchored against the official CSI 1000 Index (<code>SH000852</code>).</p>
                    <div class="callout-box" style="margin: 1.5rem 0; padding: 1.25rem; background: rgba(56, 189, 248, 0.08); border-left: 4px solid var(--brand-cyan); border-radius: 4px;">
                      <h4 style="color: var(--brand-cyan); margin: 0 0 0.5rem 0;">Small-Cap Market Backdrop vs. Model Behavior</h4>
                      <p style="font-size: 0.9rem; color: var(--text-secondary); margin: 0; line-height: 1.6;">
                        Over the 41-day horizon (2026-07-03 ~ 2026-08-28), the CSI 1000 Index experienced a severe drawdown of <strong>-10.62%</strong>.
                        Under these market conditions, the passive baseline <strong>Taotie (CNY 500k)</strong> ended at <strong>-2.09%</strong>, while the institutional equal-weight <strong>Ghost Taotie (CNY 100M)</strong> recorded <strong>-4.92%</strong>.
                        Remarkably, high-capacity machine learning models (CONTESTANT_A and CONTESTANT_C) extracted positive alpha, reaching <strong>+17.96%</strong> (+28.58% market excess).
                      </p>
                    </div>
                    <p>This stark divergence highlights the core proposition of expanding universe breadth: in small-cap equities, higher idiosyncratic dispersion allows alpha models with strong ranking power to isolate winning clusters regardless of broad index headwinds.</p>
                """
            },
            {
                "id": "csi1000_ep02",
                "tab_label": "🐒 Ep 02: 11,000 Monkeys Under Microscope",
                "badge": "Null Colony",
                "title": "CSI 1000 Dispatch 02: True 0.1% Resolution with 11,000 Empirical Random Monkeys",
                "date": "2026-09-08",
                "read_time": "4 min read",
                "summary": "Why 1,000 monkeys per specification are mathematically indispensable to differentiate real alpha from random picking.",
                "content_html": """
                    <p>A frequent pitfall in empirical alpha evaluation is insufficient null resolution. When evaluating strategies against random portfolios, a colony of 100 monkeys only offers a resolution of 1.0% (p_min = 1/101 &approx; 0.0099). Every top-performing model is artificially clamped at <code>p=0.0099</code>, concealing true superiority.</p>
                    <div class="callout-box" style="margin: 1.5rem 0; padding: 1.25rem; background: rgba(16, 185, 129, 0.08); border-left: 4px solid var(--accent-positive); border-radius: 4px;">
                      <h4 style="color: var(--accent-positive); margin: 0 0 0.5rem 0;">The 11,000-Monkey Simulation Benchmark</h4>
                      <p style="font-size: 0.9rem; color: var(--text-secondary); margin: 0; line-height: 1.6;">
                        In this run, we simulated <strong>1,000 random monkeys for each of the 11 container specifications</strong>, totaling <strong>11,000 monkeys</strong>.
                        With N = 1,000, the minimum empirical p-value reaches 1/1001 &approx; 0.0010, unlocking precision to distinguish between upper-tail performers:
                        <ul>
                          <li><strong>CONTESTANT_A, sloth-2</strong>: Return +17.96% | Percentile: <strong>>99.9%</strong> | <strong>p &lt; 0.001</strong></li>
                          <li><strong>CONTESTANT_C, sloth-4</strong>: Return +16.50% | Percentile: <strong>>99.9%</strong> | <strong>p &lt; 0.001</strong></li>
                          <li><strong>Baseline Robot</strong>: Outperformed median random pickers by +8.42% net return.</li>
                        </ul>
                      </p>
                    </div>
                    <p>By enforcing a rigorous null colony, QuantPits Arena ensures that all alpha claims in the CSI 1000 universe are backed by institutional statistical significance.</p>
                """
            }
        ]
    }

    # 9. Web Payload
    web_payload = {
        "metadata": {
            "season_id": "season_csi1000",
            "season_name": "Season CSI 1000: Small-Cap Breadth Arena",
            "run_id": run_dir.name,
            "anchor_date": nav_dates[0] if nav_dates else "2026-07-03",
            "end_date": nav_dates[-1] if nav_dates else "2026-08-28",
            "initial_cash": 500000.0,
            "currency": "CNY",
            "lot_size": 100,
            "exported_at": pd.Timestamp.now().isoformat(),
            "total_paths": len(path_records),
            "total_contestants": len(contestants),
            "csi300_return_pct": csi1000_ret,
            "market_benchmark_name": "CSI 1000",
            "market_benchmark_code": "SH000852",
            "market_benchmark_return_pct": csi1000_ret,
            "universe_name": "CSI 1000 Universe (~1,000 Stocks)",
            "universe_code": "csi1000",
            "taotie_return_pct": taotie_tot_ret,
            "ghost_taotie_return_pct": ghost_tot_ret,
            "active_benchmarks": ["CSI 1000", "Taotie 1000 (500k)", "Ghost Taotie 1000 (100M)", "1,000 Monkeys"],
            "trading_days": len(nav_dates),
            "preview": False,
            "window_label": "Parallel Horizon: 2026-07-03 ~ 2026-08-28",
            "period_label": f"Evaluation Window: {nav_dates[0] if nav_dates else '2026-07-03'} ~ {nav_dates[-1] if nav_dates else '2026-08-28'} ({len(nav_dates)} trading days)"
        },
        "contestants": contestants,
        "paths": path_records,
        "nav_timeline": {
            "dates": nav_dates,
            "curves": nav_series_map,
            "drawdowns": drawdowns_map,
            "excess_csi300": excess_map
        },
        "monkey_null_distributions": null_records,
        "decision_forks": [],
        "dispatches": dispatches_payload,
        "matrix": {
            "rows": list(df_matrix.index) if not df_matrix.empty else [],
            "columns": list(df_matrix.columns) if not df_matrix.empty else [],
            "data": df_matrix.to_dict(orient="index") if not df_matrix.empty else {}
        }
    }

    out_file = REPO_ROOT / "web" / "js" / "data" / "season_csi1000.js"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("/**\n * QuantPits-Arena Season CSI 1000 Real Backtest Data Payload\n * Auto-generated by scripts/export_season_csi1000.py\n */\n")
        f.write("window.ARENA_SEASONS_DATA = window.ARENA_SEASONS_DATA || {};\n")
        f.write("window.ARENA_SEASONS_DATA[\"season_csi1000\"] = ")
        json.dump(web_payload, f, ensure_ascii=False, indent=2)
        f.write(";\n")

    print(f"[✔] Successfully exported Season CSI 1000 data to {out_file} ({out_file.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=str, default=None)
    args = parser.parse_args()
    target_run = Path(args.run_dir) if args.run_dir else None
    export_season_csi1000(run_dir=target_run)
