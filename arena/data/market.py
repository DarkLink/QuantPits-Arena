"""Daily-bar quotes: executions require a current quote; marks may be stale."""
from bisect import bisect_right
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Optional
import numpy as np
import pandas as pd
from arena.config import QLIB_DATA_URI


def valid_price(value):
    return np.isfinite(value) and value > 0


@dataclass(frozen=True)
class Quote:
    price: float
    source_date: str
    stale: bool


class MarketDataProvider:
    def __init__(self, provider_uri: Optional[Path] = None, use_real_qlib=False):
        self.provider_uri = provider_uri or QLIB_DATA_URI
        self.use_real_qlib = use_real_qlib
        self._cache = {}
        self._tradable_cache = {}
        self._history = {}
        self.direction_status = {}
        self.events = {}
        self.metadata_coverage = {'corporate_actions': False, 'direction_status': False}

    def load_qlib_data(self, instruments, start_date, end_date):
        import qlib
        from qlib.data import D
        qlib.init(provider_uri=str(self.provider_uri), region='cn')
        # Include prior quotes for instruments suspended throughout the requested window.
        history_start = (pd.Timestamp(start_date) - pd.Timedelta(days=120)).strftime('%Y-%m-%d')
        df = D.features(instruments, ['$open', '$close', '$factor', '$volume'],
                        start_time=history_start, end_time=end_date, freq='day')
        for (inst, dt), row in df.iterrows():
            date = pd.Timestamp(dt).strftime('%Y-%m-%d')
            factor = float(row['$factor'])
            opening = float(row['$open'])
            close = float(row['$close'])
            volume = float(row['$volume'])
            self._cache[(inst, date)] = {
                'factor': factor, 'adj_open': opening, 'adj_close': close,
                'real_open': opening / factor if valid_price(factor) else np.nan,
                'real_close': close / factor if valid_price(factor) else np.nan,
            }
            # Retrospective daily-bar proxy; strict mode requires separate opening metadata.
            self._tradable_cache[(inst, date)] = valid_price(volume)
        self._reindex()

    def _reindex(self):
        self._history = {}
        for (inst, date), row in sorted(self._cache.items()):
            if valid_price(row['real_close']):
                self._history.setdefault(inst, []).append(date)

    def preflight(self, profile, cutoff=None):
        if self.use_real_qlib and cutoff is not None:
            observed=[date for (_,date),row in self._cache.items() if valid_price(row.get('real_close',np.nan))]
            if not observed or max(observed)<cutoff:
                raise ValueError('Market snapshot does not cover the requested valuation cutoff')
        if profile == 'strict_execution' and not all(self.metadata_coverage.values()):
            raise ValueError('Strict execution requires verified corporate-action and direction-status coverage')

    def get_execution_price(self, instrument, date, field='open'):
        key = (instrument, date)
        if key not in self._cache and not self.use_real_qlib:
            self._generate(instrument, date)
        value = self._cache.get(key, {}).get(f'real_{field}', np.nan)
        return float(value) if valid_price(value) else np.nan

    def quote(self, instrument, date):
        value = self.get_execution_price(instrument, date, 'close')
        if valid_price(value):
            return Quote(value, date, False)
        dates = self._history.get(instrument)
        if dates is None:
            self._reindex()
            dates = self._history.get(instrument, [])
        idx = bisect_right(dates, date) - 1
        if idx < 0:
            raise ValueError('No valid historical valuation quote')
        source = dates[idx]
        return Quote(float(self._cache[(instrument, source)]['real_close']), source, True)

    def get_real_price(self, instrument, date, field='open'):
        if field == 'close':
            return self.quote(instrument, date).price
        return self.get_execution_price(instrument, date, field)

    def get_adj_price(self, instrument, date, field='close'):
        key = (instrument, date)
        if key not in self._cache and not self.use_real_qlib:
            self._generate(instrument, date)
        value = self._cache.get(key, {}).get(f'adj_{field}', np.nan)
        if valid_price(value):
            return float(value)
        if field == 'close':
            quote = self.quote(instrument, date)
            return float(self._cache[(instrument, quote.source_date)]['adj_close'])
        return np.nan

    def is_tradable(self, instrument, date, direction=None):
        key = (instrument, date)
        if direction and (instrument, date, direction) in self.direction_status:
            return self.direction_status[(instrument, date, direction)]
        if key not in self._tradable_cache:
            if self.use_real_qlib:
                return False
            self._tradable_cache[key] = self._hash(f'tradable_{instrument}_{date}') % 100 >= 3
        return self._tradable_cache[key]

    def corporate_events(self, date):
        return self.events.get(date, [])

    @staticmethod
    def _hash(value):
        return int.from_bytes(sha256(value.encode()).digest()[:8], 'little')

    def _generate(self, instrument, date):
        base = (self._hash(instrument) % 7000 + 1000) / 100
        factor = (self._hash(f'factor_{instrument}') % 250 + 50) / 100
        drift = (self._hash(f'drift_{instrument}_{date}') % 40 - 20) / 1000
        self._cache[(instrument, date)] = {
            'factor': factor, 'real_open': base, 'real_close': base * (1 + drift),
            'adj_open': base * factor, 'adj_close': base * (1 + drift) * factor}
