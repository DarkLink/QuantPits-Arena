"""
arena/controls/monkey.py
========================
Parametric Monkey Colony (参数化猴子群落) 零假设基准控制组
支持覆盖全部 11 种策略规格 (TopK/DropN 组合，包含饕餮全池) 的 100 只确定性随机猴子控制组。
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
import numpy as np
import pandas as pd

from arena.calendar import WeeklyCycle
from arena.portfolio.engine import PortfolioEngine
from arena.portfolio.types import PortfolioPath, DailyValuation, WeeklySettlement


@dataclass(frozen=True)
class StrategySpec:
    """投资组合执行策略规格定义"""
    spec_id: str
    topk: int
    n_drop: int
    passive_pool: bool = False
    description: str = ""


# 覆盖 Extended Zoo 全部 11 种独特投资组合策略规格
CANONICAL_STRATEGY_SPECS: Dict[str, StrategySpec] = {
    "P_22_3": StrategySpec("P_22_3", 22, 3, False, "Robot, Sloth-1~4, Snail-1~4, Meerkat-10~90, Koala"),
    "P_22_11": StrategySpec("P_22_11", 22, 11, False, "Rabbit-1 (半仓换手)"),
    "P_22_22": StrategySpec("P_22_22", 22, 22, False, "Rabbit-2 (全仓换手)"),
    "P_22_1": StrategySpec("P_22_1", 22, 1, False, "Turtle (极低换手)"),
    "P_5_1": StrategySpec("P_5_1", 5, 1, False, "Eagle-5/1 (极端集中组合)"),
    "P_11_2": StrategySpec("P_11_2", 11, 2, False, "Eagle-11/2 (紧凑半数组合)"),
    "P_44_6": StrategySpec("P_44_6", 44, 6, False, "Eagle-44/6 (2 倍容量宽度)"),
    "P_66_9": StrategySpec("P_66_9", 66, 9, False, "Eagle-66/9 (3 倍容量宽度)"),
    "P_88_12": StrategySpec("P_88_12", 88, 12, False, "Eagle-88/12 (4 倍容量宽度)"),
    "P_123_17": StrategySpec("P_123_17", 123, 17, False, "WhaleShark (半池大容量组合)"),
    "P_ALL_0": StrategySpec("P_ALL_0", 0, 0, True, "Taotie (全池吞噬被动组合)"),
}


def map_animal_to_spec_id(animal_id: str) -> str:
    """根据动物 ID 映射至对应的策略规格代号"""
    if animal_id in ["robot", "koala"] or animal_id.startswith("sloth-") or animal_id.startswith("snail-") or animal_id.startswith("meerkat-"):
        return "P_22_3"
    elif animal_id == "rabbit-1":
        return "P_22_11"
    elif animal_id == "rabbit-2":
        return "P_22_22"
    elif animal_id == "turtle":
        return "P_22_1"
    elif animal_id == "eagle-5-1":
        return "P_5_1"
    elif animal_id == "eagle-11-2":
        return "P_11_2"
    elif animal_id == "eagle-44-6":
        return "P_44_6"
    elif animal_id == "eagle-66-9":
        return "P_66_9"
    elif animal_id == "eagle-88-12":
        return "P_88_12"
    elif animal_id == "whale-shark":
        return "P_123_17"
    elif animal_id == "taotie":
        return "P_ALL_0"
    return "P_22_3"


class MonkeyColony:
    """
    参数化猴子群落零假设控制组：
    - 每组配置 colony_size（默认 1000 只）随机猴子；
    - 使用确定性伪随机数发生器 (Seed = base_seed + monkey_idx * 10007 + cycle_idx * 37)；
    - 严格遵循真实 50 万初始资金与 100 股最小交易单位约束；
    - 针对特定 (TopK, DropN) 策略规格产出零假设分布与经验显著性检验统计量。
    """

    def __init__(self, colony_size: int = 1000, base_seed: int = 2026):
        self.colony_size = colony_size
        self.base_seed = base_seed

    def generate_monkey_score(
        self,
        monkey_idx: int,
        cycle_idx: int,
        instruments: List[str]
    ) -> pd.Series:
        """
        生成指定猴子在指定周期的确定性随机截面得分。
        """
        seed = (self.base_seed + monkey_idx * 10007 + cycle_idx * 37) % (2**31 - 1)
        rng = np.random.RandomState(seed)
        scores = rng.uniform(0.0, 1.0, size=len(instruments))
        return pd.Series(scores, index=instruments)

    def init_group_engines(
        self,
        spec: StrategySpec,
        initial_cash: float = 500_000.0,
        deal_price_mode: str = "open"
    ) -> List[PortfolioEngine]:
        """初始化一个策略组的 N 只猴子 PortfolioEngine 实例"""
        engines = []
        for m in range(self.colony_size):
            engine = PortfolioEngine(
                contestant_id=f"MONKEY_{spec.spec_id}",
                animal_id=f"m_{m:04d}",
                topk=spec.topk,
                initial_cash=initial_cash,
                deal_price_mode=deal_price_mode
            )
            engines.append(engine)
        return engines

    def step_group(
        self,
        spec: StrategySpec,
        cycle: WeeklyCycle,
        engines: List[PortfolioEngine],
        universe: List[str],
        price_lookup_fn: Callable[[str, str, str], float],
        tradability_filter_fn: Optional[Callable[[str, str], bool]] = None,
    ):
        """单周推进一组猴子"""
        is_first = (cycle.cycle_idx == 0)
        c_idx = cycle.cycle_idx

        for m, engine in enumerate(engines):
            score = self.generate_monkey_score(monkey_idx=m, cycle_idx=c_idx, instruments=universe)
            order = engine.generate_order(
                score=score,
                topk=spec.topk,
                n_drop=spec.n_drop,
                trade_date=cycle.trade_date,
                is_first_entry=is_first,
                tradability_filter=tradability_filter_fn,
                price_lookup=price_lookup_fn,
                passive_pool=spec.passive_pool
            )
            engine.execute_weekly_cycle(
                cycle=cycle,
                order=order,
                price_lookup=price_lookup_fn
            )

    def run_group(
        self,
        spec: StrategySpec,
        cycles: List[WeeklyCycle],
        universe_provider_fn: Callable[[str], List[str]],
        price_lookup_fn: Callable[[str, str, str], float],
        tradability_filter_fn: Optional[Callable[[str, str], bool]] = None,
        initial_cash: float = 500_000.0,
        deal_price_mode: str = "open",
    ) -> List[PortfolioPath]:
        """批量运行一个策略规格组的完整猴群回测"""
        # 特殊优化：若为全池纯被动策略 (Taotie: passive_pool=True, topk=0, n_drop=0)，所有猴子行为绝对等价
        if spec.passive_pool and spec.topk == 0 and spec.n_drop == 0:
            single_engine = PortfolioEngine(
                contestant_id=f"MONKEY_{spec.spec_id}",
                animal_id="m_0000",
                topk=0,
                initial_cash=initial_cash,
                deal_price_mode=deal_price_mode
            )
            for cycle in cycles:
                universe = universe_provider_fn(cycle.decision_date)
                is_first = (cycle.cycle_idx == 0)
                mock_score = pd.Series(1.0, index=universe)
                order = single_engine.generate_order(
                    score=mock_score,
                    topk=0,
                    n_drop=0,
                    trade_date=cycle.trade_date,
                    is_first_entry=is_first,
                    tradability_filter=tradability_filter_fn,
                    price_lookup=price_lookup_fn,
                    passive_pool=True
                )
                single_engine.execute_weekly_cycle(cycle, order, price_lookup_fn)
            base_path = single_engine.to_portfolio_path()
            return [base_path] * self.colony_size

        engines = self.init_group_engines(spec, initial_cash, deal_price_mode)
        for cycle in cycles:
            universe = universe_provider_fn(cycle.decision_date)
            self.step_group(spec, cycle, engines, universe, price_lookup_fn, tradability_filter_fn)
        return [engine.to_portfolio_path() for engine in engines]

    def summarize_distribution(self, values: List[float]) -> Dict[str, float]:
        """计算零假设分布的核心统计量 (min, p05, median, p95, max, mean, std)"""
        arr = np.array(values)
        if len(arr) == 0:
            return {"min": 0.0, "p05": 0.0, "median": 0.0, "p95": 0.0, "max": 0.0, "mean": 0.0, "std": 0.0}

        return {
            "min": float(np.min(arr)),
            "p05": float(np.percentile(arr, 5)),
            "median": float(np.median(arr)),
            "p95": float(np.percentile(arr, 95)),
            "max": float(np.max(arr)),
            "mean": float(np.mean(arr)),
            "std": float(np.std(arr)),
        }

    def compute_empirical_pvalue(
        self,
        target_value: float,
        monkey_values: List[float],
        higher_is_better: bool = True
    ) -> float:
        """
        计算实证单侧 p-value (含 plus-one 有限样本校正)：
        p = (count + 1) / (N + 1)
        避免在有限样本下得出 p = 0.0 的非物理结论。
        若 p < 0.05，表示在经验零假设下具有统计显著性。
        """
        arr = np.array(monkey_values)
        n = len(arr)
        if n == 0:
            return 1.0
        if higher_is_better:
            count = int(np.sum(arr >= target_value))
        else:
            count = int(np.sum(arr <= target_value))
        return float((count + 1) / (n + 1))

    def compute_percentile_rank(self, target_value: float, monkey_values: List[float]) -> float:
        """
        计算目标模型在猴子群落中的百分位排名 (0.0 ~ 1.0, 越大越好)。
        含 plus-one 有限样本校正：count / (N + 1)，最高不超过 N / (N + 1)。
        """
        arr = np.array(monkey_values)
        n = len(arr)
        if n == 0:
            return 0.5
        count = int(np.sum(arr < target_value))
        return float(count / (n + 1))
