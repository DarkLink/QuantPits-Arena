"""Explicit execution assumptions shared by contestants and controls."""
from dataclasses import dataclass, asdict
import hashlib
import json


@dataclass(frozen=True)
class ExecutionPolicy:
    version: str = 'execution-v2'
    deal_price_mode: str = 'open'
    lot_size: int = 100
    allow_fractional_shares: bool = False
    open_cost: float = 0.0005
    close_cost: float = 0.0015
    min_cost: float = 5.0
    greedy_allocation: bool = False
    profile: str = 'daily_bar_research'
    valuation: str = 'last_valid_close'
    corporate_actions: str = 'verified_events_only'

    def __post_init__(self):
        if self.deal_price_mode not in ('open', 'close') or self.lot_size < 1:
            raise ValueError('Invalid execution price or lot size')
        if min(self.open_cost, self.close_cost, self.min_cost) < 0:
            raise ValueError('Costs must be nonnegative')
        if self.profile not in ('daily_bar_research', 'strict_execution'):
            raise ValueError('Unknown execution profile')

    @property
    def signature(self):
        return hashlib.sha256(json.dumps(asdict(self), sort_keys=True).encode()).hexdigest()

    @classmethod
    def from_season(cls, cfg):
        fields = ('deal_price_mode', 'lot_size', 'allow_fractional_shares',
                  'open_cost', 'close_cost', 'min_cost')
        values = {key: getattr(cfg, key) for key in fields}
        values.update(cfg.raw_dict.get('execution_policy', {}))
        return cls(**values)
