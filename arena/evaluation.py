"""Native authorized historical refresh, with immutable inputs and staged release."""
import hashlib
import json
import pickle
import shutil
import subprocess
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from arena.config import REPO_ROOT, RUNS_DIR
from arena.seasons import SeasonManager
from arena.runner.weekly_cycle import WeeklyCycleRunner
from arena.reports.sanitizer import DualTierExporter
from arena.controls.compact import run_compact, evaluate_batch, pack_inputs
from arena.controls.monkey import MonkeyColony, CANONICAL_STRATEGY_SPECS
from arena.portfolio.engine import PortfolioEngine
from arena.state import atomic_pickle, atomic_write, operation_lock
from arena.reports.statistics import adjust


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def save_json(path,value):
    atomic_write(path,json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False).encode())


def targets():
    return [s for s in SeasonManager.list_seasons() if SeasonManager.get_season_config(s).status in ('ACTIVE','PREVIEW','DEMO')]


def verify_execution_sources(run_dir):
    path=Path(run_dir)/'public/evaluation_manifest.json'
    if not path.exists():
        return  # Cold-start diagnostics have no published generation to continue.
    metadata=json.loads(path.read_text())
    for relative,expected in metadata.get('execution_source_hashes',{}).items():
        if digest(REPO_ROOT/relative)!=expected:
            raise ValueError('Published execution sources changed; create an explicit full refresh')


def verify_market(provider, anchor_date, end_date):
    """Independent named-field verification against the frozen local quote cache."""
    from qlib.data import D
    instruments=sorted({key[0] for key in provider._cache})
    frame=D.features(instruments,['$factor','$open','$close'],start_time=anchor_date,end_time=end_date,freq='day')
    count=0;maximum=0.
    for (inst,date),row in frame.iterrows():
        day=pd.Timestamp(date).strftime('%Y-%m-%d')
        factor=float(row['$factor'])
        for field in ('open','close'):
            adjusted=float(row['$'+field])
            expected=adjusted/factor if np.isfinite(factor) and factor>0 and np.isfinite(adjusted) and adjusted>0 else np.nan
            actual=provider.get_execution_price(inst,day,field)
            if np.isnan(expected) != np.isnan(actual):raise ValueError('Frozen quote validity differs from the source')
            if np.isnan(expected) and np.isnan(actual):continue
            if not np.isfinite(actual):raise ValueError('Frozen quote validity differs from the source')
            difference=abs(actual-expected)
            maximum=max(maximum,difference);count+=1
    if maximum>1e-12:raise ValueError('Frozen execution quote differs from named source fields')
    return dict(checked_quotes=count,max_absolute_error=maximum)


def effective_config(sid):
    cfg=SeasonManager.get_season_config(sid)
    cfg.raw_dict['execution_policy']={'profile':'daily_bar_research','greedy_allocation':False}
    for benchmark in cfg.raw_dict.get('benchmarks',[]):
        if benchmark.get('id')=='taotie':
            benchmark['initial_cash']=cfg.initial_cash
            benchmark['display_name']='Taotie (Executable Passive)'
        elif benchmark.get('id')=='ghost_taotie':
            benchmark['display_name']='Ghost Taotie (Capital Granularity Scenario)'
    return cfg


