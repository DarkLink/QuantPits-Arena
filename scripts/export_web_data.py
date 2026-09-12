"""
scripts/export_web_data.py
==========================
Unified Web Data Exporter for QuantPits-Arena.
Delegates to DualTierExporter to guarantee 100% compliance with REFACTORING_SPEC.md.
"""

import sys
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from arena.seasons import SeasonManager
from arena.reports import DualTierExporter


def export_data(run_dir: Path = None, is_preview: bool = False):
    season_id = "season_01"
    cfg = SeasonManager.get_season_config(season_id)
    run_id = run_dir.name if run_dir else f"{season_id}_run"
    base_dir = run_dir.parent if run_dir else (REPO_ROOT / "runs")

    mode_str = "PREVIEW (Local Unreleased Sandbox)" if is_preview else "PRODUCTION (Public Baseline)"
    print(f"[*] Exporting Season 1 data from {run_id} [{mode_str}] via DualTierExporter...")

    exporter = DualTierExporter(run_id=run_id, base_dir=base_dir)
    out_file = REPO_ROOT / "web" / "js" / "data" / ("arena_data_preview.js" if is_preview else "arena_data.js")
    
    result = exporter.export_web_payload(season_cfg=cfg, web_output_path=out_file)
    print(f"[✔] Successfully exported web payload: {result} ({result.stat().st_size / 1024:.1f} KB)")
    return result


def main():
    parser = argparse.ArgumentParser(description="Export web data payload")
    parser.add_argument("--run-dir", type=str, default=None, help="Explicit run directory to export")
    parser.add_argument("--preview", action="store_true", help="Export to arena_data_preview.js with preview metadata")
    args = parser.parse_args()

    target_run = Path(args.run_dir) if args.run_dir else None
    export_data(run_dir=target_run, is_preview=args.preview)


if __name__ == "__main__":
    main()
