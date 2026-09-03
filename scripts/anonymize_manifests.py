#!/usr/bin/env python3
"""
scripts/anonymize_manifests.py
==============================
自动化将 manifests/private/ 中的私有模型清单转换为 manifests/public/ 下的完全匿名化清单。

原则：
1. 剥离真实模型类名、算法族名称、成员细节、本地文件路径
2. 统一转换为 CONTESTANT_A ~ CONTESTANT_F 抽象代号
3. 仅保留训练截断日、成员数、融合机制、完整性等级等必要的公开评测元数据
"""

import sys
from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
PRIVATE_DIR = REPO_ROOT / "manifests" / "private"
PUBLIC_DIR = REPO_ROOT / "manifests" / "public"
ALIAS_MAP_FILE = PRIVATE_DIR / "alias_map.yaml"


def main():
    if not ALIAS_MAP_FILE.exists():
        print(f"[ERROR] 找不到映射文件: {ALIAS_MAP_FILE}")
        sys.exit(1)

    with open(ALIAS_MAP_FILE, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    mappings = config.get("mappings", [])
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

    print(f"正在转换 {len(mappings)} 个选手配置为公开匿名版本...")

    for item in mappings:
        priv_path = PRIVATE_DIR / item["private_file"]
        if not priv_path.exists():
            print(f"[WARN] 找不到私有文件: {priv_path}")
            continue

        with open(priv_path, "r", encoding="utf-8") as f:
            priv_data = yaml.safe_load(f)

        # 构建匿名版本字典
        member_count = len(priv_data.get("members", []))
        adapter_type = item.get("training_mode", "ensemble_static")

        pub_data = {
            "contestant_id": item["anonymous_id"],
            "display_name": item["anonymous_display_name"],
            "family": item["anonymous_family"],
            "artifact_date": priv_data.get("artifact_date"),
            "train_cutoff": priv_data.get("train_cutoff"),
            "historical_role": priv_data.get("historical_role", ""),
            "training_mode": item["training_mode"],
            "feature_set": "mixed_multi_dim" if "mixed" in str(priv_data.get("feature_set", "")) else (
                f"filtered_{priv_data.get('adapter_config', {}).get('d_feat', 20)}dim"
            ),
            "members": [
                {
                    "name": "member_1",
                    "member_count": member_count,
                }
            ],
            "inference_adapter": adapter_type,
            "adapter_config": {
                k: v for k, v in priv_data.get("adapter_config", {}).items()
                if k in ("fusion_method", "fillna_value", "fold_aggregation", "d_feat", "step_len")
            },
            "integrity_class": priv_data.get("integrity_class", "ORIGINAL"),
            "known_issues": priv_data.get("known_issues", []),
            "arena_eligible_from": priv_data.get("arena_eligible_from", "2026-07-01"),
            "paired_rival": item.get("paired_rival"),
            "notes": "Anonymized contestant metadata for public benchmark."
        }

        # 特殊处理：如果是 CPCV，标注 fold 数
        if "cpcv" in item["training_mode"]:
            pub_data["members"][0]["folds"] = 8

        pub_path = PUBLIC_DIR / item["public_file"]
        with open(pub_path, "w", encoding="utf-8") as f:
            yaml.dump(pub_data, f, sort_keys=False, allow_unicode=True)

        print(f"  [OK] {item['private_file']} -> {item['public_file']} ({item['anonymous_id']})")

    print("匿名清单生成完毕。")


if __name__ == "__main__":
    main()
