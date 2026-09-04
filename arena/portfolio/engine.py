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
    PortfolioPath,
    EngineCheckpoint,
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
        topk: int = DEFAULT_TOPK,
        initial_cash: float = DEFAULT_INITIAL_CASH,
        cost_model: Optional[CostModel] = None,
        deal_price_mode: str = DEFAULT_DEAL_PRICE,
        allow_fractional_shares: bool = False,  # 默认不支持碎股
        lot_size: int = 100,                     # A股一手 100 股
    ):
        self.contestant_id = contestant_id
        self.animal_id = animal_id
        self.topk = topk
        self.initial_cash = float(initial_cash)
        self.cash_balance = float(initial_cash)
        self.cost_model = cost_model or CostModel()
        self.deal_price_mode = deal_price_mode
        self.allow_fractional_shares = allow_fractional_shares
        self.lot_size = lot_size

        # 当前持仓: {instrument: shares}
        self.holdings: Dict[str, float] = {}

        # 估值时序与日志
        self.daily_valuations: List[DailyValuation] = []
        self.weekly_settlements: List[WeeklySettlement] = []
        self.trades: List[TradeRecord] = []

        # 资本粒度与 Affordability 诊断采集器 (Capital-Granularity Instrumentation)
        self.target_capacities: List[int] = []
        self.buy_attempt_count: int = 0
        self.unaffordable_buy_count: int = 0
        self.rebalance_days_with_buy: int = 0
        self.unaffordable_event_days: int = 0

    def get_current_held_instruments(self) -> Set[str]:
        return {inst for inst, shares in self.holdings.items() if shares > 0}

    def generate_order(
        self,
        score: Optional[pd.Series],
        topk: int = DEFAULT_TOPK,
        n_drop: int = 3,
        trade_date: str = "",
        is_first_entry: bool = False,
        tradability_filter: Optional[Callable[[str, str], bool]] = None,
        price_lookup: Optional[Callable[[str, str, str], float]] = None,
        passive_pool: bool = False,
    ) -> Optional[Order]:
        """
        根据当周得分与策略生成调仓订单（含出池被动优先调仓机制与 DropN 预算约束）。

        调仓规则：
        1. 出池优先于 DROP：当前持仓中不在有效池中的标的优先卖出；
        2. 调仓卖出上限不超过 DropN：单期卖出总数受限于 n_drop（多余出池标的留待下期处理）；
        3. 出池卖出后若仍有剩余 DropN 配额，继续按打分进行常规主动 Drop；
        4. 饕餮（全池纯被动）：全量被动卖出出池标的、全量买入新入池标的。
        """
        if score is None:
            # 冷启动空仓期（如 Sloth 前置周期）：不产生订单，维持空仓
            return None

        current_held = self.get_current_held_instruments()

        # 筛选具备可交易性且“买得起”的候选标的列表（顺延缓冲机制）
        sorted_candidates = list(score.sort_values(ascending=False).index)
        tradable_candidates = []

        # 预估单只标的分配可用资金
        effective_topk = len(sorted_candidates) if (topk <= 0 or topk >= len(sorted_candidates)) else topk
        if is_first_entry or len(current_held) == 0:
            est_per_stock_cash = (self.cash_balance * 0.995) / max(effective_topk, 1)
        else:
            est_per_stock_cash = self.initial_cash / max(effective_topk, 1)

        for inst in sorted_candidates:
            # 1. 停牌/涨跌停过滤
            if tradability_filter is not None and not tradability_filter(inst, trade_date):
                continue

            # 2. 资金承受能力过滤：若不支持碎股且买不起一手 (100股)，跳过并顺延
            # 注意：对于全池纯被动动物 (passive_pool=True，如饕餮)，目标是全量覆盖池中所有标的，
            # 无后续标的可以顺延，因此不在候选阶段提前截断剔除，而是在撮合执行阶段真实体现资本粒度受阻与跳过！
            if not passive_pool and not self.allow_fractional_shares and price_lookup is not None:
                p = price_lookup(inst, trade_date, self.deal_price_mode)
                if p > 0 and (p * self.lot_size) > est_per_stock_cash:
                    continue

            tradable_candidates.append(inst)

        # 重新校准实际有效 topk（不超过实际可交易候选池大小）
        if topk <= 0 or topk >= len(tradable_candidates):
            target_capacity = len(tradable_candidates)
        else:
            target_capacity = topk

        self.target_capacities.append(target_capacity)

        # 1. 首次建仓（或持仓为空时的首次买入）
        if is_first_entry or len(current_held) == 0:
            target_buys = tradable_candidates[:target_capacity]
            return Order(
                trade_date=trade_date,
                buy_instruments=target_buys,
                sell_instruments=[],
                is_first_entry=True
            )

        # 2. 常规周频调仓
        # 识别出池持仓与在池持仓
        out_of_pool_held = [inst for inst in current_held if inst not in tradable_candidates]
        in_pool_held = [inst for inst in current_held if inst in tradable_candidates]

        target_topk = tradable_candidates[:target_capacity]

        # 模式 A: 纯被动全池复制模式（如饕餮 Taotie: passive_pool=True 或 n_drop=0 且全池）
        if passive_pool or (n_drop == 0 and target_capacity >= len(tradable_candidates)):
            sell_list = list(out_of_pool_held)
            buy_list = [inst for inst in tradable_candidates if inst not in current_held]
            if len(sell_list) == 0 and len(buy_list) == 0:
                return Order(trade_date=trade_date, buy_instruments=[], sell_instruments=[], is_first_entry=False)
            return Order(trade_date=trade_date, buy_instruments=buy_list, sell_instruments=sell_list, is_first_entry=False)

        # 模式 B: 主动配额调仓模式（含出池被动优先调仓与 DropN 卖出上限约束）
        max_sells = n_drop

        # 1) 出池优先卖出（上限不超过 DropN）
        sells_from_out = out_of_pool_held[:max_sells]
        remaining_drop = max_sells - len(sells_from_out)

        # 2) 若仍有剩余 DropN 额度，进行常规主动得分 Drop
        sells_from_active = []
        if remaining_drop > 0 and len(in_pool_held) > 0:
            held_in_score = [inst for inst in in_pool_held if inst in score.index]
            held_score_series = score.loc[held_in_score]

            exits_not_in_target = [inst for inst in in_pool_held if inst not in target_topk]
            exits_not_in_target_sorted = list(held_score_series.loc[exits_not_in_target].nsmallest(len(exits_not_in_target)).index)

            in_target_held = [inst for inst in in_pool_held if inst in target_topk]
            in_target_held_sorted = list(held_score_series.loc[in_target_held].nsmallest(len(in_target_held)).index)

            active_candidates = exits_not_in_target_sorted + in_target_held_sorted
            entrants = [inst for inst in target_topk if inst not in current_held]

            # 主动换出受限于剩余配额、新入围需求以及可换出标的数
            num_active = min(remaining_drop, len(entrants), len(active_candidates))
            sells_from_active = active_candidates[:num_active]

        sell_list = sells_from_out + sells_from_active

        # 3) 计算买入标的列表，维持目标持仓规模 (卖出后组合实际保留的总持股数)
        retained_held = [inst for inst in current_held if inst not in sell_list]
        need_to_buy = max(0, target_capacity - len(retained_held))

        available_buys = [inst for inst in tradable_candidates if inst not in current_held or inst in sell_list]
        buy_list = available_buys[:need_to_buy]

        if len(buy_list) == 0 and len(sell_list) == 0:
            return Order(
                trade_date=trade_date,
                buy_instruments=[],
                sell_instruments=[],
                is_first_entry=False
            )

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
        # 如果是首次运行，记录 T0 起点 (Anchor 收盘状态: NAV=1.000000, 现金=100%, 仓位=0%)
        if len(self.daily_valuations) == 0:
            self.daily_valuations.append(
                DailyValuation(
                    date=cycle.decision_date,
                    cash=self.cash_balance,
                    holdings_value=0.0,
                    total_asset=self.cash_balance,
                    nav=1.0,
                    daily_return=0.0
                )
            )

        prev_nav = self.daily_valuations[-1].nav
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
                self.rebalance_days_with_buy += 1
                day_had_unaffordable = False

                # 等权分配当前可用资金
                # 为防止佣金滑点导致透支，保留 0.5% 现金缓冲
                investable_cash = self.cash_balance * 0.995
                per_stock_cash = investable_cash / len(order.buy_instruments)

                for inst in order.buy_instruments:
                    self.buy_attempt_count += 1
                    price = price_lookup(inst, cycle.trade_date, exec_field)
                    if self.allow_fractional_shares:
                        shares = per_stock_cash / price
                    else:
                        lots = int(per_stock_cash / (price * self.lot_size))
                        shares = float(lots * self.lot_size)

                    if shares < (1.0 if self.allow_fractional_shares else float(self.lot_size)):
                        # 买不起一手 (100股)，严格记录不可负担跳过次数 (Affordability Skip)
                        self.unaffordable_buy_count += 1
                        day_had_unaffordable = True
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

                if day_had_unaffordable:
                    self.unaffordable_event_days += 1

        # --- Phase 2: 周内日频盯市估值 (Daily Marked-to-Market) ---
        for day in cycle.trading_days:
            # 每日以当日收盘价核算持仓市值
            held_market_value = 0.0
            act_held_count = 0
            for inst, shares in self.holdings.items():
                if shares > 0:
                    c_price = price_lookup(inst, day, "close")
                    held_market_value += shares * c_price
                    act_held_count += 1

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
                    daily_return=daily_ret,
                    num_holdings=act_held_count
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
        """导出完整的回测路径对象并汇总资本粒度诊断指标 (Capital Granularity Diagnostics)"""
        # 1. 目标与实际持仓统计 (排除尚未入场的 T0 锚定决策日)
        market_valuations = self.daily_valuations[1:] if len(self.daily_valuations) > 1 else self.daily_valuations

        target_mean = float(np.mean(self.target_capacities)) if self.target_capacities else float(self.topk)

        daily_holdings = [v.num_holdings for v in market_valuations]
        act_mean = float(np.mean(daily_holdings)) if daily_holdings else 0.0
        act_min = int(np.min(daily_holdings)) if daily_holdings else 0
        act_max = int(np.max(daily_holdings)) if daily_holdings else 0

        # 2. Affordability 统计
        unaff_buy_cnt = self.unaffordable_buy_count
        buy_att_cnt = self.buy_attempt_count
        unaff_ratio = (unaff_buy_cnt / buy_att_cnt) if buy_att_cnt > 0 else 0.0

        unaff_days = self.unaffordable_event_days
        reb_buy_days = self.rebalance_days_with_buy
        unaff_day_ratio = (unaff_days / reb_buy_days) if reb_buy_days > 0 else 0.0

        # 3. 现金与仓位暴露统计 (交易期)
        cash_ratios = [v.cash / v.total_asset for v in market_valuations if v.total_asset > 0]
        mean_cash = float(np.mean(cash_ratios)) if cash_ratios else 1.0
        max_cash = float(np.max(cash_ratios)) if cash_ratios else 1.0
        final_cash = float(cash_ratios[-1]) if cash_ratios else 1.0
        mean_invested = max(0.0, 1.0 - mean_cash)

        diagnostics = {
            "target_holdings_mean": round(target_mean, 2),
            "actual_holdings_mean": round(act_mean, 2),
            "actual_holdings_min": act_min,
            "actual_holdings_max": act_max,
            "buy_attempt_count": buy_att_cnt,
            "unaffordable_buy_count": unaff_buy_cnt,
            "unaffordable_buy_ratio": round(unaff_ratio, 4),
            "unaffordable_event_days": unaff_days,
            "unaffordable_event_day_ratio": round(unaff_day_ratio, 4),
            "mean_cash_ratio": round(mean_cash, 4),
            "max_cash_ratio": round(max_cash, 4),
            "final_cash_ratio": round(final_cash, 4),
            "mean_invested_ratio": round(mean_invested, 4),
        }

        return PortfolioPath(
            contestant_id=self.contestant_id,
            animal_id=self.animal_id,
            daily_valuations=list(self.daily_valuations),
            weekly_settlements=list(self.weekly_settlements),
            trades=list(self.trades),
            final_holdings=dict(self.holdings),
            diagnostics=diagnostics
        )

    def export_checkpoint(self) -> EngineCheckpoint:
        """导出当前组合引擎的完整无损状态快照"""
        last_cycle = self.weekly_settlements[-1].week_idx if self.weekly_settlements else -1
        last_date = self.weekly_settlements[-1].settle_date if self.weekly_settlements else ""
        return EngineCheckpoint(
            contestant_id=self.contestant_id,
            animal_id=self.animal_id,
            topk=self.topk,
            initial_cash=self.initial_cash,
            cash_balance=self.cash_balance,
            deal_price_mode=self.deal_price_mode,
            allow_fractional_shares=self.allow_fractional_shares,
            lot_size=self.lot_size,
            holdings=dict(self.holdings),
            daily_valuations=list(self.daily_valuations),
            weekly_settlements=list(self.weekly_settlements),
            trades=list(self.trades),
            target_capacities=list(self.target_capacities),
            buy_attempt_count=self.buy_attempt_count,
            unaffordable_buy_count=self.unaffordable_buy_count,
            rebalance_days_with_buy=self.rebalance_days_with_buy,
            unaffordable_event_days=self.unaffordable_event_days,
            cost_model_state={
                "open_cost": self.cost_model.open_cost,
                "close_cost": self.cost_model.close_cost,
                "min_cost": self.cost_model.min_cost,
            },
            last_cycle_idx=last_cycle,
            last_settle_date=last_date
        )

    @classmethod
    def from_checkpoint(cls, cp: EngineCheckpoint) -> "PortfolioEngine":
        """从无损状态快照恢复组合引擎实例"""
        cost_model = CostModel(
            open_cost=cp.cost_model_state.get("open_cost", 0.0005),
            close_cost=cp.cost_model_state.get("close_cost", 0.0015),
            min_cost=cp.cost_model_state.get("min_cost", 5.0),
        )
        engine = cls(
            contestant_id=cp.contestant_id,
            animal_id=cp.animal_id,
            topk=cp.topk,
            initial_cash=cp.initial_cash,
            cost_model=cost_model,
            deal_price_mode=cp.deal_price_mode,
            allow_fractional_shares=cp.allow_fractional_shares,
            lot_size=cp.lot_size,
        )
        engine.cash_balance = float(cp.cash_balance)
        engine.holdings = dict(cp.holdings)
        engine.daily_valuations = list(cp.daily_valuations)
        engine.weekly_settlements = list(cp.weekly_settlements)
        engine.trades = list(cp.trades)
        engine.target_capacities = list(cp.target_capacities)
        engine.buy_attempt_count = int(cp.buy_attempt_count)
        engine.unaffordable_buy_count = int(cp.unaffordable_buy_count)
        engine.rebalance_days_with_buy = int(cp.rebalance_days_with_buy)
        engine.unaffordable_event_days = int(cp.unaffordable_event_days)
        return engine

