"""Date routing keeps earlier inference versions unchanged."""
from types import SimpleNamespace
import yaml
import pytest

from arena.contestants import lifecycle


def test_version_selection_is_bound_to_effective_date(tmp_path,monkeypatch):
    monkeypatch.setattr(lifecycle,'REPO_ROOT',tmp_path)
    path=tmp_path/'manifests/private/revision.yaml';path.parent.mkdir(parents=True)
    path.write_text(yaml.safe_dump(dict(contestant_id='CONTESTANT_H',adapter_config={'version_id':'revision_2'})))
    base=SimpleNamespace(contestant_id='CONTESTANT_H',adapter_config=dict(version_id='revision_1',versions=[
        dict(effective_decision='2026-11-27',manifest='manifests/private/revision.yaml')]))
    assert lifecycle.select_version(base,'2026-11-26') is base
    assert lifecycle.select_version(base,'2026-11-27').adapter_config['version_id']=='revision_2'
    assert lifecycle.select_version(base,'2026-11-26') is base
    assert base.adapter_config['version_id']=='revision_1'


def test_version_cannot_belong_to_another_participant(tmp_path,monkeypatch):
    monkeypatch.setattr(lifecycle,'REPO_ROOT',tmp_path)
    path=tmp_path/'revision.yaml'
    path.write_text(yaml.safe_dump(dict(contestant_id='CONTESTANT_G')))
    base=SimpleNamespace(contestant_id='CONTESTANT_H',adapter_config=dict(versions=[
        dict(effective_decision='2026-11-27',manifest='revision.yaml')]))
    with pytest.raises(ValueError,match='different participant'):
        lifecycle.select_version(base,'2026-11-27')
