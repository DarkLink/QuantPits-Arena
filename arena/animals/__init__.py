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


def get_all_animals() -> list:
    """返回 Arena 全部 13 种标准动物实例列表"""
    return [
        Robot(),
        Sloth(delay_weeks=1),
        Sloth(delay_weeks=2),
        Sloth(delay_weeks=3),
        Sloth(delay_weeks=4),
        Snail(delay_weeks=1),
        Snail(delay_weeks=2),
        Snail(delay_weeks=3),
        Snail(delay_weeks=4),
        Rabbit(variant=1),
        Rabbit(variant=2),
        Turtle(),
        Koala(),
    ]


__all__ = [
    "Animal",
    "Robot",
    "Sloth",
    "Snail",
    "Rabbit",
    "Turtle",
    "Koala",
    "get_all_animals",
]
