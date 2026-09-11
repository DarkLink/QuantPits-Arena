"""
arena/seasons/manager.py
========================
多赛季配置管理器 (Season Isolation Manager)
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from pathlib import Path
import yaml

from arena.config import (
    REPO_ROOT,
    DEFAULT_ANCHOR_DATE,
    DEFAULT_FIRST_TRADE_DATE,
    DEFAULT_END_DATE,
    DEFAULT_INITIAL_CASH,
    DEFAULT_TOPK,
    DEFAULT_CANONICAL_DROP_N,
    DEFAULT_DEAL_PRICE,
)

SEASONS_DIR = REPO_ROOT / "seasons"


@dataclass
class SeasonConfig:
    """赛季核心配置对象"""
    season_id: str
    title: str
    status: str
    description: str
    anchor_date: str
    first_trade_date: str
    end_date: str
    cycle_freq: str
    initial_cash: float
    deal_price_mode: str
    lot_size: int
    allow_fractional_shares: bool
    open_cost: float
    close_cost: float
    min_cost: float
    topk: int
    n_drop: int
    benchmarks: List[Dict[str, Any]]
    raw_dict: Dict[str, Any] = field(default_factory=dict)

    @property
    def universe_code(self) -> str:
        univ = self.raw_dict.get("universe", {})
        return univ.get("code", univ.get("market", "csi300"))

    @property
    def market_benchmark_symbol(self) -> str:
        univ = self.raw_dict.get("universe", {})
        for b in self.raw_dict.get("benchmarks", []):
            if b.get("type") == "INDEX" or "symbol" in b:
                return b.get("symbol", "SH000300")
        return univ.get("market_benchmark_symbol", univ.get("benchmark_index", "SH000300"))

    @property
    def market_benchmark_name(self) -> str:
        univ = self.raw_dict.get("universe", {})
        for b in self.raw_dict.get("benchmarks", []):
            if b.get("type") == "INDEX" or "symbol" in b:
                return b.get("display_name", "Market Benchmark")
        return univ.get("market_benchmark_name", "Market Benchmark")



class SeasonManager:
    """
    赛季管理器：负责赛季发现、配置读取与环境隔离。
    默认且强制保障：未指明赛季时自动对齐到 season_01，确保历史与当前运行 100% 不受破坏。
    """

    DEFAULT_SEASON = "season_01"

    @classmethod
    def list_seasons(cls) -> List[str]:
        """列出所有已存在的赛季 ID"""
        if not SEASONS_DIR.exists():
            return [cls.DEFAULT_SEASON]
        seasons = [
            d.name for d in sorted(SEASONS_DIR.iterdir())
            if d.is_dir() and ((d / "season_config.yaml").exists() or (d / "season.yaml").exists())
        ]
        return seasons if seasons else [cls.DEFAULT_SEASON]

    @classmethod
    def get_season_config(cls, season_id: Optional[str] = None) -> SeasonConfig:
        """
        获取指定赛季的配置。
        若未传参则默认获取 season_01。
        若目标文件不存在则优雅回退至默认参数构建。
        """
        sid = season_id or cls.DEFAULT_SEASON
        config_path = SEASONS_DIR / sid / "season_config.yaml"
        if not config_path.exists():
            config_path = SEASONS_DIR / sid / "season.yaml"

        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                doc = yaml.safe_load(f) or {}

            cal = doc.get("horizon", doc.get("calendar", {}))
            exe = doc.get("capital", doc.get("execution", {}))
            return SeasonConfig(
                season_id=doc.get("season_id", sid),
                title=doc.get("title", f"QuantPits Arena {sid}"),
                status=doc.get("status", "ACTIVE"),
                description=doc.get("description", ""),
                anchor_date=cal.get("anchor_date", DEFAULT_ANCHOR_DATE),
                first_trade_date=cal.get("first_trade_date", DEFAULT_FIRST_TRADE_DATE),
                end_date=cal.get("end_date", DEFAULT_END_DATE),
                cycle_freq=cal.get("cycle_freq", "weekly"),
                initial_cash=float(exe.get("initial_cash", DEFAULT_INITIAL_CASH)),
                deal_price_mode=exe.get("deal_price_mode", DEFAULT_DEAL_PRICE),
                lot_size=int(exe.get("lot_size", 100)),
                allow_fractional_shares=bool(exe.get("allow_fractional_shares", False)),
                open_cost=float(exe.get("open_cost", 0.0005)),
                close_cost=float(exe.get("close_cost", 0.0015)),
                min_cost=float(exe.get("min_cost", 5.0)),
                topk=int(exe.get("topk", DEFAULT_TOPK)),
                n_drop=int(exe.get("n_drop", DEFAULT_CANONICAL_DROP_N)),
                benchmarks=doc.get("benchmarks", []),
                raw_dict=doc
            )

        # 回退兜底构建
        return SeasonConfig(
            season_id=sid,
            title=f"QuantPits Arena {sid}",
            status="ACTIVE",
            description="Fallback Season Config",
            anchor_date=DEFAULT_ANCHOR_DATE,
            first_trade_date=DEFAULT_FIRST_TRADE_DATE,
            end_date=DEFAULT_END_DATE,
            cycle_freq="weekly",
            initial_cash=DEFAULT_INITIAL_CASH,
            deal_price_mode=DEFAULT_DEAL_PRICE,
            lot_size=100,
            allow_fractional_shares=False,
            open_cost=0.0005,
            close_cost=0.0015,
            min_cost=5.0,
            topk=DEFAULT_TOPK,
            n_drop=DEFAULT_CANONICAL_DROP_N,
            benchmarks=[{"id": "taotie"}, {"id": "csi300"}, {"id": "monkeys"}],
            raw_dict={}
        )
