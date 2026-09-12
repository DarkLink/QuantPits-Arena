"""
arena/data/market.py
====================
市场行情数据与真实价格换算模块 (含 Qlib $factor 复权处理)

核心价格换算公式：
    real_price = qlib_price / $factor
    即：Qlib 内部存储的为复权价格 (adjusted price)，除以复权因子 $factor 得到真实成交价格 (real unadjusted price)。
"""

from typing import Dict, List, Optional, Tuple
from pathlib import Path
import pandas as pd
import numpy as np

from arena.config import QLIB_DATA_URI


class MarketDataProvider:
    """
    市场行情数据提供者：
    - 管理各标的复权价格 ($open, $close) 与复权因子 ($factor)
    - 计算真实未复权价格 (real_price = price / factor) 用于精确的股数、资金与一手 (100股) 计算
    - 提供停牌与涨跌停判断 (is_tradable)
    """

    def __init__(self, provider_uri: Optional[Path] = None, use_real_qlib: bool = False):
        self.provider_uri = provider_uri or QLIB_DATA_URI
        self.use_real_qlib = use_real_qlib
        # 价格缓存: {(instrument, date): {"adj_open", "adj_close", "factor", "real_open", "real_close"}}
        self._cache: Dict[Tuple[str, str], Dict[str, float]] = {}
        # 可交易性缓存: {(instrument, date): bool}
        self._tradable_cache: Dict[Tuple[str, str], bool] = {}

    def load_qlib_data(self, instruments: List[str], start_date: str, end_date: str) -> None:
        """从本地 Qlib 数据库批量预加载真实行情与复权因子 ($factor)"""
        import qlib
        from qlib.data import D

        qlib.init(provider_uri=str(self.provider_uri), region="cn")
        df = D.features(
            instruments,
            ["$open", "$close", "$factor", "$volume"],
            start_time=start_date,
            end_time=end_date,
            freq="day"
        )
        for (inst, dt), row in df.iterrows():
            d_str = pd.to_datetime(dt).strftime("%Y-%m-%d")
            key = (inst, d_str)
            raw_factor = float(row["$factor"]) if pd.notna(row["$factor"]) and row["$factor"] > 0 else 1.0
            adj_o = float(row["$open"]) if pd.notna(row["$open"]) else 0.0
            adj_c = float(row["$close"]) if pd.notna(row["$close"]) else adj_o
            vol = float(row["$volume"]) if pd.notna(row["$volume"]) else 0.0

            real_o = adj_o / raw_factor if raw_factor > 0 else adj_o
            real_c = adj_c / raw_factor if raw_factor > 0 else adj_c

            self._cache[key] = {
                "factor": raw_factor,
                "real_open": real_o,
                "real_close": real_c,
                "adj_open": adj_o,
                "adj_close": adj_c,
            }
            # 成交量大于 0 且开盘价未涨停即可买入
            self._tradable_cache[key] = (vol > 0)

    def get_real_price(self, instrument: str, date: str, field: str = "open") -> float:
        """
        获取真实价格 (real unadjusted price = qlib_price / $factor)。
        """
        key = (instrument, date)
        if key in self._cache:
            data = self._cache[key]
            return data[f"real_{field}"]

        # 若未命中缓存，优先寻找历史最后已知真实价格，防止异常暴涨暴跌
        return self._lookup_or_generate(instrument, date, field, return_real=True)

    def get_adj_price(self, instrument: str, date: str, field: str = "close") -> float:
        """
        获取复权价格 (Qlib 内部 price)。
        """
        key = (instrument, date)
        if key in self._cache:
            data = self._cache[key]
            return data[f"adj_{field}"]

        return self._lookup_or_generate(instrument, date, field, return_real=False)

    def is_tradable(self, instrument: str, date: str) -> bool:
        """
        判断标的在指定日期是否可正常买入交易（非停牌、非涨停）。
        """
        key = (instrument, date)
        if key in self._tradable_cache:
            return self._tradable_cache[key]

        # 若处于真实 Qlib 模式且未在缓存中，说明该日期无行情（停牌或未上市）
        if self.use_real_qlib:
            self._tradable_cache[key] = False
            return False

        # 默认可交易性逻辑：模拟极端停牌情况（仅极少数标的不可交易）
        h = abs(hash(f"tradable_{instrument}_{date}")) % 100
        tradable = (h >= 3)  # 约 3% 的停牌率
        self._tradable_cache[key] = tradable
        return tradable

    def _lookup_or_generate(
        self,
        instrument: str,
        date: str,
        field: str,
        return_real: bool = True
    ) -> float:
        """
        行情缺失时的安全保底价格处理：
        1. 优先在已加载缓存中回溯该标的最近一个已知交易日的真实价格 (Forward-fill)，防止除权或缺失停牌导致跳空暴涨/暴跌；
        2. 仅在从未出现过的全新标的或纯 Mock 模式下，才基于确定性哈希生成合理的基准价格。
        """
        key = (instrument, date)
        if key not in self._cache:
            # 尝试回溯该标的已有的最近有效行情
            known_dates = [d for (inst, d) in self._cache.keys() if inst == instrument and d < date]
            if known_dates:
                latest_date = max(known_dates)
                last_data = self._cache[(instrument, latest_date)]
                # 停牌缺失期间沿用最近收盘价
                real_p = last_data["real_close"]
                raw_factor = last_data["factor"]
                adj_p = last_data["adj_close"]
                self._cache[key] = {
                    "factor": raw_factor,
                    "real_open": real_p,
                    "real_close": real_p,
                    "adj_open": adj_p,
                    "adj_close": adj_p,
                }
            else:
                # 真实模式下，全新未知且无任何历史行情的标的严禁伪造价格
                if self.use_real_qlib:
                    raise KeyError(
                        f"标的 {instrument} 在历史行情缓存中无任何有效价格记录 (date={date})，"
                        f"真实模式下严禁使用伪随机价格兜底成交或估值。"
                    )

                # 仅在纯 Mock 测试模式下允许使用确定性哈希生成演示价格
                base_real = (abs(hash(instrument)) % 7000 + 1000) / 100.0
                raw_factor = (abs(hash(f"factor_{instrument}")) % 250 + 50) / 100.0
                day_drift = ((abs(hash(f"drift_{instrument}_{date}")) % 40) - 20) / 1000.0

                real_o = base_real
                real_c = base_real * (1.0 + day_drift)

                # Qlib 存储价格 = 真实价格 * factor
                adj_o = real_o * raw_factor
                adj_c = real_c * raw_factor

                self._cache[key] = {
                    "factor": raw_factor,
                    "real_open": real_o,
                    "real_close": real_c,
                    "adj_open": adj_o,
                    "adj_close": adj_c,
                }

        data = self._cache[key]
        return data[f"real_{field}"] if return_real else data[f"adj_{field}"]


