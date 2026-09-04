"""
arena.animals
=============
9 种标准执行动物
"""

from arena.animals.base import Animal
from arena.animals.robot import Robot
from arena.animals.sloth import Sloth
from arena.animals.snail import Snail
from arena.animals.rabbit import Rabbit
from arena.animals.turtle import Turtle
from arena.animals.koala import Koala
from arena.animals.meerkat import Meerkat
from arena.animals.eagle import Eagle
from arena.animals.whale_shark import WhaleShark
from arena.animals.taotie import Taotie


def get_all_animals() -> list:
    """返回 Arena 全部 29 种完整动物实例列表"""
    animals = [
        # 基准与延迟动物
        Robot(),
        Sloth(delay_weeks=1),
        Sloth(delay_weeks=2),
        Sloth(delay_weeks=3),
        Sloth(delay_weeks=4),
        Snail(delay_weeks=1),
        Snail(delay_weeks=2),
        Snail(delay_weeks=3),
        Snail(delay_weeks=4),
        # 换手带宽与反转动物
        Rabbit(variant=1),
        Rabbit(variant=2),
        Turtle(),
        Koala(),
    ]
    # 狐獴群 (10% ~ 90% 百分位切片)
    for p in range(10, 100, 10):
        animals.append(Meerkat(percentile=p))

    # 鹰群 (不同容量与换手带宽)
    eagle_specs = [(5, 1), (11, 2), (44, 6), (66, 9), (88, 12)]
    for topk, n_drop in eagle_specs:
        animals.append(Eagle(topk=topk, n_drop=n_drop))

    # 鲸鲨 (半池 50%)
    animals.append(WhaleShark())
    # 注：饕餮 (Taotie) 作为全池纯被动控制基准，已解耦并迁移至 arena.controls.TaotieBenchmark

    return animals


__all__ = [
    "Animal",
    "Robot",
    "Sloth",
    "Snail",
    "Rabbit",
    "Turtle",
    "Koala",
    "Meerkat",
    "Eagle",
    "WhaleShark",
    "Taotie",
    "get_all_animals",
]
