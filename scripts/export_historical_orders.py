#!/usr/bin/env python3
"""
scripts/export_historical_orders.py
====================================
Exports and anonymizes historical trading orders across QuantPits-Arena seasons.

Implements the 4-Week Delayed Disclosure Protocol:
- Cutoff Horizon: Evaluated as of 2026-09-04.
- Unlocked Cycles: Cycles with trade date <= 2026-08-07 (Cycle 1 to Cycle 5) are UNLOCKED
  and published to `data/orders/<season_id>/cycle_<N>_orders.json`.
- Embargoed Cycles: Cycles with trade date > 2026-08-07 (Cycle 6 to Cycle 8) remain EMBARGOED.
  Their SHA-256 digest is computed and registered in `commitments/embargo_commitments.yaml`.

Privacy & Red-Line Rules (AGENTS.md Compliant):
- Contestant identities: Mapped to CONTESTANT_A ~ CONTESTANT_F via manifests/private/alias_map.yaml.
- Instruments: Deterministically anonymized to STOCK_001 ~ STOCK_NNN.
- Ticker mapping table is strictly stored in manifests/private/ticker_map.yaml (gitignored).
- Zero user home paths, zero real tickers, zero private model names.
"""

import sys
import json
import hashlib
from datetime import datetime
from pathlib import Path
import yaml
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFESTS_PRIVATE = REPO_ROOT / "manifests" / "private"
ALIAS_MAP_FILE = MANIFESTS_PRIVATE / "alias_map.yaml"
TICKER_MAP_FILE = MANIFESTS_PRIVATE / "ticker_map.yaml"
DATA_ORDERS_DIR = REPO_ROOT / "data" / "orders"
COMMITMENTS_YAML = REPO_ROOT / "commitments" / "embargo_commitments.yaml"

# 4-Week Embargo horizon relative to 2026-09-04
EVALUATION_HORIZON = "2026-09-04"
EMBARGO_CUTOFF_DATE = "2026-08-07"  # Trade date <= 2026-08-07 is unlocked (>= 4 weeks ago)


def load_alias_mapping():
    """Loads private-to-anonymous contestant ID mapping."""
    if not ALIAS_MAP_FILE.exists():
        print(f"[WARN] {ALIAS_MAP_FILE} not found. Using identity mapping.")
        return {}
    with open(ALIAS_MAP_FILE, "r", encoding="utf-8") as f:
        doc = yaml.safe_load(f) or {}
    mapping = {}
    for item in doc.get("mappings", []):
        mapping[item["private_id"]] = item["anonymous_id"]
    return mapping


def get_or_create_ticker_mapping(instruments):
    """Loads or creates deterministic anonymized ticker mapping STOCK_001 ~ STOCK_NNN."""
    MANIFESTS_PRIVATE.mkdir(parents=True, exist_ok=True)
    existing_map = {}
    if TICKER_MAP_FILE.exists():
        with open(TICKER_MAP_FILE, "r", encoding="utf-8") as f:
            existing_map = yaml.safe_load(f) or {}

    sorted_instruments = sorted(list(set(instruments)))
    updated = False
    next_idx = len(existing_map) + 1

    for inst in sorted_instruments:
        if inst not in existing_map:
            existing_map[inst] = f"STOCK_{next_idx:03d}"
            next_idx += 1
            updated = True

    if updated:
        with open(TICKER_MAP_FILE, "w", encoding="utf-8") as f:
            yaml.safe_dump(existing_map, f, sort_keys=True)

    return existing_map


