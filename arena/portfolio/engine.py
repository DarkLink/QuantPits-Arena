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
        greedy_allocation: bool = False,        # 是否开启贪心瀑布流再分配 (消除一手约束导致的死现金沉淀)
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
        self.greedy_allocation = greedy_allocation

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
        self.rejected_orders = []
        self.applied_events = set()
        self.stale_marks = []
        self.cash_entitlements = {}

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

        # Stable ties preserve the declared input order. Pool membership is independent
        # of affordability and opening execution status.
        score = score[np.isfinite(score.to_numpy())]
        ranked = list(score.sort_values(ascending=False, kind="stable").index)
        current = sorted(self.get_current_held_instruments())
        effective_k = len(ranked) if topk <= 0 else min(topk, len(ranked))
        budget = (self.cash_balance * .995 if not current or is_first_entry else self.initial_cash) / max(effective_k, 1)
        candidates = []
        for inst in ranked:
            if not self._tradable(tradability_filter, inst, trade_date, "BUY"):
                continue
            if price_lookup is not None:
                p = self._price(price_lookup, inst, trade_date, self.deal_price_mode, True)
                if not np.isfinite(p) or p <= 0:
                    continue
                if not passive_pool and not self.allow_fractional_shares and inst not in current and p * self.lot_size > budget:
                    continue
            candidates.append(inst)
        capacity = len(candidates) if topk <= 0 else min(topk, len(candidates))
        self.target_capacities.append(capacity)
        if not current or is_first_entry:
            return Order(trade_date, candidates[:capacity], [], True)
        sellable = [i for i in current if self._tradable(tradability_filter, i, trade_date, "SELL")
                    and (price_lookup is None or self._price(price_lookup, i, trade_date, self.deal_price_mode, True) > 0)]
        out = [i for i in sellable if i not in score.index]
        inside = [i for i in sellable if i in score.index]
        if passive_pool or (n_drop == 0 and capacity >= len(candidates)):
            return Order(trade_date, [i for i in candidates if i not in current], out)
        sells = out[:n_drop]
        target = candidates[:capacity]
        # Lowest score exits first; deterministic identifier breaks equal-score ties.
        active = sorted(inside, key=lambda i: (i in target, float(score[i]), i))
        entrants = [i for i in target if i not in current]
        count = min(max(0, n_drop-len(sells)), len(entrants), len(active))
        sells += active[:count]
        need = max(0, capacity - (len(current)-len(sells)))
        buys = [i for i in candidates if i not in current or i in sells][:need]
        return Order(trade_date, buys, sells)

    @staticmethod
    def freeze_order(score, trade_date, **policy):
        if score is None:
            return None
        return Order(trade_date, [], [], frozen_score=score.copy(deep=True), policy=policy)

    @staticmethod
    def _tradable(callback, instrument, date, side):
        if callback is None:
            return True
        owner = getattr(callback, "__self__", None)
        if owner is not None and hasattr(owner, "direction_status"):
            return callback(instrument, date, side)
        return callback(instrument, date)

    @staticmethod
    def _price(callback, instrument, date, field, execution=False):
        owner = getattr(callback, "__self__", None)
        try:
            if execution and owner is not None and hasattr(owner, "get_execution_price"):
                return owner.get_execution_price(instrument, date, field)
            return float(callback(instrument, date, field))
        except (KeyError, ValueError, TypeError):
            return np.nan

    def apply_corporate_events(self, date, events):
        for event in events:
            key = event["event_id"]
            if key in self.applied_events:
                continue
            ratio = float(event.get("share_ratio", 1.0))
            dividend = float(event.get("cash_per_share", 0.0))
            if not np.isfinite(ratio) or ratio <= 0 or not np.isfinite(dividend) or dividend < 0:
                raise ValueError("Invalid verified corporate event")
            inst = event["instrument"]
            shares = self.holdings.get(inst, 0.0)
            kind = event.get("event_type", "effective_action")
            entitlement = event.get("entitlement_id", key)
            if kind == "cash_record":
                if entitlement in self.cash_entitlements:
                    raise ValueError("Duplicate dividend entitlement")
                self.cash_entitlements[entitlement] = shares * dividend
            elif kind == "cash_payment":
                if entitlement not in self.cash_entitlements:
                    raise ValueError("Missing recorded dividend entitlement")
                self.cash_balance += self.cash_entitlements.pop(entitlement)
            elif kind == "effective_action":
                self.cash_balance += shares * dividend
            else:
                raise ValueError("Unknown verified event type")
            if shares and kind == "effective_action":
                self.holdings[inst] = shares * ratio
            self.applied_events.add(key)

    def execute_weekly_cycle(self, cycle, order, price_lookup, tradability_filter=None):
        before = self.export_checkpoint()
        try:
            return self._execute_weekly_cycle(cycle, order, price_lookup, tradability_filter)
        except BaseException:
            restored = self.from_checkpoint(before)
            self.__dict__.update(restored.__dict__)
            raise

    def _execute_weekly_cycle(
        self,
        cycle: WeeklyCycle,
        order: Optional[Order],
        price_lookup: Callable[[str, str, str], float],
        tradability_filter: Optional[Callable[[str, str], bool]] = None,
    ) -> WeeklySettlement:
        """
        执行一个完整周频周期的撮合与日频盯市估值。

        Args:
            cycle: WeeklyCycle 对象 (包含 trade_date, settle_date, trading_days)
            order: 周一调仓订单 (若为 None 则本周不调仓)
            price_lookup: 价格查询函数 (instrument, date, field='open'|'close') -> float
            tradability_filter: 可交易性检查函数 (instrument, date) -> bool (停牌标的无法成交)
        """
        if not cycle.has_rebalance and order is not None:
            raise ValueError("Valuation-only cycles cannot execute rebalance orders")
        last_date = self.daily_valuations[-1].date if self.daily_valuations else ""
        if last_date >= cycle.settle_date and self.weekly_settlements:
            return self.weekly_settlements[-1]
        owner = getattr(price_lookup, "__self__", None)
        if cycle.trade_date and cycle.trade_date > last_date and owner is not None and hasattr(owner, "corporate_events"):
            self.apply_corporate_events(cycle.trade_date, owner.corporate_events(cycle.trade_date))
        if order is not None and order.frozen_score is not None and cycle.trade_date and cycle.trade_date > last_date:
            order = self.generate_order(order.frozen_score, trade_date=cycle.trade_date,
                                        price_lookup=price_lookup, tradability_filter=tradability_filter,
                                        **order.policy)
        if cycle.trade_date and cycle.trade_date <= last_date:
            order = None
        if not cycle.has_rebalance and order is not None:
            raise ValueError("Valuation-only cycles cannot execute rebalance orders")

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
        previous = next((w for w in self.weekly_settlements if w.week_idx == cycle.cycle_idx), None)
        start_week_nav = previous.start_nav if previous else prev_nav
        weekly_cost = 0.0
        turnover_value = 0.0

        # --- Phase 1: 周一开盘执行订单 ---
        if order is not None:
            exec_field = self.deal_price_mode  # "open" 或 "close"

            # 1.1 先执行卖出订单，释放现金
            for inst in order.sell_instruments:
                if inst in self.holdings and self.holdings[inst] > 0:
                    # 停牌/不可交易标的无法卖出，继续留在持仓中 ("烂在手里")
                    if tradability_filter is not None and not self._tradable(tradability_filter, inst, cycle.trade_date, "SELL"):
                        continue

                    shares = self.holdings[inst]
                    price = self._price(price_lookup, inst, cycle.trade_date, exec_field, True)
                    if not np.isfinite(price) or price <= 0:
                        self.rejected_orders.append({"date": cycle.trade_date, "instrument": inst, "side": "SELL", "reason": "invalid_quote"})
                        continue
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
                    if not self._tradable(tradability_filter, inst, cycle.trade_date, "BUY"):
                        self.rejected_orders.append({"date": cycle.trade_date, "instrument": inst, "side": "BUY", "reason": "direction_status"})
                        continue
                    try:
                        price = self._price(price_lookup, inst, cycle.trade_date, exec_field, True)
                    except Exception:
                        # 无法获取有效真实价格，严禁使用模拟数据撮合，直接跳过
                        continue
                    if not np.isfinite(price) or price <= 0:
                        continue
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

                # 1.3 贪心瀑布流再分配 (Greedy Waterfall Reallocation)
                # 若开启 greedy_allocation 且存在买不起跳过/零头找零沉淀的富余现金：
                # 只要剩余现金仍足以购买至少某只标的 1 手，优先挑选“当前持仓市值最低”的标的追加 1 手，
                # 从而在最大化资金利用率 (投资仓位 >95%) 的同时以离散整手最佳逼近等权分配。
                if self.greedy_allocation and not self.allow_fractional_shares and self.cash_balance > 0:
                    price_cache: Dict[str, float] = {}
                    for inst in order.buy_instruments:
                        try:
                            p = self._price(price_lookup, inst, cycle.trade_date, exec_field, True)
                            if np.isfinite(p) and p > 0 and self._tradable(tradability_filter, inst, cycle.trade_date, "BUY"):
                                price_cache[inst] = p
                        except Exception:
                            pass

                    while True:
                        candidates = []
                        for inst, p in price_cache.items():
                            lot_gross = self.lot_size * p
                            lot_cost = self.cost_model.calculate_buy_cost(lot_gross)
                            total_needed = lot_gross + lot_cost
                            if total_needed <= self.cash_balance:
                                cur_val = self.holdings.get(inst, 0.0) * p
                                candidates.append((cur_val, p, inst, lot_gross, lot_cost, total_needed))

                        if not candidates:
                            break

                        # 优先选择当前持仓市值最少者，若市值相同则选择单手成本较低者
                        candidates.sort(key=lambda x: (x[0], x[1]))
                        _, p, best_inst, lot_gross, lot_cost, total_spent = candidates[0]

                        self.cash_balance -= total_spent
                        self.holdings[best_inst] = self.holdings.get(best_inst, 0.0) + float(self.lot_size)
                        weekly_cost += lot_cost
                        turnover_value += lot_gross

                        self.trades.append(
                            TradeRecord(
                                date=cycle.trade_date,
                                instrument=best_inst,
                                direction="BUY",
                                price=p,
                                shares=float(self.lot_size),
                                value=lot_gross,
                                cost=lot_cost
                            )
                        )

        # --- Phase 2: 周内日频盯市估值 (Daily Marked-to-Market) ---
        for day in cycle.trading_days:
            if day <= last_date:
                continue
            if owner is not None and hasattr(owner, "corporate_events"):
                self.apply_corporate_events(day, owner.corporate_events(day))
            # 每日以当日收盘价核算持仓市值
            held_market_value = 0.0
            act_held_count = 0
            for inst, shares in self.holdings.items():
                if shares > 0:
                    c_price = self._price(price_lookup, inst, day, "close")
                    if not np.isfinite(c_price) or c_price <= 0:
                        raise ValueError("Held position has no valid valuation quote")
                    if owner is not None and hasattr(owner, "quote"):
                        q = owner.quote(inst, day)
                        if q.stale:
                            self.stale_marks.append({"date": day, "instrument": inst, "source_date": q.source_date})
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
        if previous:
            settlement.weekly_cost += previous.weekly_cost
            settlement.turnover += previous.turnover
            self.weekly_settlements.remove(previous)
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
            "rejected_order_count": len(self.rejected_orders),
            "stale_mark_count": len(self.stale_marks),
            "turnover_convention": "buy_plus_sell_over_start_assets",
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
            last_settle_date=last_date,
            greedy_allocation=self.greedy_allocation,
            rejected_orders=list(self.rejected_orders),
            applied_events=sorted(self.applied_events),
            stale_marks=list(self.stale_marks),
            cash_entitlements=dict(self.cash_entitlements),
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
            greedy_allocation=getattr(cp, "greedy_allocation", False),
        )
        engine.rejected_orders = list(getattr(cp, "rejected_orders", []))
        engine.applied_events = set(getattr(cp, "applied_events", []))
        engine.stale_marks = list(getattr(cp, "stale_marks", []))
        engine.cash_entitlements = dict(getattr(cp, "cash_entitlements", {}))
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

