#!/usr/bin/env python3
"""
scripts/commit_embargo.py
=========================
QuantPits-Arena Cryptographic Timeliness & Commitment Generator.

Implements a formal Commit-and-Reveal Protocol (Proof of Non-Tampering / Proof of Timeliness).
Allows the research team to commit SHA-256 digests of newly evaluated trading cycles (e.g., Cycle 8 ending 2026-09-04)
to the public GitHub repository on the completion day (2026-09-05), while the underlying market data remains
embargoed from full public release until the scheduled unlock date (2026-09-11).

Once the embargo date arrives and full data is published, any independent researcher can verify
that the revealed data is bit-for-bit identical to the committed hashes, proving zero look-ahead bias
and zero hindsight parameter tuning.
"""

import sys
import re
import json
import hashlib
from datetime import datetime
from pathlib import Path
import yaml
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
COMMITMENTS_YAML = REPO_ROOT / "commitments" / "embargo_commitments.yaml"
COMMITMENTS_JSON = REPO_ROOT / "web" / "js" / "data" / "commitments.json"


def sha256_file(filepath: Path) -> str:
    """Computes standard SHA-256 digest of a local file."""
    if not filepath.exists():
        return ""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def find_preview_dir(explicit_dir: str = None) -> Path:
    if explicit_dir:
        p = Path(explicit_dir)
        if p.exists():
            return p
    runs_dir = REPO_ROOT / "runs"
    for p in sorted(runs_dir.glob("preview_*"), reverse=True):
        if p.is_dir() and (p / "public" / "daily_nav_curves.csv").exists():
            return p
    raise FileNotFoundError("Could not find preview sandbox run directory in runs/preview_*")


