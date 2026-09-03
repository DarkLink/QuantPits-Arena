"""
arena.contestants
=================
选手清单、注册表与推理适配器
"""

from arena.contestants.manifest import ContestantManifest, ContestantMember, load_manifest
from arena.contestants.registry import ContestantRegistry

__all__ = [
    "ContestantManifest",
    "ContestantMember",
    "load_manifest",
    "ContestantRegistry",
]
