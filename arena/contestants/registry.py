"""
arena/contestants/registry.py
=============================
参赛选手注册表与别名映射管理
"""

from typing import Dict, List, Optional
from pathlib import Path
import yaml

from arena.config import (
    MANIFESTS_PRIVATE_DIR,
    MANIFESTS_PUBLIC_DIR,
    ALIAS_MAP_FILE
)
from arena.contestants.manifest import ContestantManifest, load_manifest


class ContestantRegistry:
    """
    选手注册表：
    - 支持私有层真名与公开层匿名代号的双向索引
    - 优先加载本地 private 清单（具备完整 artifact_path 与超参配置，用于真实推理）
    - 在纯公开环境下自动降级加载 public 匿名清单
    """

    def __init__(self, private_dir: Optional[Path] = None, public_dir: Optional[Path] = None):
        self.private_dir = private_dir or MANIFESTS_PRIVATE_DIR
        self.public_dir = public_dir or MANIFESTS_PUBLIC_DIR
        self.alias_map_file = self.private_dir / "alias_map.yaml"

        # 映射缓存: {id: ContestantManifest}
        self._contestants: Dict[str, ContestantManifest] = {}
        # 别名映射: {alias: canonical_id}
        self._alias_to_id: Dict[str, str] = {}
        # 匿名映射: {private_id: anonymous_id}
        self._private_to_anon: Dict[str, str] = {}

        self._discover_and_register()

    def _discover_and_register(self):
        """执行选手扫描与别名映射加载"""
        has_private = self.private_dir.exists() and self.alias_map_file.exists()

        if has_private:
            with open(self.alias_map_file, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            mappings = config.get("mappings", [])
            for item in mappings:
                priv_id = item["private_id"]
                anon_id = item["anonymous_id"]
                priv_file = self.private_dir / item["private_file"]

                if priv_file.exists():
                    manifest = load_manifest(priv_file)
                    self._contestants[priv_id] = manifest
                    # 支持以匿名代号直接查询私有 manifest
                    self._alias_to_id[anon_id] = priv_id
                    self._private_to_anon[priv_id] = anon_id
        else:
            # 公开模式：直接扫描 manifests/public/
            if self.public_dir.exists():
                for yaml_file in sorted(self.public_dir.glob("*.yaml")):
                    manifest = load_manifest(yaml_file)
                    cid = manifest.contestant_id
                    self._contestants[cid] = manifest
                    self._alias_to_id[cid] = cid

    def get_contestant(self, identifier: str) -> ContestantManifest:
        """根据真实 ID 或匿名代号获取 Manifest"""
        canonical_id = self._alias_to_id.get(identifier, identifier)
        if canonical_id in self._contestants:
            return self._contestants[canonical_id]
        raise KeyError(f"未找到参赛选手: {identifier}")

    def list_contestants(self) -> List[ContestantManifest]:
        """返回已注册的所有选手 Manifest 列表"""
        return list(self._contestants.values())

    def get_anonymous_id(self, identifier: str) -> str:
        """获取指定选手的公开匿名代号"""
        if identifier in self._private_to_anon:
            return self._private_to_anon[identifier]
        if "CONTESTANT_" in identifier:
            return identifier
        return self._private_to_anon.get(identifier, identifier)
