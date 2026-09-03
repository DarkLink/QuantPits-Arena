"""
tests/test_animal_contract.py
=============================
Animal 动物园信号变换与调仓策略契约的前置验证测试 (Verification First)

验证目标：
1. Robot: 原样直通信号，canonical policy (topk=22, n_drop=3)
2. Sloth (树懒 1~4): 
   - 验证信号可用性时间向后延迟 (Delay availability)，绝非未来信息
   - 冷启动边界处理（前 N 周尚无足够延迟历史时，如何安全平稳过渡）
3. Rabbit (兔子 1~2):
   - Rabbit-1: 半仓调仓带宽 (topk // 2 = 11)
   - Rabbit-2: 全仓调仓带宽 (topk = 22)
4. Turtle (乌龟):
   - 极低换手带宽 (n_drop = 1)
5. Koala (考拉):
   - 截面反转 (Rank Reversal)，验证确定性、单调反转性与中性分值
"""

import pandas as pd
import numpy as np
import pytest


def simulate_cross_sectional_score(dates: list, instruments: list):
    """构建多周期截面打分测试数据 (MultiIndex: datetime, instrument)"""
    records = []
    for d_idx, d in enumerate(dates):
        for i_idx, inst in enumerate(instruments):
            # 随周期有轻微波动的合成得分
            score = (i_idx + 1) / len(instruments) + 0.01 * d_idx
            records.append({"datetime": d, "instrument": inst, "score": score})
    df = pd.DataFrame(records).set_index(["datetime", "instrument"])
    return df["score"]


from arena.animals import (
    Robot, Sloth, Rabbit, Turtle, Koala, get_all_animals
)


def test_get_all_animals_completeness():
    """验证 9 种动物齐备"""
    animals = get_all_animals()
    assert len(animals) == 9
    ids = [a.animal_id for a in animals]
    assert ids == [
        "robot", "sloth-1", "sloth-2", "sloth-3", "sloth-4",
        "rabbit-1", "rabbit-2", "turtle", "koala"
    ]


def test_robot_contract():
    """验证 Robot 策略契约与信号直通"""
    stocks = [f"STOCK_{i:02d}" for i in range(30)]
    score = pd.Series(np.linspace(0.1, 0.9, 30), index=stocks)
    robot = Robot()

    transformed = robot.transform_signal(score, {}, cycle_idx=0)
    assert transformed.equals(score)

    policy = robot.get_portfolio_policy()
    assert policy["topk"] == 22
    assert policy["n_drop"] == 3


def test_koala_rank_inversion_contract():
    """验证 Koala 反向截面排名契约"""
    stocks = [f"STOCK_{i:02d}" for i in range(10)]
    score = pd.Series(np.linspace(0.1, 0.9, 10), index=stocks)
    koala = Koala()

    inverted = koala.transform_signal(score, {}, cycle_idx=0)

    # 验证原第一名在反转后排在最后
    assert score.idxmax() == inverted.idxmin()
    assert score.idxmin() == inverted.idxmax()
    assert np.allclose(inverted.min(), 0.0)
    assert np.allclose(inverted.max(), 1.0)


def test_rabbit_and_turtle_dropn_contract():
    """验证 Rabbit 与 Turtle 的 DropN 策略契约"""
    r1 = Rabbit(variant=1)
    assert r1.get_portfolio_policy()["n_drop"] == 11

    r2 = Rabbit(variant=2)
    assert r2.get_portfolio_policy()["n_drop"] == 22

    turtle = Turtle()
    assert turtle.get_portfolio_policy()["n_drop"] == 1


def test_sloth_option_b_cold_start_contract():
    """
    验证 Sloth 方案 B 冷启动：
    - 前 N 周 (cycle_idx < delay_weeks) 返回 None（空仓现金）
    - cycle_idx == delay_weeks 时返回 cycle 0 信号
    - 后续周期返回 cycle_idx - delay_weeks 信号
    """
    stocks = [f"STOCK_{i:02d}" for i in range(10)]
    score_c0 = pd.Series(np.linspace(0.1, 0.9, 10), index=stocks)
    score_c1 = pd.Series(np.linspace(0.2, 0.8, 10), index=stocks)
    score_c2 = pd.Series(np.linspace(0.3, 0.7, 10), index=stocks)

    history = {0: score_c0, 1: score_c1, 2: score_c2}

    # 测试 Sloth-1
    sloth1 = Sloth(delay_weeks=1)
    # Cycle 0: 前置期未满 1 周 -> None (保持空仓现金)
    assert sloth1.transform_signal(score_c0, history, cycle_idx=0) is None
    # Cycle 1: 达到 1 周延迟 -> 返回 Cycle 0 信号 (首次建仓)
    sig_c1 = sloth1.transform_signal(score_c1, history, cycle_idx=1)
    assert sig_c1.equals(score_c0)
    # Cycle 2: 延迟使用 Cycle 1 信号 (调仓)
    sig_c2 = sloth1.transform_signal(score_c2, history, cycle_idx=2)
    assert sig_c2.equals(score_c1)

    # 测试 Sloth-2
    sloth2 = Sloth(delay_weeks=2)
    # Cycle 0 和 Cycle 1 都必须保持空仓现金
    assert sloth2.transform_signal(score_c0, history, cycle_idx=0) is None
    assert sloth2.transform_signal(score_c1, history, cycle_idx=1) is None
    # Cycle 2: 达到 2 周延迟 -> 首次建仓使用 Cycle 0 信号
    sig2_c2 = sloth2.transform_signal(score_c2, history, cycle_idx=2)
    assert sig2_c2.equals(score_c0)

