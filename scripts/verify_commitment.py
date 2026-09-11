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

    print("=" * 70)
    print(" 🔍 QuantPits-Arena 密码学承诺可信核验 (Commitment Verification)")
    policy = doc.get("policy", {})
    if policy:
        print(f"    评测基准截止日: {policy.get('evaluation_horizon')} | 解锁边界: <= {policy.get('unlocked_boundary_date')}")
        print(f"    模型状态: {policy.get('model_status')}")
    print("=" * 70)

    targets = [c for c in commitments if c.get("cycle_id") == cycle_id] if cycle_id else commitments
    if not targets:
        print(f"[FAIL] 清单中未找到周期为 {cycle_id} 的承诺！")
        sys.exit(1)

    all_matched = True

    for target in targets:
        cid = target.get("cycle_id")
        status = target.get("status")
        expected_hash = target.get("orders_sha256")
        manifest_rel = target.get("manifest_file")
        t_date = target.get("trade_date")

        if status == "UNLOCKED":
            manifest_path = REPO_ROOT / manifest_rel
            if not manifest_path.exists():
                print(f" ❌ [MISSING] {cid} ({t_date}): 目标明细文件不存在 -> {manifest_rel}")
                all_matched = False
                continue

            with open(manifest_path, "rb") as f:
                actual_hash = hashlib.sha256(f.read()).hexdigest()

            if actual_hash == expected_hash:
                print(f" ✅ [MATCH] {cid} ({t_date}) [UNLOCKED]: SHA-256 吻合 ({actual_hash[:16]}...) -> {manifest_rel}")
            else:
                print(f" ❌ [MISMATCH] {cid} ({t_date}): 哈希不匹配！预期 {expected_hash[:16]}... 实际 {actual_hash[:16]}...")
                all_matched = False
        else:
            print(f" 🔒 [EMBARGOED] {cid} ({t_date}): 处于4周保护期内，仅公开Git存证哈希 ({expected_hash[:16]}...)")

    print("-" * 70)
    if all_matched:
        print(" 🎉 [VERIFIED] 密码学核验 100% 成功通过！")
        print("    已解锁周期的明细哈希与 Git 存证完全一致，未解锁周期已锁定哈希防篡改。")
        print("=" * 70 + "\n")
        sys.exit(0)
    else:
        print(" ⚠️ [FAIL] 密码学核验失败：发现不匹配项！")
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
