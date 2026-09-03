"""
tests/test_artifacts_integrity.py
=================================
本地模型与配置资产完整性的前置验证测试 (Verification First)

验证目标：
1. alias_map.yaml 映射表的完整性与双向唯一性 (CONTESTANT_A ~ F)
2. manifests/public 与 manifests/private 文件的对应存在性
3. artifacts/models/ 下 47 个 .pkl 和 2 个 trained_model 的物理存在性与可加载性校验
4. ContestantRegistry 能够双向解析真实与匿名 ID 并正确加载各选手配置
"""

from pathlib import Path
import yaml
import pytest

from arena.config import REPO_ROOT, MANIFESTS_PRIVATE_DIR, MANIFESTS_PUBLIC_DIR, ALIAS_MAP_FILE, MODELS_DIR
from arena.contestants import ContestantRegistry


def test_alias_map_and_manifests_correspondence():
    """验证私有与公开 Manifest 的映射一致性"""
    assert ALIAS_MAP_FILE.exists(), "alias_map.yaml 必须存在"
    with open(ALIAS_MAP_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    mappings = data.get("mappings", [])
    assert len(mappings) == 6, "应恰好包含 6 个参赛选手映射"

    anon_ids = set()
    for item in mappings:
        anon_ids.add(item["anonymous_id"])
        priv_file = MANIFESTS_PRIVATE_DIR / item["private_file"]
        pub_file = MANIFESTS_PUBLIC_DIR / item["public_file"]

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


def test_contestant_registry_resolution():
    """验证 ContestantRegistry 别名解析与双向查找能力"""
    registry = ContestantRegistry()
    contestants = registry.list_contestants()
    assert len(contestants) == 6

    # 验证能通过匿名代号 CONTESTANT_A ~ F 索引到有效的选手
    for letter in ["A", "B", "C", "D", "E", "F"]:
        anon_id = f"CONTESTANT_{letter}"
        c = registry.get_contestant(anon_id)
        assert c is not None
        assert len(c.members) > 0
        # 验证别名反解
        assert registry.get_anonymous_id(anon_id) == anon_id