def freeze(root,sids,end_date):
    inputs=root/'inputs';inputs.mkdir(parents=True,exist_ok=True)
    marker=inputs/'manifest.json'
    if marker.exists():
        saved=json.loads(marker.read_text())
        if saved['cutoff']!=end_date or sorted(saved['seasons'])!=sorted(sids):
            raise ValueError('Immutable evaluation selection differs')
        for rel,sha in saved['files'].items():
            if digest(root/rel)!=sha: raise ValueError('Frozen input digest changed')
        return saved
    legacy=root/'legacy';legacy.mkdir(parents=True,exist_ok=True)
    for name in ('chronicles','web/js/data','seasons'):
        source=REPO_ROOT/name
        if source.exists(): shutil.copytree(source,legacy/name,dirs_exist_ok=True)
    files={}
    for sid in sids:
        src=RUNS_DIR/f'{sid}_run'
        shutil.copytree(src,legacy/'runs'/src.name,dirs_exist_ok=True)
        checkpoint=src/'checkpoints/latest_state.pkl'
        with checkpoint.open('rb') as stream: state=pickle.load(stream)
        cfg=effective_config(sid)
        if cfg.end_date!=end_date: raise ValueError('Refresh cutoff must equal the existing evaluated cutoff')
        runner=WeeklyCycleRunner(anchor_date=cfg.anchor_date,end_date=end_date,season_id=sid,
            initial_cash=cfg.initial_cash,frozen_signals=state['signal_history'])
        expected={c.cycle_idx for c in runner.cycles}
        for history in state['signal_history'].values():
            if set(history)!=expected: raise ValueError('Legacy signal history has a missing or extra cycle')
            for score in history.values():
                if not score.index.is_unique or not np.isfinite(score.to_numpy()).all():
                    raise ValueError('Frozen legacy signals are invalid')
        path=inputs/f'{sid}_signals.pkl';atomic_pickle(path,state['signal_history'])
        runner._init_engines(runner.registry.list_contestants())
        runner._setup_market_provider(runner.registry.list_contestants(),None,None)
        validation=verify_market(runner.market_provider,cfg.anchor_date,end_date)
        save_json(inputs/f'{sid}_quote_validation.json',validation)
        runner.market_provider.snapshot_frozen=True
        path=inputs/f'{sid}_market.pkl';atomic_pickle(path,runner.market_provider)
        for path in (inputs/f'{sid}_signals.pkl',inputs/f'{sid}_market.pkl'):
            files[str(path.relative_to(root))]=digest(path)
        print(f'[freeze] {sid}: legacy signals and current daily-bar snapshot saved',flush=True)
    manifest=dict(cutoff=end_date,seasons=sids,files=files,
        historical_signal_source='legacy_checkpoint_actual_raw_signals',market_vintage='current_market_snapshot',
        profile='daily_bar_research',corporate_action_coverage=False,opening_direction_coverage=False)
    save_json(marker,manifest)
    return manifest


def runner_from_inputs(root,sid,end_date):
    with (root/'inputs'/f'{sid}_signals.pkl').open('rb') as stream: signals=pickle.load(stream)
    with (root/'inputs'/f'{sid}_market.pkl').open('rb') as stream: market=pickle.load(stream)
    cfg=effective_config(sid)
    runner=WeeklyCycleRunner(anchor_date=cfg.anchor_date,end_date=end_date,season_id=sid,
        initial_cash=cfg.initial_cash,frozen_signals=signals,market_provider=market,
        run_dir=root/'staging/runs'/f'{sid}_run')
    runner.source_signature=hashlib.sha256((digest(root/'inputs'/f'{sid}_signals.pkl')+digest(root/'inputs'/f'{sid}_market.pkl')).encode()).hexdigest()
    return runner,cfg


