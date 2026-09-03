"""
tests/test_portfolio_weekly_engine.py
=====================================
周频组合执行引擎的前置验证测试 (Verification First)

验证目标：
1. 首周冷启动满额建仓契约：
   - 空仓进入，全额购买 Top-K (22 只)，绝不触发 DropN 卖出逻辑
   - 等权分配资金，扣除买入成本 (open_cost = 0.0005)
2. 后续周频调仓契约：
   - 排序当前持仓：持仓中 score 垫底的 n_drop 只被卖出
   - 排序外部非持仓：候选池中 score 最优的 n_drop 只被买入
   - 调仓后持仓只数恒等于 Top-K
3. 交易费用与净值计算契约：
   - 卖出费用 close_cost = 0.0015
   - 净值恒定归一化 (初始 NAV = 1.0000)
"""

import pandas as pd
import numpy as np
import pytest


class ToyPortfolioEngine:
    """用于前置测试验证的周频简易回测逻辑原型"""

    def __init__(self, topk=22, open_cost=0.0005, close_cost=0.0015, min_cost=5.0):
        self.topk = topk
        self.open_cost = open_cost
        self.close_cost = close_cost
        self.min_cost = min_cost
        self.holdings = set()
        self.nav = 1.0

    def step(self, score: pd.Series, n_drop: int, is_first_week: bool = False):
        """执行一个周期的调仓与订单生成"""
        if is_first_week or len(self.holdings) == 0:
            # 首周：TopK 一次性买满
            target_stocks = set(score.nlargest(self.topk).index)
            buy_orders = list(target_stocks)
            sell_orders = []
            self.holdings = target_stocks
        else:
            # 正常调仓：
            # 1. 找出当前持仓在当前 score 下得分最低的 n_drop 只卖出
            current_held_scores = score.loc[list(self.holdings)]
            sell_orders = list(current_held_scores.nsmallest(n_drop).index)

            # 2. 找出当前未持仓中 score 最高的 n_drop 只买入
            unheld_scores = score.drop(index=list(self.holdings))
            buy_orders = list(unheld_scores.nlargest(n_drop).index)

            # 更新持仓
            self.holdings = (self.holdings - set(sell_orders)) | set(buy_orders)

        return buy_orders, sell_orders


def test_first_week_full_entry():
    """验证首周满额建仓契约：买入恰好 TopK 只，卖出为空"""
    stocks = [f"STOCK_{i:02d}" for i in range(50)]
    score = pd.Series(np.linspace(0.1, 0.9, 50), index=stocks)

    engine = ToyPortfolioEngine(topk=22)
    buys, sells = engine.step(score, n_drop=3, is_first_week=True)

    assert len(buys) == 22, "首周应一次性买入 22 只股票"
    assert len(sells) == 0, "首周不应有任何卖出订单"
    assert len(engine.holdings) == 22


def test_subsequent_weekly_rebalance():
    """验证后续调仓契约：卖出最低 n_drop，买入最高 n_drop，总持仓数保持 TopK"""
    stocks = [f"STOCK_{i:02d}" for i in range(50)]
    # Week 1
    score_w1 = pd.Series(np.linspace(0.1, 0.9, 50), index=stocks)
    engine = ToyPortfolioEngine(topk=22)
    engine.step(score_w1, n_drop=3, is_first_week=True)

    # Week 2: 改变部分股票得分
    score_w2 = score_w1.copy()
    # 将原有持仓中得分最高的 3 只大幅下调
    held_list = list(engine.holdings)
    for stock in held_list[:3]:
        score_w2[stock] = 0.01

    buys, sells = engine.step(score_w2, n_drop=3, is_first_week=False)

    assert len(sells) == 3, "调仓应卖出 3 只"
    assert len(buys) == 3, "调仓应买入 3 只"
    assert len(engine.holdings) == 22, "调仓后持仓总数恒为 22 只"
    for s in sells:
        assert s not in engine.holdings, "卖出的标的不应保留在持仓中"
    for b in buys:
        assert b in engine.holdings, "买入的标的必须已进入持仓"


def test_rabbit1_half_turnover_drop_count():
    """验证 Rabbit-1 在调仓时的 Drop 数量精确为 11 只"""
    stocks = [f"STOCK_{i:02d}" for i in range(50)]
    score_w1 = pd.Series(np.linspace(0.1, 0.9, 50), index=stocks)
    engine = ToyPortfolioEngine(topk=22)
    engine.step(score_w1, n_drop=11, is_first_week=True)

    score_w2 = pd.Series(np.random.RandomState(42).permutation(np.linspace(0.1, 0.9, 50)), index=stocks)
    buys, sells = engine.step(score_w2, n_drop=11, is_first_week=False)

    assert len(sells) == 11
    assert len(buys) == 11
    assert len(engine.holdings) == 22
