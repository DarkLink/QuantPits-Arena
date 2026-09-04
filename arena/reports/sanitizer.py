"""
arena/reports/sanitizer.py
==========================
双层输出架构与自动化脱敏导出器 (Dual-Tier Output Exporter)
"""

from typing import Dict, List, Any
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


