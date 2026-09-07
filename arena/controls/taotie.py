"""
arena/controls/taotie.py
=======================
向后兼容别名重导出模块。
原 TaotieBenchmark 已正规化迁移至 arena.benchmarks.taotie.TaotieBenchmark。
"""

from arena.benchmarks.taotie import TaotieBenchmark

__all__ = ["TaotieBenchmark"]
