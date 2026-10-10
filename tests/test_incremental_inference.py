"""Verify immutable cache history and failure atomicity without model assets."""

import pickle
from types import SimpleNamespace

import pandas as pd
import pytest

from arena.inference import incremental


@pytest.fixture
def cache_setup(tmp_path, monkeypatch):
    dates = ["2026-09-24", "2026-09-30", "2026-10-09"]
    calendar = SimpleNamespace(
        is_trading_day=lambda d: d in dates,
        get_trading_days=lambda start, end: [d for d in dates if start <= d <= end],
    )
    member = SimpleNamespace(
        workflow_yaml="artifacts/configs/member_1.yaml",
        artifact_path="artifacts/models/member_1.pkl",
        artifact_pattern=None,
    )
    for rel in [member.workflow_yaml, member.artifact_path]:
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"synthetic fixture")
    contestant = SimpleNamespace(contestant_id="candidate_1", members=[member])
    registry = SimpleNamespace(
        list_contestants=lambda: [contestant],
        get_anonymous_id=lambda cid: "CONTESTANT_A",
    )
    monkeypatch.setattr(incremental, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(incremental, "TradingCalendar", lambda: calendar)
    monkeypatch.setattr(incremental, "ContestantRegistry", lambda: registry)
    path = tmp_path / "artifacts/predictions/all_contestants_oos.pkl"
    path.parent.mkdir(parents=True)
    history = {dates[0]: pd.Series([0.2, 0.8], index=["STOCK_01", "STOCK_02"])}
    with path.open("wb") as stream:
        pickle.dump({"candidate_1": history, "CONTESTANT_A": history}, stream)
    return path, dates, member


def install_inference(monkeypatch, days):
    calls = []
    def infer(**kwargs):
        calls.append(kwargs)
        with kwargs["output_file"].open("wb") as stream:
            pickle.dump({"candidate_1": days}, stream)
    monkeypatch.setattr(incremental, "run_batch_inference", infer)
    return calls


def test_extension_preserves_history_and_aliases(cache_setup, monkeypatch):
    path, dates, _ = cache_setup
    with path.open("rb") as stream:
        baseline = pickle.load(stream)
    # Batch output may contain an overlapping date: it must never replace history.
    fresh = {d: pd.Series([0.9, 0.1], index=["STOCK_01", "STOCK_02"]) for d in dates}
    calls = install_inference(monkeypatch, fresh)
    incremental.extend_predictions("csirun300", dates[-1])
    with path.open("rb") as stream:
        updated = pickle.load(stream)
    assert calls[0]["oos_start"] == dates[1]
    assert calls[0]["oos_end"] == dates[-1]
    for key in baseline:
        pd.testing.assert_series_equal(updated[key][dates[0]], baseline[key][dates[0]])
        assert list(updated[key]) == dates
        pd.testing.assert_series_equal(updated[key][dates[-1]], fresh[dates[-1]])
    incremental.extend_predictions("csirun300", dates[-1])
    assert len(calls) == 1


@pytest.mark.parametrize("invalid", ["missing", "nan", "duplicate"])
def test_invalid_extension_leaves_cache_identical(cache_setup, monkeypatch, invalid):
    path, dates, _ = cache_setup
    baseline_bytes = path.read_bytes()
    fresh = {d: pd.Series([0.5], index=["STOCK_01"]) for d in dates[1:]}
    if invalid == "missing":
        fresh.pop(dates[-1])
    elif invalid == "nan":
        fresh[dates[-1]].iloc[0] = float("nan")
    else:
        fresh[dates[-1]] = pd.Series([0.1, 0.9], index=["STOCK_01", "STOCK_01"])
    install_inference(monkeypatch, fresh)
    with pytest.raises(ValueError, match="incomplete prediction extension"):
        incremental.extend_predictions("csirun300", dates[-1])
    assert path.read_bytes() == baseline_bytes
    assert not list(path.parent.glob("incremental_*"))


def test_inference_failure_leaves_cache_identical(cache_setup, monkeypatch):
    path, dates, _ = cache_setup
    baseline_bytes = path.read_bytes()
    def fail(**kwargs):
        raise RuntimeError("synthetic inference failure")
    monkeypatch.setattr(incremental, "run_batch_inference", fail)
    with pytest.raises(RuntimeError):
        incremental.extend_predictions("csirun300", dates[-1])
    assert path.read_bytes() == baseline_bytes
    assert not list(path.parent.glob("incremental_*"))


def test_missing_assets_fail_before_inference(cache_setup, monkeypatch):
    path, dates, member = cache_setup
    (incremental.REPO_ROOT / member.artifact_path).unlink()
    calls = install_inference(monkeypatch, {})
    baseline_bytes = path.read_bytes()
    with pytest.raises(ValueError, match="missing local inference assets"):
        incremental.extend_predictions("csirun300", dates[-1])
    assert not calls
    assert path.read_bytes() == baseline_bytes


def test_nontrading_cutoff_rejected(cache_setup, monkeypatch):
    path, _, _ = cache_setup
    calls = install_inference(monkeypatch, {})
    with pytest.raises(ValueError, match="available trading day"):
        incremental.extend_predictions("csirun300", "2026-10-10")
    assert not calls


def test_inconsistent_aliases_rejected(cache_setup, monkeypatch):
    path, dates, _ = cache_setup
    with path.open("rb") as stream:
        cached = pickle.load(stream)
    cached["CONTESTANT_A"] = {dates[0]: pd.Series([0.5], index=["STOCK_01"])}
    with path.open("wb") as stream:
        pickle.dump(cached, stream)
    baseline_bytes = path.read_bytes()
    calls = install_inference(monkeypatch, {})
    with pytest.raises(ValueError, match="inconsistent cached aliases"):
        incremental.extend_predictions("csirun300", dates[-1])
    assert not calls
    assert path.read_bytes() == baseline_bytes


def test_cli_dispatches_incremental_parameters(monkeypatch):
    import cli
    import sys
    calls = []
    monkeypatch.setattr(sys, "argv", ["cli.py", "infer-update", "--universe", "csi500",
                                     "--end-date", "2026-10-09"])
    monkeypatch.setattr(incremental, "extend_predictions", lambda **kwargs: calls.append(kwargs))
    cli.main()
    assert calls == [{"market": "csi500", "end_date": "2026-10-09"}]
