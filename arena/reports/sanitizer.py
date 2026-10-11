"""
arena/reports/sanitizer.py
==========================
双层输出架构与自动化脱敏导出器 (Dual-Tier Output Exporter)
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
import json
import pandas as pd

from arena.config import RUNS_DIR
from arena.portfolio.types import PortfolioPath
from arena.contestants.registry import ContestantRegistry


class DualTierExporter:
    """
    双层数据导出与脱敏管道：
    - private/: 隔离存储本地独占明细（真实股票代码、成交价格、个股股数）
    - public/: 生成完全脱敏的公开版本（归一化 NAV、宏观收益指标、Model × Animal 矩阵，无个股指纹）
    """

    def __init__(self, run_id: str, base_dir: Path = RUNS_DIR):
        self.run_id = run_id
        self.run_dir = base_dir / run_id
        self.private_dir = self.run_dir / "private"
        self.public_dir = self.run_dir / "public"
        self.reports_dir = self.public_dir / "reports"

        self.private_dir.mkdir(parents=True, exist_ok=True)
        self.public_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def export(
        self,
        results: Dict[tuple, PortfolioPath],
        registry: ContestantRegistry
    ) -> Dict[str, Path]:
        """
        执行全量双层导出与脱敏。
        """
        # 1. 收集日频 NAV 曲线与诊断指标（公开层）
        nav_dict = {}
        summary_rows = []
        diagnostics_rows = []
        matrix_data: Dict[str, Dict[str, float]] = {}

        for (cid, aid), path in results.items():
            anon_cid = registry.get_anonymous_id(cid)
            col_name = f"{anon_cid}_{aid}"

            # 日频 NAV 时序
            s = path.nav_series
            if len(s) > 0:
                nav_dict[col_name] = s

            # 基础绩效指标
            tot_ret = path.total_return
            mdd = path.max_drawdown
            diag = path.diagnostics or {}

            summary_rows.append({
                "contestant_id": anon_cid,
                "animal_id": aid,
                "total_return_pct": f"{tot_ret * 100:.2f}%",
                "max_drawdown_pct": f"{mdd * 100:.2f}%",
                "final_nav": f"{s.iloc[-1]:.4f}" if len(s) > 0 else "1.0000",
                "target_holdings_mean": diag.get("target_holdings_mean", 0),
                "actual_holdings_mean": diag.get("actual_holdings_mean", 0),
                "unaffordable_buy_count": diag.get("unaffordable_buy_count", 0),
                "unaffordable_buy_ratio": f"{diag.get('unaffordable_buy_ratio', 0.0) * 100:.2f}%",
                "mean_cash_ratio": f"{diag.get('mean_cash_ratio', 0.0) * 100:.2f}%",
                "max_cash_ratio": f"{diag.get('max_cash_ratio', 0.0) * 100:.2f}%",
                "final_cash_ratio": f"{diag.get('final_cash_ratio', 0.0) * 100:.2f}%",
            })

            # 完整诊断明细行
            diagnostics_rows.append({
                "contestant_id": anon_cid,
                "animal_id": aid,
                "target_holdings_mean": diag.get("target_holdings_mean", 0),
                "actual_holdings_mean": diag.get("actual_holdings_mean", 0),
                "actual_holdings_min": diag.get("actual_holdings_min", 0),
                "actual_holdings_max": diag.get("actual_holdings_max", 0),
                "buy_attempt_count": diag.get("buy_attempt_count", 0),
                "unaffordable_buy_count": diag.get("unaffordable_buy_count", 0),
                "unaffordable_buy_ratio": f"{diag.get('unaffordable_buy_ratio', 0.0) * 100:.2f}%",
                "unaffordable_event_days": diag.get("unaffordable_event_days", 0),
                "unaffordable_event_day_ratio": f"{diag.get('unaffordable_event_day_ratio', 0.0) * 100:.2f}%",
                "mean_cash_ratio": f"{diag.get('mean_cash_ratio', 0.0) * 100:.2f}%",
                "max_cash_ratio": f"{diag.get('max_cash_ratio', 0.0) * 100:.2f}%",
                "final_cash_ratio": f"{diag.get('final_cash_ratio', 0.0) * 100:.2f}%",
                "mean_invested_ratio": f"{diag.get('mean_invested_ratio', 0.0) * 100:.2f}%",
            })

            # Model × Animal 矩阵数据
            if anon_cid not in matrix_data:
                matrix_data[anon_cid] = {}
            matrix_data[anon_cid][aid] = tot_ret

        # 写入 public/daily_nav_curves.csv
        pub_nav_file = self.public_dir / "daily_nav_curves.csv"
        if nav_dict:
            df_nav = pd.DataFrame(nav_dict).sort_index()
            df_nav.to_csv(pub_nav_file, index_label="datetime")

        # 写入 public/summary_metrics.csv
        pub_metrics_file = self.public_dir / "summary_metrics.csv"
        df_summary = pd.DataFrame(summary_rows)
        df_summary.to_csv(pub_metrics_file, index=False)

        # 写入 public/capital_constraint_diagnostics.csv
        pub_diag_file = self.public_dir / "capital_constraint_diagnostics.csv"
        df_diag = pd.DataFrame(diagnostics_rows)
        df_diag.to_csv(pub_diag_file, index=False)

        # 写入 public/model_animal_matrix.csv
        pub_matrix_file = self.public_dir / "model_animal_matrix.csv"
        df_matrix = pd.DataFrame(matrix_data).T
        df_matrix.to_csv(pub_matrix_file)

        # 写入 public/reports/
        self._export_markdown_reports(df_summary, df_matrix, df_diag)

        # 2. 写入 private/（本地独占明细）
        priv_trades_file = self.private_dir / "raw_trades.csv"
        all_trades = []
        for (cid, aid), path in results.items():
            for t in path.trades:
                all_trades.append({
                    "contestant_id": cid,
                    "animal_id": aid,
                    "date": t.date,
                    "instrument": t.instrument,
                    "direction": t.direction,
                    "price": t.price,
                    "shares": t.shares,
                    "value": t.value,
                    "cost": t.cost
                })
        if all_trades:
            pd.DataFrame(all_trades).to_csv(priv_trades_file, index=False)

        return {
            "public_nav": pub_nav_file,
            "public_metrics": pub_metrics_file,
            "public_diagnostics": pub_diag_file,
            "public_matrix": pub_matrix_file,
            "private_trades": priv_trades_file
        }

    @staticmethod
    def _to_markdown_table(df: pd.DataFrame, include_index: bool = False) -> str:
        """生成标准 GitHub Markdown 管道表格（无需第三方 tabulate 依赖）"""
        try:
            return df.to_markdown(index=include_index)
        except Exception:
            headers = list(df.columns)
            if include_index:
                headers = [""] + headers
            header_line = "| " + " | ".join(str(h) for h in headers) + " |"
            sep_line = "| " + " | ".join("---" for _ in headers) + " |"
            lines = [header_line, sep_line]
            for idx, row in df.iterrows():
                vals = [str(idx)] if include_index else []
                vals.extend([str(v) for v in row.values])
                lines.append("| " + " | ".join(vals) + " |")
            return "\n".join(lines)

    def _export_markdown_reports(self, df_summary: pd.DataFrame, df_matrix: pd.DataFrame, df_diag: pd.DataFrame):
        """生成脱敏公开的 Markdown 报告"""
        to_md = self._to_markdown_table

        # 1. Leaderboard (公开层核心排行榜，保持简洁核心字段)
        lb_file = self.reports_dir / "leaderboard.md"
        with open(lb_file, "w", encoding="utf-8") as f:
            f.write("# QuantPits Graveyard Arena — Leaderboard\n\n")
            f.write(f"Run ID: `{self.run_id}`\n\n")
            # 展示核心收益列
            core_cols = ["contestant_id", "animal_id", "total_return_pct", "max_drawdown_pct", "final_nav"]
            f.write(to_md(df_summary[core_cols], include_index=False))
            f.write("\n\n---\n\n")
            f.write("## Capital Granularity Diagnostics Summary\n\n")
            f.write("Below is the affordability and cash deployment diagnostics across capacity breadth groups:\n\n")
            # 抽取关键字段展示
            diag_summary_cols = [
                "contestant_id", "animal_id", "target_holdings_mean", "actual_holdings_mean",
                "unaffordable_buy_count", "unaffordable_buy_ratio", "mean_cash_ratio", "final_cash_ratio"
            ]
            f.write(to_md(df_diag[diag_summary_cols], include_index=False))
            f.write("\n\n> See `reports/capital_granularity_diagnostics.md` for full methodology, environment constraints, and group comparisons.\n")

        # 2. Matrix
        mt_file = self.reports_dir / "model_animal_matrix.md"
        with open(mt_file, "w", encoding="utf-8") as f:
            f.write("# QuantPits Graveyard Arena — Model × Animal Return Matrix\n\n")
            f.write(f"Run ID: `{self.run_id}`\n\n")
            # 转为百分比展示
            map_func = getattr(df_matrix, "map", getattr(df_matrix, "applymap", None))
            df_pct = map_func(lambda v: f"{v * 100:.2f}%" if pd.notnull(v) else "-")
            f.write(to_md(df_pct, include_index=True))
            f.write("\n")

        # 3. Capital Granularity Diagnostics Report (专门诊断报告)
        diag_file = self.reports_dir / "capital_granularity_diagnostics.md"
        with open(diag_file, "w", encoding="utf-8") as f:
            f.write("# QuantPits Graveyard Arena — Capital Granularity Diagnostics\n\n")
            f.write(f"Run ID: `{self.run_id}`\n\n")
            f.write("## 1. Unified Execution Environment Constraints\n\n")
            f.write("All contestants and animal portfolios in this Arena were executed under strictly standardized real-world capital constraints:\n\n")
            f.write("- **Initial Capital**: `CNY 500,000` (fixed benchmark per portfolio)\n")
            f.write("- **Lot Sizing Rule**: `lot_size = 100` (China A-share standard; fractional / partial-lot buying is disabled)\n")
            f.write("- **Affordability Rule**: If allocated cash for an instrument cannot purchase 1 lot (`price * 100 > allocated_cash`), the BUY order is **skipped** (unaffordable skip)\n")
            f.write("- **Residual Cash Rule**: Residual unspent cash remains in the cash account without secondary redistribution or round-up leverage\n")
            f.write("- **Universe Exit Rule**: Out-of-pool holdings are prioritized for exit, strictly bounded by the animal's `DropN` quota\n\n")

            f.write("## 2. Research Interpretation & Methodology\n\n")
            f.write("For broader portfolios with large `TopK` (e.g., Eagle-44/66/88, Whale Shark, Taotie), performance variations must **not** be automatically interpreted as pure signal breadth sensitivity.\n\n")
            f.write("Under fixed CNY 500,000 capital:\n")
            f.write("1. As target capacity grows, theoretical cash allocation per stock decreases (`500k / K`);\n")
            f.write("2. Higher-priced stocks naturally trigger the 1-lot affordability constraint and get skipped;\n")
            f.write("3. Actual holdings may systematically diverge from theoretical target capacity, leading to natural cash retention;\n")
            f.write("4. Therefore, these animals stress-test the compound interaction of:  \n")
            f.write("   $$\\text{Effective Performance} = \\text{Signal Breadth} \\times \\text{Portfolio Policy} \\times \\text{Finite-Capital Granularity}$$\n")
            f.write("This is **not** a simulation artifact or defect, but a deliberately preserved realistic execution boundary.\n\n")

            f.write("## 3. Taotie Benchmark Definition\n\n")
            f.write("> **Taotie (饕餮)** is explicitly defined as a **capital-constrained full-universe executable benchmark**, rather than a theoretical unconstrained equal-weight index. Under CNY 500,000 capital, it represents the realistic portfolio formed when attempting to track the eligible universe purely through passive exit/entry rebalancing without fractional shares.\n\n")

            f.write("## 4. Breadth Groups Comparison\n\n")
            breadth_animals = ["eagle-5-1", "eagle-11-2", "robot", "eagle-44-6", "eagle-66-9", "eagle-88-12", "whale-shark", "taotie"]
            sub_breadth = df_diag[df_diag["animal_id"].isin(breadth_animals)].copy()
            if not sub_breadth.empty:
                # 合并收益指标
                merged_breadth = pd.merge(
                    sub_breadth,
                    df_summary[["contestant_id", "animal_id", "total_return_pct", "max_drawdown_pct"]],
                    on=["contestant_id", "animal_id"],
                    how="left"
                )
                comp_cols = [
                    "contestant_id", "animal_id", "target_holdings_mean", "actual_holdings_mean",
                    "unaffordable_buy_count", "unaffordable_buy_ratio", "mean_cash_ratio",
                    "total_return_pct", "max_drawdown_pct"
                ]
                f.write(to_md(merged_breadth[comp_cols], include_index=False))
                f.write("\n\n")

            f.write("## 5. Comprehensive Diagnostics Matrix (All Contestants × Animals)\n\n")
            f.write(to_md(df_diag, include_index=False))
            f.write("\n")

    def export_monkey_reports(
        self,
        monkey_results: Dict[str, List[PortfolioPath]],
        contestant_results: Dict[tuple, PortfolioPath],
        registry: ContestantRegistry
    ) -> Dict[str, Path]:
        """
        导出参数化猴子群落零假设分布报告与经验显著性检验报告。
        """
        from arena.controls.monkey import CANONICAL_STRATEGY_SPECS, map_animal_to_spec_id, MonkeyColony

        import numpy as np
        from arena.reports.statistics import empirical
        colony = MonkeyColony()
        distributions, summaries = {}, []
        for spec_id, paths in monkey_results.items():
            spec = CANONICAL_STRATEGY_SPECS[spec_id]
            values = np.asarray(paths.returns if hasattr(paths, "returns") else [p.total_return for p in paths])
            distributions[spec_id] = values
            dist = colony.summarize_distribution(values)
            summaries.append(dict(strategy_spec=spec_id, topk=spec.topk, n_drop=spec.n_drop,
                description=spec.description, colony_size=len(values), deterministic=spec.passive_pool,
                **{f"monkey_{k}":v*100 for k,v in dist.items()}))
        rows=[]
        for (cid,aid),path in contestant_results.items():
            spec_id=map_animal_to_spec_id(aid)
            values=distributions.get(spec_id)
            tested=spec_id is not None and not CANONICAL_STRATEGY_SPECS[spec_id].passive_pool
            row=dict(contestant_id=registry.get_anonymous_id(cid),animal_id=aid,strategy_spec=spec_id,
                     actual_return_pct=path.total_return*100,
                     test_status="random_control" if tested else "not_applicable",
                     empirical_p_value=None,significant_95pct=False,monkey_count=0,
                     monkey_median_pct=float(np.median(values))*100 if values is not None else None,
                     excess_over_monkey_pct=(path.total_return-float(np.median(values)))*100 if values is not None else None)
            if tested:
                row.update(empirical(path.total_return,values))
            rows.append(row)
        dist_path=self.public_dir / "monkey_null_distributions.csv"
        sig_path=self.public_dir / "contestant_monkey_significance.csv"
        pd.DataFrame(summaries).to_csv(dist_path,index=False)
        pd.DataFrame(rows).to_csv(sig_path,index=False)
        report=self.reports_dir / "monkey_null_distributions.md"
        report.write_text("# Random-control diagnostics\n\n"
            "Only TopK/DropN determine matching. Ten random specifications and one deterministic passive reference. "
            "All paths use the declared execution policy; delayed animals retain their own cold/warm start.\n\n"
            "Upper-tail p = (k+1)/(N+1), including ties. N and k are saved without rounding. "
            "Deterministic and unmatched references have no random-control p value. "
            "Confidence intervals describe Monte Carlo tail uncertainty, not additional market observations.\n\n"
            +self._to_markdown_table(pd.DataFrame(summaries))+"\n",encoding="utf-8")
        return dict(monkey_distributions_csv=dist_path,contestant_significance_csv=sig_path,monkey_report_md=report)

    def export_web_payload(
        self,
        season_cfg: Any,
        manifests_public_dir: Optional[Path] = None,
        web_output_path: Optional[Path] = None,
        publish_auxiliary: bool = True
    ) -> Path:
        """
        Universal Web Payload Serializer (Stage 3).
        Consolidates Stage 2 outputs, manifests, and season declarative metadata into:
        web/js/data/{season_id}.js and updates seasons_index.js.
        """
        import numpy as np
        import yaml
        from arena.config import REPO_ROOT

        pub_dir = self.public_dir
        season_id = getattr(season_cfg, "season_id", self.run_id)
        raw_dict = getattr(season_cfg, "raw_dict", {}) or {}

        # 1. Manifests
        manifests_dir = manifests_public_dir or (REPO_ROOT / "manifests" / "public")
        contestants = []
        if manifests_dir.exists():
            for mf in sorted(manifests_dir.glob("*.yaml")):
                with open(mf, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
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

        # 2. Public CSVs
        df_metrics = pd.read_csv(pub_dir / "summary_metrics.csv", float_precision="round_trip") if (pub_dir / "summary_metrics.csv").exists() else pd.DataFrame()
        df_diag = pd.read_csv(pub_dir / "capital_constraint_diagnostics.csv", float_precision="round_trip") if (pub_dir / "capital_constraint_diagnostics.csv").exists() else pd.DataFrame()
        df_sig = pd.read_csv(pub_dir / "contestant_monkey_significance.csv", float_precision="round_trip") if (pub_dir / "contestant_monkey_significance.csv").exists() else pd.DataFrame()
        df_null = pd.read_csv(pub_dir / "monkey_null_distributions.csv", float_precision="round_trip") if (pub_dir / "monkey_null_distributions.csv").exists() else pd.DataFrame()
        df_matrix = pd.read_csv(pub_dir / "model_animal_matrix.csv", index_col=0, float_precision="round_trip") if (pub_dir / "model_animal_matrix.csv").exists() else pd.DataFrame()
        if not df_matrix.empty:
            df_matrix = df_matrix[~df_matrix.index.astype(str).str.contains("BENCHMARK", case=False, na=False)]
            cols_to_drop = [c for c in ["taotie", "ghost_taotie"] if c in df_matrix.columns]
            if cols_to_drop:
                df_matrix = df_matrix.drop(columns=cols_to_drop)

        # 3. NAV curves
        df_nav = pd.read_csv(pub_dir / "daily_nav_curves.csv", float_precision="round_trip") if (pub_dir / "daily_nav_curves.csv").exists() else pd.DataFrame()
        nav_dates = df_nav["datetime"].tolist() if "datetime" in df_nav.columns else []
        nav_series_map: Dict[str, List[float]] = {}
        for col in df_nav.columns:
            if col != "datetime":
                nav_series_map[col] = [float(v) for v in df_nav[col].tolist()]

        # 4. Market benchmark from universe definition or benchmarks list
        univ = raw_dict.get("universe", {})
        bench_symbol = "sh000300"
        bench_name = "CSI 300"

        # Check benchmarks list first
        bench_list = raw_dict.get("benchmarks", [])
        for b in bench_list:
            if b.get("type") == "INDEX" or "symbol" in b:
                bench_symbol = b.get("symbol", "SH000300").lower()
                bench_name = b.get("display_name", bench_name)
                break
        else:
            bench_symbol = univ.get("market_benchmark_symbol", univ.get("benchmark_index", "SH000300")).lower()
            bench_name = univ.get("market_benchmark_name", "CSI 300")

        bench_name = bench_name.replace("(Market Benchmark)", "").replace("()", "").strip()
        univ_name = univ.get("name", univ.get("market", f"{bench_name} Universe"))
        univ_code = univ.get("code", univ.get("market", "universe"))

        bench_curve: List[float] = []
        bench_ret = 0.0
        try:
            from arena.calendar import TradingCalendar
            cal = TradingCalendar()
            bin_file = Path.home() / ".qlib" / "qlib_data" / "cn_data" / "features" / bench_symbol / "close.day.bin"
            if bin_file.exists() and len(nav_dates) > 0:
                from arena.benchmarks.index import read_feature_slice
                d_start=cal.day_to_idx[nav_dates[0]]
                d_end=cal.day_to_idx[nav_dates[-1]]
                prices=read_feature_slice(bin_file,d_start,d_end)
                if len(prices)==len(nav_dates):
                    bench_curve=[float(p/prices[0]) for p in prices]
                    bench_ret=float((prices[-1]/prices[0]-1)*100)
        except Exception:
            pass

        if bench_curve:
            nav_series_map[f"BENCHMARK_{univ_code}"] = bench_curve
            nav_series_map["BENCHMARK_market"] = bench_curve
            nav_series_map["BENCHMARK_csi300"] = bench_curve  # Fallback compatibility

        def _parse_pct(val: Any, default: float = 0.0) -> float:
            if isinstance(val, (int, float)):
                return float(val) if np.isfinite(val) else default
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

            tot_ret = _parse_pct(s_info.get("actual_return_pct", row.get("total_return_pct", 0.0)))
            mdd = _parse_pct(row.get("max_drawdown_pct", 0.0))
            monkey_med = _parse_pct(s_info.get("monkey_median_pct", 0.0))
            excess_monkey = _parse_pct(s_info.get("excess_over_monkey_pct", tot_ret - monkey_med))
            pct_rank = _parse_pct(s_info.get("percentile_rank", 50.0))
            raw_p = s_info.get("empirical_p_value")
            p_val = float(raw_p) if raw_p is not None and pd.notna(raw_p) else None

            col_key = f"{cid}_{aid}"
            sharpe = 0.0
            if col_key in nav_series_map:
                series = pd.Series(nav_series_map[col_key])
                mdd = float(-(series / series.cummax() - 1).min()) * 100
                rets = series.pct_change().dropna()
                if len(rets) > 1 and rets.std() > 0:
                    sharpe = round(float((rets.mean() / rets.std()) * (250 ** 0.5)), 2)

            def _get_animal_category(animal_id: str) -> str:
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
                    return "Whale Shark (Broad Selection)"
                elif animal_id == "taotie":
                    return "Taotie (100% Passive)"
                elif animal_id == "ghost_taotie":
                    return "Ghost Taotie (Capital Granularity Scenario)"
                return "Custom"

            badges = []
            if pct_rank >= 99.0:
                badges.append("Alpha Outlier (>99%)")
            if sharpe >= 2.0:
                badges.append("High Sharpe (≥2.0)")
            if _parse_pct(d_info.get("unaffordable_buy_ratio", 0)) > 20.0:
                badges.append("Capital Friction (>20%)")

            final_nav = round(float(nav_series_map[col_key][-1]), 4) if col_key in nav_series_map and len(nav_series_map[col_key]) > 0 else 1.0

            from arena.controls.monkey import map_animal_to_spec_id
            spec_id = map_animal_to_spec_id(aid)

            path_records.append({
                "path_id": f"{cid}_{aid}",
                "contestant_id": cid,
                "animal_id": aid,
                "strategy_spec": spec_id,
                "animal_category": _get_animal_category(aid),
                "display_name": f"{cid} × {aid}",
                "total_return_pct": tot_ret,
                "max_drawdown_pct": mdd,
                "final_nav": final_nav,
                "sharpe_ratio": sharpe,
                "excess_over_csi300_pct": tot_ret - bench_ret,
                "excess_over_monkey_pct": excess_monkey,
                "percentile_rank": pct_rank if p_val is not None else None,
                "monkey_percentile": pct_rank if p_val is not None else None,
                "monkey_percentile_rank": pct_rank if p_val is not None else None,
                "empirical_p_value": p_val,
                "p_value": p_val,
                "is_statistically_significant": (p_val is not None and p_val < 0.05),
                "test_status": s_info.get("test_status", "not_evaluated"),
                "monkey_count": int(s_info.get("monkey_count", 0)),
                "exceedance_count": int(s_info["exceedance_count"]) if pd.notna(s_info.get("exceedance_count")) else None,
                "p_resolution": float(s_info["p_resolution"]) if pd.notna(s_info.get("p_resolution")) else None,
                **{key: float(s_info[key]) if pd.notna(s_info.get(key)) else None for key in
                   ("bonferroni_p", "holm_p", "bh_q", "by_q", "mc_tail_lower_95", "mc_tail_upper_95")},
                "family_size": int(s_info.get("family_size", 0)),
                "is_bonferroni_significant": bool(s_info.get("bonferroni_p", 1.0) < .05),
                "buy_attempt_count": int(d_info.get("buy_attempt_count", 0)),
                "unaffordable_buy_ratio": _parse_pct(d_info.get("unaffordable_buy_ratio", 0)),
                "unaffordable_buy_count": int(d_info.get("unaffordable_buy_count", 0)),
                "unaffordable_event_days": int(d_info.get("unaffordable_event_days", 0)),
                "mean_cash_ratio": _parse_pct(d_info.get("mean_cash_ratio", 0)),
                "mean_cash_ratio_pct": _parse_pct(d_info.get("mean_cash_ratio", 0)),
                "max_cash_ratio": _parse_pct(d_info.get("max_cash_ratio", 0)),
                "max_cash_ratio_pct": _parse_pct(d_info.get("max_cash_ratio", 0)),
                "final_cash_ratio": _parse_pct(d_info.get("final_cash_ratio", 0)),
                "target_holdings_mean": float(d_info.get("target_holdings_mean", 22.0)),
                "actual_holdings_mean": float(d_info.get("actual_holdings_mean", 22.0)),
                "badges": badges
            })

        # Drawdowns & excess curves
        drawdowns_map: Dict[str, List[float]] = {}
        excess_map: Dict[str, List[float]] = {}
        for k, curve in nav_series_map.items():
            if curve:
                s = pd.Series(curve)
                cummax = s.cummax()
                dd = ((s - cummax) / cummax) * 100.0
                drawdowns_map[k] = [round(float(v), 2) for v in dd.tolist()]
                if bench_curve and len(bench_curve) == len(curve):
                    excess = [round(float((c - b) * 100.0), 2) for c, b in zip(curve, bench_curve)]
                    excess_map[k] = excess

        # Benchmark returns
        evaluation_file = self.public_dir / "evaluation_manifest.json"
        evaluation_metadata = json.loads(evaluation_file.read_text()) if evaluation_file.exists() else {}
        taotie_tot_ret = round(float((nav_series_map["BENCHMARK_taotie"][-1] - 1.0) * 100.0), 2) if "BENCHMARK_taotie" in nav_series_map and nav_series_map["BENCHMARK_taotie"] else 0.0
        ghost_tot_ret = round(float((nav_series_map["BENCHMARK_ghost_taotie"][-1] - 1.0) * 100.0), 2) if "BENCHMARK_ghost_taotie" in nav_series_map and nav_series_map["BENCHMARK_ghost_taotie"] else 0.0

        timeline_file = self.public_dir / "monkey_timeline.json"
        null_timeline = json.loads(timeline_file.read_text()) if timeline_file.exists() else {}
        hist_file = self.public_dir / "monkey_histograms.json"
        null_histograms = json.loads(hist_file.read_text()) if hist_file.exists() else {}
        null_records = []
        if not df_null.empty:
            for r in df_null.to_dict(orient="records"):
                min_v = _parse_pct(r.get("monkey_min", r.get("min_return_pct", 0)))
                p05_v = _parse_pct(r.get("monkey_p05", r.get("p05_return_pct", 0)))
                med_v = _parse_pct(r.get("monkey_median", r.get("median_return_pct", 0)))
                mean_v = _parse_pct(r.get("monkey_mean", r.get("mean_return_pct", 0)))
                p95_v = _parse_pct(r.get("monkey_p95", r.get("p95_return_pct", 0)))
                max_v = _parse_pct(r.get("monkey_max", r.get("max_return_pct", 0)))
                std_v = _parse_pct(r.get("monkey_std", r.get("std_return_pct", 0)))

                null_records.append({
                    "strategy_spec": r.get("strategy_spec", ""),
                    "deterministic": bool(r.get("deterministic", False)),
                    "settlement_quantiles": null_timeline.get(r.get("strategy_spec"), {}),
                    "histogram": null_histograms.get(r.get("strategy_spec"), {}),
                    "description": r.get("description", ""),
                    "topk": r.get("topk", ""),
                    "n_drop": r.get("n_drop", ""),
                    "monkey_min": min_v,
                    "monkey_p05": p05_v,
                    "monkey_median": med_v,
                    "monkey_mean": mean_v,
                    "monkey_p95": p95_v,
                    "monkey_max": max_v,
                    "monkey_std": std_v,
                    "min_return_pct": min_v,
                    "p05_return_pct": p05_v,
                    "median_return_pct": med_v,
                    "mean_return_pct": mean_v,
                    "p95_return_pct": p95_v,
                    "max_return_pct": max_v,
                    "colony_size": int(r.get("colony_size", 1000))
                })

        dispatches_payload = raw_dict.get("dispatches", {})
        if dispatches_payload and "episodes" in dispatches_payload:
            try:
                import markdown
                for ep in dispatches_payload["episodes"]:
                    f_path = ep.get("file")
                    if f_path:
                        candidates = [
                            REPO_ROOT / f_path,
                            REPO_ROOT / "web" / f_path,
                            REPO_ROOT / "chronicles" / "en" / Path(f_path).name,
                            REPO_ROOT / "web" / "chronicles" / "en" / Path(f_path).name,
                        ]
                        for c in candidates:
                            if c.exists() and c.is_file():
                                with open(c, "r", encoding="utf-8") as f_md:
                                    md_content = f_md.read()
                                ep["content_html"] = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
                                break
            except Exception as e:
                print(f"[WARN] Failed to compile markdown file for dispatches: {e}")

        if not dispatches_payload:
            dispatches_payload = {
                "executive": {
                    "headline": f"{season_id} Official Report",
                    "core_theme": "Automated Backtest and Risk Analysis",
                    "tldr": "Execution complete across all canonical animals and benchmarks."
                },
                "climate": {
                    "regime": "Dynamic",
                    "macro_events": []
                },
                "episodes": []
            }

        testbed_desc = univ.get("testbed_desc", f"{univ_name} testbed")
        timeliness_proof = raw_dict.get("banner", {}).get("proof_text") or (
            f"🔬 <strong style=\"color: var(--text-secondary);\">{bench_name} Testbed Proof:</strong> "
            f"{univ_name} with empirical random monkeys verified over {nav_dates[0] if nav_dates else ''} ~ {nav_dates[-1] if nav_dates else ''}. "
            f"Unfalsifiable empirical null resolution."
        )

        meta_dict = {
            "season_id": season_id,
            "season_title": getattr(season_cfg, "title", season_id),
            "season_subtitle": getattr(season_cfg, "description", ""),
            "status": getattr(season_cfg, "status", "ACTIVE"),
            "total_paths": len(path_records),
            **evaluation_metadata,
            "total_contestants": len(contestants),
            "csi300_return_pct": bench_ret,
            "market_benchmark_name": bench_name,
            "market_benchmark_code": bench_symbol.upper(),
            "market_benchmark_return_pct": bench_ret,
            "universe_name": univ_name,
            "universe_size": season_cfg.raw_dict.get("universe", {}).get("stock_count"),
            "universe_code": univ_code,
            "testbed_desc": testbed_desc,
            "timeliness_proof": timeliness_proof,
            "taotie_return_pct": taotie_tot_ret,
            "ghost_taotie_return_pct": ghost_tot_ret,
            "active_benchmarks": [
                bench_name,
                f"Taotie ({univ_code})",
                f"Ghost Taotie ({univ_code})",
                f"10 Random Specifications / {sum(r['colony_size'] for r in null_records if not r['deterministic']):,} Random Paths + 1 Deterministic Reference"
            ],
            "trading_days": len(nav_dates),
            "nav_observations": len(nav_dates),
            "valuation_sessions": max(0, len(nav_dates) - 1),
            "preview": False,
            "window_label": f"Evaluation Window: {nav_dates[0] if nav_dates else ''} ~ {nav_dates[-1] if nav_dates else ''}",
            "period_label": f"Evaluation Window: {nav_dates[0] if nav_dates else ''} ~ {nav_dates[-1] if nav_dates else ''} ({len(nav_dates)} NAV observations including anchor)"
        }

        web_payload = {
            "meta": meta_dict,
            "metadata": meta_dict,
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

        out_file = web_output_path or (REPO_ROOT / "web" / "js" / "data" / f"{season_id}.js")
        out_file.parent.mkdir(parents=True, exist_ok=True)
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(f"/**\n * QuantPits-Arena {season_id} Backtest Data Payload\n * Auto-generated by DualTierExporter.export_web_payload\n */\n")
            f.write("window.ARENA_SEASONS_DATA = window.ARENA_SEASONS_DATA || {};\n")
            f.write(f"window.ARENA_SEASONS_DATA[\"{season_id}\"] = ")
            json.dump(web_payload, f, ensure_ascii=False, indent=2)
            f.write(";\n")
        # Also synchronize legacy arena_data.js for Season 1 canonical baseline
        if publish_auxiliary and season_id == "season_01":
            try:
                arena_file = REPO_ROOT / "web" / "js" / "data" / "arena_data.js"
                with open(arena_file, "w", encoding="utf-8") as f_ad:
                    f_ad.write("/**\n * QuantPits-Arena Pre-compiled Public Data Payload\n * Auto-generated by DualTierExporter.export_web_payload (Season 1 Canonical Baseline)\n */\n")
                    f_ad.write("window.ARENA_DATA = ")
                    json.dump(web_payload, f_ad, ensure_ascii=False, indent=2)
                    f_ad.write(";\n")
                    f_ad.write("window.ARENA_SEASONS_DATA = window.ARENA_SEASONS_DATA || {};\n")
                    f_ad.write('window.ARENA_SEASONS_DATA["season_01"] = window.ARENA_DATA;\n')
            except Exception as e:
                print(f"[WARN] Failed to auto-sync arena_data.js: {e}")

        # 6. Auto-sync seasons_index.js
        try:
            if publish_auxiliary:
                self._sync_seasons_index(season_cfg, web_payload)
        except Exception as e:
            print(f"[WARN] Failed to auto-sync seasons_index.js: {e}")

        # 7. Auto-sync web/index.html script tag
        try:
            if publish_auxiliary:
                self._sync_index_html(season_id)
        except Exception as e:
            print(f"[WARN] Failed to auto-sync web/index.html: {e}")

        return out_file

    def _sync_seasons_index(self, season_cfg: Any, web_payload: Dict[str, Any]) -> None:
        """保持 web/js/data/seasons_index.js 自动注册与日期指标同步更新"""
        import re
        from arena.config import REPO_ROOT
        index_file = REPO_ROOT / "web" / "js" / "data" / "seasons_index.js"
        if not index_file.exists():
            return

        content = index_file.read_text(encoding="utf-8")
        season_id = web_payload["meta"]["season_id"]
        meta = web_payload["meta"]
        dates = web_payload.get("nav_timeline", {}).get("dates", [])
        anchor = dates[0] if dates else season_cfg.anchor_date
        new_end = dates[-1] if dates else season_cfg.end_date
        td_count = len(dates) if dates else meta.get("trading_days", 0)
        pattern = rf'({{\s*["\']?id["\']?:\s*["\']{re.escape(season_id)}["\'].*?\}})'
        match = re.search(pattern, content, flags=re.DOTALL)

        # 若已存在该赛季条目，则增量更新其 end_date 和 trading_days
        if match:
            if new_end and td_count:
                # 定位该赛季在数组中的块进行针对性替换
                if match:
                    block = match.group(1)
                    # 更新 end_date
                    updated_block = re.sub(
                        r'(["\']?end_date["\']?:\s*["\'])[\d\-]+(["\'])',
                        rf'\g<1>{new_end}\g<2>',
                        block
                    )
                    # 更新 trading_days
                    updated_block = re.sub(
                        r'(["\']?trading_days["\']?:\s*)\d+',
                        rf'\g<1>{td_count}',
                        updated_block
                    )
                    # 更新 period (YYYY.MM - YYYY.MM)
                    try:
                        cal_end_ym = new_end[:7].replace("-", ".")
                        updated_block = re.sub(
                            r'(["\']?period["\']?:\s*["\'][\d\.]+\s*-\s*)[\d\.]+(["\'])',
                            rf'\g<1>{cal_end_ym}\g<2>',
                            updated_block
                        )
                    except Exception:
                        pass
                    if updated_block != block:
                        content = content[:match.start()] + updated_block + content[match.end():]
                        index_file.write_text(content, encoding="utf-8")
            return

        # 组装新赛季条目
        new_entry = {
            "id": season_id,
            "title": meta.get("season_title", season_id),
            "short_title": meta.get("universe_name", season_id),
            "status": meta.get("status", "ACTIVE"),
            "badge_type": "active" if meta.get("status") == "ACTIVE" else "warning",
            "period": f"{anchor[:7].replace('-', '.')} - {new_end[:7].replace('-', '.')}",
            "anchor_date": anchor,
            "end_date": new_end,
            "trading_days": td_count,
            "contestants_count": meta.get("total_contestants", 6),
            "animals_count": 28,
            "benchmarks": meta.get("active_benchmarks", []),
            "description": meta.get("season_subtitle", f"{season_id} backtest testbed"),
            "dispatches_banner": {
                "tag": f"🔬 {season_id} Arena",
                "title": f"{meta.get('season_title', season_id)} Active Evaluation.",
                "link": "#dispatches",
                "link_text": f"Read {season_id} Dispatches &rarr;"
            },
            "methodology": {
                "framework_name": f"{meta.get('universe_name', 'Custom Universe')} Empirical Evaluation",
                "anchor_spec": f"Retrospective Common Anchor ({anchor})",
                "capital_spec": "Standardized simulation budget with 100-share trading lots; normalized NAV",
                "benchmarks_summary": f"Market Index ({meta.get('market_benchmark_name', 'Index')}) + Taotie + Ghost Taotie + 10 random TopK/DropN groups plus one deterministic passive reference",
                "execution_flow": "Monday Open Rebalance; Holiday Mondays Skip Trading; Daily Valuation"
            }
        }

        # 插入到 window.ARENA_SEASONS_INDEX 数组末尾
        formatted_entry = json.dumps(new_entry, ensure_ascii=False, indent=2)
        # 缩进对齐
        indented_entry = "  " + formatted_entry.replace("\n", "\n  ")
        pattern = r"(window\.ARENA_SEASONS_INDEX\s*=\s*\[)(.*?)(\];)"
        match = re.search(pattern, content, flags=re.DOTALL)
        if match:
            existing_body = match.group(2).rstrip()
            if existing_body and not existing_body.endswith(","):
                existing_body += ","
            new_content = match.group(1) + existing_body + "\n" + indented_entry + "\n" + match.group(3) + content[match.end():]
            index_file.write_text(new_content, encoding="utf-8")

    def _sync_index_html(self, season_id: str) -> None:
        """确保 web/index.html 中包含对应 season script 标签"""
        from arena.config import REPO_ROOT
        import re
        html_file = REPO_ROOT / "web" / "index.html"
        if not html_file.exists():
            return

        content = html_file.read_text(encoding="utf-8")
        version = re.search(r'js/data/seasons_index\.js\?v=([^"\']+)', content)
        suffix = f"?v={version.group(1)}" if version else ""
        target_script = f'<script src="js/data/{season_id}.js{suffix}"></script>'
        if f'js/data/{season_id}.js' in content:
            return

        # 在最后一个 season_xxx.js 后面插入
        lines = content.splitlines()
        insert_idx = -1
        for i, line in enumerate(lines):
            if "js/data/season_" in line:
                insert_idx = i

        if insert_idx != -1:
            indent = "  "
            lines.insert(insert_idx + 1, f"{indent}{target_script}")
            html_file.write_text("\n".join(lines) + "\n", encoding="utf-8")


def sync_chronicles() -> int:
    """
    自动同步并对齐 chronicles/en/*.md 到 web/chronicles/en/*.md
    返回同步或更新的文件数量。
    """
    import shutil
    from arena.config import REPO_ROOT

    src_dir = REPO_ROOT / "chronicles" / "en"
    dst_dir = REPO_ROOT / "web" / "chronicles" / "en"

    if not src_dir.exists():
        return 0

    dst_dir.mkdir(parents=True, exist_ok=True)
    synced_count = 0

    for src_file in src_dir.glob("*.md"):
        dst_file = dst_dir / src_file.name
        if not dst_file.exists() or src_file.read_bytes() != dst_file.read_bytes():
            shutil.copy2(src_file, dst_file)
            synced_count += 1

    return synced_count





