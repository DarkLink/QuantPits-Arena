"""Append missing prediction dates through the existing batch inference engine."""

import glob
import os
import pickle
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

from arena.calendar import TradingCalendar
from arena.config import REPO_ROOT
from arena.contestants import ContestantRegistry
from arena.inference.batch_infer import run_batch_inference


def extend_predictions(market: str, end_date: str, output_file=None) -> Path:
    """Validate a complete extension before atomically replacing the local cache.

    Existing date slices, including private and anonymous aliases, are retained.
    Only missing trading dates are inferred; failures leave the cache untouched.
    """
    calendar = TradingCalendar()
    if not calendar.is_trading_day(end_date):
        raise ValueError("Prediction cutoff must be an available trading day")
    pred_dir = REPO_ROOT / "artifacts" / "predictions"
    filename = "all_contestants_oos.pkl" if market == "csirun300" else f"{market}_contestants_oos.pkl"
    out_file = Path(output_file) if output_file else pred_dir / filename
    if not out_file.exists():
        raise FileNotFoundError("Incremental inference requires an existing prediction cache")
    with out_file.open("rb") as stream:
        existing = pickle.load(stream)

    registry = ContestantRegistry()
    contestants = registry.list_contestants()
    if not contestants:
        raise ValueError("No contestants registered")
    required_dates = calendar.get_trading_days("2026-06-29", end_date)
    missing_dates = set()
    for contestant in contestants:
        cid = contestant.contestant_id
        alias = registry.get_anonymous_id(cid)
        cached = existing.get(cid, existing.get(alias))
        if not cached:
            raise ValueError(f"{alias}: missing historical prediction cache")
        missing_dates.update(set(required_dates) - set(cached))
        for key in {cid, alias} & existing.keys():
            other = existing[key]
            if set(other) != set(cached) or any(not other[d].equals(cached[d]) for d in cached):
                raise ValueError(f"{alias}: inconsistent cached aliases")
    if not missing_dates:
        print(f"[i] {market}: prediction cache already covers {end_date}")
        return out_file

    # Refuse incomplete local assets rather than silently changing a contestant.
    for contestant in contestants:
        alias = registry.get_anonymous_id(contestant.contestant_id)
        if not contestant.members:
            raise ValueError(f"{alias}: missing local inference assets")
        for member in contestant.members:
            if not member.workflow_yaml or not (REPO_ROOT / member.workflow_yaml).is_file():
                raise ValueError(f"{alias}: missing local inference configuration")
            if member.artifact_pattern:
                paths = glob.glob(str(REPO_ROOT / member.artifact_pattern))
                expected = member.expected_folds or member.member_count
                if len(paths) != expected:
                    raise ValueError(f"{alias}: incomplete local inference assets")
            elif not member.artifact_path or not (REPO_ROOT / member.artifact_path).is_file():
                raise ValueError(f"{alias}: missing local inference assets")

    print(f"[*] {market}: append {len(missing_dates)} trading dates through {end_date}")
    with tempfile.TemporaryDirectory(prefix="incremental_", dir=out_file.parent) as staging:
        staged_file = Path(staging) / "predictions.pkl"
        run_batch_inference(
            market=market, oos_start=min(missing_dates), oos_end=end_date,
            output_file=staged_file, force=True,
        )
        with staged_file.open("rb") as stream:
            inferred = pickle.load(stream)
        merged = {key: dict(days) for key, days in existing.items()}
        for contestant in contestants:
            cid = contestant.contestant_id
            alias = registry.get_anonymous_id(cid)
            cached = existing.get(cid, existing.get(alias))
            fresh = inferred.get(cid, inferred.get(alias, {}))
            additions = {}
            for date in set(required_dates) - set(cached):
                scores = fresh.get(date)
                if (not isinstance(scores, pd.Series) or scores.empty
                        or not scores.index.is_unique or not np.isfinite(scores.to_numpy()).all()):
                    raise ValueError(f"{alias}: incomplete prediction extension at {date}")
                additions[date] = scores
            for key in {cid, alias}:
                merged[key] = dict(cached)
                merged[key].update({d: additions[d] for d in sorted(additions)})
        with staged_file.open("wb") as stream:
            pickle.dump(merged, stream)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(staged_file, out_file)
    print(f"[PASS] {market}: appended dates validated; historical predictions preserved")
    return out_file
