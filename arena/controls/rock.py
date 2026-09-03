"""
arena/controls/rock.py
======================
Rock (永久投资组合 Permanent Portfolio) 基准接口
"""

from typing import Optional
from pathlib import Path
import pandas as pd
from arena.config import REPO_ROOT


class RockBenchmark:
    """
    Rock (Permanent Portfolio) 极简月度更新基准：
    - 支持用户手动维护的 rock_nav.csv (格式: date,nav)
    - 若文件不存在或未填入数据，优雅降级为基准留空模式 (is_active=False)
    """

    def __init__(self, csv_path: Optional[Path] = None):
        self.path = csv_path or (REPO_ROOT / "rock_nav.csv")
        self.is_active = False
        self.nav_series: Optional[pd.Series] = None
        self._load()

    def _load(self):
        if self.path.exists():
            try:
                df = pd.read_csv(self.path)
                if "date" in df.columns and "nav" in df.columns and len(df) > 0:
                    df["date"] = pd.to_datetime(df["date"])
                    self.nav_series = df.set_index("date")["nav"].sort_index()
                    self.is_active = True
            except Exception:
                self.is_active = False

    def get_nav_at(self, date_str: str) -> float:
        """获取指定日期的 Rock NAV，若未激活返回 1.0"""
        if not self.is_active or self.nav_series is None or len(self.nav_series) == 0:
            return 1.0

        ts = pd.to_datetime(date_str)
        # 取截至当日前最新的 NAV
        valid = self.nav_series.loc[:ts]
        if len(valid) > 0:
            return float(valid.iloc[-1])
        return 1.0
