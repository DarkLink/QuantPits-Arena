"""Observation and paired windows retain their own explicit close anchor."""
import pandas as pd
import pytest

from arena.portfolio.types import PortfolioPath, DailyValuation, TradeRecord
from arena.reports.comparison import compare_curves, observation_path


def test_common_window_rebases_both_paths_and_uses_percentage_points():
    dates=['2026-10-09','2026-10-12','2026-10-13']
    left=pd.Series([2.,2.2,2.1],index=dates)
    right=pd.Series([3.,3.6,3.3],index=dates)
    result=compare_curves(left,right,dates[0],dates[-1])
    assert result['reference'].tolist()==pytest.approx([1,1.1,1.05])
    assert result['candidate'].tolist()==pytest.approx([1,1.2,1.1])
    assert result['spread_pp'].tolist()==pytest.approx([0,10,5])
    assert result['sessions']==2
    later=compare_curves(left,right,dates[1],dates[-1])
    assert later['spread_pp'].iloc[-1]==pytest.approx((3.3/3.6-2.1/2.2)*100)


def test_comparison_rejects_missing_or_unmatched_observations():
    left=pd.Series([1.,1.1],index=['2026-10-09','2026-10-12'])
    right=pd.Series([1.,None],index=left.index)
    with pytest.raises(ValueError,match='missing or invalid'):
        compare_curves(left,right,'2026-10-09','2026-10-12')
    with pytest.raises(ValueError,match='anchor'):
        compare_curves(left,left,'2026-10-08','2026-10-12')
    with pytest.raises(ValueError,match='cutoff'):
        compare_curves(left,left,'2026-10-09','2026-10-13')
    assert compare_curves(left,left,'2026-10-09','2026-10-12')['spread_pp'].eq(0).all()


def test_observation_excludes_borrowed_history_and_keeps_first_loss():
    rows=[DailyValuation('2026-10-08',10,80,90,.9,0,1),
          DailyValuation('2026-10-09',20,100,120,1.2,1/3,1),
          DailyValuation('2026-10-12',18,100,118,1.18,-1/60,1)]
    path=PortfolioPath('CONTESTANT_G','robot',daily_valuations=rows,
        trades=[TradeRecord('2026-10-08','STOCK_01','BUY',1,1,1,1),
                TradeRecord('2026-10-12','STOCK_02','BUY',1,1,1,2)],
        diagnostics={'buy_attempt_count':8,'unaffordable_buy_count':3})
    view=observation_path(path,'2026-10-09',{'buy_attempt_count':6,'unaffordable_buy_count':2})
    assert view.nav_series.tolist()==pytest.approx([1,118/120])
    assert view.total_return==pytest.approx(-2/120)
    assert view.max_drawdown==pytest.approx(2/120)
    assert view.diagnostics['buy_attempt_count']==2
    assert view.diagnostics['unaffordable_buy_ratio']==.5
    assert view.diagnostics['fees_pct']==pytest.approx(2/120*100)
    assert len(view.trades)==1
    assert path.daily_valuations[0].nav==.9
