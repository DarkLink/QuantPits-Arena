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
        # 1. 收集日频 NAV 曲线（公开层）
        nav_dict = {}
        summary_rows = []
        matrix_data: Dict[str, Dict[str, float]] = {}

        for (cid, aid), path in results.items():
            anon_cid = registry.get_anonymous_id(cid)
            col_name = f"{anon_cid}_{aid}"

            # 日频 NAV 时序
            s = path.nav_series
            if len(s) > 0:
                nav_dict[col_name] = s

            # 汇总指标
            tot_ret = path.total_return
            mdd = path.max_drawdown
            summary_rows.append({
                "contestant_id": anon_cid,
                "animal_id": aid,
                "total_return_pct": f"{tot_ret * 100:.2f}%",
                "max_drawdown_pct": f"{mdd * 100:.2f}%",
                "final_nav": f"{s.iloc[-1]:.4f}" if len(s) > 0 else "1.0000"
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

        # 写入 public/model_animal_matrix.csv
        pub_matrix_file = self.public_dir / "model_animal_matrix.csv"
        df_matrix = pd.DataFrame(matrix_data).T
        df_matrix.to_csv(pub_matrix_file)

        # 写入 public/reports/leaderboard.md
        self._export_markdown_reports(df_summary, df_matrix)

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
            "public_matrix": pub_matrix_file,
            "private_trades": priv_trades_file
        }

    def _export_markdown_reports(self, df_summary: pd.DataFrame, df_matrix: pd.DataFrame):
        """生成脱敏公开的 Markdown 报告 (无需依赖 tabulate)"""
        def to_md(df: pd.DataFrame, include_index: bool = True) -> str:
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

        # Leaderboard
        lb_file = self.reports_dir / "leaderboard.md"
        with open(lb_file, "w", encoding="utf-8") as f:
            f.write("# QuantPits Graveyard Arena — Leaderboard\n\n")
            f.write(f"Run ID: `{self.run_id}`\n\n")
            f.write(to_md(df_summary, include_index=False))
            f.write("\n")

        # Matrix
        mt_file = self.reports_dir / "model_animal_matrix.md"
        with open(mt_file, "w", encoding="utf-8") as f:
            f.write("# QuantPits Graveyard Arena — Model × Animal Return Matrix\n\n")
            f.write(f"Run ID: `{self.run_id}`\n\n")
            # 转为百分比展示
            map_func = getattr(df_matrix, "map", getattr(df_matrix, "applymap", None))
            df_pct = map_func(lambda v: f"{v * 100:.2f}%" if pd.notnull(v) else "-")
            f.write(to_md(df_pct, include_index=True))
            f.write("\n")
