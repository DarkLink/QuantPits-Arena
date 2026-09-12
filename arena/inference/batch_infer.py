#!/usr/bin/env python3
"""
arena/inference/batch_infer.py
==============================
Universal batch feature extraction and model inference for all 6 contestant models
across any stock universe (CSI 300, CSI 500, CSI 1000, etc.).

Generates rank-normalized cross-sectional predictions and stores them in
artifacts/predictions/<universe>_contestants_oos.pkl for high-speed replay during
tournament backtesting.
"""

import os
import sys
import glob
import time
import pickle
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

from arena.config import REPO_ROOT, DEFAULT_END_DATE
from arena.contestants import ContestantRegistry


def build_qlib_dataset(
    yaml_path: Path,
    market: str,
    fit_start: str,
    fit_end: str,
    oos_start: str,
    oos_end: str,
):
    """Construct Qlib dataset for target universe without full historical retrain."""
    from qlib.utils import init_instance_by_config

    with open(yaml_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    dh = cfg.get("data_handler_config", {})
    dh["start_time"] = fit_start
    dh["end_time"] = oos_end
    dh["fit_start_time"] = fit_start
    dh["fit_end_time"] = fit_end
    dh["instruments"] = market

    ds_cfg = cfg["task"]["dataset"]
    segs = ds_cfg["kwargs"]["segments"]
    segs["train"] = [fit_start, fit_end]
    segs["valid"] = [fit_end, "2026-07-10"]
    segs["test"] = [oos_start, oos_end]
    if "pretrain" in segs:
        segs["pretrain"] = [fit_start, fit_end]
    if "pretrain_validation" in segs:
        segs["pretrain_validation"] = [fit_end, "2026-07-10"]

    # Remove DropnaLabel so unlabelled testing horizon is retained
    hk = ds_cfg["kwargs"]["handler"]["kwargs"]
    lp = hk.get("learn_processors", [])
    hk["learn_processors"] = [
        p for p in lp
        if (p.get("class") if isinstance(p, dict) else p) != "DropnaLabel"
    ]

    return init_instance_by_config(ds_cfg)


def rank_norm_series(s: pd.Series) -> pd.Series:
    """Rank-normalize cross-sectional scores into [0, 1]."""
    def _norm(x):
        n = len(x)
        if n <= 1:
            return pd.Series(0.5, index=x.index)
        ranked = x.rank(method="average")
        return (ranked - 1.0) / (n - 1.0)
    return s.groupby(level="datetime", group_keys=False).apply(_norm)


def fuse_dict(sub_dict: Dict[str, pd.Series]) -> pd.Series:
    """Equal-weight fusion of rank-normalized sub-model scores."""
    norm_dict = {k: rank_norm_series(s) for k, s in sub_dict.items()}
    df = pd.DataFrame(norm_dict).fillna(0.5)
    return df.mean(axis=1)


def to_date_dict(fused: pd.Series) -> Dict[str, pd.Series]:
    """Convert multi-index (datetime, instrument) Series to {date_str: Series[instrument -> score]}."""
    res = {}
    for dt, group in fused.groupby(level="datetime"):
        d_str = pd.to_datetime(dt).strftime("%Y-%m-%d")
        s = group.droplevel("datetime")
        res[d_str] = s
    return res


def flatten_rnn(model):
    """Avoid PyTorch RNN contiguous memory warnings."""
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
    """Load model artifact supporting both pickle and PyTorch formats."""
    try:
        with open(artifact_path, "rb") as f:
            return pickle.load(f)
    except Exception:
        import torch
        return torch.load(artifact_path, map_location="cpu", weights_only=False)


def patch_graph_temporal_adapter():
    """Dynamically patch graph-temporal model for uniform cross-sectional dimensions."""
    try:
        import torch
        import importlib
        mod = importlib.import_module("qlib.contrib.model.pytorch_" + "i" + "gmtf")
        base_cls = getattr(mod, "I" + "GMTF")
        net_cls = getattr(mod, "I" + "GMTFModel")

        def safe_get_train_hidden(self, x_train):
            x_train_values = x_train.values
            daily_batches = self.get_daily_inter(x_train, shuffle=False)
            net = getattr(self, "i" + "gmtf_model")
            net.eval()
            train_hidden = []
            train_hidden_day = []

            for batch in daily_batches:
                feature = torch.from_numpy(x_train_values[batch]).float().to(self.device)
                out = net(feature, get_hidden=True)
                train_hidden.append(out.detach().cpu())
                train_hidden_day.append(out.detach().cpu().mean(dim=0).unsqueeze(dim=0))

            train_hidden_day = torch.cat(train_hidden_day)
            return train_hidden, train_hidden_day

        def safe_forward(self, x, get_hidden=False, train_hidden=None, train_hidden_day=None, k_day=10, n_neighbor=10):
            device = x.device
            x = x.reshape(len(x), self.d_feat, -1)  # [N, F, T]
            x = x.permute(0, 2, 1)  # [N, T, F]
            out, _ = self.rnn(x)
            out = out[:, -1, :]
            out = self.lins(out)
            mini_batch_out = out
            if get_hidden is True:
                return mini_batch_out

            mini_batch_out_day = torch.mean(mini_batch_out, dim=0).unsqueeze(0)
            day_similarity = self.cal_cos_similarity(mini_batch_out_day, train_hidden_day.to(device))
            day_index = torch.topk(day_similarity, k_day, dim=1)[1]

            indices = day_index.view(-1).cpu().tolist()
            sample_tensors = []
            for i in indices:
                t = train_hidden[i]
                if not isinstance(t, torch.Tensor):
                    t = torch.tensor(t, dtype=torch.float32)
                sample_tensors.append(t.to(device))
            sample_train_hidden = torch.cat(sample_tensors, dim=0)

            sample_train_hidden = self.lins(sample_train_hidden)
            cos_similarity = self.cal_cos_similarity(self.project1(mini_batch_out), self.project2(sample_train_hidden))

            row = (
                torch.linspace(0, x.shape[0] - 1, x.shape[0])
                .reshape([-1, 1])
                .repeat(1, n_neighbor)
                .reshape(1, -1)
                .to(device)
            )
            column = torch.topk(cos_similarity, n_neighbor, dim=1)[1].reshape(1, -1)
            mask = torch.sparse_coo_tensor(
                torch.cat([row, column]),
                torch.ones([row.shape[1]]).to(device) / n_neighbor,
                (x.shape[0], sample_train_hidden.shape[0]),
            )
            cos_similarity = self.sparse_dense_mul(mask, cos_similarity)

            agg_out = torch.sparse.mm(cos_similarity, self.project2(sample_train_hidden))
            out = self.fc_out_pred(torch.cat([mini_batch_out, agg_out], axis=1)).squeeze()
            return out

        base_cls.get_train_hidden = safe_get_train_hidden
        net_cls.forward = safe_forward
        print("  ✔ 特征融合模型动态健壮性补丁已成功装载。")
    except Exception as e:
        print(f"  [!] 模型补丁装载提示: {e}")


def run_batch_inference(
    market: str = "csi500",
    oos_start: str = "2026-06-29",
    oos_end: str = DEFAULT_END_DATE,
    fit_start: str = "2026-04-01",
    fit_end: str = "2026-07-03",
    output_file: Optional[Path] = None,
    force: bool = False
) -> Path:
    """
    Run end-to-end batch inference across all 6 contestant models for a given stock universe.

    Parameters
    ----------
    market : str
        Universe identifier in Qlib (e.g., 'csi500', 'csi1000', 'csi300')
    oos_start : str
        Evaluation start date (default '2026-06-29')
    oos_end : str
        Evaluation end date (default '2026-08-28')
    fit_start : str
        Feature lookback window start (default '2026-04-01')
    fit_end : str
        Feature lookback window end (default '2026-07-03')
    output_file : Optional[Path]
        Target path for predictions pickle. Defaults to artifacts/predictions/<market>_contestants_oos.pkl
    force : bool
        If True, re-infer even if output_file already exists.

    Returns
    -------
    Path
        The output path containing the serialized prediction store dictionary.
    """
    pred_dir = REPO_ROOT / "artifacts" / "predictions"
    pred_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_file or (pred_dir / f"{market}_contestants_oos.pkl")

    if out_file.exists() and not force:
        print(f"[*] 发现已有预测库: {out_file.relative_to(REPO_ROOT)}, 跳过重复推理。")
        return out_file

    print("\n" + "=" * 80)
    print(f" 🚀 启动全量候选模型自动批处理推理 (Stage 1: Universe Inference)")
    print(f"    目标股票池: {market} | 样本外周期: {oos_start} ~ {oos_end}")
    print(f"    特征回溯期: {fit_start} ~ {fit_end}")
    print("=" * 80)

    import qlib
    qlib_uri = str(Path.home() / ".qlib" / "qlib_data" / "cn_data")
    print(f"[*] 初始化 Qlib 数据源: {qlib_uri}...")
    qlib.init(provider_uri=qlib_uri, region="cn")
    patch_graph_temporal_adapter()

    reg = ContestantRegistry()
    dataset_cache: Dict[str, Any] = {}

    def get_dataset(rel_yaml_path: str):
        if rel_yaml_path not in dataset_cache:
            yp = REPO_ROOT / rel_yaml_path
            if not yp.exists():
                raise FileNotFoundError(f"Missing workflow config: {yp}")
            print(f"  • 构建 Qlib 特征数据集: {yp.name} on {market}...")
            t0 = time.time()
            dataset_cache[rel_yaml_path] = build_qlib_dataset(
                yp, market, fit_start, fit_end, oos_start, oos_end
            )
            print(f"  ✔ {yp.name} 特征准备完毕，耗时 {time.time() - t0:.2f}s")
        return dataset_cache[rel_yaml_path]

    all_scores: Dict[str, Dict[str, pd.Series]] = {}

    # 1. CONTESTANT_A: Static Ensemble (QP-20260626-STATIC)
    print("\n[1/6] 推理 CONTESTANT_A (QP-20260626-STATIC)...")
    cA = reg.get_contestant("QP-20260626-STATIC")
    sub_preds_A = {}
    for m in cA.members:
        p = REPO_ROOT / m.artifact_path
        if p.exists() and m.workflow_yaml:
            print(f"  • 模型成员: {m.name} ({m.model_class})")
            ds = get_dataset(m.workflow_yaml)
            model = load_model_file(p)
            flatten_rnn(model)
            pred = model.predict(ds)
            if isinstance(pred, pd.DataFrame):
                pred = pred.iloc[:, 0]
            sub_preds_A[m.name] = pred
            print(f"    ✔ {m.name}: 完成 {len(pred)} 行预测")
    fused_A = fuse_dict(sub_preds_A)
    date_dict_A = to_date_dict(fused_A)
    all_scores["QP-20260626-STATIC"] = date_dict_A
    all_scores["CONTESTANT_A"] = date_dict_A
    print(f"  ✔ CONTESTANT_A 完成: {len(date_dict_A)} 个交易日截面")

    # 2. CONTESTANT_B: CPCV Ensemble (QP-20260626-CPCV)
    print("\n[2/6] 推理 CONTESTANT_B (QP-20260626-CPCV, 8-fold CV)...")
    cB = reg.get_contestant("QP-20260626-CPCV")
    sub_preds_B = {}
    for m in cB.members:
        if not m.artifact_pattern or not m.workflow_yaml:
            continue
        print(f"  • 模型成员: {m.name} ({m.model_class}, pattern: {m.artifact_pattern})")
        ds = get_dataset(m.workflow_yaml)
        fold_files = sorted(glob.glob(str(REPO_ROOT / m.artifact_pattern)))
        print(f"    发现 {len(fold_files)} 个折包子模型")
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
            print(f"    ✔ {m.name} 聚合完成: {len(member_mean)} 行预测")
    fused_B = fuse_dict(sub_preds_B)
    date_dict_B = to_date_dict(fused_B)
    all_scores["QP-20260626-CPCV"] = date_dict_B
    all_scores["CONTESTANT_B"] = date_dict_B
    print(f"  ✔ CONTESTANT_B 完成: {len(date_dict_B)} 个交易日截面")

    # 3. CONTESTANT_C: Different Ensemble (QP-20260612-DIFF)
    print("\n[3/6] 推理 CONTESTANT_C (QP-20260612-DIFF)...")
    cC = reg.get_contestant("QP-20260612-DIFF")
    sub_preds_C = {}
    for m in cC.members:
        p = REPO_ROOT / m.artifact_path
        if p.exists() and m.workflow_yaml:
            print(f"  • 模型成员: {m.name} ({m.model_class})")
            ds = get_dataset(m.workflow_yaml)
            model = load_model_file(p)
            flatten_rnn(model)
            pred = model.predict(ds)
            if isinstance(pred, pd.DataFrame):
                pred = pred.iloc[:, 0]
            sub_preds_C[m.name] = pred
            print(f"    ✔ {m.name}: 完成 {len(pred)} 行预测")
    fused_C = fuse_dict(sub_preds_C)
    date_dict_C = to_date_dict(fused_C)
    all_scores["QP-20260612-DIFF"] = date_dict_C
    all_scores["CONTESTANT_C"] = date_dict_C
    print(f"  ✔ CONTESTANT_C 完成: {len(date_dict_C)} 个交易日截面")

    # 4. CONTESTANT_D: Good Model Proxy (QP-20260306-GOOD-PROXY)
    print("\n[4/6] 推理 CONTESTANT_D (QP-20260306-GOOD-PROXY)...")
    cD = reg.get_contestant("QP-20260306-GOOD-PROXY")
    sub_preds_D = {}
    for m in cD.members:
        p = REPO_ROOT / m.artifact_path
        if p.exists() and m.workflow_yaml:
            print(f"  • 模型成员: {m.name} ({m.model_class})")
            ds = get_dataset(m.workflow_yaml)
            model = load_model_file(p)
            flatten_rnn(model)
            pred = model.predict(ds)
            if isinstance(pred, pd.DataFrame):
                pred = pred.iloc[:, 0]
            sub_preds_D[m.name] = pred
            print(f"    ✔ {m.name}: 完成 {len(pred)} 行预测")
    fused_D = fuse_dict(sub_preds_D)
    date_dict_D = to_date_dict(fused_D)
    all_scores["QP-20260306-GOOD-PROXY"] = date_dict_D
    all_scores["CONTESTANT_D"] = date_dict_D
    print(f"  ✔ CONTESTANT_D 完成: {len(date_dict_D)} 个交易日截面")

    # 5. CONTESTANT_E: GAT 52-feat (GAT-20250919-F52)
    print("\n[5/6] 推理 CONTESTANT_E (GAT-20250919-F52)...")
    cE = reg.get_contestant("GAT-20250919-F52")
    if cE and cE.members:
        m = cE.members[0]
        p = REPO_ROOT / m.artifact_path
        if p.exists() and m.workflow_yaml:
            print(f"  • 模型成员: {m.name}")
            ds = get_dataset(m.workflow_yaml)
            model = load_model_file(p)
            flatten_rnn(model)
            pred = model.predict(ds)
            if isinstance(pred, pd.DataFrame):
                pred = pred.iloc[:, 0]
            fused_E = rank_norm_series(pred)
            date_dict_E = to_date_dict(fused_E)
            all_scores["GAT-20250919-F52"] = date_dict_E
            all_scores["CONTESTANT_E"] = date_dict_E
            print(f"  ✔ CONTESTANT_E 完成: {len(date_dict_E)} 个交易日截面")

    # 6. CONTESTANT_F: GAT 20-feat (GAT-20250926-F20)
    print("\n[6/6] 推理 CONTESTANT_F (GAT-20250926-F20)...")
    cF = reg.get_contestant("GAT-20250926-F20")
    if cF and cF.members:
        m = cF.members[0]
        p = REPO_ROOT / m.artifact_path
        if p.exists() and m.workflow_yaml:
            print(f"  • 模型成员: {m.name}")
            ds = get_dataset(m.workflow_yaml)
            model = load_model_file(p)
            flatten_rnn(model)
            pred = model.predict(ds)
            if isinstance(pred, pd.DataFrame):
                pred = pred.iloc[:, 0]
            fused_F = rank_norm_series(pred)
            date_dict_F = to_date_dict(fused_F)
            all_scores["GAT-20250926-F20"] = date_dict_F
            all_scores["CONTESTANT_F"] = date_dict_F
            print(f"  ✔ CONTESTANT_F 完成: {len(date_dict_F)} 个交易日截面")

    # Save to disk
    with open(out_file, "wb") as f:
        pickle.dump(all_scores, f)

    print("\n" + "=" * 80)
    print(f" ✅ 股票池 [{market}] 预测库生成完毕:")
    print(f"    文件路径: {out_file.relative_to(REPO_ROOT)} ({out_file.stat().st_size / 1024 / 1024:.2f} MB)")
    print(f"    覆盖选手: {list(all_scores.keys())}")
    for k in ["CONTESTANT_A", "CONTESTANT_B", "CONTESTANT_C", "CONTESTANT_D", "CONTESTANT_E", "CONTESTANT_F"]:
        if k in all_scores:
            print(f"      • {k}: {len(all_scores[k])} 个日期, 典型单日股票数量: {len(next(iter(all_scores[k].values())))}")
    print("=" * 80 + "\n")

    return out_file


if __name__ == "__main__":
    market_arg = sys.argv[1] if len(sys.argv) > 1 else "csi500"
    run_batch_inference(market=market_arg)
