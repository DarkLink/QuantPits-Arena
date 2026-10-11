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
    file=exporter.export_web_payload(cfg,web_output_path=tmp_path/'payload.js',publish_auxiliary=False)
    program="global.window={};\n"+file.read_text()+"\nwindow.ARENA_DATA=window.ARENA_SEASONS_DATA.TEST;\n"+(REPO_ROOT/'web/js/adapter.js').read_text()+"\nconsole.log(JSON.stringify(window.arenaAdapter.paths.map(p=>[p.empirical_p_value,p.monkey_count,p.is_statistically_significant])));"
    output=subprocess.run(['node','-e',program],capture_output=True,text=True,check=True)
    data=json.loads(output.stdout)
    assert data[0]==[pytest.approx(1/100001),100000,True]
    assert data[1][0] is None and data[1][2] is False
