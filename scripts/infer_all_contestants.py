#!/usr/bin/env python3
"""
scripts/infer_all_contestants.py
================================
全量参赛选手特征前向推理与权威预测库生成工具

为本 repo artifacts/models/ 中的全部模型：
- CONTESTANT_A (06-26 Static)
- CONTESTANT_B (06-26 CPCV)
- CONTESTANT_C (06-12 Ensemble)
- CONTESTANT_D (03-06 Ensemble)
- CONTESTANT_E (GAT 52-feat)
- CONTESTANT_F (GAT 20-feat)

依据各自独立的 workflow YAML 自动构建精确匹配的 Qlib 数据集，
批量执行模型推理并按各 Manifest 规则完成集成融合，
最终持久化保存至 artifacts/predictions/all_contestants_oos.pkl。
"""

import os
import sys
import pickle
import yaml
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from arena.contestants import ContestantRegistry
from arena.contestants.adapters.base import rank_norm_equal_fusion, rank_norm_score

OOS_START = "2026-06-29"
OOS_END = "2026-08-28"
FIT_START = "2017-06-27"
FIT_END = "2022-06-26"
VALID_START = "2022-06-27"
VALID_END = "2024-06-26"

DATASET_CACHE: Dict[str, Any] = {}


def build_qlib_dataset(yaml_path: Path):
    """基于 workflow YAML 构建 Qlib 数据集 (自动剔除 OOS 时的 DropnaLabel)"""
    import qlib
    from qlib.utils import init_instance_by_config

    with open(yaml_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    dh = cfg.get("data_handler_config", {})
    dh["start_time"] = FIT_START
    dh["end_time"] = OOS_END
    dh["fit_start_time"] = FIT_START
    dh["fit_end_time"] = FIT_END
    dh["instruments"] = "csirun300"

    ds_cfg = cfg["task"]["dataset"]
    segs = ds_cfg["kwargs"]["segments"]
    segs["train"] = [FIT_START, FIT_END]
    segs["valid"] = [VALID_START, VALID_END]
    segs["test"] = [OOS_START, OOS_END]
    if "pretrain" in segs:
        segs["pretrain"] = [FIT_START, FIT_END]
    if "pretrain_validation" in segs:
        segs["pretrain_validation"] = [VALID_START, VALID_END]

    # 针对 OOS 阶段：剔除 DropnaLabel 避免 unlabeled 数据被静默清空
    hk = ds_cfg["kwargs"]["handler"]["kwargs"]
    lp = hk.get("learn_processors", [])
    hk["learn_processors"] = [
        p for p in lp
        if (p.get("class") if isinstance(p, dict) else p) != "DropnaLabel"
    ]

    return init_instance_by_config(ds_cfg)


def get_dataset_for_yaml(rel_yaml_path: str):
    """根据 yaml 路径缓存并复用 Dataset 对象"""
    if rel_yaml_path not in DATASET_CACHE:
        yp = REPO_ROOT / rel_yaml_path
        if not yp.exists():
            raise FileNotFoundError(f"未找到 workflow yaml 配置文件: {yp}")
        print(f"  • 构建模型专属数据集: {yp.name}...")
        DATASET_CACHE[rel_yaml_path] = build_qlib_dataset(yp)
        print(f"  ✔ {yp.name} 数据集构建完成！")
    return DATASET_CACHE[rel_yaml_path]


def fuse_dict(sub_dict: Dict[str, pd.Series]) -> pd.Series:
    norm_dict = {}
    for k, s in sub_dict.items():
        def _norm(x):
            n = len(x)
            if n <= 1:
                return pd.Series(0.5, index=x.index)
            ranked = x.rank(method="average")
            return (ranked - 1.0) / (n - 1.0)
        norm_dict[k] = s.groupby(level="datetime", group_keys=False).apply(_norm)
    df = pd.DataFrame(norm_dict).fillna(0.5)
    return df.mean(axis=1)


def to_date_dict(fused: pd.Series) -> Dict[str, pd.Series]:
    res = {}
    for dt, group in fused.groupby(level="datetime"):
        d_str = pd.to_datetime(dt).strftime("%Y-%m-%d")
        s = group.droplevel("datetime")
        res[d_str] = s
    return res


def flatten_rnn(model):
    try:
        if hasattr(model, "LSTM_model") and hasattr(model.LSTM_model, "flatten_parameters"):
            model.LSTM_model.flatten_parameters()
        if hasattr(model, "GRU_model") and hasattr(model.GRU_model, "flatten_parameters"):
            model.GRU_model.flatten_parameters()
        if hasattr(model, "rnn") and hasattr(model.rnn, "flatten_parameters"):
            model.rnn.flatten_parameters()
    except Exception:
        pass


def main():
    print("=" * 80)
    print(" 🚀 QuantPits-Arena 全模型前向推理与预测库生成 (All 6 Contestants)")
    print("=" * 80)

    import qlib
    qlib.init(provider_uri="~/.qlib/qlib_data/cn_data", region="cn")

    pred_dir = REPO_ROOT / "artifacts" / "predictions"
    pred_dir.mkdir(parents=True, exist_ok=True)
    out_file = pred_dir / "all_contestants_oos.pkl"

    all_scores: Dict[str, Dict[str, pd.Series]] = {}

    # 1. 载入已有高精生产历史快照 (Static & CPCV)
    archaeology_preds = Path.home() / "src/QLIB-TEST-RUN/ARCHAEOLOGY/raw_preds.pkl"
    if archaeology_preds.exists():
        print(f"[1/5] 载入历史高精生产快照 (Static & CPCV)...")
        with open(archaeology_preds, "rb") as f:
            arch_data = pickle.load(f)

        fused_static = fuse_dict(arch_data["static"])
        fused_cpcv = fuse_dict(arch_data["cpcv"])

        all_scores["QP-20260626-STATIC"] = to_date_dict(fused_static)
        all_scores["QP-20260626-CPCV"] = to_date_dict(fused_cpcv)
        print(f"  ✔ CONTESTANT_A (Static 06-26): 已就绪 {len(all_scores['QP-20260626-STATIC'])} 天真实打分")
        print(f"  ✔ CONTESTANT_B (CPCV 06-26): 已就绪 {len(all_scores['QP-20260626-CPCV'])} 天真实打分")

    reg = ContestantRegistry()

    # 2. 推理 CONTESTANT_C (06-12 Ensemble)
    print("\n[2/5] 执行 CONTESTANT_C (06-12 Ensemble) 前向推理...")
    c_diff = reg.get_contestant("QP-20260612-DIFF")
    if c_diff:
        sub_preds = {}
        for m in c_diff.members:
            p = REPO_ROOT / m.artifact_path
            if p.exists() and m.workflow_yaml:
                print(f"  • 推理成员: {m.name} ({m.model_class})")
                try:
                    ds = get_dataset_for_yaml(m.workflow_yaml)
                    with open(p, "rb") as f:
                        model = pickle.load(f)
                    flatten_rnn(model)
                    pred = model.predict(ds)
                    if isinstance(pred, pd.DataFrame):
                        pred = pred.iloc[:, 0]
                    sub_preds[m.name] = pred
                    print(f"    ✔ {m.name} 推理成功，产出 {len(pred)} 行预测！")
                except Exception as e:
                    print(f"    ✖ 成员 {m.name} 推理异常: {e}")
        if sub_preds:
            fused_diff = fuse_dict(sub_preds)
            all_scores["QP-20260612-DIFF"] = to_date_dict(fused_diff)
            print(f"  ✔ CONTESTANT_C 成功生成 {len(all_scores['QP-20260612-DIFF'])} 天融合打分！")

    # 3. 推理 CONTESTANT_D (03-06 Ensemble)
    print("\n[3/5] 执行 CONTESTANT_D (03-06 Ensemble) 前向推理...")
    c_good = reg.get_contestant("QP-20260306-GOOD-PROXY")
    if c_good:
        sub_preds = {}
        for m in c_good.members:
            p = REPO_ROOT / m.artifact_path
            if p.exists() and m.workflow_yaml:
                print(f"  • 推理成员: {m.name} ({m.model_class})")
                try:
                    ds = get_dataset_for_yaml(m.workflow_yaml)
                    with open(p, "rb") as f:
                        model = pickle.load(f)
                    flatten_rnn(model)
                    pred = model.predict(ds)
                    if isinstance(pred, pd.DataFrame):
                        pred = pred.iloc[:, 0]
                    sub_preds[m.name] = pred
                    print(f"    ✔ {m.name} 推理成功，产出 {len(pred)} 行预测！")
                except Exception as e:
                    print(f"    ✖ 成员 {m.name} 推理异常: {e}")
        if sub_preds:
            fused_good = fuse_dict(sub_preds)
            all_scores["QP-20260306-GOOD-PROXY"] = to_date_dict(fused_good)
            print(f"  ✔ CONTESTANT_D 成功生成 {len(all_scores['QP-20260306-GOOD-PROXY'])} 天融合打分！")

    # 4. 推理 CONTESTANT_E (GAT 52-feat) & CONTESTANT_F (GAT 20-feat)
    print("\n[4/5] 执行 GAT 图网络模型前向推理 (CONTESTANT_E & F)...")
    for gid in ["GAT-20250919-F52", "GAT-20250926-F20"]:
        c_gat = reg.get_contestant(gid)
        if c_gat and c_gat.members:
            m = c_gat.members[0]
            p = REPO_ROOT / m.artifact_path
            if p.exists() and m.workflow_yaml:
                print(f"  • 推理 GAT: {gid} ({m.name})")
                try:
                    ds = get_dataset_for_yaml(m.workflow_yaml)
                    with open(p, "rb") as f:
                        model = pickle.load(f)
                    flatten_rnn(model)
                    pred = model.predict(ds)
                    if isinstance(pred, pd.DataFrame):
                        pred = pred.iloc[:, 0]
                    fused_gat = fuse_dict({m.name: pred})
                    all_scores[gid] = to_date_dict(fused_gat)
                    print(f"    ✔ {gid} 成功生成 {len(all_scores[gid])} 天打分！")
                except Exception as e:
                    print(f"    [WARN] {gid} 推理跳过 (依赖旧版包装器): {e}")

    # 5. 持久化至权威预测库
    print("\n[5/5] 保存全量权威预测库...")
    with open(out_file, "wb") as f:
        pickle.dump(all_scores, f)

    print("\n" + "=" * 80)
    print(f" ✅ 权威全量预测库成功生成并保存至: {out_file.relative_to(REPO_ROOT)}")
    print(f"    覆盖参赛选手: {list(all_scores.keys())}")
    for cid, s_dict in all_scores.items():
        print(f"      • [{cid}]: 涵盖 {len(s_dict)} 个交易日打分")
    print("=" * 80)


if __name__ == "__main__":
    main()
