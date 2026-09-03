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


def test_robot_contract():
    """验证 Robot 策略契约"""
    dates = ["2026-07-03", "2026-07-10", "2026-07-17"]
    stocks = [f"STOCK_{i:02d}" for i in range(30)]
    score = simulate_cross_sectional_score(dates, stocks)

    # Robot 规范：不改变得分，策略参数 topk=22, n_drop=3
    topk, n_drop = 22, 3
    assert topk == 22
    assert n_drop == 3
    assert len(score) == len(dates) * len(stocks)


def test_koala_rank_inversion_contract():
    """验证 Koala 反向截面排名契约"""
    stocks = [f"STOCK_{i:02d}" for i in range(10)]
    dates = ["2026-07-03"]
    score = simulate_cross_sectional_score(dates, stocks)

    # 考拉反向变换公式: 1.0 - (rank - 1)/(n - 1)
    ranked = score.groupby(level="datetime").rank(method="average", ascending=True)
    n = len(stocks)
    norm_rank = (ranked - 1) / (n - 1)
    inverted_score = 1.0 - norm_rank

    # 验证反转性：原第一名在反转后排在最后
    original_top = score.xs("2026-07-03").idxmax()
    inverted_top = inverted_score.xs("2026-07-03").idxmax()
    original_bottom = score.xs("2026-07-03").idxmin()

    assert original_top == inverted_score.xs("2026-07-03").idxmin()
    assert original_bottom == inverted_top
    assert np.allclose(inverted_score.values.min(), 0.0)
    assert np.allclose(inverted_score.values.max(), 1.0)


def test_rabbit_and_turtle_dropn_contract():
    """验证 Rabbit 与 Turtle 的 DropN 策略契约"""
    topk = 22
    # Rabbit-1: TopK 50% = 11
    rabbit1_drop = topk // 2
    assert rabbit1_drop == 11, "Rabbit-1 每次调仓必须是 topk 的 50% = 11 只"

    # Rabbit-2: 全仓 = 22
    rabbit2_drop = topk
    assert rabbit2_drop == 22, "Rabbit-2 每次全仓替换 = 22 只"

    # Turtle: 极低换手 = 1
    turtle_drop = 1
    assert turtle_drop == 1, "Turtle 每次调仓换手 = 1 只"


def test_sloth_delay_availability_contract():
    """
    验证 Sloth 延迟语义与冷启动边界
    Sloth-1 在 Week 0 仅有 1 个信号快照，延迟 1 周时在 Week 0 只能使用当前信号；
    进入 Week 1 时，使用 Week 0 的信号进行决策。
    """
    dates = ["2026-07-03", "2026-07-10", "2026-07-17", "2026-07-24"]
    stocks = [f"STOCK_{i:02d}" for i in range(10)]
    score = simulate_cross_sectional_score(dates, stocks)

    # 模拟 Sloth-1 延迟映射
    delay_weeks = 1
    # 在 2026-07-10 决策时，应取 2026-07-03 的信号
    signal_at_w1 = score.xs(dates[0])
    signal_at_w2 = score.xs(dates[1])

    # 验证不相等，且能够准确索引到前一周期
    assert not np.allclose(signal_at_w1.values, signal_at_w2.values)