def find_run_trades_file(season_id: str):
    """Locates raw_trades.csv for the target season."""
    candidates = [
        REPO_ROOT / "runs" / f"{season_id}_run" / "private" / "raw_trades.csv",
        REPO_ROOT / "runs" / "preview_tournament_0904" / "private" / "raw_trades.csv",
        REPO_ROOT / "runs" / "tournament_real_1000_monkeys" / "private" / "raw_trades.csv",
        REPO_ROOT / "runs" / "season_01_run" / "private" / "raw_trades.csv",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def export_season_orders(season_id: str = "season_01", explicit_csv: Path = None):
    trades_path = explicit_csv or find_run_trades_file(season_id)
    if not trades_path or not trades_path.exists():
        print(f"[SKIP] No trades file found for {season_id}")
        return {}

    print(f"[*] Processing trades for {season_id} from {trades_path.relative_to(REPO_ROOT)}...")
    df = pd.read_csv(trades_path)
    if df.empty:
        print(f"[WARN] Trades dataframe is empty for {season_id}")
        return {}

    alias_map = load_alias_mapping()
    ticker_map = get_or_create_ticker_mapping(df["instrument"].dropna().unique())

    # Map contestant and ticker
    df["contestant_anon"] = df["contestant_id"].map(lambda x: alias_map.get(x, x))
    df["instrument_anon"] = df["instrument"].map(lambda x: ticker_map.get(x, "STOCK_UNKNOWN"))

    # Identify trade dates and cycle mapping
    unique_dates = sorted(df["date"].unique())
    print(f"    Found {len(unique_dates)} trade execution dates: {unique_dates}")

    season_orders_dir = DATA_ORDERS_DIR / season_id
    season_orders_dir.mkdir(parents=True, exist_ok=True)

    cycle_digests = {}

    for c_idx, t_date in enumerate(unique_dates, start=1):
        cycle_df = df[df["date"] == t_date].copy()
        is_unlocked = t_date <= EMBARGO_CUTOFF_DATE

        orders_list = []
        for _, row in cycle_df.iterrows():
            weight_pct = round((float(row["value"]) / 500000.0) * 100, 2)
            orders_list.append({
                "contestant_id": str(row["contestant_anon"]),
                "animal_id": str(row["animal_id"]),
                "instrument": str(row["instrument_anon"]),
                "direction": str(row["direction"]).upper(),
                "shares": int(row["shares"]),
                "weight_pct": weight_pct
            })

        cycle_payload = {
            "cycle_id": f"cycle_{c_idx}",
            "season_id": season_id,
            "trade_date": t_date,
            "status": "UNLOCKED" if is_unlocked else "EMBARGOED",
            "embargo_cutoff_date": EMBARGO_CUTOFF_DATE,
            "evaluation_horizon": EVALUATION_HORIZON,
            "total_orders": len(orders_list),
            "orders": orders_list
        }

        # Calculate canonical SHA-256
        canonical_json = json.dumps(cycle_payload, indent=2, sort_keys=True, ensure_ascii=False)
        digest = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
        cycle_digests[f"cycle_{c_idx}"] = {
            "trade_date": t_date,
            "total_orders": len(orders_list),
            "sha256": digest,
            "status": "UNLOCKED" if is_unlocked else "EMBARGOED"
        }

        if is_unlocked:
            out_file = season_orders_dir / f"cycle_{c_idx}_orders.json"
            with open(out_file, "w", encoding="utf-8") as f:
                f.write(canonical_json)
            print(f"    [UNLOCKED] Cycle {c_idx} ({t_date}): {len(orders_list)} orders -> {out_file.relative_to(REPO_ROOT)} (SHA-256: {digest[:12]}...)")
        else:
            print(f"    [EMBARGOED] Cycle {c_idx} ({t_date}): {len(orders_list)} orders in 4-week embargo. (SHA-256: {digest[:12]}...)")

    return cycle_digests


def update_commitments_manifest(all_season_digests):
    """Synchronizes Cycle 1 to Cycle 8 entries into commitments/embargo_commitments.yaml."""
    if not COMMITMENTS_YAML.exists():
        return

    with open(COMMITMENTS_YAML, "r", encoding="utf-8") as f:
        doc = yaml.safe_load(f) or {}

    doc["title"] = "QuantPits-Arena Timeliness & Anti-Tampering Commitments"
    doc["protocol"] = "Commit-and-Reveal Protocol (Git SHA-256 Proof-of-Timeliness)"
    doc["description"] = "Cryptographic proofs that out-of-sample orders and holdings were frozen before execution."
    doc["policy"] = {
        "model_status": "Historical research candidate models (Non-live / Non-production)",
        "nav_release_schedule": "Weekly targeting before Monday open (Best-effort, no hard guarantee)",
        "holdings_orders_embargo_weeks": 4,
        "evaluation_horizon": EVALUATION_HORIZON,
        "unlocked_boundary_date": EMBARGO_CUTOFF_DATE
    }

    commitments_list = []
    s1_digests = all_season_digests.get("season_01", {})

    for c_id, info in s1_digests.items():
        commitments_list.append({
            "cycle_id": c_id,
            "trade_date": info["trade_date"],
            "status": info["status"],
            "orders_sha256": info["sha256"],
            "total_orders": info["total_orders"],
            "manifest_file": f"data/orders/season_01/{c_id}_orders.json" if info["status"] == "UNLOCKED" else "(embargoed)"
        })

    doc["commitments"] = commitments_list
    doc["last_updated"] = datetime.now().astimezone().isoformat()

    with open(COMMITMENTS_YAML, "w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, sort_keys=False, allow_unicode=True)

    print(f"[+] Updated {COMMITMENTS_YAML.relative_to(REPO_ROOT)} with {len(commitments_list)} cycles.")


def main():
    print("=" * 70)
    print(f" 📦 QuantPits-Arena Historical Orders Exporter & 4-Week Embargo Manager")
    print(f"    Horizon: {EVALUATION_HORIZON} | Unlocked Cutoff: <= {EMBARGO_CUTOFF_DATE}")
    print("=" * 70)

    all_digests = {}
    seasons = ["season_01", "season_csi500", "season_csi800", "season_csi1000"]

    for sid in seasons:
        digests = export_season_orders(sid)
        if digests:
            all_digests[sid] = digests

    if "season_01" in all_digests:
        update_commitments_manifest(all_digests)

    print("-" * 70)
    print(" [✓] Order export and embargo commitment synchronization complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
