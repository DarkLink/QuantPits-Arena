"""
tests/test_season_manager.py
============================
验证多赛季隔离管理器 (SeasonManager) 配置加载、赛季发现与默认回退行为
"""

import pytest
from arena.seasons import SeasonManager, SeasonConfig


def test_season_manager_discovery():
    """验证赛季自动发现功能"""
    seasons = SeasonManager.list_seasons()
    assert seasons == ["season_01", "season_csi300", "season_csi500", "season_csi800", "season_csi1000"]
    assert [SeasonManager.get_season_config(s).title for s in seasons] == ['csirun300','CSI300','CSI500','CSI800','CSI1000']
    assert all(SeasonManager.get_season_config(s).status == 'ACTIVE' for s in seasons)


def test_default_season_01_config():
    """验证默认未传参数时自动对齐到 season_01"""
    cfg = SeasonManager.get_season_config()
    assert isinstance(cfg, SeasonConfig)
    assert cfg.season_id == "season_01"
    assert cfg.initial_cash == 500_000.0
    assert cfg.anchor_date == "2026-07-03"
    assert cfg.topk == 22
    assert cfg.n_drop == 3
    assert any(b.get("id") == "taotie" for b in cfg.benchmarks)
    assert any(b.get("id") == "csi300" for b in cfg.benchmarks)


def test_csirun300_includes_current_policy_and_ghost_reference():
    """当前执行规则和资本粒度参考直接应用于默认赛季。"""
    cfg = SeasonManager.get_season_config()
    assert cfg.title == "csirun300"
    assert cfg.status == "ACTIVE"
    assert cfg.raw_dict['execution_policy']['profile'] == 'daily_bar_research'
    benchmark_ids = [b.get("id") for b in cfg.benchmarks]
    assert "ghost_taotie" in benchmark_ids
    assert "taotie" in benchmark_ids
    with pytest.raises(ValueError,match='consolidated'):
        SeasonManager.get_season_config('season_02')


def test_nonexistent_season_graceful_fallback():
    """验证对未知赛季的请求能够安全兜底回退，绝不抛出未捕获异常"""
    cfg = SeasonManager.get_season_config("season_999")
    assert cfg.season_id == "season_999"
    assert cfg.status == "ACTIVE"
    assert cfg.initial_cash == 500_000.0
