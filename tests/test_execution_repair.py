from copy import deepcopy
from types import SimpleNamespace
import numpy as np
import pandas as pd
import pytest
from arena.calendar import WeeklyCycle
from arena.data.market import MarketDataProvider
from arena.portfolio.engine import PortfolioEngine
from arena.portfolio.types import Order
from arena.portfolio.policy import ExecutionPolicy
from arena.controls.monkey import MonkeyColony, CANONICAL_STRATEGY_SPECS
from arena.controls.compact import evaluate_batch, pack_inputs


def cycle(idx=0, days=None):
    days=days or ['2026-07-06','2026-07-07','2026-07-08']
    return WeeklyCycle(idx,'2026-07-03',days[0],days[-1],days)


def test_invalid_sell_and_buy_are_atomic():
    engine=PortfolioEngine('CONTESTANT_A','robot')
    engine.holdings={'STOCK_01':100}
    before=engine.cash_balance
    engine.execute_weekly_cycle(cycle(),Order('2026-07-06',['STOCK_02'],['STOCK_01']),
        lambda i,d,f: 10 if f=='close' else np.nan)
    assert engine.holdings=={'STOCK_01':100}
    assert engine.cash_balance==before
    assert not engine.trades
    assert engine.rejected_orders[0]['side']=='SELL'


def test_cached_and_absent_missing_quotes_agree():
    provider=MarketDataProvider(use_real_qlib=True)
    provider._cache[('STOCK_01','2026-07-03')]={'real_close':10.,'adj_close':10.,'factor':1.}
    provider._cache[('STOCK_01','2026-07-06')]={'real_close':0.,'real_open':0.}
    assert provider.get_real_price('STOCK_01','2026-07-06','close')==10
    assert provider.get_real_price('STOCK_01','2026-07-07','close')==10
    assert np.isnan(provider.get_execution_price('STOCK_01','2026-07-06'))
    assert np.isnan(provider.get_execution_price('STOCK_01','2026-07-07'))


def test_partial_week_resume_and_reentry():
    def price(i,d,f): return 10. if f=='open' else 11.
    full=PortfolioEngine('CONTESTANT_A','robot'); partial=deepcopy(full)
    order=Order('2026-07-06',['STOCK_01'],[])
    full.execute_weekly_cycle(cycle(),order,price)
    partial.execute_weekly_cycle(cycle(days=['2026-07-06']),order,price)
    partial=PortfolioEngine.from_checkpoint(partial.export_checkpoint())
    partial.execute_weekly_cycle(cycle(),order,price)
    partial.execute_weekly_cycle(cycle(),order,price)
    assert partial.daily_valuations==full.daily_valuations
    assert partial.trades==full.trades
    assert partial.weekly_settlements==full.weekly_settlements


def test_frozen_intent_avoids_future_quote_reads():
    engine=PortfolioEngine('CONTESTANT_A','robot')
    score=pd.Series([2.,1.],index=['STOCK_01','STOCK_02'])
    order=engine.freeze_order(score,'2026-07-06',topk=1,n_drop=1)
    score.iloc[0]=-10
    assert order.frozen_score.iloc[0]==2
    engine.execute_weekly_cycle(cycle(),order,lambda i,d,f: np.nan if i=='STOCK_01' and f=='open' else 10.)
    assert list(engine.holdings)==['STOCK_02']


def test_verified_events_are_idempotent_and_strict_profile_fails():
    engine=PortfolioEngine('CONTESTANT_A','robot'); engine.holdings={'STOCK_01':100}
    before=engine.cash_balance
    event={'event_id':'EVENT_01','instrument':'STOCK_01','share_ratio':2.,'cash_per_share':.5}
    engine.apply_corporate_events('2026-07-06',[event,event])
    assert engine.holdings['STOCK_01']==200
    assert engine.cash_balance-before==50
    with pytest.raises(ValueError,match='coverage'):
        MarketDataProvider().preflight('strict_execution')


