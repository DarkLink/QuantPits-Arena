"""
arena/portfolio/engine.py
=========================
周频组合回测执行引擎 (调仓周频，估值日频)
"""

from typing import Dict, List, Set, Optional, Callable, Any
import pandas as pd
import numpy as np

from arena.config import (
    DEFAULT_INITIAL_CASH,
    DEFAULT_DEAL_PRICE,
    DEFAULT_TOPK
)
from arena.portfolio.types import (
    Order,
    TradeRecord,
    DailyValuation,
    WeeklySettlement,
    PortfolioPath
)
from arena.portfolio.costs import CostModel
from arena.calendar import WeeklyCycle


class PortfolioEngine:
    """
    周频组合引擎：
    - 支持可配置成交价 (默认周一开盘价 deal_price="open")
    - 支持可交易性顺延缓冲 (Tradability Buffer：遇到停牌/涨停自动取第 23+ 名补齐)
    - 调仓周频 (周一开盘执行)，盯市估值日频 (每个交易日收盘核算 NAV)
    - 严格记录资金、佣金成本与持仓明细
    """

    def __init__(
        self,
        contestant_id: str,
        animal_id: str,
        initial_cash: float = DEFAULT_INITIAL_CASH,
        topk: int = DEFAULT_TOPK,
        deal_price_mode: str = DEFAULT_DEAL_PRICE,
        cost_model: Optional[CostModel] = None
    ):
        self.contestant_id = contestant_id
        self.animal_id = animal_id
        self.initial_cash = float(initial_cash)
        self.cash_balance = float(initial_cash)
        self.topk = topk
        self.deal_price_mode = deal_price_mode
        self.cost_model = cost_model or CostModel()

        # 当前持仓: {instrument: shares}
        self.holdings: Dict[str, float] = {}

        # 估值时序与日志
        self.daily_valuations: List[DailyValuation] = []
        self.weekly_settlements: List[WeeklySettlement] = []
        self.trades: List[TradeRecord] = []

    def get_current_held_instruments(self) -> Set[str]:
        return {inst for inst, shares in self.holdings.items() if shares > 0}

    def generate_order(
        self,
        score: Optional[pd.Series],
        topk: int = DEFAULT_TOPK,
        n_drop: int = 3,
        trade_date: str = "",
        is_first_entry: bool = False,
        tradability_filter: Optional[Callable[[str, str], bool]] = None
    ) -> Optional[Order]:
        """
        根据当周得分与策略生成调仓订单。

        Args:
            score: Animal 变换后的截面得分 Series（若为 None 表示冷启动空仓期）
            topk: 目标持股数量 (默认 22)
            n_drop: 调仓时换出换入只数 (Robot: 3, Rabbit-1: 11, Turtle: 1...)
            trade_date: 拟交易日期 (周一)
            is_first_entry: 是否为首次买入建仓
            tradability_filter: 物理可交易性过滤函数 (instrument, date) -> bool
        """
        if score is None:
            # 冷启动空仓期（如 Sloth 前置周期）：不产生订单，维持空仓
            return None

        current_held = self.get_current_held_instruments()

        # 筛选具备可交易性的候选标的列表（顺延缓冲）
        sorted_candidates = list(score.sort_values(ascending=False).index)
        if tradability_filter is not None:
            tradable_candidates = [
                inst for inst in sorted_candidates
                if tradability_filter(inst, trade_date)
            ]
        else:
            tradable_candidates = sorted_candidates

        # 1. 首次建仓（或持仓为空时的首次买入）
        if is_first_entry or len(current_held) == 0:
            target_buys = tradable_candidates[:topk]
            return Order(
                trade_date=trade_date,
                buy_instruments=target_buys,
                sell_instruments=[],
                is_first_entry=True
            )

        # 2. 常规周频调仓
        # a. 持仓中在当前 score 中得分最低的 n_drop 只卖出
        held_in_score = [inst for inst in current_held if inst in score.index]
        # 若某持仓标的不在当前得分中，优先卖出
        missing_in_score = [inst for inst in current_held if inst not in score.index]

        held_score_series = score.loc[held_in_score]
        lowest_held = list(held_score_series.nsmallest(n_drop).index)
        sell_list = (missing_in_score + lowest_held)[:n_drop]

        # b. 从非持仓的可交易标的中，按得分最高选入 n_drop 只买入
        unheld_tradable = [inst for inst in tradable_candidates if inst not in current_held]
        buy_list = unheld_tradable[:n_drop]

        return Order(
            trade_date=trade_date,
            buy_instruments=buy_list,
            sell_instruments=sell_list,
            is_first_entry=False
        )

    def execute_weekly_cycle(
        self,
        cycle: WeeklyCycle,
        order: Optional[Order],
        price_lookup: Callable[[str, str, str], float],
    ) -> WeeklySettlement:
        """
        执行一个完整周频周期的撮合与日频盯市估值。

        Args:
            cycle: WeeklyCycle 对象 (包含 trade_date, settle_date, trading_days)
            order: 周一调仓订单 (若为 None 则本周不调仓)
            price_lookup: 价格查询函数 (instrument, date, field='open'|'close') -> float
        """
        prev_nav = self.daily_valuations[-1].nav if self.daily_valuations else 1.0
        weekly_cost = 0.0
        turnover_value = 0.0

        # --- Phase 1: 周一开盘执行订单 ---
        if order is not None:
            exec_field = self.deal_price_mode  # "open" 或 "close"

            # 1.1 先执行卖出订单，释放现金
            for inst in order.sell_instruments:
                if inst in self.holdings and self.holdings[inst] > 0:
                    shares = self.holdings[inst]
                    price = price_lookup(inst, cycle.trade_date, exec_field)
                    gross_val = shares * price
                    cost = self.cost_model.calculate_sell_cost(gross_val)
                    net_val = gross_val - cost

                    self.cash_balance += net_val
                    weekly_cost += cost
                    turnover_value += gross_val
                    del self.holdings[inst]

                    self.trades.append(
                        TradeRecord(
                            date=cycle.trade_date,
                            instrument=inst,
                            direction="SELL",
                            price=price,
                            shares=shares,
                            value=gross_val,
                            cost=cost
                        )
                    )

            # 1.2 执行买入订单
            if order.buy_instruments:
                # 等权分配当前可用资金
                # 为防止佣金滑点导致透支，保留 0.5% 现金缓冲
                investable_cash = self.cash_balance * 0.995
                per_stock_cash = investable_cash / len(order.buy_instruments)

                for inst in order.buy_instruments:
                    price = price_lookup(inst, cycle.trade_date, exec_field)
                    if price <= 0:
                        continue
                    # 假设整手（或精确股数）买入
                    shares = float(int(per_stock_cash / price))
                    if shares <= 0:
                        continue
                    gross_val = shares * price
                    cost = self.cost_model.calculate_buy_cost(gross_val)
                    total_spent = gross_val + cost

                    if total_spent <= self.cash_balance:
                        self.cash_balance -= total_spent
                        self.holdings[inst] = self.holdings.get(inst, 0.0) + shares
                        weekly_cost += cost
                        turnover_value += gross_val

                        self.trades.append(
                            TradeRecord(
                                date=cycle.trade_date,
                                instrument=inst,
                                direction="BUY",
                                price=price,
                                shares=shares,
                                value=gross_val,
                                cost=cost
                            )
                        )

        # --- Phase 2: 周内日频盯市估值 (Daily Marked-to-Market) ---
        for day in cycle.trading_days:
            # 每日以当日收盘价核算持仓市值
            held_market_value = 0.0
            for inst, shares in self.holdings.items():
                if shares > 0:
                    c_price = price_lookup(inst, day, "close")
                    held_market_value += shares * c_price

            total_asset = self.cash_balance + held_market_value
            nav = total_asset / self.initial_cash

            daily_ret = (nav / prev_nav) - 1.0 if prev_nav > 0 else 0.0
            prev_nav = nav

            self.daily_valuations.append(
                DailyValuation(
                    date=day,
                    cash=self.cash_balance,
                    holdings_value=held_market_value,
                    total_asset=total_asset,
                    nav=nav,
                    daily_return=daily_ret
                )
            )

        # --- Phase 3: 周五收盘结算 ---
        settle_nav = self.daily_valuations[-1].nav
        start_week_nav = (
            self.daily_valuations[-len(cycle.trading_days)].nav
            if len(self.daily_valuations) >= len(cycle.trading_days)
            else 1.0
        )
        w_ret = (settle_nav / start_week_nav) - 1.0 if start_week_nav > 0 else 0.0
        turnover_rate = (
            turnover_value / (self.initial_cash * start_week_nav)
            if start_week_nav > 0
            else 0.0
        )

        settlement = WeeklySettlement(
            week_idx=cycle.cycle_idx,
            settle_date=cycle.settle_date,
            start_nav=start_week_nav,
            end_nav=settle_nav,
            weekly_return=w_ret,
            turnover=turnover_rate,
            weekly_cost=weekly_cost,
            num_holdings=len(self.holdings)
        )
        self.weekly_settlements.append(settlement)

        return settlement

    def to_portfolio_path(self) -> PortfolioPath:
        """导出完整的回测路径对象"""
        return PortfolioPath(
            contestant_id=self.contestant_id,
            animal_id=self.animal_id,
            daily_valuations=list(self.daily_valuations),
            weekly_settlements=list(self.weekly_settlements),
            trades=list(self.trades),
            final_holdings=dict(self.holdings)
        )
