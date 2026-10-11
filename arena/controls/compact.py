"""Batch/resumable random controls, with the reference RNG and engine contract."""
import ctypes
import hashlib
import json
import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
import numpy as np
from arena.config import REPO_ROOT
from arena.controls.monkey import CANONICAL_STRATEGY_SPECS
from arena.state import atomic_write


@dataclass
class CompactDistribution:
    returns: np.ndarray
    weekly_nav: np.ndarray
    deterministic: bool = False


def _kernel():
    source = Path(__file__).with_name('compact_kernel.cpp')
    digest = hashlib.sha256(source.read_bytes()).hexdigest()[:16]
    target = REPO_ROOT / 'artifacts/native' / f'controls_{digest}.so'
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_suffix('.tmp.so')
        subprocess.run(['g++', '-O3', '-std=c++17', '-fopenmp', '-shared', '-fPIC',
                        str(source), '-o', str(temporary)], check=True)
        os.replace(temporary, target)
    library = ctypes.CDLL(str(target))
    fn = library.evaluate
    pointer = np.ctypeslib.ndpointer(flags='C_CONTIGUOUS')
    fn.argtypes = [ctypes.c_int]*8 + [pointer]*8 + [pointer]*4 + [ctypes.c_double, ctypes.c_int, ctypes.c_int] + [ctypes.c_double]*3 + [pointer]*5 + [ctypes.c_int]
    fn.restype = None
    return fn


def pack_inputs(runner, cycles, price_lookup, tradability):
    first_history = next(iter(runner.signal_history.values()))
    pools = [list(first_history[c.cycle_idx].index) if c.has_rebalance else [] for c in cycles]
    instruments = sorted({i for pool in pools for i in pool})
    index = {i:j for j,i in enumerate(instruments)}
    U, C = len(instruments), len(cycles)
    universe = np.full((C,U), -1, dtype=np.int32)
    sizes = np.array([len(p) for p in pools], dtype=np.int32)
    opening = np.full((C,U), np.nan)
    buy_ok, sell_ok = np.zeros((C,U), dtype=np.uint8), np.zeros((C,U), dtype=np.uint8)
    days = [d for c in cycles for d in c.trading_days]
    marks = np.ones((len(days),U))
    from arena.portfolio.engine import PortfolioEngine as Engine
    for c,cycle in enumerate(cycles):
        universe[c,:sizes[c]] = [index[i] for i in pools[c]]
        if cycle.has_rebalance:
            for j,inst in enumerate(instruments):
                opening[c,j] = Engine._price(price_lookup, inst, cycle.trade_date, runner.deal_price_mode, True)
                buy_ok[c,j] = Engine._tradable(tradability, inst, cycle.trade_date, 'BUY')
                sell_ok[c,j] = Engine._tradable(tradability, inst, cycle.trade_date, 'SELL')
    # Unlisted names can lack a quote before entering the universe; an unheld
    # placeholder must never be used for an existing position.
    for d,day in enumerate(days):
        for j,inst in enumerate(instruments):
            value = Engine._price(price_lookup, inst, day, 'close')
            marks[d,j] = value if np.isfinite(value) and value > 0 else np.nan
    ends = np.cumsum([len(c.trading_days) for c in cycles]).astype(np.int32)
    starts = np.concatenate(([0], ends[:-1])).astype(np.int32)
    return dict(universe=universe, sizes=sizes, opening=opening, marks=marks,
                buy_ok=buy_ok, sell_ok=sell_ok, starts=starts, ends=ends,
                cycle_ids=np.array([c.cycle_idx for c in cycles],dtype=np.int32),
                rebalance=np.array([c.has_rebalance for c in cycles],dtype=np.int32)), days


def evaluate_batch(inputs, policy, initial, first_id, count, base_seed=2026, threads=8, state=None):
    specs = [s for s in CANONICAL_STRATEGY_SPECS.values() if not s.passive_pool]
    ks = np.array([s.topk for s in specs], dtype=np.int32)
    drops = np.array([s.n_drop for s in specs], dtype=np.int32)
    S,H = len(specs), int(ks.sum())
    C,U = inputs['universe'].shape
    if policy.greedy_allocation:
        raise ValueError('Compact controls require the standard allocation policy')
    if state is None:
        cash = np.full((count,S),float(initial))
        ids = np.full((count,H),-1,dtype=np.int32)
        qty = np.zeros((count,H))
    else:
        cash,ids,qty = (state[k].copy() for k in ('cash','ids','qty'))
    returns,nav = np.zeros((count,S)),np.zeros((count,S,C))
    args = [inputs[k] for k in ('cycle_ids','universe','sizes','rebalance','starts','ends')]
    _kernel()(count,first_id,base_seed,U,C,len(inputs['marks']),S,H,
              *args,ks,drops,inputs['opening'],inputs['marks'],inputs['buy_ok'],inputs['sell_ok'],
              float(initial),policy.lot_size,int(policy.allow_fractional_shares),
              policy.open_cost,policy.close_cost,policy.min_cost,cash,ids,qty,returns,nav,threads)
    if not np.isfinite(returns).all():
        raise ValueError('Controls have an unpriced held position')
    return dict(cash=cash,ids=ids,qty=qty,returns=returns,weekly_nav=nav)


