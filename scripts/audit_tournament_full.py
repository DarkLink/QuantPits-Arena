#!/usr/bin/env python3
"""
scripts/audit_tournament_full.py
================================
全量 54 条路径与 6 大选手的全景工程审计与量化指标核算脚本
"""

import sys
import pickle
import yaml
import hashlib
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from arena.contestants import ContestantRegistry
from arena.calendar import TradingCalendar

RUN_DIR = REPO_ROOT / "runs" / "full_tournament_all_6_contestants"
PUBLIC_DIR = RUN_DIR / "public"
PRIVATE_DIR = RUN_DIR / "private"

# 加载基础产物
nav_df = pd.read_csv(PUBLIC_DIR / "daily_nav_curves.csv")
nav_df["datetime"] = pd.to_datetime(nav_df["datetime"])
nav_df.set_index("datetime", inplace=True)

metrics_df = pd.read_csv(PUBLIC_DIR / "summary_metrics.csv")
trades_df = pd.read_csv(PRIVATE_DIR / "raw_trades.csv")
trades_df["date"] = pd.to_datetime(trades_df["date"])

with open(REPO_ROOT / "artifacts" / "predictions" / "all_contestants_oos.pkl", "rb") as f:
    pred_store = pickle.load(f)

with open(REPO_ROOT / "manifests" / "private" / "alias_map.yaml", "r", encoding="utf-8") as f:
    alias_data = yaml.safe_load(f)

alias_map = {m["private_id"]: m["anonymous_id"] for m in alias_data["mappings"]}
rev_alias_map = {m["anonymous_id"]: m["private_id"] for m in alias_data["mappings"]}

reg = ContestantRegistry()
calendar = TradingCalendar()
cycles = calendar.build_weekly_cycles("2026-07-03", "2026-08-28")

print("=" * 80)
print(" 🔍 PART 1: 选手 ID 映射确认")
print("=" * 80)
for m in alias_data["mappings"]:
    print(f"{m['anonymous_id']:<15} -> {m['private_id']:<25} ({m['anonymous_display_name']})")

print("\n" + "=" * 80)
print(" 🔍 PART 2: Section 3 — Sloth Warm-up / Exposure-length 深度核算")
print("=" * 80)

# 对每个 contestant × animal 计算持仓与交易时序指标
sloth_animals = ["robot", "sloth-1", "sloth-2", "sloth-3", "sloth-4"]
contestants_anon = sorted(list(rev_alias_map.keys()))

sloth_rows = []
for c_anon in contestants_anon:
    c_priv = rev_alias_map[c_anon]
    for anim in sloth_animals:
        col_name = f"{c_anon}_{anim}"
        c_trades = trades_df[(trades_df["contestant_id"] == c_priv) & (trades_df["animal_id"] == anim)]
        
        # 交易统计
        trade_count = len(c_trades)
        buy_trades = c_trades[c_trades["direction"] == "BUY"]
        sell_trades = c_trades[c_trades["direction"] == "SELL"]
        buy_count = len(buy_trades)
        sell_count = len(sell_trades)
        rebalance_dates = c_trades["date"].drop_duplicates().sort_values().tolist()
        rebalance_count = len(rebalance_dates)
        
        first_rebal = rebalance_dates[0].strftime("%Y-%m-%d") if rebalance_count > 0 else "N/A"
        first_pos_date = first_rebal
        
        # 换手额与交易成本
        total_buy_val = buy_trades["value"].sum()
        total_sell_val = sell_trades["value"].sum()
        total_traded_val = total_buy_val + total_sell_val
        turnover = (total_traded_val / 2.0) / 500000.0  # 基准初始本金 500,000
        trans_cost = c_trades["cost"].sum()
        
        # NAV 曲线分析持仓状态
        # 若持仓为空，当天收益率与现金一致。从 trades 计算真实每日股票市值与现金
        # 模拟当日持仓
        daily_dates = nav_df.index
        # 从交易还原每日持仓
        holding_days = 0
        cash_balances = []
        curr_cash = 500000.0
        curr_shares = {}
        
        # 预先按日归集交易
        daily_trades_map = {}
        for d, grp in c_trades.groupby("date"):
            daily_trades_map[pd.to_datetime(d)] = grp
            
        for d in daily_dates:
            if d in daily_trades_map:
                grp = daily_trades_map[d]
                for _, tr in grp.iterrows():
                    inst = tr["instrument"]
                    sh = tr["shares"]
                    val = tr["value"]
                    co = tr["cost"]
                    if tr["direction"] == "BUY":
                        curr_cash -= (val + co)
                        curr_shares[inst] = curr_shares.get(inst, 0.0) + sh
                    else:
                        curr_cash += (val - co)
                        curr_shares[inst] = curr_shares.get(inst, 0.0) - sh
            active_stocks = sum(1 for s in curr_shares.values() if s > 0)
            if active_stocks > 0:
                holding_days += 1
            # 记录现金比例 (以初始 50 万为基准 NAV 的估算)
            nav_val = nav_df.loc[d, col_name] * 500000.0
            cash_balances.append(curr_cash / max(nav_val, 1.0))
            
        days_in_market_ratio = holding_days / len(daily_dates)
        avg_cash_weight = np.mean(cash_balances)
        last_pos_date = daily_dates[-1].strftime("%Y-%m-%d") if holding_days > 0 else "N/A"
        
        sloth_rows.append({
            "contestant": c_anon,
            "animal": anim,
            "first_valid_signal": "2026-07-03",
            "first_pos_date": first_pos_date,
            "first_rebal_date": first_rebal,
            "last_pos_date": last_pos_date,
            "days_with_position": holding_days,
            "days_in_market_ratio": f"{days_in_market_ratio:.1%}",
            "rebal_count": rebalance_count,
            "trade_count": trade_count,
            "buy_count": buy_count,
            "sell_count": sell_count,
            "turnover": f"{turnover:.2f}x",
            "cost_rmb": f"{trans_cost:.1f}",
            "cost_pct": f"{(trans_cost / 500000.0):.2%}",
            "avg_cash_weight": f"{avg_cash_weight:.1%}",
            "final_return": metrics_df[(metrics_df["contestant_id"] == c_anon) & (metrics_df["animal_id"] == anim)]["total_return_pct"].values[0]
        })

