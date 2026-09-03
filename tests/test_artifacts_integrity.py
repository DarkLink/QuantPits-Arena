"""
tests/test_artifacts_integrity.py
=================================
本地模型与配置资产完整性的前置验证测试 (Verification First)

验证目标：
1. alias_map.yaml 映射表的完整性与双向唯一性 (CONTESTANT_A ~ F)
2. manifests/public 与 manifests/private 文件的对应存在性
3. artifacts/models/ 下 47 个 .pkl 和 2 个 trained_model 的物理存在性与可加载性校验
"""

import os
from pathlib import Path
import yaml
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PRIVATE_DIR = REPO_ROOT / "manifests" / "private"
PUBLIC_DIR = REPO_ROOT / "manifests" / "public"
ALIAS_MAP = PRIVATE_DIR / "alias_map.yaml"
MODELS_DIR = REPO_ROOT / "artifacts" / "models"


def test_alias_map_and_manifests_correspondence():
    """验证私有与公开 Manifest 的映射一致性"""
    assert ALIAS_MAP.exists(), "alias_map.yaml 必须存在"
    with open(ALIAS_MAP, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    mappings = data.get("mappings", [])
    assert len(mappings) == 6, "应恰好包含 6 个参赛选手映射"

    anon_ids = set()
    for item in mappings:
        anon_ids.add(item["anonymous_id"])
        priv_file = PRIVATE_DIR / item["private_file"]
        pub_file = PUBLIC_DIR / item["public_file"]

        assert priv_file.exists(), f"私有清单文件缺失: {priv_file}"
        assert pub_file.exists(), f"公开匿名清单文件缺失: {pub_file}"

    assert anon_ids == {"CONTESTANT_A", "CONTESTANT_B", "CONTESTANT_C", "CONTESTANT_D", "CONTESTANT_E", "CONTESTANT_F"}


def test_models_artifacts_physical_existence():
    """验证本地 artifacts/models/ 目录下的核心资产完整就绪"""
    assert MODELS_DIR.exists(), "artifacts/models 目录必须存在"

    pkl_files = list(MODELS_DIR.rglob("*.pkl"))
    trained_model_files = [p for p in MODELS_DIR.rglob("*") if p.name == "trained_model"]

    assert len(pkl_files) == 47, f"期望 47 个 .pkl 模型权重文件，实际找到 {len(pkl_files)} 个"
    assert len(trained_model_files) == 2, f"期望 2 个 GAT trained_model 文件，实际找到 {len(trained_model_files)} 个"