def replay(root,sid,end_date):
    runner,cfg=runner_from_inputs(root,sid,end_date)
    results=runner.run()
    for path in results.values():
        if path.daily_valuations[0].nav!=1 or path.daily_valuations[-1].date!=end_date:
            raise ValueError('Invalid anchor or actual valuation cutoff')
        if any(not np.isfinite(t.price) or t.price<=0 for t in path.trades):
            raise ValueError('Invalid executed price')
    runner.save_checkpoint_to_disk(runner.run_dir/'checkpoints',runner.last_completed_cycle_idx)
    exporter=DualTierExporter(f'{sid}_run',base_dir=root/'staging/runs')
    exporter.export(results,runner.registry)
    metadata=dict(evaluation_id=root.name,engine_version='execution-v2',
        profile='daily_bar_research',cutoff=end_date,source_signature=runner.source_signature,
        signal_source='frozen_legacy_actual_raw_signals',market_vintage='current_market_snapshot',
        retrospective_replay=True,corporate_action_coverage=False,opening_direction_coverage=False,
        taotie_capital_ratio=1.,taotie_greedy_allocation=False,ghost_capital_ratio=runner.ghost_taotie_benchmark.engine.initial_cash/runner.initial_cash,
        limitations=['Unverified corporate actions are not reconstructed from adjustment factors.',
                     'Full-day volume is a retrospective tradability proxy; opening price limits and capacity are unverified.'])
    save_json(exporter.public_dir/'evaluation_manifest.json',metadata)
    original=pd.read_csv(root/'legacy/runs'/f'{sid}_run/public/daily_nav_curves.csv', float_precision="round_trip").set_index('datetime')
    corrected=pd.read_csv(exporter.public_dir/'daily_nav_curves.csv', float_precision="round_trip").set_index('datetime')
    changes=[]
    for name in original.columns:
        old,new=original[name],corrected[name]
        mdd=lambda x:float(-(x/x.cummax()-1).min())
        changes.append(dict(season_id=sid,path_id=name,legacy_return_pct=(old.iloc[-1]-1)*100,
            corrected_return_pct=(new.iloc[-1]-1)*100,return_delta_pp=(new.iloc[-1]-old.iloc[-1])*100,
            legacy_mdd_pct=mdd(old)*100,corrected_mdd_pct=mdd(new)*100,
            max_nav_delta_pp=float(np.max(np.abs(new-old)))*100))
    pd.DataFrame(changes).to_csv(exporter.public_dir/'legacy_comparison.csv',index=False)
    # Real-price equivalence precedes pilot; include distant global IDs as well as zero.
    inputs,_=pack_inputs(runner,runner.cycles,market_price:=runner.market_provider.get_real_price,runner.market_provider.is_tradable)
    errors=[];daily_errors=[]
    pools=[list(next(iter(runner.signal_history.values()))[c.cycle_idx].index) for c in runner.cycles]
    for first in (0,19997):
        compact=evaluate_batch(inputs,runner.execution_policy,runner.initial_cash,first,3,threads=2)
        specs=[s for s in CANONICAL_STRATEGY_SPECS.values() if not s.passive_pool]
        for m in range(3):
            for j,spec in enumerate(specs):
                engine=PortfolioEngine('CONTROL','random',topk=spec.topk,initial_cash=runner.initial_cash)
                for c,pool in zip(runner.cycles,pools):
                    score=MonkeyColony().generate_monkey_score(first+m,c.cycle_idx,pool)
                    order=engine.generate_order(score,spec.topk,spec.n_drop,c.trade_date,c.cycle_idx==0,
                        runner.market_provider.is_tradable,market_price) if c.has_rebalance else None
                    engine.execute_weekly_cycle(c,order,market_price,runner.market_provider.is_tradable)
                errors.append(abs(engine.to_portfolio_path().total_return-compact['returns'][m,j]))
                reference=np.array([v.nav for v in engine.daily_valuations[1:]])
                daily_errors.append(float(np.max(np.abs(reference-compact['daily_nav'][m,j]))))
    maximum=float(max(errors))
    max_daily=float(max(daily_errors))
    if maximum>1e-12 or max_daily>1e-12: raise ValueError('Real-price compact/reference discrepancy')
    save_json(exporter.public_dir/'reference_validation.json',dict(paths=len(errors),max_return_error=maximum,
        max_daily_nav_error=max_daily,daily_nav_compared=True,tolerance=1e-12))
    print(f'[replay] {sid}: {len(results)} paths; {len(errors)} control comparisons; max error={maximum:.3g}',flush=True)
    return runner,results,exporter


def load_replayed(root,sid,end_date):
    runner,cfg=runner_from_inputs(root,sid,end_date)
    runner.load_checkpoint_from_disk(runner.run_dir/'checkpoints/latest_state.pkl')
    results={k:e.to_portfolio_path() for k,e in runner.engines.items()}
    results[('BENCHMARK','taotie')]=runner.taotie_benchmark.engine.to_portfolio_path()
    results[('BENCHMARK','ghost_taotie')]=runner.ghost_taotie_benchmark.engine.to_portfolio_path()
    return runner,results,DualTierExporter(f'{sid}_run',base_dir=root/'staging/runs')


def family_corrections(root,sids):
    frames=[]
    for sid in sids:
        path=root/'staging/runs'/f'{sid}_run/public/contestant_monkey_significance.csv'
        frame=pd.read_csv(path, float_precision="round_trip")
        valid=frame['exceedance_count'].notna() & (frame['monkey_count']>0)
        frame.loc[valid,'empirical_p_value']=(frame.loc[valid,'exceedance_count']+1)/(frame.loc[valid,'monkey_count']+1)
        frame.loc[valid,'percentile_rank']=100*(frame.loc[valid,'monkey_count']-frame.loc[valid,'exceedance_count'])/(frame.loc[valid,'monkey_count']+1)
        frame['season_id']=sid;frames.append(frame)
    combined=pd.concat(frames,ignore_index=True)
    mask=combined['contestant_id'].str.startswith('CONTESTANT_') & combined['empirical_p_value'].notna()
    if int(mask.sum())!=840: raise ValueError('Declared 840-comparison family is incomplete')
    values=combined.loc[mask,'empirical_p_value'].to_numpy()
    for method,values_adj in adjust(values).items():
        key={'bonferroni':'bonferroni_p','holm':'holm_p','bh':'bh_q','by':'by_q'}[method]
        combined.loc[mask,key]=values_adj
    combined['family_size']=840
    combined['family_scope']='five_pools_six_contestants_28_animals_cumulative_cutoff'
    for sid in sids:
        combined[combined.season_id==sid].drop(columns='season_id').to_csv(root/'staging/runs'/f'{sid}_run/public/contestant_monkey_significance.csv',index=False)
    out=root/'staging/public';out.mkdir(parents=True,exist_ok=True)
    combined.to_csv(out/'all_seasons_significance.csv',index=False)
    summary=dict(family_size=840,alpha=.05,strict_threshold=.05/840,
        raw=int((values<.05).sum()),**{k:int((v<.05).sum()) for k,v in adjust(values).items()})
    save_json(out/'family_manifest.json',summary)
    return summary