sloth_df = pd.DataFrame(sloth_rows)
print(sloth_df[["contestant", "animal", "first_pos_date", "days_with_position", "days_in_market_ratio", "rebal_count", "turnover", "avg_cash_weight", "final_return"]].to_string(index=False))

print("\n" + "=" * 80)
print(" 🔍 PART 3: Section 4 — Sloth Signal Shift 方向与延迟核查 (Spot-check)")
print("=" * 80)

check_cycles = [cycles[1], cycles[4], cycles[6]]  # cycle 1 (07-10/07-13), cycle 4 (07-31/08-03), cycle 6 (08-14/08-17)
for c_anon in ["CONTESTANT_A", "CONTESTANT_B"]:
    print(f"\n--- {c_anon} ---")
    for cyc in check_cycles:
        c_idx = cyc.cycle_idx
        exec_date = cyc.trade_date
        print(f"Cycle {c_idx} | 决策日 (周五): {cyc.decision_date} | 执行日 (周一): {exec_date}")
        for delay in [1, 2, 3, 4]:
            if c_idx < delay:
                print(f"  sloth-{delay}: cycle_idx={c_idx} < delay={delay} -> Cold start (100% Cash / No signal)")
            else:
                src_idx = c_idx - delay
                src_cyc = cycles[src_idx]
                src_signal_date = src_cyc.decision_date
                # 验证是否为过去日期
                is_causal = pd.to_datetime(src_signal_date) < pd.to_datetime(exec_date)
                diff_days = (pd.to_datetime(exec_date) - pd.to_datetime(src_signal_date)).days
                print(f"  sloth-{delay}: source_cycle={src_idx} | source_signal_date={src_signal_date} | delay_days={diff_days}d | Causal={is_causal}")

print("\n" + "=" * 80)
print(" 🔍 PART 4: Section 5 — Koala 完整性与特征分布审计 (All Contestants)")
print("=" * 80)

# 对各选手的预测打分与 Robot/Koala 选股进行深度对比
koala_stats = []
for c_priv, c_anon in alias_map.items():
    scores_dict = pred_store[c_priv]
    all_dates = sorted(list(scores_dict.keys()))
    
    # 统计 45 天打分分布
    scores_list = [scores_dict[d] for d in all_dates]
    
    valid_counts = [s.dropna().count() for s in scores_list]
    unique_counts = [s.dropna().nunique() for s in scores_list]
    std_counts = [s.dropna().std() for s in scores_list]
    nan_ratios = [s.isna().mean() for s in scores_list]
    
    # 检验 Robot 与 Koala 的选股交集 (在 8 个周频决策日)
    overlaps = []
    jaccards = []
    robot_scores = []
    koala_orig_scores = []
    rank_corrs = []
    
    for cyc in cycles:
        d = cyc.decision_date
        if d not in scores_dict:
            continue
        sc = scores_dict[d].dropna()
        
        # Robot 选择 Top 22
        top_robot = set(sc.nlargest(22).index)
        
        # Koala 对得分做 1.0 - norm_rank, 选择 Top 22（即原打分最低的 22 只）
        norm_r = (sc.rank(ascending=True) - 1.0) / (len(sc) - 1.0)
        koala_sc = 1.0 - norm_r
        top_koala = set(koala_sc.nlargest(22).index)
        
        overlap = len(top_robot.intersection(top_koala))
        jaccard = overlap / len(top_robot.union(top_koala))
        overlaps.append(overlap)
        jaccards.append(jaccard)
        
        robot_scores.append(sc.loc[list(top_robot)].mean())
        koala_orig_scores.append(sc.loc[list(top_koala)].mean())
        
        # Rank correlation between original score and koala score
        rc = sc.corr(koala_sc, method="spearman")
        rank_corrs.append(rc)
        
    koala_stats.append({
        "contestant": c_anon,
        "robot_mean_score": f"{np.mean(robot_scores):.4f}",
        "koala_mean_orig_score": f"{np.mean(koala_orig_scores):.4f}",
        "overlap_mean": f"{np.mean(overlaps):.2f}",
        "overlap_max": int(np.max(overlaps)),
        "jaccard_mean": f"{np.mean(jaccards):.3f}",
        "rank_corr": f"{np.mean(rank_corrs):.4f}",
        "valid_univ_med": int(np.median(valid_counts)),
        "unique_score_med": int(np.median(unique_counts)),
        "score_std_med": f"{np.median(std_counts):.4f}",
        "nan_ratio": f"{np.mean(nan_ratios):.2%}"
    })

