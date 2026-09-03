"""
arena/contestants/manifest.py
=============================
Contestant Manifest 数据结构与加载器
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path
import yaml


@dataclass
class ContestantMember:
    """Ensemble 子成员定义"""
    name: str
    member_count: int = 1
    model_class: Optional[str] = None
    feature_set: Optional[str] = None
    workflow_yaml: Optional[str] = None
    artifact_path: Optional[str] = None
    artifact_pattern: Optional[str] = None
    expected_folds: Optional[int] = None
    experiment_id: Optional[str] = None
    recorder_id: Optional[str] = None


@dataclass
class ContestantManifest:
    """参赛选手 Manifest 规范"""
    contestant_id: str
    display_name: str
    family: str
    artifact_date: str
    train_cutoff: str
    historical_role: str
    training_mode: str
    feature_set: str
    inference_adapter: str
    adapter_config: Dict[str, Any] = field(default_factory=dict)
    members: List[ContestantMember] = field(default_factory=list)
    integrity_class: str = "ORIGINAL"
    known_issues: List[str] = field(default_factory=list)
    arena_eligible_from: str = "2026-07-01"
    paired_rival: Optional[str] = None
    notes: str = ""
    # 溯源标记：来源文件路径及是否为公开匿名版
    source_file: Optional[str] = None
    is_anonymous: bool = False


def load_manifest(yaml_path: Path) -> ContestantManifest:
    """加载单个 Manifest YAML 文件并解析为 ContestantManifest 对象"""
    if not yaml_path.exists():
        raise FileNotFoundError(f"Manifest 文件不存在: {yaml_path}")

    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    raw_members = data.get("members", [])
    members = []
    for m in raw_members:
        members.append(
            ContestantMember(
                name=m.get("name", "member_1"),
                member_count=m.get("member_count", 1),
                model_class=m.get("model_class"),
                feature_set=m.get("feature_set"),
                workflow_yaml=m.get("workflow_yaml"),
                artifact_path=m.get("artifact_path"),
                artifact_pattern=m.get("artifact_pattern"),
                expected_folds=m.get("expected_folds"),
                experiment_id=m.get("experiment_id"),
                recorder_id=m.get("recorder_id")
            )
        )

    is_anon = "CONTESTANT_" in data.get("contestant_id", "")

    return ContestantManifest(
        contestant_id=data.get("contestant_id", ""),
        display_name=data.get("display_name", ""),
        family=data.get("family", ""),
        artifact_date=str(data.get("artifact_date", "")),
        train_cutoff=str(data.get("train_cutoff", "")),
        historical_role=data.get("historical_role", ""),
        training_mode=data.get("training_mode", "ensemble_static"),
        feature_set=data.get("feature_set", ""),
        inference_adapter=data.get("inference_adapter", "ensemble_static"),
        adapter_config=data.get("adapter_config", {}),
        members=members,
        integrity_class=data.get("integrity_class", "ORIGINAL"),
        known_issues=data.get("known_issues", []),
        arena_eligible_from=str(data.get("arena_eligible_from", "2026-07-01")),
        paired_rival=data.get("paired_rival"),
        notes=data.get("notes", ""),
        source_file=str(yaml_path),
        is_anonymous=is_anon
    )
