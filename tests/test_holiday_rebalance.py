"""Holiday Mondays skip orders while daily valuation and signal history continue."""

from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import Mock

import pandas as pd
import pytest

from arena.calendar import TradingCalendar, WeeklyCycle
from arena.portfolio import PortfolioEngine
from arena.portfolio.types import Order
from arena.runner import WeeklyCycleRunner
from arena.animals.sloth import Sloth
from arena.animals.snail import Snail
from arena.benchmarks import TaotieBenchmark, GhostTaotieBenchmark
from arena.controls.monkey import MonkeyColony, StrategySpec


@pytest.fixture
def calendar(tmp_path):
    path = tmp_path / "day.txt"
    path.write_text("\n".join([
        "2026-09-24", "2026-09-28", "2026-09-29", "2026-09-30",
        "2026-10-08", "2026-10-09", "2026-10-12", "2026-10-13",
        "2026-10-14", "2026-10-15", "2026-10-16",
    ]))
    return TradingCalendar(path)


def prices(instrument, date, field):
    assert instrument == "STOCK_01"
    if field == "open":
        assert date in {"2026-09-28", "2026-10-12"}
        return 10.0
    return {"2026-09-28": 11.0, "2026-09-29": 11.5,
            "2026-09-30": 12.0, "2026-10-08": 10.0,
            "2026-10-09": 9.0}.get(date, 10.0)


def test_calendar_holiday_and_next_monday(calendar):
    cycles = calendar.build_weekly_cycles("2026-09-24", "2026-10-16")
    assert [c.trade_date for c in cycles] == ["2026-09-28", None, "2026-10-12"]
    assert cycles[1].trading_days == ["2026-10-08", "2026-10-09"]
    assert cycles[1].decision_date == "2026-09-30"
    assert cycles[2].decision_date == "2026-10-09"
    assert [c.cycle_idx for c in cycles] == [0, 1, 2]


@pytest.mark.parametrize("cutoff", ["2026-09-28", "2026-09-29", "2026-09-30", "2026-10-08"])
def test_calendar_never_values_past_cutoff(calendar, cutoff):
    cycles = calendar.build_weekly_cycles("2026-09-24", cutoff)
    assert cycles[-1].settle_date == cutoff
    assert all(day <= cutoff for c in cycles for day in c.trading_days)


def funded_engine(first):
    engine = PortfolioEngine("CONTESTANT_A", "robot", topk=1,
                             initial_cash=100_000_000)
    engine.execute_weekly_cycle(first, Order(first.trade_date, ["STOCK_01"], [], True), prices)
    return engine


def assert_hold_only(engine, before, cycle):
    assert engine.holdings == before.holdings
    assert engine.cash_balance == before.cash_balance
    assert engine.trades == before.trades
    assert engine.target_capacities == before.target_capacities
    assert engine.buy_attempt_count == before.buy_attempt_count
    assert [v.date for v in engine.daily_valuations[-2:]] == cycle.trading_days
    settlement = engine.weekly_settlements[-1]
    assert settlement.weekly_cost == 0
    assert settlement.turnover == 0
    assert settlement.start_nav == before.daily_valuations[-1].nav
    assert settlement.weekly_return == pytest.approx(
        engine.daily_valuations[-1].nav / before.daily_valuations[-1].nav - 1)


def test_engine_preserves_portfolio_and_full_period_return(calendar):
    first, holiday = calendar.build_weekly_cycles("2026-09-24", "2026-10-09")
    engine = funded_engine(first)
    first_settlement = engine.weekly_settlements[0]
    assert first_settlement.start_nav == 1.0
    assert first_settlement.weekly_return == pytest.approx(first_settlement.end_nav - 1)
    before = deepcopy(engine)
    engine.execute_weekly_cycle(holiday, None, prices)
    assert_hold_only(engine, before, holiday)


def test_engine_rejects_holiday_orders_before_mutation(calendar):
    first, holiday = calendar.build_weekly_cycles("2026-09-24", "2026-10-09")
    engine = funded_engine(first)
    before = deepcopy(engine)
    with pytest.raises(ValueError, match="Valuation-only"):
        engine.execute_weekly_cycle(holiday, Order("2026-10-08", [], ["STOCK_01"]), prices)
    assert engine.daily_valuations == before.daily_valuations
    assert engine.trades == before.trades


@pytest.mark.parametrize("benchmark_class", [TaotieBenchmark, GhostTaotieBenchmark])
def test_benchmarks_skip_order_generation(calendar, benchmark_class):
    first, holiday = calendar.build_weekly_cycles("2026-09-24", "2026-10-09")
    benchmark = benchmark_class(initial_cash=100_000_000)
    benchmark.step(first, ["STOCK_01"], prices)
    before = deepcopy(benchmark.engine)
    benchmark.engine.generate_order = Mock(side_effect=AssertionError("Unexpected order"))
    benchmark.step(holiday, price_lookup_fn=prices)
    assert_hold_only(benchmark.engine, before, holiday)


