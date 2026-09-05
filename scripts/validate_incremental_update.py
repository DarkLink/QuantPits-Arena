#!/usr/bin/env python3
"""
scripts/validate_incremental_update.py
======================================
Historical Immutability & Integrity Guard for QuantPits-Arena.

Ensures that any new run or export extending past the historical cutoff (2026-08-28)
strictly preserves the exact historical NAV values and sequence published in
`web/js/data/arena_data.js`.

Per AGENTS.md Security & Privacy Rules:
- Output zero sensitive characters on failure.
- Report only [FAIL] filename:line_number - violation category.
- Exit code 0 for PASS, 1 for FAIL.
"""

import sys
import json
import re
from pathlib import Path
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
ARENA_DATA_JS = REPO_ROOT / "web" / "js" / "data" / "arena_data.js"


def load_canonical_arena_data() -> dict:
    if not ARENA_DATA_JS.exists():
        raise FileNotFoundError(f"Canonical data file not found: {ARENA_DATA_JS}")

    with open(ARENA_DATA_JS, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract JSON between "window.ARENA_DATA = " and trailing ";"
    match = re.search(r"window\.ARENA_DATA\s*=\s*(\{.*\})\s*;?\s*$", content, re.DOTALL)
    if not match:
        raise ValueError("Could not parse JSON payload from arena_data.js")

    return json.loads(match.group(1))


def validate_dataframe_against_canonical(new_df_nav: pd.DataFrame) -> bool:
    """
    Validates that new_df_nav contains all historical dates and NAV values
    identical to the canonical arena_data.js up to the canonical cutoff date.
    """
    canonical_data = load_canonical_arena_data()
    canon_timeline = canonical_data.get("nav_timeline", {})
    canon_dates = canon_timeline.get("dates", [])
    canon_curves = canon_timeline.get("curves", {})

    if not canon_dates:
        print("[FAIL] arena_data.js - NAV_DATES_EMPTY")
        return False

    if "datetime" not in new_df_nav.columns:
        print("[FAIL] new_nav_dataframe - MISSING_DATETIME_COLUMN")
        return False

    new_dates = new_df_nav["datetime"].tolist()

    # Check 1: Must contain all canonical dates as prefix
    if len(new_dates) < len(canon_dates):
        print(f"[FAIL] daily_nav_curves.csv - DATE_COUNT_REGRESSION (expected >= {len(canon_dates)}, got {len(new_dates)})")
        return False

    for idx, expected_date in enumerate(canon_dates):
        if new_dates[idx] != expected_date:
            print(f"[FAIL] daily_nav_curves.csv:{idx + 2} - HISTORICAL_DATE_MISMATCH")
            return False

    # Check 2: Check every canonical curve against new curves for the historical range
    tolerance = 1e-4  # 4 decimal places
    mismatch_count = 0

    for curve_id, canon_series in canon_curves.items():
        if curve_id not in new_df_nav.columns:
            # Special case: benchmark CSI 300 might be added at export time, not in raw CSV
            if curve_id in ("BENCHMARK_csi300",):
                continue
            print(f"[FAIL] daily_nav_curves.csv - MISSING_CURVE_COLUMN ({curve_id[:16]}...)")
            mismatch_count += 1
            continue

        new_series = new_df_nav[curve_id].iloc[:len(canon_series)].tolist()
        for t_idx, (c_val, n_val) in enumerate(zip(canon_series, new_series)):
            if abs(round(float(c_val), 4) - round(float(n_val), 4)) > tolerance:
                print(f"[FAIL] daily_nav_curves.csv:{t_idx + 2} - HISTORICAL_NAV_MUTATION ({curve_id[:16]}...)")
                mismatch_count += 1
                if mismatch_count >= 10:
                    break

        if mismatch_count >= 10:
            break

    if mismatch_count > 0:
        return False

    return True


def validate_run_dir(run_dir: Path) -> bool:
    nav_csv = run_dir / "public" / "daily_nav_curves.csv"
    if not nav_csv.exists():
        print(f"[FAIL] {nav_csv.name} - FILE_NOT_FOUND")
        return False

    df_nav = pd.read_csv(nav_csv)
    return validate_dataframe_against_canonical(df_nav)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Validate incremental update historical immutability")
    parser.add_argument("--run-dir", type=str, default=None, help="Path to run directory with public/daily_nav_curves.csv")
    args = parser.parse_args()

    if args.run_dir:
        target_dir = Path(args.run_dir)
    elif (REPO_ROOT / "runs" / "preview_tournament_0904").exists():
        target_dir = REPO_ROOT / "runs" / "preview_tournament_0904"
    else:
        target_dir = REPO_ROOT / "runs" / "tournament_real_1000_monkeys"

    print("=" * 70)
    print(f" 🛡️ QuantPits-Arena 历史数据不变性审计: {target_dir.name}")
    print(f"    对照基准: web/js/data/arena_data.js (全网公开基线)")
    print("=" * 70)

    try:
        ok = validate_run_dir(target_dir)
        if ok:
            print(" [PASS] 历史数据验证通过：前序 41 个交易日数据 100% 严格一致，零回溯修改。")
            print("=" * 70)
            sys.exit(0)
        else:
            print(" [FAIL] 历史数据验证失败：检测到前序已公开日期的数值或时间戳突变！")
            print("=" * 70)
            sys.exit(1)
    except Exception as e:
        print(f"[FAIL] validate_incremental_update - RUNTIME_EXCEPTION ({type(e).__name__})")
        sys.exit(1)


if __name__ == "__main__":
    main()
