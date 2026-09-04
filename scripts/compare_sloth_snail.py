#!/usr/bin/env python3
import pandas as pd
from pathlib import Path

run_dir = Path("runs/full_tournament_with_snail")
metrics_df = pd.read_csv(run_dir / "public/summary_metrics.csv")
trades_df = pd.read_csv(run_dir / "private/raw_trades.csv")

print("=" * 85)
print(" 🐌 Sloth vs Snail 对比审计 (45 交易日 / 8 调仓周期)")
print("=" * 85)

from arena.contestants import ContestantRegistry

registry = ContestantRegistry()
contestant_map = {registry.get_anonymous_id(c.contestant_id): c.contestant_id for c in registry.list_contestants()}

contestants = ["CONTESTANT_A", "CONTESTANT_B", "CONTESTANT_C", "CONTESTANT_D", "CONTESTANT_E", "CONTESTANT_F"]
animals = ["robot", "sloth-1", "sloth-2", "sloth-3", "sloth-4", "snail-1", "snail-2", "snail-3", "snail-4"]

for anon_id in contestants:
    real_id = contestant_map[anon_id]
    print(f"\n--- {anon_id} ({real_id}) ---")
    sub_metrics = metrics_df[metrics_df["contestant_id"] == anon_id].set_index("animal_id")
    print(f"{'Animal':10s} | {'Return':8s} | {'MDD':7s} | {'First Pos Date':14s} | {'Trade Cnt':10s} | {'Turnover':11s}")
    print("-" * 77)
    for a in animals:
        ret = sub_metrics.loc[a, "total_return_pct"]
        mdd = sub_metrics.loc[a, "max_drawdown_pct"]
        
        # 从 trades_df 获取首个交易日和交易次数
        sub_trades = trades_df[(trades_df["contestant_id"] == real_id) & (trades_df["animal_id"] == a)]
        trade_cnt = len(sub_trades)
        first_date = sub_trades["date"].min() if trade_cnt > 0 else "None"
        turnover = sub_trades["value"].sum() if trade_cnt > 0 else 0.0
        
        print(f"{a:10s} | {ret:8s} | {mdd:7s} | {str(first_date):14s} | {trade_cnt:10d} | {turnover:11.0f}")

print("\n" + "=" * 85)
