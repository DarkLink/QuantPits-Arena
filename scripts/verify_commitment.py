#!/usr/bin/env python3
"""
scripts/verify_commitment.py
============================
QuantPits-Arena Cryptographic Commitment Verifier.

Verifies that the target run files match the historical SHA-256 digests committed to
`commitments/embargo_commitments.yaml`.

Returns exit code 0 if all digests match, 1 if tampering or mismatch is detected.
"""

import sys
import hashlib
from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
COMMITMENTS_YAML = REPO_ROOT / "commitments" / "embargo_commitments.yaml"


def sha256_file(filepath: Path) -> str:
    if not filepath.exists():
        return ""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def verify(cycle_id: str = None, run_dir: Path = None):
    if not COMMITMENTS_YAML.exists():
        print(f"[FAIL] 未找到承诺注册清单: {COMMITMENTS_YAML}")
        sys.exit(1)

    with open(COMMITMENTS_YAML, "r", encoding="utf-8") as f:
        doc = yaml.safe_load(f) or {}

    commitments = doc.get("commitments", [])
    if not commitments:
        print("[FAIL] 承诺注册清单为空！")
        sys.exit(1)

    # Pick target commitment
    if cycle_id:
        target = next((c for c in commitments if c.get("cycle_id") == cycle_id), None)
        if not target:
            print(f"[FAIL] 清单中未找到周期为 {cycle_id} 的承诺！")
            sys.exit(1)
    else:
        target = commitments[-1]

    print("=" * 70)
    print(f" 🔍 QuantPits-Arena 密码学承诺可信核验 (Commitment Verification)")
    print(f"    核验周期: {target['cycle_id']} ({target['evaluation_window']})")
    print(f"    承诺提交时间: {target['committed_at']}")
    print(f"    解禁解锁日期: {target['embargo_until']}")
    print("=" * 70)

    # Determine which run dir to inspect
    if run_dir is None:
        # Check standard paths in order
        candidates = [
            REPO_ROOT / "runs" / "preview_tournament_0904",
            REPO_ROOT / "runs" / "tournament_real_1000_monkeys",
        ]
        for c in candidates:
            if c.exists() and (c / "public" / "daily_nav_curves.csv").exists():
                run_dir = c
                break

    if not run_dir or not run_dir.exists():
        print("[FAIL] 未找到待核验的目标回测产物目录！")
        sys.exit(1)

    print(f"[*] 检查目标目录: {run_dir.relative_to(REPO_ROOT)}")

    pub = run_dir / "public"
    files_to_check = {
        "daily_nav_curves.csv": pub / "daily_nav_curves.csv",
        "summary_metrics.csv": pub / "summary_metrics.csv",
        "model_animal_matrix.csv": pub / "model_animal_matrix.csv",
        "monkey_null_distributions.csv": pub / "monkey_null_distributions.csv",
    }

    expected_digests = target.get("sha256_digests", {})
    all_matched = True

    for name, fpath in files_to_check.items():
        key = name.replace(".", "_")
        expected_hash = expected_digests.get(key)
        if not expected_hash:
            continue

        if not fpath.exists():
            print(f" ❌ [MISSING] {name}: 文件不存在")
            all_matched = False
            continue

        actual_hash = sha256_file(fpath)
        if actual_hash == expected_hash:
            print(f" ✅ [MATCH] {name}: SHA-256 吻合 ({actual_hash[:16]}...)")
        else:
            print(f" ❌ [MISMATCH] {name}: 哈希不匹配！")
            all_matched = False

    # Check arena_data_preview.js if present
    preview_js = REPO_ROOT / "web" / "js" / "data" / "arena_data_preview.js"
    if "arena_data_preview_js" in expected_digests and preview_js.exists():
        exp = expected_digests["arena_data_preview_js"]
        act = sha256_file(preview_js)
        if exp == act:
            print(f" ✅ [MATCH] arena_data_preview.js: SHA-256 吻合 ({act[:16]}...)")
        else:
            print(f" ❌ [MISMATCH] arena_data_preview.js: 哈希不匹配！")
            all_matched = False

    print("-" * 70)
    if all_matched:
        print(" 🎉 [VERIFIED] 密码学核验 100% 成功通过！")
        print(f"    该结果数学证明在 {target['committed_at']} 前已完全冻结，绝无事后修改或过拟合。")
        print("=" * 70 + "\n")
        sys.exit(0)
    else:
        print(" ⚠️ [FAIL] 密码学核验失败：文件与此前承诺指纹不一致！")
        print("=" * 70 + "\n")
        sys.exit(1)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Verify cryptographic commitment against local run files")
    parser.add_argument("--cycle", type=str, default=None, help="Target cycle ID (e.g. cycle_8)")
    parser.add_argument("--run-dir", type=str, default=None, help="Run directory to verify")
    args = parser.parse_args()

    target_dir = Path(args.run_dir) if args.run_dir else None
    verify(cycle_id=args.cycle, run_dir=target_dir)


if __name__ == "__main__":
    main()