koala_df = pd.DataFrame(koala_stats)
print(koala_df.to_string(index=False))

print("\n" + "=" * 80)
print(" 🔍 PART 5: Section 7 & 8 — Rabbit / Turtle / Transaction Cost 审计")
print("=" * 80)

anim_order_check = []
for c_anon in contestants_anon:
    c_priv = rev_alias_map[c_anon]
    for anim in ["turtle", "robot", "rabbit-1", "rabbit-2"]:
        col = f"{c_anon}_{anim}"
        c_tr = trades_df[(trades_df["contestant_id"] == c_priv) & (trades_df["animal_id"] == anim)]
        t_count = len(c_tr)
        rebal_count = c_tr["date"].nunique()
        tot_val = c_tr["value"].sum()
        turnover = (tot_val / 2.0) / 500000.0
        tot_cost = c_tr["cost"].sum()
        cost_pct = tot_cost / 500000.0
        
        net_ret = metrics_df[(metrics_df["contestant_id"] == c_anon) & (metrics_df["animal_id"] == anim)]["total_return_pct"].values[0]
        net_ret_val = float(net_ret.replace("%", "")) / 100.0
        gross_ret_val = net_ret_val + cost_pct
        
        anim_order_check.append({
            "contestant": c_anon,
            "animal": anim,
            "rebal_count": rebal_count,
            "trade_count": t_count,
            "turnover": f"{turnover:.2f}x",
            "cost_rmb": f"{tot_cost:.1f}",
            "cost_pct": f"{cost_pct:.2%}",
            "gross_return": f"{gross_ret_val:.2%}",
            "net_return": net_ret
        })

anim_df = pd.DataFrame(anim_order_check)
print(anim_df.to_string(index=False))

print("\n" + "=" * 80)
print(" 🔍 PART 6: Section 9 — Prediction Coverage / Score Health (45 Days)")
print("=" * 80)

score_health = []
for c_priv, c_anon in alias_map.items():
    s_dict = pred_store[c_priv]
    t_days = len(s_dict)
    all_dates = sorted(list(s_dict.keys()))
    
    val_lens = [len(s_dict[d].dropna()) for d in all_dates]
    nan_lens = [s_dict[d].isna().sum() for d in all_dates]
    inf_lens = [np.isinf(s_dict[d]).sum() for d in all_dates]
    tot_lens = [len(s_dict[d]) for d in all_dates]
    unq_lens = [s_dict[d].dropna().nunique() for d in all_dates]
    std_lens = [s_dict[d].dropna().std() for s in [s_dict[d]] for d in all_dates]
    
    score_health.append({
        "contestant_id": c_anon,
        "private_id": c_priv,
        "trading_days": t_days,
        "val_min": np.min(val_lens),
        "val_med": int(np.median(val_lens)),
        "val_max": np.max(val_lens),
        "nan_ratio": f"{np.sum(nan_lens) / np.sum(tot_lens):.2%}",
        "inf_ratio": f"{np.sum(inf_lens) / np.sum(tot_lens):.2%}",
        "unq_score_med": int(np.median(unq_lens)),
        "std_med": f"{np.median(std_lens):.4f}",
        "missing_days": 45 - t_days
    })

sh_df = pd.DataFrame(score_health)
print(sh_df.to_string(index=False))

print("\n" + "=" * 80)
print(" 🔍 PART 7: Section 10 — Artifact / Prediction Output Hash 确认")
print("=" * 80)

for c_priv, c_anon in alias_map.items():
    s_dict = pred_store[c_priv]
    # 计算 prediction 的 sha256
    serialized = pickle.dumps(s_dict)
    p_hash = hashlib.sha256(serialized).hexdigest()[:16]
    c_obj = reg.get_contestant(c_priv)
    
    print(f"[{c_anon}] {c_priv}")
    print(f"  • Training Mode: {c_obj.training_mode}")
    print(f"  • Members Count: {len(c_obj.members)}")
    print(f"  • Prediction Hash: {p_hash}")
    for m in c_obj.members:
        p_path = REPO_ROOT / (m.artifact_path or "")
        p_exists = p_path.exists()
        print(f"    - member: {m.name} | class: {m.model_class} | exists: {p_exists}")
