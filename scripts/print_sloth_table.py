import pandas as pd
import numpy as np

nav_df = pd.read_csv("runs/full_tournament_all_6_contestants/public/daily_nav_curves.csv")
trades_df = pd.read_csv("runs/full_tournament_all_6_contestants/private/raw_trades.csv")
metrics_df = pd.read_csv("runs/full_tournament_all_6_contestants/public/summary_metrics.csv")

nav_df["datetime"] = pd.to_datetime(nav_df["datetime"])
nav_df.set_index("datetime", inplace=True)
trades_df["date"] = pd.to_datetime(trades_df["date"])

alias_map = {
    "QP-20260626-STATIC": "CONTESTANT_A",
    "QP-20260626-CPCV": "CONTESTANT_B",
    "QP-20260612-DIFF": "CONTESTANT_C",
    "QP-20260306-GOOD-PROXY": "CONTESTANT_D",
    "GAT-20250919-F52": "CONTESTANT_E",
    "GAT-20250926-F20": "CONTESTANT_F"
}

rows = []
for p_id, a_id in alias_map.items():
    for anim in ["robot", "sloth-1", "sloth-2", "sloth-3", "sloth-4"]:
        tr = trades_df[(trades_df["contestant_id"] == p_id) & (trades_df["animal_id"] == anim)]
        dates = sorted(tr["date"].drop_duplicates().tolist())
        first_date = dates[0].strftime("%Y-%m-%d") if dates else "N/A"
        rebal_count = len(dates)
        trade_count = len(tr)
        buy_count = len(tr[tr["direction"] == "BUY"])
        sell_count = len(tr[tr["direction"] == "SELL"])
        
        # 统计有持仓的天数
        # 通过该列 NAV 是否与上日完全相等且等于 1.0 来判断是否未入场
        col = f"{a_id}_{anim}"
        series = nav_df[col]
        # 第一天为 2026-07-03 (周五) 1.0
        # 首次发生交易日
        if first_date != "N/A":
            pos_days = (nav_df.index >= pd.to_datetime(first_date)).sum()
        else:
            pos_days = 0
            
        tot_days = len(nav_df)
        ratio = pos_days / tot_days
        
        tot_val = tr["value"].sum()
        turnover = (tot_val / 2.0) / 500000.0
        cost = tr["cost"].sum()
        
        ret = metrics_df[(metrics_df["contestant_id"] == a_id) & (metrics_df["animal_id"] == anim)]["total_return_pct"].values[0]
        
        rows.append({
            "contestant": a_id,
            "animal": anim,
            "first_pos_date": first_date,
            "days_with_pos": pos_days,
            "market_ratio": f"{ratio:.1%}",
            "rebal_cnt": rebal_count,
            "trade_cnt": trade_count,
            "buy_cnt": buy_count,
            "sell_cnt": sell_count,
            "turnover": f"{turnover:.2f}x",
            "cost_rmb": f"{cost:.1f}",
            "net_return": ret
        })

df = pd.DataFrame(rows)
df.to_csv("runs/full_tournament_all_6_contestants/public/reports/sloth_audit_table.csv", index=False)
print(df.to_string(index=False))