def refresh(args):
    root=REPO_ROOT/'artifacts/evaluations'/args.evaluation_id
    if root.parent!=REPO_ROOT/'artifacts/evaluations': raise ValueError('Invalid evaluation identifier')
    sids=targets()
    with operation_lock(REPO_ROOT/'artifacts/evaluations/refresh.lock'):
        from arena.reports.refresh_release import recover_pending_publications
        recover_pending_publications()
        freeze(root,sids,args.end_date)
        stage=args.stage
        if stage=='verify-inputs':
            for sid in sids:
                runner,cfg=runner_from_inputs(root,sid,args.end_date)
                # Initialize Qlib before the independent named-field query.
                import qlib
                qlib.init(provider_uri=str(runner.market_provider.provider_uri),region='cn')
                result=verify_market(runner.market_provider,cfg.anchor_date,args.end_date)
                save_json(root/'inputs'/f'{sid}_quote_validation.json',result)
                print(f'[quotes] {sid}: {result}',flush=True)
        if stage in ('all','replay'):
            for sid in sids: replay(root,sid,args.end_date)
        for phase,count in [('pilot',args.pilot_count),('formal',args.monkey_count)]:
            if stage not in ('all',phase): continue
            for sid in sids:
                runner,results,exporter=load_replayed(root,sid,args.end_date)
                distributions=run_compact(runner,runner.run_dir/'monkey/compact',count,args.batch_size,args.threads,args.timeout)
                if phase=='formal':
                    exporter.export_monkey_reports(distributions,results,runner.registry)
                    manifest=json.loads((exporter.public_dir/'evaluation_manifest.json').read_text())
                    manifest.update(monkeys_per_random_spec=count,random_paths=count*10,
                        deterministic_references=1,p_resolution=1/(count+1),family_size=840,
                        monkey_nav_frequency='daily')
                    save_json(exporter.public_dir/'evaluation_manifest.json',manifest)
                del distributions
            if phase=='pilot':
                save_json(root/'pilot_complete.json',dict(count=count,seasons=sids,complete=True))
                print('[pilot] all pools completed; proceeding with the predeclared formal budget',flush=True)
        if stage in ('all','formal'):
            summary=family_corrections(root,sids)
            print(f'[statistics] {summary}',flush=True)
        if stage in ('all','publish'):
            from arena.reports.refresh_release import publish
            publish(root,sids,args.end_date,args.monkey_count)


