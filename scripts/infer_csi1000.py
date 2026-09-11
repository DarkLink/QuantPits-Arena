#!/usr/bin/env python3
"""
scripts/infer_csi1000.py
========================
Batch feature extraction and model inference for all 6 candidate models on the CSI 1000 stock universe.
Stores fused rank-normalized predictions in artifacts/predictions/csi1000_contestants_oos.pkl.
"""

import os
import sys
import glob
import time
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

OOS_START = "2026-06-29"
OOS_END = "2026-08-28"
FIT_START = "2026-04-01"  # 60-day rolling lookback for indicators
FIT_END = "2026-07-03"
MARKET = "csi1000"

DATASET_CACHE: Dict[str, Any] = {}


def build_qlib_dataset(yaml_path: Path):
    """Construct Qlib dataset for CSI 1000 without full historical retrain."""
    from qlib.utils import init_instance_by_config

    with open(yaml_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    dh = cfg.get("data_handler_config", {})
    dh["start_time"] = FIT_START
    dh["end_time"] = OOS_END
    dh["fit_start_time"] = FIT_START
    dh["fit_end_time"] = FIT_END
    dh["instruments"] = MARKET

    ds_cfg = cfg["task"]["dataset"]
    segs = ds_cfg["kwargs"]["segments"]
    segs["train"] = [FIT_START, FIT_END]
    segs["valid"] = [FIT_END, "2026-07-10"]
    segs["test"] = [OOS_START, OOS_END]
    if "pretrain" in segs:
        segs["pretrain"] = [FIT_START, FIT_END]
    if "pretrain_validation" in segs:
        segs["pretrain_validation"] = [FIT_END, "2026-07-10"]

    # Remove DropnaLabel so unlabelled testing horizon is retained
    hk = ds_cfg["kwargs"]["handler"]["kwargs"]
    lp = hk.get("learn_processors", [])
    hk["learn_processors"] = [
        p for p in lp
        if (p.get("class") if isinstance(p, dict) else p) != "DropnaLabel"
    ]

    return init_instance_by_config(ds_cfg)


def get_dataset_for_yaml(rel_yaml_path: str):
    if rel_yaml_path not in DATASET_CACHE:
        yp = REPO_ROOT / rel_yaml_path
        if not yp.exists():
            raise FileNotFoundError(f"Missing workflow config: {yp}")
        print(f"  • Building Qlib dataset for {yp.name} on {MARKET}...")
        t0 = time.time()
        DATASET_CACHE[rel_yaml_path] = build_qlib_dataset(yp)
        print(f"  ✔ {yp.name} dataset ready in {time.time() - t0:.2f}s")
    return DATASET_CACHE[rel_yaml_path]


def rank_norm_series(s: pd.Series) -> pd.Series:
    def _norm(x):
        n = len(x)
        if n <= 1:
            return pd.Series(0.5, index=x.index)
        ranked = x.rank(method="average")
        return (ranked - 1.0) / (n - 1.0)
    return s.groupby(level="datetime", group_keys=False).apply(_norm)


def fuse_dict(sub_dict: Dict[str, pd.Series]) -> pd.Series:
    norm_dict = {k: rank_norm_series(s) for k, s in sub_dict.items()}
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


def load_model_file(artifact_path: Path):
    try:
        with open(artifact_path, "rb") as f:
            return pickle.load(f)
    except Exception:
        import torch
        return torch.load(artifact_path, map_location="cpu", weights_only=False)


def main():
    print("=" * 80)
    print(" 🚀 QuantPits-Arena CSI 1000 Full Model Inference (All 6 Contestants)")
    print(f"    Universe: {MARKET} (1,000 Stocks) | Horizon: {OOS_START} ~ {OOS_END}")
    print("=" * 80)

    import qlib
    qlib_uri = str(Path.home() / ".qlib" / "qlib_data" / "cn_data")
    print(f"[*] Initializing Qlib: {qlib_uri}...")
    qlib.init(provider_uri=qlib_uri, region="cn")

    reg = ContestantRegistry()
    pred_dir = REPO_ROOT / "artifacts" / "predictions"
    pred_dir.mkdir(parents=True, exist_ok=True)
    out_file = pred_dir / "csi1000_contestants_oos.pkl"

    all_scores: Dict[str, Dict[str, pd.Series]] = {}

    # 1. CONTESTANT_A: Static Ensemble (QP-20260626-STATIC)
    print("\n[1/6] Running CONTESTANT_A (QP-20260626-STATIC)...")
    cA = reg.get_contestant("QP-20260626-STATIC")
    sub_preds_A = {}
    for m in cA.members:
        p = REPO_ROOT / m.artifact_path
        if p.exists() and m.workflow_yaml:
            print(f"  • Member: {m.name} ({m.model_class})")
            ds = get_dataset_for_yaml(m.workflow_yaml)
            model = load_model_file(p)
            flatten_rnn(model)
            pred = model.predict(ds)
            if isinstance(pred, pd.DataFrame):
                pred = pred.iloc[:, 0]
            sub_preds_A[m.name] = pred
            print(f"    ✔ {m.name}: {len(pred)} rows predicted")
    fused_A = fuse_dict(sub_preds_A)
    date_dict_A = to_date_dict(fused_A)
    all_scores["QP-20260626-STATIC"] = date_dict_A
    all_scores["CONTESTANT_A"] = date_dict_A
    print(f"  ✔ CONTESTANT_A ready: {len(date_dict_A)} trading dates")

    # 2. CONTESTANT_B: CPCV Ensemble (QP-20260626-CPCV)
    print("\n[2/6] Running CONTESTANT_B (QP-20260626-CPCV, 8-fold CV)...")
    cB = reg.get_contestant("QP-20260626-CPCV")
    sub_preds_B = {}
    for m in cB.members:
        if not m.artifact_pattern or not m.workflow_yaml:
            continue
        print(f"  • Member: {m.name} ({m.model_class}, pattern: {m.artifact_pattern})")
        ds = get_dataset_for_yaml(m.workflow_yaml)
        fold_files = sorted(glob.glob(str(REPO_ROOT / m.artifact_pattern)))
        print(f"    Found {len(fold_files)} fold models")
        fold_preds = []
        for fp in fold_files:
            model = load_model_file(Path(fp))
            flatten_rnn(model)
            p = model.predict(ds)
            if isinstance(p, pd.DataFrame):
                p = p.iloc[:, 0]
            fold_preds.append(p)
        if fold_preds:
            member_mean = pd.concat(fold_preds, axis=1).mean(axis=1)
            sub_preds_B[m.name] = member_mean
            print(f"    ✔ {m.name} aggregated: {len(member_mean)} rows")
    fused_B = fuse_dict(sub_preds_B)
    date_dict_B = to_date_dict(fused_B)
    all_scores["QP-20260626-CPCV"] = date_dict_B
    all_scores["CONTESTANT_B"] = date_dict_B
    print(f"  ✔ CONTESTANT_B ready: {len(date_dict_B)} trading dates")

    # 3. CONTESTANT_C: Different Ensemble (QP-20260612-DIFF)
    print("\n[3/6] Running CONTESTANT_C (QP-20260612-DIFF)...")
    cC = reg.get_contestant("QP-20260612-DIFF")
    sub_preds_C = {}
    for m in cC.members:
        p = REPO_ROOT / m.artifact_path
        if p.exists() and m.workflow_yaml:
            print(f"  • Member: {m.name} ({m.model_class})")
            ds = get_dataset_for_yaml(m.workflow_yaml)
            model = load_model_file(p)
            flatten_rnn(model)
            pred = model.predict(ds)
            if isinstance(pred, pd.DataFrame):
                pred = pred.iloc[:, 0]
            sub_preds_C[m.name] = pred
            print(f"    ✔ {m.name}: {len(pred)} rows predicted")
    fused_C = fuse_dict(sub_preds_C)
    date_dict_C = to_date_dict(fused_C)
    all_scores["QP-20260612-DIFF"] = date_dict_C
    all_scores["CONTESTANT_C"] = date_dict_C
    print(f"  ✔ CONTESTANT_C ready: {len(date_dict_C)} trading dates")

    # 4. CONTESTANT_D: Good Model Proxy (QP-20260306-GOOD-PROXY)
    print("\n[4/6] Running CONTESTANT_D (QP-20260306-GOOD-PROXY)...")
    cD = reg.get_contestant("QP-20260306-GOOD-PROXY")
    sub_preds_D = {}
    for m in cD.members:
        p = REPO_ROOT / m.artifact_path
        if p.exists() and m.workflow_yaml:
            print(f"  • Member: {m.name} ({m.model_class})")
            ds = get_dataset_for_yaml(m.workflow_yaml)
            model = load_model_file(p)
            flatten_rnn(model)
            pred = model.predict(ds)
            if isinstance(pred, pd.DataFrame):
                pred = pred.iloc[:, 0]
            sub_preds_D[m.name] = pred
            print(f"    ✔ {m.name}: {len(pred)} rows predicted")
    fused_D = fuse_dict(sub_preds_D)
    date_dict_D = to_date_dict(fused_D)
    all_scores["QP-20260306-GOOD-PROXY"] = date_dict_D
    all_scores["CONTESTANT_D"] = date_dict_D
    print(f"  ✔ CONTESTANT_D ready: {len(date_dict_D)} trading dates")

    # 5. CONTESTANT_E: GAT 52-feat (GAT-20250919-F52)
    print("\n[5/6] Running CONTESTANT_E (GAT-20250919-F52)...")
    cE = reg.get_contestant("GAT-20250919-F52")
    if cE and cE.members:
        m = cE.members[0]
        p = REPO_ROOT / m.artifact_path
        if p.exists() and m.workflow_yaml:
            print(f"  • Member: {m.name}")
            ds = get_dataset_for_yaml(m.workflow_yaml)
            model = load_model_file(p)
            flatten_rnn(model)
            pred = model.predict(ds)
            if isinstance(pred, pd.DataFrame):
                pred = pred.iloc[:, 0]
            fused_E = rank_norm_series(pred)
            date_dict_E = to_date_dict(fused_E)
            all_scores["GAT-20250919-F52"] = date_dict_E
            all_scores["CONTESTANT_E"] = date_dict_E
            print(f"  ✔ CONTESTANT_E ready: {len(date_dict_E)} trading dates")

    # 6. CONTESTANT_F: GAT 20-feat (GAT-20250926-F20)
    print("\n[6/6] Running CONTESTANT_F (GAT-20250926-F20)...")
    cF = reg.get_contestant("GAT-20250926-F20")
    if cF and cF.members:
        m = cF.members[0]
        p = REPO_ROOT / m.artifact_path
        if p.exists() and m.workflow_yaml:
            print(f"  • Member: {m.name}")
            ds = get_dataset_for_yaml(m.workflow_yaml)
            model = load_model_file(p)
            flatten_rnn(model)
            pred = model.predict(ds)
            if isinstance(pred, pd.DataFrame):
                pred = pred.iloc[:, 0]
            fused_F = rank_norm_series(pred)
            date_dict_F = to_date_dict(fused_F)
            all_scores["GAT-20250926-F20"] = date_dict_F
            all_scores["CONTESTANT_F"] = date_dict_F
            print(f"  ✔ CONTESTANT_F ready: {len(date_dict_F)} trading dates")

    # Save to file
    with open(out_file, "wb") as f:
        pickle.dump(all_scores, f)

    print("\n" + "=" * 80)
    print(f" ✅ CSI 1000 Prediction Store successfully generated:")
    print(f"    Path: {out_file.relative_to(REPO_ROOT)}")
    print(f"    Contestants covered: {list(all_scores.keys())}")
    for k in ["CONTESTANT_A", "CONTESTANT_B", "CONTESTANT_C", "CONTESTANT_D", "CONTESTANT_E", "CONTESTANT_F"]:
        if k in all_scores:
            print(f"      • {k}: {len(all_scores[k])} dates, sample day has {len(next(iter(all_scores[k].values())))} stocks")
    print("=" * 80)


if __name__ == "__main__":
    main()