@pytest.mark.parametrize("passive", [False, True])
def test_monkey_batch_and_step_hold_on_holiday(calendar, passive):
    cycles = calendar.build_weekly_cycles("2026-09-24", "2026-10-09")
    colony = MonkeyColony(colony_size=2)
    spec = StrategySpec("TEST", 0 if passive else 1, 0 if passive else 1, passive)
    provider = Mock(return_value=["STOCK_01"])
    paths = colony.run_group(spec, cycles, provider, prices, initial_cash=100_000_000)
    assert provider.call_count == 1
    for path in paths:
        assert {t.date for t in path.trades} == {"2026-09-28"}
        assert path.weekly_settlements[-1].turnover == 0
        assert path.nav_series.index[-1].strftime("%Y-%m-%d") == "2026-10-09"
    engine = funded_engine(cycles[0])
    before = deepcopy(engine)
    colony.generate_monkey_score = Mock(side_effect=AssertionError("Unexpected score"))
    colony.step_group(spec, cycles[1], [engine], [], prices)
    assert_hold_only(engine, before, cycles[1])


def make_runner(calendar, tmp_path):
    runner = WeeklyCycleRunner(anchor_date="2026-09-24", end_date="2026-10-16",
                               calendar=calendar, animals=[Sloth(1), Snail(1)],
                               registry=SimpleNamespace(), run_dir=tmp_path)
    contestant = SimpleNamespace(contestant_id="CONTESTANT_A")
    runner.adapters[contestant.contestant_id] = SimpleNamespace(
        predict=lambda start_date, end_date: pd.Series(1.0, index=["STOCK_01"]))
    runner.signal_history[contestant.contestant_id] = {0: pd.Series(0.5, index=["STOCK_01"])}
    first = runner.cycles[0]
    for animal in runner.animals:
        runner.engines[(contestant.contestant_id, animal.animal_id)] = funded_engine(first)
    runner.taotie_benchmark.engine = funded_engine(first)
    runner.ghost_taotie_benchmark.engine = funded_engine(first)
    return runner, [contestant]


def test_runner_hold_only_keeps_delay_history_and_exports_no_orders(calendar, tmp_path):
    runner, contestants = make_runner(calendar, tmp_path)
    holiday, monday = runner.cycles[1:]
    runner.export_isolated_orders = Mock(side_effect=AssertionError("Unexpected export"))
    engines = list(runner.engines.values()) + [runner.taotie_benchmark.engine,
                                             runner.ghost_taotie_benchmark.engine]
    before = [deepcopy(e) for e in engines]
    for engine in engines:
        engine.generate_order = Mock(side_effect=AssertionError("Unexpected order"))
    runner.step_cycle(holiday, contestants, prices)
    assert runner.last_completed_cycle_idx == 1
    for engine, old in zip(engines, before):
        assert_hold_only(engine, old, holiday)
    history = runner.signal_history["CONTESTANT_A"]
    assert set(history) == {0, 1}
    for animal in runner.animals:
        pd.testing.assert_series_equal(animal.transform_signal(pd.Series(dtype=float), history,
                                                              monday.cycle_idx), history[1])


def test_friday_does_not_precommit_holiday_orders(calendar, tmp_path):
    runner, contestants = make_runner(calendar, tmp_path)
    runner.export_isolated_orders = Mock()
    current, next_orders = runner.step_friday_cycle(runner.cycles[0], contestants, prices,
                                                   pending_orders={})
    assert current == {}
    assert next_orders is None
    runner.export_isolated_orders.assert_not_called()
    assert 1 in runner.signal_history["CONTESTANT_A"]


def test_friday_valuation_then_precommits_next_monday(calendar, tmp_path):
    runner, contestants = make_runner(calendar, tmp_path)
    runner.export_isolated_orders = Mock()
    settled, pending = runner.step_friday_cycle(runner.cycles[1], contestants, prices)
    assert settled == {}
    assert pending
    assert all(order.trade_date == "2026-10-12" for order in pending.values() if order)
    assert runner.export_isolated_orders.call_count == 1
    assert runner.export_isolated_orders.call_args.args[0] == runner.cycles[2]


def test_runner_rejects_pending_holiday_orders_before_valuation(calendar, tmp_path):
    runner, contestants = make_runner(calendar, tmp_path)
    engine = next(iter(runner.engines.values()))
    previous_dates = [v.date for v in engine.daily_valuations]
    with pytest.raises(ValueError, match="Valuation-only"):
        runner.step_friday_cycle(runner.cycles[1], contestants, prices,
                                 pending_orders={("CONTESTANT_A", "sloth-1"):
                                                 Order("2026-10-08", [], ["STOCK_01"])})
    assert [v.date for v in engine.daily_valuations] == previous_dates