def commit_cycle(run_dir: Path = None, embargo_until: str = "2026-09-11"):
    preview_dir = run_dir or find_preview_dir()
    pub_dir = preview_dir / "public"
    nav_csv = pub_dir / "daily_nav_curves.csv"
    metrics_csv = pub_dir / "summary_metrics.csv"
    matrix_csv = pub_dir / "model_animal_matrix.csv"
    null_csv = pub_dir / "monkey_null_distributions.csv"
    preview_js = REPO_ROOT / "web" / "js" / "data" / "arena_data_preview.js"

    print("=" * 70)
    print(f" 🔐 QuantPits-Arena 密码学及时性承诺生成器 (Commitment Scheme)")
    print(f"    沙盒来源: {preview_dir.name}")
    print("=" * 70)

    if not nav_csv.exists():
        print(f"[ERROR] 未找到必要的回测产物: {nav_csv}")
        sys.exit(1)

    df_nav = pd.read_csv(nav_csv)
    dates = df_nav["datetime"].tolist()
    anchor_date = dates[0]
    cutoff_date = dates[-1]
    trading_days = len(dates)

    # 1. Compute Cryptographic Hashes (SHA-256)
    digests = {
        "daily_nav_curves_csv": sha256_file(nav_csv),
        "summary_metrics_csv": sha256_file(metrics_csv),
        "model_animal_matrix_csv": sha256_file(matrix_csv),
        "monkey_null_distributions_csv": sha256_file(null_csv),
        "arena_data_preview_js": sha256_file(preview_js) if preview_js.exists() else None,
    }

    # Merkle root combination
    combined_str = "|".join(filter(None, [
        digests["daily_nav_curves_csv"],
        digests["summary_metrics_csv"],
        digests["model_animal_matrix_csv"],
        digests["monkey_null_distributions_csv"]
    ]))
    merkle_root = hashlib.sha256(combined_str.encode("utf-8")).hexdigest()

    # Determine Cycle ID based on number of trading days
    # Cycle 0 was 5 days, Cycle 7 was 41 days, Cycle 8 is 46 days
    cycle_idx = max(0, (trading_days - 1) // 5)
    cycle_id = f"cycle_{cycle_idx}"

    now_iso = datetime.now().astimezone().isoformat(timespec="seconds")

    commitment_entry = {
        "cycle_id": cycle_id,
        "evaluation_window": f"{anchor_date} ~ {cutoff_date}",
        "cutoff_date": cutoff_date,
        "trading_days": trading_days,
        "embargo_until": embargo_until,
        "committed_at": now_iso,
        "status": "EMBARGOED",
        "merkle_root": merkle_root,
        "sha256_digests": digests,
        "verification_command": f"python3 scripts/verify_commitment.py --cycle {cycle_id}"
    }

    # 2. Update commitments/embargo_commitments.yaml
    COMMITMENTS_YAML.parent.mkdir(parents=True, exist_ok=True)
    existing_commitments = []
    if COMMITMENTS_YAML.exists():
        try:
            with open(COMMITMENTS_YAML, "r", encoding="utf-8") as f:
                doc = yaml.safe_load(f) or {}
                existing_commitments = doc.get("commitments", [])
        except Exception:
            existing_commitments = []

    # Deduplicate / replace by cycle_id
    filtered = [c for c in existing_commitments if c.get("cycle_id") != cycle_id]
    filtered.append(commitment_entry)

    yaml_doc = {
        "title": "QuantPits-Arena Timeliness & Anti-Tampering Commitments",
        "protocol": "Commitment Scheme (SHA-256 Proof-of-Timeliness)",
        "description": "Cryptographic proofs that out-of-sample arena evaluations were frozen in real-time before public embargo reveal.",
        "last_updated": now_iso,
        "commitments": filtered
    }

    with open(COMMITMENTS_YAML, "w", encoding="utf-8") as f:
        yaml.dump(yaml_doc, f, allow_unicode=True, sort_keys=False, default_flow_style=False)

    # 3. Export commitments.json for web frontend integration
    COMMITMENTS_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(COMMITMENTS_JSON, "w", encoding="utf-8") as f:
        json.dump(yaml_doc, f, ensure_ascii=False, indent=2)

    # 4. Auto-update web/index.html Proof of Timeliness notice banner
    index_html = REPO_ROOT / "web" / "index.html"
    if index_html.exists():
        commit_date = now_iso.split("T")[0]
        hash_short = digests["daily_nav_curves_csv"][:8]
        new_span = (
            f'<span>🔐 <strong style="color: var(--text-secondary);">Proof of Timeliness:</strong> '
            f'Next cycle (through {cutoff_date}) cryptographically committed on {commit_date} '
            f'(<code style="font-size: 10px; color: var(--brand-cyan);">SHA-256: {hash_short}...</code>). '
            f'Public reveal embargoed until {embargo_until}.</span>'
        )
        html_text = index_html.read_text(encoding="utf-8")
        updated_html = re.sub(
            r'<span>🔐\s*<strong style="color: var\(--text-secondary\);">Proof of Timeliness:</strong>.*?</span>',
            new_span,
            html_text,
            flags=re.DOTALL
        )
        if updated_html != html_text:
            index_html.write_text(updated_html, encoding="utf-8")
            print(f"    • 网页横幅已同步自动更新: {index_html.relative_to(REPO_ROOT)}")

    print(f"\n[✔] 密码学承诺已成功落盘！")
    print(f"    • 评估周期: {anchor_date} ~ {cutoff_date} ({trading_days} 个交易日, {cycle_id})")
    print(f"    • 承诺生成时间: {now_iso}")
    print(f"    • 解禁公布时间: {embargo_until}")
    print(f"    • Merkle Root: {merkle_root}")
    print(f"    • daily_nav_curves.csv SHA-256: {digests['daily_nav_curves_csv']}")
    if digests['arena_data_preview_js']:
        print(f"    • arena_data_preview.js SHA-256: {digests['arena_data_preview_js']}")
    print(f"    • 承诺记录清单: {COMMITMENTS_YAML.relative_to(REPO_ROOT)}")
    print(f"    • 前端公开指纹: {COMMITMENTS_JSON.relative_to(REPO_ROOT)}")
    print("=" * 70 + "\n")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate cryptographic timeliness commitment for embargoed cycle")
    parser.add_argument("--run-dir", type=str, default=None, help="Preview run directory")
    parser.add_argument("--embargo-until", type=str, default="2026-09-11", help="Public reveal date (YYYY-MM-DD)")
    args = parser.parse_args()

    target_dir = Path(args.run_dir) if args.run_dir else None
    commit_cycle(run_dir=target_dir, embargo_until=args.embargo_until)


if __name__ == "__main__":
    main()
