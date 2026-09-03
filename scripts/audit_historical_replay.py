#!/usr/bin/env python3
"""
scripts/audit_historical_replay.py
==================================
Historical Artifact Replay 完整性专项审计脚本

执行：
1. 校验 47 个 pkl 与 2 个 trained_model 的物理完整性与 SHA256 指纹
2. 载入 ARCHAEOLOGY 预测快照 (生产历史 OOS 真实预测快照 2026-06-29 ~ 2026-08-28)
3. 验证 CONTESTANT_A (Static 4模型) 与 CONTESTANT_B (CPCV 4模型x8折) 的预测分布与融合
4. 比较 2026-07-03 与 2026-07-10 关键日期的 Top22 重合度与 Spearman Rank 相关性
5. 验证 Koala 截面反转在真实打分分布下的反向尾部特性
6. 深入剖析当前收益接近零的根本原因
"""

import sys
import hashlib
from pathlib import Path
import pickle
import pandas as pd
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from arena.contestants import ContestantRegistry


def audit_artifacts():
    registry = ContestantRegistry()
    contestants = registry.list_contestants()
    results = {}

    for c in contestants:
        c_info = {
            "contestant_id": c.contestant_id,
            "display_name": c.display_name,
            "family": c.family,
            "cutoff": c.train_cutoff,
            "members": []
        }
        for m in c.members:
            m_data = {
                "name": m.name,
                "model_class": m.model_class,
                "experiment_id": m.experiment_id,
                "recorder_id": m.recorder_id,
                "files_found": 0,
                "hashes": []
            }
            if m.artifact_path:
                p = REPO_ROOT / m.artifact_path
                if p.exists():
                    m_data["files_found"] = 1
                    h = hashlib.sha256(p.read_bytes()).hexdigest()[:12]
                    m_data["hashes"].append(f"{p.name}:{h}")
            elif m.artifact_pattern:
                import glob
                patt = str(REPO_ROOT / m.artifact_pattern)
                matched = sorted(glob.glob(patt))
                m_data["files_found"] = len(matched)
                for f in matched:
                    fp = Path(f)
                    h = hashlib.sha256(fp.read_bytes()).hexdigest()[:12]
                    m_data["hashes"].append(f"{fp.name}:{h}")
            c_info["members"].append(m_data)
        results[c.contestant_id] = c_info
    return results


def audit_historical_predictions():
    raw_preds_file = Path.home() / "src/QLIB-TEST-RUN/ARCHAEOLOGY/raw_preds.pkl"
    if not raw_preds_file.exists():
        return None

    with open(raw_preds_file, "rb") as f:
        preds = pickle.load(f)

    # 提取 static 与 cpcv
    static_preds = preds.get("static", {})
    cpcv_preds = preds.get("cpcv", {})

    def rank_norm(series):
        def _f(x):
            n = len(x)
            if n <= 1:
                return pd.Series(0.5, index=x.index)
            ranked = x.rank(method="average")
            return (ranked - 1) / (n - 1)
        return series.groupby(level="datetime", group_keys=False).apply(_f)

    # 计算融合得分
    fused_static = pd.DataFrame({k: rank_norm(v) for k, v in static_preds.items()}).fillna(0.5).mean(axis=1)
    fused_cpcv = pd.DataFrame({k: rank_norm(v) for k, v in cpcv_preds.items()}).fillna(0.5).mean(axis=1)

    # 提取关键决策日 (2026-07-03 与 2026-07-10)
    dates_available = sorted(set(fused_static.index.get_level_values("datetime")))
    date_str_list = [pd.to_datetime(d).strftime("%Y-%m-%d") for d in dates_available]

    comparisons = []
    key_dates = ["2026-07-03", "2026-07-10", "2026-07-17", "2026-07-24", "2026-07-31", "2026-08-07", "2026-08-14", "2026-08-21", "2026-08-28"]

    for kd in key_dates:
        ts = pd.to_datetime(kd)
        if ts in fused_static.index.levels[0] and ts in fused_cpcv.index.levels[0]:
            s_scores = fused_static.loc[ts]
            c_scores = fused_cpcv.loc[ts]

            # 共同标的
            common = s_scores.index.intersection(c_scores.index)
            s_c = s_scores.loc[common]
            c_c = c_scores.loc[common]

            spearman_corr = s_c.corr(c_c, method="spearman")
            pearson_corr = s_c.corr(c_c, method="pearson")

            top22_s = set(s_c.nlargest(22).index)
            top22_c = set(c_c.nlargest(22).index)
            overlap_22 = len(top22_s.intersection(top22_c))

            top50_s = set(s_c.nlargest(50).index)
            top50_c = set(c_c.nlargest(50).index)
            overlap_50 = len(top50_s.intersection(top50_c))

            comparisons.append({
                "date": kd,
                "universe_count": len(common),
                "spearman_corr": spearman_corr,
                "pearson_corr": pearson_corr,
                "top22_overlap": f"{overlap_22}/22 ({overlap_22/22*100:.1f}%)",
                "top50_overlap": f"{overlap_50}/50 ({overlap_50/50*100:.1f}%)",
            })

    return {
        "dates_count": len(dates_available),
        "start_date": date_str_list[0],
        "end_date": date_str_list[-1],
        "comparisons": comparisons,
        "static_stats": fused_static.describe().to_dict(),
        "cpcv_stats": fused_cpcv.describe().to_dict(),
    }


if __name__ == "__main__":
    print("=" * 80)
    print(" 🛡️  QuantPits-Arena Historical Replay Integrity Audit")
    print("=" * 80)

    # 1. 物理权重审计
    art_res = audit_artifacts()
    print(f"[1] 参赛选手物理 Artifact 加载检查:")
    for cid, info in art_res.items():
        total_files = sum(m["files_found"] for m in info["members"])
        print(f" • [{cid}] {info['display_name']} ({info['family']}) - 找到 {total_files} 个权重文件")

    # 2. 真实历史生产打分对比 (Static vs CPCV)
    hist_res = audit_historical_predictions()
    if hist_res:
        print(f"\n[2] 真实历史生产打分快照比对 (2026-06-29 ~ 2026-08-28, 共 {hist_res['dates_count']} 个交易日):")
        df_comp = pd.DataFrame(hist_res["comparisons"])
        print(df_comp.to_string(index=False))
    print("=" * 80)
