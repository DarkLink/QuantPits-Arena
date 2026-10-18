"""Explicit observation windows shared by exporters and comparisons."""

import copy

import numpy as np
import pandas as pd


def window_curve(curve, start, end=None):
    series = curve.loc[start:end].copy()
    if series.empty or str(series.index[0])[:10] != str(start)[:10]:
        raise ValueError('The common anchor is not covered')
    if end is not None and str(series.index[-1])[:10] != str(end)[:10]:
        raise ValueError('The requested comparison cutoff is not covered')
    if not np.isfinite(series.to_numpy()).all() or (series <= 0).any():
        raise ValueError('Comparison window has a missing or invalid valuation')
    return series / series.iloc[0]


def compare_curves(reference, candidate, start, end):
    left, right = window_curve(reference, start, end), window_curve(candidate, start, end)
    if not left.index.equals(right.index):
        raise ValueError('Comparison paths cover different dates')
    return dict(reference=left, candidate=right, spread_pp=(right-left)*100,
                sessions=len(left)-1, start=start, end=end)


def observation_path(path, anchor, baseline=None):
    if not anchor:
        return path
    rows = [v for v in path.daily_valuations if v.date >= anchor]
    if not rows or rows[0].date != anchor:
        raise ValueError('Observation anchor is not present in the research path')
    result = copy.deepcopy(path)
    result.daily_valuations = copy.deepcopy(rows)
    base = rows[0].total_asset
    if base <= 0:
        raise ValueError('Observation anchor must have positive research assets')
    for i, value in enumerate(result.daily_valuations):
        value.nav = value.total_asset/base
        value.daily_return = value.nav/result.daily_valuations[i-1].nav-1 if i else 0.
    result.trades = [copy.deepcopy(v) for v in path.trades if v.date > anchor]
    result.weekly_settlements = [copy.deepcopy(v) for v in path.weekly_settlements if v.settle_date > anchor]
    baseline = baseline or {}
    diag = result.diagnostics
    for key in ('buy_attempt_count', 'unaffordable_buy_count', 'unaffordable_event_days',
                'rejected_order_count', 'stale_mark_count', 'rebalance_days_with_buy'):
        diag[key] = max(0, diag.get(key, 0)-baseline.get(key, 0))
    attempts = diag.get('buy_attempt_count', 0)
    diag['unaffordable_buy_ratio'] = diag.get('unaffordable_buy_count', 0)/attempts if attempts else 0.
    buy_days = diag.get('rebalance_days_with_buy', 0)
    diag['unaffordable_event_day_ratio'] = diag.get('unaffordable_event_days', 0)/buy_days if buy_days else 0.
    period = result.daily_valuations[1:]
    holdings = [v.num_holdings for v in period]
    ratios = [v.cash/v.total_asset for v in period]
    diag.update(actual_holdings_mean=float(np.mean(holdings)) if holdings else 0.,
                actual_holdings_min=min(holdings, default=0), actual_holdings_max=max(holdings, default=0),
                mean_cash_ratio=float(np.mean(ratios)) if ratios else 1.,
                max_cash_ratio=max(ratios, default=1.), final_cash_ratio=ratios[-1] if ratios else 1.,
                mean_invested_ratio=1-float(np.mean(ratios)) if ratios else 0.,
                observation_start=anchor, fees_pct=sum(v.cost for v in result.trades)/base*100,
                turnover=sum(v.turnover for v in result.weekly_settlements))
    return result