def run_compact(runner, directory, count, batch_size=1000, threads=8, timeout=7200):
    directory=Path(directory); directory.mkdir(parents=True,exist_ok=True)
    price,tradability=runner._setup_market_provider(runner.registry.list_contestants(),None,None)
    inputs,days=pack_inputs(runner,runner.cycles,price,tradability)
    source = hashlib.sha256(Path(__file__).with_name('compact_kernel.cpp').read_bytes() + Path(__file__).read_bytes()).hexdigest()
    digest=hashlib.sha256((runner.execution_policy.signature+str(runner.initial_cash)+source).encode())
    for key,value in inputs.items(): digest.update(key.encode()+value.tobytes())
    signature=digest.hexdigest()
    manifest={'version':'compact-v2','signature':signature,'count':count,'batch_size':batch_size,
              'seed':2026,'cutoff':days[-1],'random_specs':10,'deterministic_references':1,
              'policy_signature':runner.execution_policy.signature,'code_signature':source}
    manifest['days']=days
    manifest['decision_dates']=[c.decision_date for c in runner.cycles]
    old_path=directory/'manifest.json'
    prior_inputs=directory/f'input_{signature}.npz'
    append_from=None
    if old_path.exists():
        old=json.loads(old_path.read_text())
        if old.get('code_signature')!=source:
            raise ValueError('Control implementation changed; use a new evaluation directory')
        if old['batch_size']!=batch_size or old['policy_signature']!=manifest['policy_signature']:
            raise ValueError('Control policy or batch layout changed; use a new evaluation directory')
        if old['signature']!=signature:
            old_days=old.get('days',[])
            prior_inputs=directory/f"input_{old['signature']}.npz"
            if not prior_inputs.exists() or not old_days or days[:len(old_days)]!=old_days:
                raise ValueError('Historical control dates changed')
            with np.load(prior_inputs) as prior:
                old_c=len(prior['cycle_ids'])
                for key in ('universe','sizes','opening','buy_ok','sell_ok','cycle_ids'):
                    if not np.array_equal(prior[key],inputs[key][:old_c],equal_nan=True):
                        raise ValueError('Historical control decision or market data changed')
                if not np.array_equal(prior['marks'],inputs['marks'][:len(old_days)],equal_nan=True):
                    raise ValueError('Historical valuation inputs changed')
            append_from=len(old_days)
    if not old_path.exists():
        temporary=prior_inputs.with_suffix('.tmp.npz')
        np.savez(temporary,**inputs)
        os.replace(temporary,prior_inputs)
        manifest['complete']=False
        atomic_write(old_path,json.dumps(manifest,indent=2).encode())
    arrays,navs=[],[];
    started=time.monotonic()
    for first in range(0,count,batch_size):
        size=min(batch_size,count-first)
        path=directory/f'batch_{first:08d}_{size:05d}.npz'
        needs_append=False
        if path.exists() and append_from is not None:
            with np.load(path) as prior_batch:
                needs_append=str(prior_batch['cutoff'])!=days[-1]
        if not path.exists() or needs_append:
            if time.monotonic()-started>timeout: raise TimeoutError('Control evaluation time budget reached; completed batches are resumable')
            if needs_append:
                old_count=append_from
                first_cycle=int(np.searchsorted(inputs['ends'],old_count,side='right'))
                subset={key:value[first_cycle:].copy() for key,value in inputs.items() if key!='marks'}
                subset['marks']=np.ascontiguousarray(inputs['marks'][old_count:])
                subset['starts']=np.maximum(subset['starts'],old_count)-old_count
                subset['ends']-=old_count
                for j,c in enumerate(runner.cycles[first_cycle:]):
                    subset['rebalance'][j]=bool(c.has_rebalance and c.trade_date>days[old_count-1])
                with np.load(path) as stored:
                    state={key:stored[key] for key in ('cash','ids','qty')}
                    old_nav=stored['weekly_nav']
                values=evaluate_batch(subset,runner.execution_policy,runner.initial_cash,first,size,threads=threads,state=state)
                values['weekly_nav']=np.concatenate((old_nav[:,:,:first_cycle],values['weekly_nav']),axis=2)
            else:
                values=evaluate_batch(inputs,runner.execution_policy,runner.initial_cash,first,size,threads=threads)
            values['cutoff']=np.array(days[-1])
            temporary=path.with_suffix('.tmp.npz')
            np.savez(temporary,**values)
            with temporary.open('rb') as stream: os.fsync(stream.fileno())
            os.replace(temporary,path)
        with np.load(path) as stored:
            arrays.append(stored['returns']);navs.append(stored['weekly_nav'])
        if first % (batch_size*10)==0 or first+size==count:
            print(f'[controls] {runner.season_id} {first+size}/{count} per random spec; elapsed={time.monotonic()-started:.1f}s',flush=True)
    returns,nav=np.concatenate(arrays),np.concatenate(navs)
    specs=[s for s in CANONICAL_STRATEGY_SPECS.values() if not s.passive_pool]
    manifest['complete']=True
    prior_inputs=directory/f'input_{signature}.npz'
    temporary=prior_inputs.with_suffix('.tmp.npz')
    np.savez(temporary,**inputs)
    os.replace(temporary,prior_inputs)
    manifest['elapsed_seconds']=time.monotonic()-started
    manifest['batch_hashes']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(directory.glob('batch_*.npz'))}
    atomic_write(old_path,json.dumps(manifest,indent=2).encode())
    result={s.spec_id:CompactDistribution(returns[:,j],nav[:,j,:]) for j,s in enumerate(specs)}
    passive=runner.taotie_benchmark.engine
    result['P_ALL_0']=CompactDistribution(np.array([passive.to_portfolio_path().total_return]),
        np.array([[w.end_nav for w in passive.weekly_settlements]]),True)
    return result
