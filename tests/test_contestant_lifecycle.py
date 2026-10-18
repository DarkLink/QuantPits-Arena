"""Admission preserves economic state while isolating mutable histories."""
import copy
import json
from types import SimpleNamespace

import pandas as pd
import pytest

from arena.contestants.lifecycle import clone_participant, generation_root
from arena.portfolio.engine import PortfolioEngine
from arena.portfolio.types import DailyValuation


def source_state():
    engine = PortfolioEngine('CONTESTANT_A', 'robot', initial_cash=100)
    engine.holdings = {'STOCK_01': 2}
    engine.daily_valuations = [DailyValuation('2026-10-09', 20, 80, 100, 1, 0, 1)]
    engine.rejected_orders = [{'reason': 'synthetic rejection'}]
    cp = engine.export_checkpoint()
    return dict(engines={('CONTESTANT_A','robot'):cp},
                signal_history={'CONTESTANT_A':{13:pd.Series([.2,.8],index=['STOCK_01','STOCK_02'])}},
                last_completed_cycle_idx=13, policy_signature='synthetic-policy')


def test_admission_is_a_deep_economic_copy():
    original=source_state()
    child,baseline=clone_participant(original,'CONTESTANT_A','CONTESTANT_G','2026-10-09')
    source=original['engines'][('CONTESTANT_A','robot')]
    new=child['engines'][('CONTESTANT_G','robot')]
    assert new.contestant_id=='CONTESTANT_G'
    assert new.holdings==source.holdings
    assert new.daily_valuations==source.daily_valuations
    assert child['last_completed_cycle_idx']==13
    assert baseline['robot']['rejected_order_count']==1
    new.holdings['STOCK_01']=3
    new.daily_valuations[0].nav=2
    new.rejected_orders[0]['reason']='changed'
    child['signal_history']['CONTESTANT_G'][13].iloc[0]=.9
    assert source.holdings['STOCK_01']==2
    assert source.daily_valuations[0].nav==1
    assert source.rejected_orders[0]['reason']=='synthetic rejection'
    assert original['signal_history']['CONTESTANT_A'][13].iloc[0]==.2
    assert child['signal_history']['CONTESTANT_A'][13].iloc[0]==.2


def test_admission_refuses_a_wrong_or_mixed_cutoff():
    state=source_state()
    other=copy.deepcopy(next(iter(state['engines'].values())))
    other.daily_valuations[-1].date='2026-10-08'
    state['engines'][('CONTESTANT_B','robot')]=other
    with pytest.raises(ValueError,match='exact admission'):
        clone_participant(state,'CONTESTANT_A','CONTESTANT_G','2026-10-09')


def test_admission_rejects_an_existing_identity():
    with pytest.raises(ValueError,match='already present'):
        clone_participant(source_state(),'CONTESTANT_A','CONTESTANT_A','2026-10-09')


@pytest.mark.parametrize('name',['../escape','a/b','', '.hidden'])
def test_generation_cannot_escape_private_root(name):
    with pytest.raises(ValueError,match='Invalid generation'):
        generation_root(name)


def test_admission_requires_verification_bound_to_cache_and_manifest(tmp_path, monkeypatch):
    import arena.contestants.lifecycle as lifecycle
    root=tmp_path/'candidate'
    root.mkdir()
    manifest=tmp_path/'participant.yaml'
    manifest.write_text('anonymous participant')
    target=SimpleNamespace(contestant_id='CONTESTANT_G',source_file=manifest)
    registry=SimpleNamespace(get_contestant=lambda _:target,get_anonymous_id=lambda value:value)
    monkeypatch.setattr(lifecycle,'candidate_registry',lambda _:registry)
    monkeypatch.setattr(lifecycle,'check_assets',lambda _:None)
    (root/'entry.json').write_text(json.dumps(dict(spec=dict(first_signal_date='2026-10-09'),target_id='CONTESTANT_G')))
    cache=lifecycle.candidate_cache(root,'csi300')
    cache.parent.mkdir(parents=True)
    cache.write_bytes(b'synthetic frozen scores')
    with pytest.raises(ValueError,match='every pool'):
        lifecycle.verify_admission_predictions(root,['csi300'])
    report=root/'verification/csi300_2026-10-09.json'
    report.parent.mkdir()
    report.write_text(json.dumps(dict(complete=True,cache_sha256=lifecycle.fingerprint(cache),checks=[dict(
        participant='CONTESTANT_G',date='2026-10-09',max_score_difference=0,
        manifest_sha256=lifecycle.fingerprint(manifest))])))
    lifecycle.verify_admission_predictions(root,['csi300'])
    cache.write_bytes(b'different scores')
    with pytest.raises(ValueError,match='stale'):
        lifecycle.verify_admission_predictions(root,['csi300'])