def test_compact_reference_all_specs_and_global_id_prefix():
    cycles=[cycle(0),WeeklyCycle(1,'2026-07-10','2026-07-13','2026-07-14',['2026-07-13','2026-07-14']),
            WeeklyCycle(2,'2026-07-17',None,'2026-07-20',['2026-07-20'])]
    names=[f'STOCK_{j:03d}' for j in range(150)]
    pools=[names[:140],names[10:],[]]
    history={i:pd.Series(1.,index=p) for i,p in enumerate(pools)}
    provider=MarketDataProvider(use_real_qlib=True)
    for d in ['2026-07-03']+[d for c in cycles for d in c.trading_days]:
        for j,n in enumerate(names):
            p=8+j*.7
            provider._cache[(n,d)]={'real_open':p,'real_close':p*(1+int(d[-2:])*.001),'factor':1.,'adj_close':p}
            provider._tradable_cache[(n,d)]=j%13!=0
    provider._cache[(names[11],'2026-07-13')]['real_open']=np.nan
    provider.direction_status[(names[12],'2026-07-13','SELL')]=False
    runner=SimpleNamespace(signal_history={'CONTESTANT_A':history},deal_price_mode='open')
    inputs,_=pack_inputs(runner,cycles,provider.get_real_price,provider.is_tradable)
    policy=ExecutionPolicy()
    result=evaluate_batch(inputs,policy,500000.,7,4,threads=2)
    specs=[s for s in CANONICAL_STRATEGY_SPECS.values() if not s.passive_pool]
    for m in range(4):
        for s,spec in enumerate(specs):
            engine=PortfolioEngine('CONTESTANT_A','robot',topk=spec.topk)
            for c,pool in zip(cycles,pools):
                if c.has_rebalance:
                    scores=MonkeyColony().generate_monkey_score(m+7,c.cycle_idx,pool)
                    order=engine.generate_order(scores,spec.topk,spec.n_drop,c.trade_date,c.cycle_idx==0,provider.is_tradable,provider.get_real_price)
                else: order=None
                engine.execute_weekly_cycle(c,order,provider.get_real_price,provider.is_tradable)
            assert result['returns'][m,s]==pytest.approx(engine.to_portfolio_path().total_return,abs=1e-12)
            assert result['weekly_nav'][m,s]==pytest.approx([w.end_nav for w in engine.weekly_settlements],abs=1e-12)
    pieces=[evaluate_batch(inputs,policy,500000.,i,2,threads=1)['returns'] for i in [7,9]]
    np.testing.assert_array_equal(result['returns'],np.concatenate(pieces))


def test_split_value_and_record_payment_survive_sale():
    engine=PortfolioEngine('CONTESTANT_A','robot')
    first=WeeklyCycle(0,'2026-07-03','2026-07-06','2026-07-06',['2026-07-06'])
    engine.execute_weekly_cycle(first,Order('2026-07-06',['STOCK_01'],[]),lambda i,d,f:10.)
    before_asset=engine.cash_balance+engine.holdings['STOCK_01']*10
    shares=engine.holdings['STOCK_01']
    engine.apply_corporate_events('2026-07-07',[{'event_id':'SPLIT_01','instrument':'STOCK_01','share_ratio':2.}])
    assert engine.cash_balance+engine.holdings['STOCK_01']*5==pytest.approx(before_asset)
    record={'event_id':'RECORD_01','entitlement_id':'DIVIDEND_01','event_type':'cash_record','instrument':'STOCK_01','cash_per_share':.5}
    engine.apply_corporate_events('2026-07-07',[record])
    engine.holdings.clear()
    engine=PortfolioEngine.from_checkpoint(engine.export_checkpoint())
    before=engine.cash_balance
    pay={'event_id':'PAY_01','entitlement_id':'DIVIDEND_01','event_type':'cash_payment','instrument':'STOCK_01'}
    engine.apply_corporate_events('2026-07-08',[pay,pay])
    assert engine.cash_balance-before==shares


def test_missing_mark_rolls_back_entire_cycle():
    engine=PortfolioEngine('CONTESTANT_A','robot')
    before=engine.export_checkpoint()
    with pytest.raises(ValueError,match='valuation'):
        engine.execute_weekly_cycle(cycle(),Order('2026-07-06',['STOCK_01'],[]),lambda i,d,f:10. if f=='open' else np.nan)
    assert engine.export_checkpoint()==before


def test_disk_commitment_roundtrip_and_tamper(tmp_path):
    import pickle
    from arena.runner.commitments import save_commitment,load_commitment
    current=cycle()
    order=PortfolioEngine.freeze_order(pd.Series([2.,1.],index=['STOCK_01','STOCK_02']),current.trade_date,topk=1,n_drop=1)
    path=tmp_path/'intent.pkl';policy=ExecutionPolicy().signature
    save_commitment(path,{('CONTESTANT_A','robot'):order},current,policy)
    loaded=load_commitment(path,current,policy)
    pd.testing.assert_series_equal(loaded[('CONTESTANT_A','robot')].frozen_score,order.frozen_score)
    with path.open('rb') as stream: envelope=pickle.load(stream)
    envelope['payload']+=b'altered'
    with path.open('wb') as stream: pickle.dump(envelope,stream)
    with pytest.raises(ValueError,match='hash'):
        load_commitment(path,current,policy)


