"""Canonical cache names keep the full universe separate from its subset."""

from pathlib import Path

from arena.config import REPO_ROOT


def prediction_cache_path(market: str, root: Path = REPO_ROOT) -> Path:
    filename = "all_contestants_oos.pkl" if market == "csirun300" else f"{market}_contestants_oos.pkl"
    return root / "artifacts" / "predictions" / filename
