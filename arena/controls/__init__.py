"""
arena.controls
==============
控制组与基准：Monkey Colony 与 Rock
"""

from arena.controls.monkey import (
    MonkeyColony,
    StrategySpec,
    CANONICAL_STRATEGY_SPECS,
    map_animal_to_spec_id,
)
from arena.controls.rock import RockBenchmark
from arena.controls.taotie import TaotieBenchmark

__all__ = [
    "MonkeyColony",
    "StrategySpec",
    "CANONICAL_STRATEGY_SPECS",
    "map_animal_to_spec_id",
    "RockBenchmark",
    "TaotieBenchmark",
]