def test_compact_disk_append_same_week_and_new_week(tmp_path):
    from arena.controls.compact import run_compact
    names=[f'STOCK_{j:03d}' for j in range(30)]
    first=cycle(days=['2026-07-06'])
    complete=cycle()
    following=WeeklyCycle(1,'2026-07-10','2026-07-13','2026-07-14',['2026-07-13','2026-07-14'])
    history={i:pd.Series(1.,index=names) for i in range(2)}
    def prices(i,d,f):return 10. if f=='open' else 10+int(d[-2:])*.01
    passive=PortfolioEngine('BENCHMARK','taotie')
    runner=SimpleNamespace(signal_history={'CONTESTANT_A':history},deal_price_mode='open',
        execution_policy=ExecutionPolicy(),initial_cash=500000.,season_id='TEST',
        registry=SimpleNamespace(list_contestants=lambda:[]),
        _setup_market_provider=lambda *args:(prices,None),cycles=[first],
        taotie_benchmark=SimpleNamespace(engine=passive))
    run_compact(runner,tmp_path/'incremental',8,4,threads=1)
    runner.cycles=[complete,following]
    incremental=run_compact(runner,tmp_path/'incremental',8,4,threads=2)
    full=run_compact(runner,tmp_path/'full',8,4,threads=1)
    for spec in incremental:
        np.testing.assert_array_equal(incremental[spec].returns,full[spec].returns)
        np.testing.assert_array_equal(incremental[spec].weekly_nav,full[spec].weekly_nav)
    # Retry is idempotent; an altered historical price invalidates the generation.
    retry=run_compact(runner,tmp_path/'incremental',8,4,threads=1)
    np.testing.assert_array_equal(retry['P_22_3'].returns,full['P_22_3'].returns)
    runner._setup_market_provider=lambda *args:(lambda i,d,f:11.,None)
    with pytest.raises(ValueError,match='Historical'):
        run_compact(runner,tmp_path/'incremental',8,4,threads=1)


def test_market_load_maps_fields_by_name_not_position(monkeypatch):
    import sys
    # A permuted frame catches a positional mapping bug independently of engine parity.
    frame=pd.DataFrame([[.5,1000.,10.,9.],[np.nan,1000.,10.,9.]],
        index=pd.MultiIndex.from_tuples([('STOCK_01',pd.Timestamp('2026-07-06')),('STOCK_02',pd.Timestamp('2026-07-06'))]),
        columns=['$factor','$volume','$close','$open'])
    monkeypatch.setitem(sys.modules,'qlib',SimpleNamespace(init=lambda **kwargs:None))
    monkeypatch.setitem(sys.modules,'qlib.data',SimpleNamespace(D=SimpleNamespace(features=lambda *args,**kwargs:frame)))
    provider=MarketDataProvider(use_real_qlib=True)
    provider.load_qlib_data(['STOCK_01','STOCK_02'],'2026-07-06','2026-07-06')
    assert provider.get_execution_price('STOCK_01','2026-07-06','open')==18.
    assert provider.get_execution_price('STOCK_01','2026-07-06','close')==20.
    assert np.isnan(provider.get_execution_price('STOCK_02','2026-07-06','open'))


def test_runner_restore_rejects_capital_change():
    from arena.runner.weekly_cycle import WeeklyCycleRunner
    runner=WeeklyCycleRunner(mock_mode=True)
    runner._init_engines(runner.registry.list_contestants()[:1])
    state=runner.export_checkpoint()
    changed=WeeklyCycleRunner(mock_mode=True,initial_cash=1000000.)
    with pytest.raises(ValueError,match='capital'):
        changed.load_checkpoint(state)


def test_feature_slice_reads_nonzero_float32_offset(tmp_path):
    from arena.benchmarks.index import read_feature_slice
    path=tmp_path/'index.bin'
    np.array([13.,10.,11.,12.],dtype='<f4').tofile(path)
    np.testing.assert_array_equal(read_feature_slice(path,14,15),[11.,12.])
    with pytest.raises(ValueError,match='cover'):
        read_feature_slice(path,12,15)


def test_published_source_change_blocks_continuation(tmp_path):
    import json
    from arena.evaluation import verify_execution_sources
    public=tmp_path/'public';public.mkdir()
    (public/'evaluation_manifest.json').write_text(json.dumps({'execution_source_hashes':{'arena/portfolio/engine.py':'invalid_digest'}}))
    with pytest.raises(ValueError,match='execution sources changed'):
        verify_execution_sources(tmp_path)
