"""
arena.contestants.adapters
==========================
模型推理适配器与工厂函数
"""

from arena.contestants.manifest import ContestantManifest
from arena.contestants.adapters.base import (
    BaseInferenceAdapter,
    rank_norm_score,
    rank_norm_equal_fusion,
)
from arena.contestants.adapters.mock import MockInferenceAdapter
from arena.contestants.adapters.static import StaticEnsembleAdapter
from arena.contestants.adapters.cpcv import CPCVEnsembleAdapter
from arena.contestants.adapters.gat import GATAdapter


def create_adapter(
    manifest: ContestantManifest,
    mock: bool = False
) -> BaseInferenceAdapter:
    """
    适配器工厂函数：
    依据 manifest 的 inference_adapter 字段或 mock 标志实例化对应适配器。
    """
    if mock:
        return MockInferenceAdapter(manifest)

    adapter_name = manifest.inference_adapter.lower()

    if "cpcv" in adapter_name or "ensemble_cv" in adapter_name:
        return CPCVEnsembleAdapter(manifest)
    elif "static" in adapter_name or "ensemble_static" in adapter_name:
        return StaticEnsembleAdapter(manifest)
    elif "gat" in adapter_name or "single_model" in adapter_name:
        return GATAdapter(manifest)
    else:
        # 默认使用静态适配器
        return StaticEnsembleAdapter(manifest)


__all__ = [
    "BaseInferenceAdapter",
    "rank_norm_score",
    "rank_norm_equal_fusion",
    "MockInferenceAdapter",
    "StaticEnsembleAdapter",
    "CPCVEnsembleAdapter",
    "GATAdapter",
    "create_adapter",
]