def advance(args):
    """Advance all active pools in staging; publish dates only after full coverage."""
    import argparse
    from cli import cmd_step
    end=args.end_date or min(SeasonManager.get_season_config(s).end_date for s in targets())
    pd.Timestamp(end)
    from arena.calendar import TradingCalendar
    authorized_days=TradingCalendar().get_trading_days(min(SeasonManager.get_season_config(s).anchor_date for s in targets()),end)
    if not authorized_days:raise ValueError('Authorized cutoff contains no valuation sessions')
    end=authorized_days[-1]
    sids=targets()
    selected=getattr(args,'seasons',None)
    if selected not in (None,['all']) and set(selected)!=set(sids):
        raise ValueError('A complete 840-item release requires the five active pools; use step for an isolated local run')
    if not getattr(args,'monkeys',True):
        raise ValueError('A published rollforward requires current controls; use step --no-monkeys for local diagnostics')
    if getattr(args,'mock',False):
        raise ValueError('Mock data cannot replace the public active generation; use isolated run --mock')
    root=REPO_ROOT/'artifacts/evaluations'/f"advance_{end.replace('-','')}"
    with operation_lock(REPO_ROOT/'artifacts/evaluations/refresh.lock'):
        from arena.reports.refresh_release import recover_pending_publications
        recover_pending_publications()
        actual_dates=[]
        for sid in sids:
            cp=RUNS_DIR/f'{sid}_run/checkpoints/latest_state.pkl'
            with cp.open('rb') as stream: state=pickle.load(stream)
            actual_dates.append(next(iter(state['engines'].values())).daily_valuations[-1].date)
        if any(date>end for date in actual_dates): raise ValueError('Cannot rewind a published evaluation')
        if all(date==end for date in actual_dates):
            subprocess.run([sys.executable,str(REPO_ROOT/'scripts/audit_privacy.py')],check=True)
            print(f'[rollforward] all pools already valued through {end}; no duplicate execution',flush=True)
            return
        root.mkdir(parents=True,exist_ok=True)
        journal=root/'advance_journal.json'
        save_json(journal,dict(phase='staging',requested_cutoff=end,seasons=sids,previous_cutoffs=actual_dates))
        legacy=root/'legacy'
        for name in ('chronicles','web/js/data','seasons'):
            if not (legacy/name).exists():shutil.copytree(REPO_ROOT/name,legacy/name)
        for sid in sids:
            source=RUNS_DIR/f'{sid}_run'
            if not (legacy/'runs'/source.name).exists():shutil.copytree(source,legacy/'runs'/source.name)
            staged=root/'staging/runs'/source.name
            if not staged.exists():shutil.copytree(source,staged)
            cmd_step(argparse.Namespace(season=sid,run_id=None,output=str(root/'staging/runs'),
                anchor_date=SeasonManager.get_season_config(sid).anchor_date,end_date=end,
                initial_cash=500000.,mock=False,monkeys=True,monkey_count=args.monkey_count,contestants=None))
        files={}
        inputs=root/'inputs';inputs.mkdir(exist_ok=True)
        for sid in sids:
            cfg=effective_config(sid)
            run_dir=root/'staging/runs'/f'{sid}_run'
            with (run_dir/'checkpoints/latest_state.pkl').open('rb') as stream: state=pickle.load(stream)
            signals=state['signal_history']
            runner=WeeklyCycleRunner(anchor_date=cfg.anchor_date,end_date=end,initial_cash=cfg.initial_cash,
                season_id=sid,frozen_signals=signals,run_dir=run_dir)
            runner.load_checkpoint(state)
            runner._setup_market_provider(runner.registry.list_contestants(),None,None)
            runner.market_provider.snapshot_frozen=True
            atomic_pickle(inputs/f'{sid}_signals.pkl',signals)
            atomic_pickle(inputs/f'{sid}_market.pkl',runner.market_provider)
            for name in ('signals','market'):
                path=inputs/f'{sid}_{name}.pkl';files[str(path.relative_to(root))]=digest(path)
            runner.source_signature=hashlib.sha256((files[f'inputs/{sid}_signals.pkl']+files[f'inputs/{sid}_market.pkl']).encode()).hexdigest()
            runner.save_checkpoint_to_disk(run_dir/'checkpoints',runner.last_completed_cycle_idx)
            metadata_path=run_dir/'public/evaluation_manifest.json'
            metadata=json.loads(metadata_path.read_text())
            metadata.update(evaluation_id=root.name,cutoff=end,source_signature=runner.source_signature,
                            signal_source='preserved_prefix_plus_native_incremental_signals')
            save_json(metadata_path,metadata)
        save_json(inputs/'manifest.json',dict(cutoff=end,seasons=sids,files=files,
            historical_signal_source='preserved_prefix_plus_native_incremental_signals',market_vintage='current_market_snapshot'))
        family_corrections(root,sids)
        from arena.reports.refresh_release import publish
        publish(root,sids,end,args.monkey_count)
        # Global defaults move only after the generation is complete; no pre-compute bump.
        config=REPO_ROOT/'arena/config.py'
        import re
        code=config.read_text()
        code=re.sub(r'(DEFAULT_END_DATE\s*=\s*)[\"\'][^\"\']+[\"\']',lambda m:m.group(1)+repr(end),code)
        atomic_write(config,code.encode())
        save_json(journal,dict(phase='complete',requested_cutoff=end,seasons=sids))
