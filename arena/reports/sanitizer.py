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

        colony = MonkeyColony()
        summary_rows = []
        spec_distributions = {}

        # 1. 汇总各策略规格的零假设分布指标
        for spec_id, paths in monkey_results.items():
            spec = CANONICAL_STRATEGY_SPECS.get(spec_id)
            returns = [p.total_return for p in paths]
            dist = colony.summarize_distribution(returns)
            spec_distributions[spec_id] = {
                "paths": paths,
                "returns": returns,
                "dist": dist
            }

            topk_str = "全池" if (spec and spec.topk == 0) else str(spec.topk if spec else "N/A")
            ndrop_str = "被动" if (spec and spec.n_drop == 0 and spec.passive_pool) else str(spec.n_drop if spec else "N/A")
            desc = spec.description if spec else ""

            summary_rows.append({
                "strategy_spec": spec_id,
                "topk": topk_str,
                "n_drop": ndrop_str,
                "description": desc,
                "colony_size": len(paths),
                "monkey_min": f"{dist['min'] * 100:.2f}%",
                "monkey_p05": f"{dist['p05'] * 100:.2f}%",
                "monkey_median": f"{dist['median'] * 100:.2f}%",
                "monkey_mean": f"{dist['mean'] * 100:.2f}%",
                "monkey_p95": f"{dist['p95'] * 100:.2f}%",
                "monkey_max": f"{dist['max'] * 100:.2f}%",
                "monkey_std": f"{dist['std'] * 100:.2f}%",
            })

        pub_dist_csv = self.public_dir / "monkey_null_distributions.csv"
        df_dist = pd.DataFrame(summary_rows)
        df_dist.to_csv(pub_dist_csv, index=False)

        # 2. 计算各参赛选手对标对应猴子分布的显著性指标
        significance_rows = []
        for (cid, aid), path in contestant_results.items():
            anon_cid = registry.get_anonymous_id(cid)
            spec_id = map_animal_to_spec_id(aid)
            spec_info = spec_distributions.get(spec_id)

            act_ret = path.total_return
            if spec_info and spec_info["returns"]:
                monkey_rets = spec_info["returns"]
                p_val = colony.compute_empirical_pvalue(act_ret, monkey_rets, higher_is_better=True)
                pct_rank = colony.compute_percentile_rank(act_ret, monkey_rets)
                median_monkey = spec_info["dist"]["median"]
                excess_over_monkey = act_ret - median_monkey
            else:
                p_val = 1.0
                pct_rank = 0.5
                median_monkey = 0.0
                excess_over_monkey = 0.0

            significance_rows.append({
                "contestant_id": anon_cid,
                "animal_id": aid,
                "strategy_spec": spec_id,
                "actual_return_pct": f"{act_ret * 100:.2f}%",
                "monkey_median_pct": f"{median_monkey * 100:.2f}%",
                "excess_over_monkey_pct": f"{excess_over_monkey * 100:+.2f}%",
                "percentile_rank": f"{pct_rank * 100:.1f}%",
                "empirical_p_value": f"{p_val:.4f}",
                "significant_95pct": "YES (p < 0.05)" if p_val < 0.05 else "NO"
            })

        pub_sig_csv = self.public_dir / "contestant_monkey_significance.csv"
        df_sig = pd.DataFrame(significance_rows)
        df_sig.to_csv(pub_sig_csv, index=False)

        actual_colony_size = len(next(iter(monkey_results.values()))) if monkey_results else 1000
        total_groups = len(monkey_results)
        total_monkeys = total_groups * actual_colony_size

        # 3. 产出 Markdown 报告
        report_md = self.reports_dir / "monkey_null_distributions.md"
        with open(report_md, "w", encoding="utf-8") as f:
            f.write("# QuantPits Graveyard Arena — Parametric Monkey Colony Diagnostics\n\n")
            f.write(f"Run ID: `{self.run_id}`\n\n")
            f.write("## 1. Methodology & Scientific Rationale\n\n")
            f.write("The **Parametric Monkey Colony** serves as the rigorous empirical null model for evaluating whether contestants' alpha returns are statistically distinguishable from pure random stock picking.\n\n")
            f.write("- **Zero Future Information**: Every monkey draws uniform random scores across the cross-section using deterministic seeds: `seed = (2026 + m * 10007 + t * 37) % (2**31 - 1)`.\n")
            f.write("- **Strict Parity**: Each monkey group operates under the **exact same 100-share minimum trading lot and CNY 500,000 capital constraints** as the real models.\n")
            f.write(f"- **Complete Parameter Coverage**: All {total_groups} distinct portfolio execution policies (TopK / DropN pairs, including Taotie passive full-universe) are individually benchmarked by {actual_colony_size} random monkeys ({total_monkeys:,} monkeys total).\n")
            f.write("- **Empirical P-Value**: Formally defined as $p = \\frac{1}{N} \\sum_{i=1}^N \\mathbb{I}(\\text{monkey}_i \\ge \\text{actual_return})$. $p < 0.05$ indicates significant alpha superiority over random chance at 95% confidence.\n\n")

            f.write(f"## 2. Null Distributions by Strategy Parameter Group ({total_groups} Groups × {actual_colony_size} Monkeys)\n\n")
            f.write(self._to_markdown_table(df_dist, include_index=False))
            f.write("\n\n")

            f.write("## 3. Contestant Significance vs. Corresponding Monkey Colony\n\n")
            f.write(self._to_markdown_table(df_sig, include_index=False))
            f.write("\n")

        return {
            "monkey_distributions_csv": pub_dist_csv,
            "contestant_significance_csv": pub_sig_csv,
            "monkey_report_md": report_md
        }

    def export_web_payload(
        self,
        season_cfg: Any,
        manifests_public_dir: Optional[Path] = None,
        web_output_path: Optional[Path] = None
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

        # 3. NAV curves
        df_nav = pd.read_csv(pub_dir / "daily_nav_curves.csv") if (pub_dir / "daily_nav_curves.csv").exists() else pd.DataFrame()
        nav_dates = df_nav["datetime"].tolist() if "datetime" in df_nav.columns else []
        nav_series_map: Dict[str, List[float]] = {}
        for col in df_nav.columns:
            if col != "datetime":
                nav_series_map[col] = [round(float(v), 4) for v in df_nav[col].tolist()]

        # 4. Market benchmark from universe definition or benchmarks list
        univ = raw_dict.get("universe", {})
        bench_symbol = "sh000300"
        bench_name = "Market Benchmark"

        # Check benchmarks list first
        bench_list = raw_dict.get("benchmarks", [])
        for b in bench_list:
            if b.get("type") == "INDEX" or "symbol" in b:
                bench_symbol = b.get("symbol", "SH000300").lower()
                bench_name = b.get("display_name", bench_name)
                break
        else:
            bench_symbol = univ.get("market_benchmark_symbol", univ.get("benchmark_index", "SH000300")).lower()
            bench_name = univ.get("market_benchmark_name", "Market Benchmark")

        univ_name = univ.get("name", univ.get("market", "Benchmark Universe"))
        univ_code = univ.get("code", univ.get("market", "universe"))

        bench_curve: List[float] = []
        bench_ret = 0.0
        try:
            from arena.calendar import TradingCalendar
            cal = TradingCalendar()
            bin_file = Path.home() / ".qlib" / "qlib_data" / "cn_data" / "features" / bench_symbol / "close.day.bin"
            if bin_file.exists() and len(nav_dates) > 0:
                with open(bin_file, "rb") as f:
                    start_idx = np.fromfile(f, dtype="<u4", count=1)[0]
                    data = np.fromfile(f, dtype="<f4")
                d_start = cal.day_to_idx.get(nav_dates[0], 0)
                d_end = cal.day_to_idx.get(nav_dates[-1], 0)
                if d_start >= start_idx and d_end >= d_start:
                    prices = data[d_start - start_idx : d_end - start_idx + 1]
                    if len(prices) == len(nav_dates) and prices[0] > 0:
                        bench_curve = [round(float(p / prices[0]), 4) for p in prices]
                        bench_ret = round(float((prices[-1] / prices[0] - 1) * 100), 2)
        except Exception:
            pass

        if bench_curve:
            nav_series_map[f"BENCHMARK_{univ_code}"] = bench_curve
            nav_series_map["BENCHMARK_csi300"] = bench_curve  # Fallback compatibility

        def _parse_pct(val: Any, default: float = 0.0) -> float:
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

            tot_ret = _parse_pct(row.get("total_return_pct", 0.0))
            mdd = _parse_pct(row.get("max_drawdown_pct", 0.0))
            monkey_med = _parse_pct(s_info.get("monkey_median_pct", 0.0))
            excess_monkey = _parse_pct(s_info.get("excess_over_monkey_pct", tot_ret - monkey_med))
            pct_rank = _parse_pct(s_info.get("percentile_rank", 50.0))
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
            if _parse_pct(d_info.get("unaffordable_buy_ratio", 0)) > 20.0:
                badges.append("Capital Friction (>20%)")

            final_nav = round(float(nav_series_map[col_key][-1]), 4) if col_key in nav_series_map and len(nav_series_map[col_key]) > 0 else 1.0

            path_records.append({
                "path_id": f"{cid}_{aid}",
                "contestant_id": cid,
                "animal_id": aid,
                "animal_category": _get_animal_category(aid),
                "display_name": f"{cid} × {aid}",
                "total_return_pct": tot_ret,
                "max_drawdown_pct": mdd,
                "final_nav": final_nav,
                "sharpe_ratio": sharpe,
                "excess_over_csi300_pct": round(tot_ret - bench_ret, 2),
                "excess_over_monkey_pct": round(excess_monkey, 2),
                "percentile_rank": round(pct_rank, 1),
                "monkey_percentile": round(pct_rank, 1),
                "monkey_percentile_rank": round(pct_rank, 1),
                "empirical_p_value": p_val,
                "p_value": p_val,
                "is_statistically_significant": (p_val < 0.05),
                "unaffordable_buy_ratio": _parse_pct(d_info.get("unaffordable_buy_ratio", 0)),
                "unaffordable_buy_count": int(d_info.get("unaffordable_buy_count", 0)),
                "unaffordable_event_days": int(d_info.get("unaffordable_event_days", 0)),
                "mean_cash_ratio": _parse_pct(d_info.get("mean_cash_ratio", 0)),
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
        taotie_tot_ret = round(float((nav_series_map["BENCHMARK_taotie"][-1] - 1.0) * 100.0), 2) if "BENCHMARK_taotie" in nav_series_map and nav_series_map["BENCHMARK_taotie"] else 0.0
        ghost_tot_ret = round(float((nav_series_map["BENCHMARK_ghost_taotie"][-1] - 1.0) * 100.0), 2) if "BENCHMARK_ghost_taotie" in nav_series_map and nav_series_map["BENCHMARK_ghost_taotie"] else 0.0

        null_records = []
        if not df_null.empty:
            for r in df_null.to_dict(orient="records"):
                null_records.append({
                    "strategy_spec": r.get("strategy_spec", ""),
                    "mean_return_pct": _parse_pct(r.get("mean_return_pct", 0)),
                    "median_return_pct": _parse_pct(r.get("median_return_pct", 0)),
                    "p05_return_pct": _parse_pct(r.get("p05_return_pct", 0)),
                    "p95_return_pct": _parse_pct(r.get("p95_return_pct", 0)),
                    "min_return_pct": _parse_pct(r.get("min_return_pct", 0)),
                    "max_return_pct": _parse_pct(r.get("max_return_pct", 0)),
                    "colony_size": int(r.get("colony_size", 1000))
                })

        dispatches_payload = raw_dict.get("dispatches", {})
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

        web_payload = {
            "meta": {
                "season_id": season_id,
                "season_title": getattr(season_cfg, "title", season_id),
                "season_subtitle": getattr(season_cfg, "description", ""),
                "status": getattr(season_cfg, "status", "ACTIVE"),
                "total_paths": len(path_records),
                "total_contestants": len(contestants),
                "csi300_return_pct": bench_ret,
                "market_benchmark_name": bench_name,
                "market_benchmark_code": bench_symbol.upper(),
                "market_benchmark_return_pct": bench_ret,
                "universe_name": univ_name,
                "universe_code": univ_code,
                "taotie_return_pct": taotie_tot_ret,
                "ghost_taotie_return_pct": ghost_tot_ret,
                "active_benchmarks": [bench_name, f"Taotie ({univ_code}) (500k)", f"Ghost Taotie ({univ_code}) (100M)", "1,000 Monkeys"],
                "trading_days": len(nav_dates),
                "preview": False,
                "window_label": f"Evaluation Window: {nav_dates[0] if nav_dates else ''} ~ {nav_dates[-1] if nav_dates else ''}",
                "period_label": f"Evaluation Window: {nav_dates[0] if nav_dates else ''} ~ {nav_dates[-1] if nav_dates else ''} ({len(nav_dates)} trading days)"
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

        out_file = web_output_path or (REPO_ROOT / "web" / "js" / "data" / f"{season_id}.js")
        out_file.parent.mkdir(parents=True, exist_ok=True)
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(f"/**\n * QuantPits-Arena {season_id} Backtest Data Payload\n * Auto-generated by DualTierExporter.export_web_payload\n */\n")
            f.write("window.ARENA_SEASONS_DATA = window.ARENA_SEASONS_DATA || {};\n")
            f.write(f"window.ARENA_SEASONS_DATA[\"{season_id}\"] = ")
            json.dump(web_payload, f, ensure_ascii=False, indent=2)
            f.write(";\n")

        # 6. Auto-sync seasons_index.js
        try:
            self._sync_seasons_index(season_cfg, web_payload)
        except Exception as e:
            print(f"[WARN] Failed to auto-sync seasons_index.js: {e}")

        # 7. Auto-sync web/index.html script tag
        try:
            self._sync_index_html(season_id)
        except Exception as e:
            print(f"[WARN] Failed to auto-sync web/index.html: {e}")

        return out_file

    def _sync_seasons_index(self, season_cfg: Any, web_payload: Dict[str, Any]) -> None:
        """保持 web/js/data/seasons_index.js 自动注册"""
        import re
        from arena.config import REPO_ROOT
        index_file = REPO_ROOT / "web" / "js" / "data" / "seasons_index.js"
        if not index_file.exists():
            return

        content = index_file.read_text(encoding="utf-8")
        season_id = web_payload["meta"]["season_id"]
        if f'id: "{season_id}"' in content or f'id: \'{season_id}\'' in content or f'"id": "{season_id}"' in content:
            return

        # 组装新赛季条目
        meta = web_payload["meta"]
        new_entry = {
            "id": season_id,
            "title": meta.get("season_title", season_id),
            "short_title": meta.get("universe_name", season_id),
            "status": meta.get("status", "ACTIVE"),
            "badge_type": "active" if meta.get("status") == "ACTIVE" else "warning",
            "period": "2026.07 - 2026.08",
            "anchor_date": "2026-07-03",
            "end_date": "2026-08-28",
            "trading_days": meta.get("trading_days", 41),
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
                "anchor_spec": "Parallel Calibration Anchor (2026-07-03 Initiation)",
                "capital_spec": "CNY 500,000 baseline capital with 100-share trading lots",
                "benchmarks_summary": f"Market Index ({meta.get('market_benchmark_name', 'Index')}) + Taotie + Ghost Taotie (100M) + 1,000 Matched Monkeys",
                "execution_flow": "Weekly Rebalance, Monday Open Execution, Daily Marked-to-Market"
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
        html_file = REPO_ROOT / "web" / "index.html"
        if not html_file.exists():
            return

        content = html_file.read_text(encoding="utf-8")
        target_script = f'<script src="js/data/{season_id}.js?v=4.7"></script>'
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




