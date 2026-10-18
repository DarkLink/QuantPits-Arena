"""Append missing prediction dates through the existing batch inference engine."""

import glob
import os
import pickle
import tempfile
import contextlib
import io
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

from arena.calendar import TradingCalendar
from arena.config import REPO_ROOT
from arena.contestants import ContestantRegistry
from arena.inference.batch_infer import run_batch_inference
from arena.inference.cache import prediction_cache_path


def extend_predictions(market: str, end_date: str, output_file=None, registry=None) -> Path:
    """Validate a complete extension before atomically replacing the local cache.

    Existing date slices, including private and anonymous aliases, are retained.
    Only missing trading dates are inferred; failures leave the cache untouched.
    """
    calendar = TradingCalendar()
    if not calendar.is_trading_day(end_date):
        raise ValueError("Prediction cutoff must be an available trading day")
    out_file = Path(output_file) if output_file else prediction_cache_path(market, REPO_ROOT)
    if not out_file.exists():
        raise FileNotFoundError("Incremental inference requires an existing prediction cache")
    with out_file.open("rb") as stream:
        existing = pickle.load(stream)

    registry = registry or ContestantRegistry()
    contestants = registry.list_contestants()
    if not contestants:
        raise ValueError("No contestants registered")
    required_dates = calendar.get_trading_days("2026-06-29", end_date)
    missing_dates = set()
    missing_by_id = {}
    for contestant in contestants:
        cid = contestant.contestant_id
        alias = registry.get_anonymous_id(cid)
        cached = existing.get(cid, existing.get(alias))
        first_signal = getattr(contestant, 'observation_start', None)
        if not cached and not first_signal:
            raise ValueError(f"{alias}: missing historical prediction cache")
        cached = cached or {}
        required = {d for d in required_dates if not first_signal or d >= first_signal}
        missing_by_id[cid] = required - set(cached)
        missing_dates.update(missing_by_id[cid])
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
        legacy_missing = set().union(*(missing_by_id[c.contestant_id] for c in contestants
                                      if not getattr(c, 'observation_start', None)))
        inferred = {}
        if legacy_missing:
            from arena.state import atomic_pickle
            signature = hashlib.sha256(out_file.read_bytes())
            signature.update((Path(__file__).with_name('batch_infer.py')).read_bytes())
            signature.update((Path(__file__).with_name('registered.py')).read_bytes())
            for participant in contestants:
                if getattr(participant, 'observation_start', None):
                    continue
                for member in participant.members:
                    paths = [REPO_ROOT/member.workflow_yaml]
                    if member.artifact_pattern:
                        paths.extend(Path(p) for p in glob.glob(str(REPO_ROOT/member.artifact_pattern)))
                    else:
                        paths.append(REPO_ROOT/member.artifact_path)
                    for path in paths:
                        with path.open('rb') as stream:
                            signature.update(hashlib.file_digest(stream,'sha256').digest())
            signature.update(f'{market}:{min(legacy_missing)}:{end_date}'.encode())
            resume_file = out_file.parent/f'resume_{market}_{end_date}_legacy.pkl'
            if resume_file.exists():
                with resume_file.open('rb') as stream:
                    resume = pickle.load(stream)
                if resume['signature'] == signature.hexdigest():
                    inferred = resume['predictions']
            if not inferred:
                with contextlib.redirect_stdout(io.StringIO()):
                    run_batch_inference(
                        market=market, oos_start=min(legacy_missing), oos_end=end_date,
                        output_file=staged_file, force=True,
                    )
                with staged_file.open("rb") as stream:
                    inferred = pickle.load(stream)
                atomic_pickle(resume_file, dict(signature=signature.hexdigest(),predictions=inferred))
        for contestant in contestants:
            missing = missing_by_id[contestant.contestant_id]
            if getattr(contestant, 'observation_start', None) and missing:
                from arena.inference.registered import infer_registered
                inferred[contestant.contestant_id] = infer_registered(
                    contestant, market, min(missing), end_date)
        merged = {key: dict(days) for key, days in existing.items()}
        for contestant in contestants:
            cid = contestant.contestant_id
            alias = registry.get_anonymous_id(cid)
            cached = existing.get(cid, existing.get(alias, {}))
            fresh = inferred.get(cid, inferred.get(alias, {}))
            additions = {}
            for date in missing_by_id[cid]:
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
        resume = out_file.parent/f'resume_{market}_{end_date}_legacy.pkl'
        if resume.exists():
            resume.unlink()
    print(f"[PASS] {market}: appended dates validated; historical predictions preserved")
    return out_file
