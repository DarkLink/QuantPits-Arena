import json
import subprocess
from types import SimpleNamespace
import numpy as np
import pandas as pd
import pytest
from arena.reports.statistics import empirical,adjust
from arena.controls.compact import CompactDistribution
from arena.portfolio.types import PortfolioPath,DailyValuation
from arena.reports.sanitizer import DualTierExporter
from arena.config import REPO_ROOT


def test_exact_count_precision_and_840_threshold():
    assert empirical(1,np.zeros(100000))['empirical_p_value']==1/100001
    values=np.zeros(100000);values[:4]=1
    stats=empirical(1,values)
    assert stats['exceedance_count']==4
    assert stats['empirical_p_value']<.05/840
    values[4]=1
    assert empirical(1,values)['empirical_p_value']>.05/840
    # Strict boundary is attainable at N=16799, and fails strict significance.
    assert empirical(1,np.zeros(16799))['empirical_p_value']==.05/840
    result=adjust([.01,.03,.04])
    np.testing.assert_allclose(result['bonferroni'],[.03,.09,.12])
    np.testing.assert_allclose(result['holm'],[.03,.06,.06])
    np.testing.assert_allclose(result['bh'],[.03,.04,.04])


def test_csv_web_adapter_preserves_small_p_and_na(tmp_path):
    nav=PortfolioPath('CONTESTANT_A','robot',daily_valuations=[
        DailyValuation('2026-07-03',0,0,0,1.,0),DailyValuation('2026-07-06',0,0,0,1.2,.2)])
    reference=PortfolioPath('BENCHMARK','taotie',daily_valuations=nav.daily_valuations)
    exporter=DualTierExporter('TEST',tmp_path)
    registry=SimpleNamespace(get_anonymous_id=lambda c:c)
    exporter.export({('CONTESTANT_A','robot'):nav,('BENCHMARK','taotie'):reference},registry)
    exporter.export_monkey_reports({'P_22_3':CompactDistribution(np.zeros(100000),np.ones((100000,1))),
        'P_ALL_0':CompactDistribution(np.array([.2]),np.array([[1.2]]),True)},
        {('CONTESTANT_A','robot'):nav,('BENCHMARK','taotie'):reference},registry)
    frame=pd.read_csv(exporter.public_dir/'contestant_monkey_significance.csv')
    assert frame.loc[0,'empirical_p_value']==pytest.approx(1/100001)
    assert pd.isna(frame.loc[1,'empirical_p_value'])
    cfg=SimpleNamespace(season_id='TEST',raw_dict={},title='TEST',description='TEST',status='DRAFT',
        anchor_date='2026-07-03',end_date='2026-07-06')
    daily={'P_22_3':{
        '2026-07-03':dict(p05=1.,median=1.,p95=1.),
        '2026-07-06':dict(p05=.9999876543210988,median=1.,p95=1.0123456789012345)}}
    (exporter.public_dir/'monkey_timeline.json').write_text(json.dumps(daily))
    (exporter.public_dir/'monkey_settlement_timeline.json').write_text(json.dumps({'P_22_3':{'2026-07-06':daily['P_22_3']['2026-07-06']}}))
    file=exporter.export_web_payload(cfg,web_output_path=tmp_path/'payload.js',publish_auxiliary=False)
    payload=json.loads(file.read_text().split('window.ARENA_SEASONS_DATA["TEST"] = ',1)[1].rstrip().rstrip(';'))
    null=next(r for r in payload['monkey_null_distributions'] if r['strategy_spec']=='P_22_3')
    assert null['daily_quantiles']==daily['P_22_3']
    assert list(null['settlement_quantiles'])==['2026-07-06']
    program="global.window={};\n"+file.read_text()+"\nwindow.ARENA_DATA=window.ARENA_SEASONS_DATA.TEST;\n"+(REPO_ROOT/'web/js/adapter.js').read_text()+"\nconsole.log(JSON.stringify(window.arenaAdapter.paths.map(p=>[p.empirical_p_value,p.monkey_count,p.is_statistically_significant])));"
    output=subprocess.run(['node','-e',program],capture_output=True,text=True,check=True)
    data=json.loads(output.stdout)
    assert data[0]==[pytest.approx(1/100001),100000,True]
    assert data[1][0] is None and data[1][2] is False


def test_observation_payload_has_no_borrowed_history_or_significance(tmp_path):
    rows=[DailyValuation('2026-10-08',10,80,90,.9,0,1),
          DailyValuation('2026-10-09',20,100,120,1.2,1/3,1),
          DailyValuation('2026-10-12',18,100,118,1.18,-1/60,1)]
    paths={(cid,'robot'):PortfolioPath(cid,'robot',daily_valuations=rows) for cid in ('CONTESTANT_A','CONTESTANT_G')}
    registry=SimpleNamespace(get_anonymous_id=lambda c:c,
        get_contestant=lambda c:SimpleNamespace(observation_start='2026-10-09' if c=='CONTESTANT_G' else None))
    exporter=DualTierExporter('TEST',tmp_path)
    exporter.export(paths,registry)
    exporter.export_monkey_reports({'P_22_3':CompactDistribution(np.zeros(10),np.ones((10,1)))},paths,registry)
    cfg=SimpleNamespace(season_id='TEST',raw_dict={},title='TEST',description='TEST',status='DRAFT',
        anchor_date='2026-10-08',end_date='2026-10-12')
    import yaml
    public=tmp_path/'public_manifests';public.mkdir()
    (public/'contestant_g.yaml').write_text(yaml.safe_dump(dict(contestant_id='CONTESTANT_G',
        observation_start='2026-10-09',retrained_from='CONTESTANT_A',
        retraining_context=dict(information_cutoff='2026-10-09',first_execution='2026-10-12',
                               internal_note='excluded from public context'))))
    output=exporter.export_web_payload(cfg,manifests_public_dir=public,web_output_path=tmp_path/'payload.js',publish_auxiliary=False)
    payload=json.loads(output.read_text().split('window.ARENA_SEASONS_DATA["TEST"] = ',1)[1].rstrip().rstrip(';'))
    row=next(p for p in payload['paths'] if p['contestant_id']=='CONTESTANT_G')
    participant=payload['contestants'][0]
    assert participant['retrained_from']=='CONTESTANT_A'
    assert participant['retraining_context']==dict(information_cutoff='2026-10-09',first_execution='2026-10-12')
    assert row['test_status']=='observation'
    for field in ('empirical_p_value','is_statistically_significant','is_bonferroni_significant',
                  'percentile_rank','bonferroni_p','sharpe_ratio'):
        assert row[field] is None
    curve=payload['nav_timeline']['curves']['CONTESTANT_G_robot']
    assert curve[0] is None and curve[1:]==pytest.approx([1,118/120])
    assert payload['nav_timeline']['dates']==['2026-10-08','2026-10-09','2026-10-12']
    assert payload['nav_timeline']['curves']['CONTESTANT_A_robot']==pytest.approx([.9,1.2,1.18])
    original=next(p for p in payload['paths'] if p['contestant_id']=='CONTESTANT_A')
    assert original['observation_start'] is None
    assert original['test_status']=='random_control'
    assert original['empirical_p_value'] is not None
    report=(exporter.reports_dir/'leaderboard.md').read_text()
    assert 'Separate observation windows' in report and '2026-10-09' in report
