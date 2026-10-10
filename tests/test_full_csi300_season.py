"""Full CSI 300 must never reuse the csirun300 subset's prediction cache."""

import json
import pickle
import re
from types import SimpleNamespace

import pandas as pd
import pytest

import cli
from arena.inference.cache import prediction_cache_path
from arena.reports.sanitizer import DualTierExporter
from arena.runner import weekly_cycle
from arena.seasons.manager import SeasonManager
from arena.contestants.adapters.historical import HistoricalReplayAdapter


def test_full_pool_is_a_distinct_season():
    assert SeasonManager.get_season_config("season_01").universe_code == "csirun300"
    assert SeasonManager.get_season_config("season_csi300").universe_code == "csi300"
    assert prediction_cache_path("csi300") != prediction_cache_path("csirun300")


def test_pipeline_infers_full_pool_despite_existing_subset(tmp_path, monkeypatch):
    subset = prediction_cache_path("csirun300", tmp_path)
    subset.parent.mkdir(parents=True)
    subset.write_bytes(b"subset fixture")
    monkeypatch.setattr(cli, "REPO_ROOT", tmp_path)
    calls = []
    import arena.inference.batch_infer as batch
    monkeypatch.setattr(batch, "run_batch_inference", lambda **kw: calls.append(kw))
    for name in ("cmd_run", "cmd_export_web", "cmd_audit"):
        monkeypatch.setattr(cli, name, lambda args: None)
    cli.cmd_pipeline(SimpleNamespace(season="season_csi300", run_id=None, force_infer=False))
    assert len(calls) == 1
    assert calls[0]["market"] == "csi300"
    assert calls[0]["output_file"] == prediction_cache_path("csi300", tmp_path)
    assert subset.read_bytes() == b"subset fixture"


def test_runner_refuses_subset_fallback(tmp_path, monkeypatch):
    subset = prediction_cache_path("csirun300", tmp_path)
    subset.parent.mkdir(parents=True)
    subset.write_bytes(b"subset fixture")
    monkeypatch.setattr(weekly_cycle, "REPO_ROOT", tmp_path)
    with pytest.raises(FileNotFoundError, match="Season prediction cache missing"):
        weekly_cycle.WeeklyCycleRunner(season_id="season_csi300")


def test_explicit_store_does_not_fill_missing_date_from_old_snapshot(tmp_path, monkeypatch):
    cache = tmp_path / "predictions.pkl"
    with cache.open("wb") as stream:
        pickle.dump({"CONTESTANT_A": {}}, stream)
    manifest = SimpleNamespace(contestant_id="CONTESTANT_A", training_mode="frozen")
    adapter = HistoricalReplayAdapter(manifest, auth_store_path=cache, snapshot_path=tmp_path / "absent.pkl")
    monkeypatch.setattr(HistoricalReplayAdapter, "_cached_stores", {})
    monkeypatch.setattr(HistoricalReplayAdapter, "_cached_raw_preds", {
        adapter.role_key: {"member_1": pd.Series([0.8], index=pd.MultiIndex.from_tuples([
            (pd.Timestamp("2026-07-03"), "STOCK_01")
        ]))}
    })
    with pytest.raises(ValueError, match="Authoritative prediction cache"):
        adapter.predict("2026-07-03", "2026-07-03")


def test_new_frontend_registration_uses_actual_dates_and_can_advance(tmp_path, monkeypatch):
    import arena.config as config
    monkeypatch.setattr(config, "REPO_ROOT", tmp_path)
    index = tmp_path / "web/js/data/seasons_index.js"
    index.parent.mkdir(parents=True)
    index.write_text('window.ARENA_SEASONS_INDEX = [];\n')
    exporter = DualTierExporter("synthetic", base_dir=tmp_path / "runs")
    cfg = SimpleNamespace(anchor_date="2026-07-03", end_date="2026-09-30")
    payload = {"meta": {"season_id": "season_csi300", "status": "ACTIVE"},
               "nav_timeline": {"dates": ["2026-07-03", "2026-09-30"]}}
    exporter._sync_seasons_index(cfg, payload)
    payload["nav_timeline"]["dates"].append("2026-10-09")
    exporter._sync_seasons_index(cfg, payload)
    entries = json.loads(re.search(r'=\s*(\[.*\]);', index.read_text(), re.S).group(1))
    assert len(entries) == 1
    assert entries[0]["end_date"] == "2026-10-09"
    assert entries[0]["anchor_date"] == "2026-07-03"
    assert entries[0]["trading_days"] == 3
    assert entries[0]["period"] == "2026.07 - 2026.10"


def test_new_season_script_uses_current_frontend_version(tmp_path, monkeypatch):
    import arena.config as config
    monkeypatch.setattr(config, "REPO_ROOT", tmp_path)
    html = tmp_path / "web/index.html"
    html.parent.mkdir(parents=True)
    html.write_text('<script src="js/data/seasons_index.js?v=6.3"></script>\n'
                    '<script src="js/data/season_01.js?v=6.3"></script>\n')
    exporter = DualTierExporter("synthetic", base_dir=tmp_path / "runs")
    exporter._sync_index_html("season_csi300")
    exporter._sync_index_html("season_csi300")
    assert html.read_text().count('js/data/season_csi300.js?v=6.3') == 1


def test_bump_date_updates_auto_registered_quoted_entry(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "REPO_ROOT", tmp_path)
    cfg_dir = tmp_path / "seasons/season_csi300"
    cfg_dir.mkdir(parents=True)
    (cfg_dir / "season_config.yaml").write_text('calendar:\n  end_date: "2026-09-30"\n')
    index = tmp_path / "web/js/data/seasons_index.js"
    index.parent.mkdir(parents=True)
    index.write_text('window.ARENA_SEASONS_INDEX = ' + json.dumps([{
        "id": "season_csi300", "end_date": "2026-09-30", "trading_days": 63,
        "period": "2026.07 - 2026.09"
    }]) + ';')
    cli.cmd_bump_date(SimpleNamespace(end_date="2026-10-09", seasons=["season_csi300"]))
    entries = json.loads(index.read_text().split('=', 1)[1].rstrip(';'))
    assert entries[0]["end_date"] == "2026-10-09"
    assert entries[0]["trading_days"] == 65
    assert entries[0]["period"] == "2026.07 - 2026.10"
