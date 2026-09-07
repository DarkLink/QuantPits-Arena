"""
arena/benchmarks
================
统一基准治理体系模块 (First-Class Benchmark System)
"""

from arena.benchmarks.base import Benchmark, BenchmarkCategory
from arena.benchmarks.taotie import TaotieBenchmark
from arena.benchmarks.ghost_taotie import GhostTaotieBenchmark
from arena.benchmarks.index import IndexBenchmark

__all__ = [
    "Benchmark",
    "BenchmarkCategory",
    "TaotieBenchmark",
    "GhostTaotieBenchmark",
    "IndexBenchmark",
]
