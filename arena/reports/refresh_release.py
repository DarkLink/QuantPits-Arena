"""Build verifiable repaired dispatches and publish one complete website bundle."""
import json
import os
import pickle
import re
import shutil
import subprocess
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import yaml
from arena.config import REPO_ROOT, RUNS_DIR
from arena.seasons import SeasonManager
from arena.evaluation import effective_config, load_replayed, save_json, digest
from arena.reports.statistics import empirical, adjust
from arena.state import atomic_write


def table(frame):
    from arena.reports.sanitizer import DualTierExporter
    formatted=frame.copy()
    for column in formatted:
        if pd.api.types.is_float_dtype(formatted[column]):
            formatted[column]=formatted[column].map(lambda v:f'{v:.4f}')
    return DualTierExporter._to_markdown_table(formatted,include_index=False)


def ptext(value):
    return 'N/A' if value is None or pd.isna(value) else f'{value:.6g}'


def public_paths(nav):
    return [c for c in nav if c.startswith('CONTESTANT_')]


def release_html(html, evaluation_id):
    """Install one bundle loader, including when republishing an existing release."""
    html=re.sub(r'([?&]v=)[^\"\' >]+',lambda m:m.group(1)+evaluation_id,html)
    html=re.sub(r'^.*<script src="js/data/(?:arena_(?:data(?:_preview)?|release)|seasons_index|season_[^"?]+)\.js[^\n]*\n','',html,flags=re.M)
    return re.sub(r'^([ \t]*)(<script src="js/adapter\.js[^\n]*)(\n|$)',
        lambda m:f'{m[1]}<script src="js/data/arena_release.js?v={evaluation_id}"></script>\n{m[1]}{m[2]}{m[3]}',
        html,count=1,flags=re.M)


def recover_publication(root):
    """Roll an interrupted publication back using its write-ahead journal."""
    journal_path=root/'publication_journal.json'
    if not journal_path.exists():return False
    journal=json.loads(journal_path.read_text())
    if journal['phase']!='prepared':return False
    for item in reversed(journal.get('runs',[])):
        target=RUNS_DIR/item['name'];backup=root/'swapped_runs'/item['name']
        ready=RUNS_DIR/item['ready']
        # A backup proves that the old directory was moved, even when installing
        # its replacement failed before returning to the caller.
        if backup.exists():
            if target.exists():shutil.rmtree(target)
            os.replace(backup,target)
        elif not item['existed'] and target.exists():
            shutil.rmtree(target)
        if ready.exists():shutil.rmtree(ready)
    for item in reversed(journal['files']):
        target=REPO_ROOT/item['path'];backup=root/'publication_backup'/item['path']
        if item['existed']:atomic_write(target,backup.read_bytes())
        elif target.exists():target.unlink()
    journal['phase']='rolled_back';save_json(journal_path,journal)
    return True


def recover_pending_publications():
    """Called under the common operation lock before reading live checkpoints."""
    for journal in sorted((REPO_ROOT/'artifacts/evaluations').glob('*/publication_journal.json')):
        if recover_publication(journal.parent):
            print(f'[recovery] {journal.parent.name}: interrupted publication rolled back',flush=True)


def replace_run(root,item):
    target=RUNS_DIR/item['name'];ready=RUNS_DIR/item['ready']
    replacement=root/'staging/runs'/item['name']
    if ready.exists():shutil.rmtree(ready)
    shutil.copytree(replacement,ready)
    backup=root/'swapped_runs'/item['name']
    backup.parent.mkdir(parents=True,exist_ok=True)
    if backup.exists():raise RuntimeError('Unrecovered publication run backup exists')
    if target.exists():os.replace(target,backup)
    os.replace(ready,target)


def read_controls(directory, count):
    manifest=json.loads((directory/'manifest.json').read_text())
    if not manifest.get('complete') or manifest['count']!=count:
        raise ValueError('Formal control coverage is incomplete')
    if manifest.get('nav_frequency')!='daily':
        raise ValueError('Daily controls require a fresh evaluation of weekly-only caches')
    data=np.empty((count,manifest['random_specs'],len(manifest['days'])))
    first=0
    for name,sha in manifest['batch_hashes'].items():
        path=directory/name
        if digest(path)!=sha: raise ValueError('Control batch digest differs')
        with np.load(path) as batch:
            values=batch['daily_nav'];size=len(values)
            if values.shape[1:]!=data.shape[1:] or first+size>count:
                raise ValueError('Daily control coverage differs')
            data[first:first+size]=values;first+=size
    if first!=count or not np.isfinite(data).all() or not (data>0).all():
        raise ValueError('Daily control sample count or valuation differs')
    return data,manifest


def build_monitoring(root,sids,count):
    from arena.controls.monkey import CANONICAL_STRATEGY_SPECS,map_animal_to_spec_id
    specs=[s.spec_id for s in CANONICAL_STRATEGY_SPECS.values() if not s.passive_pool]
    spec_index={s:i for i,s in enumerate(specs)}
    collected=[]; datasets={}
    for sid in sids:
        runner,paths,exporter=load_replayed(root,sid,json.loads((root/'inputs/manifest.json').read_text())['cutoff'])
        nav=pd.read_csv(exporter.public_dir/'daily_nav_curves.csv',index_col='datetime', float_precision="round_trip")
        control,manifest=read_controls(runner.run_dir/'monkey/compact',count)
        dates=[c.settle_date for c in runner.cycles]
        daily_dates=[runner.anchor_date]+manifest['days']
        if daily_dates!=nav.index.tolist():raise ValueError('Daily controls and contestants use different dates')
        dataset=dict(runner=runner,paths=paths,exporter=exporter,nav=nav,dates=dates,daily_dates=daily_dates,
                     spec_index=spec_index,cfg=effective_config(sid))
        datasets[sid]=dataset
        snapshots={}
        settlements={}
        histograms={}
        for spec,j in spec_index.items():
            # Each date's null sample is contiguous; retain only one pool's raw
            # matrix at a time, never all five complete daily matrices.
            values=np.ascontiguousarray(control[:,j,:].T)
            quantiles=np.quantile(values,[.05,.5,.95],axis=1)
            snapshots[spec]={runner.anchor_date:dict(p05=1.,median=1.,p95=1.)}
            snapshots[spec].update({date:dict(p05=float(quantiles[0,c]),median=float(quantiles[1,c]),p95=float(quantiles[2,c])) for c,date in enumerate(manifest['days'])})
            settlements[spec]={date:snapshots[spec][date] for date in dates}
            hist,edges=np.histogram((values[-1]-1)*100,bins=64)
            histograms[spec]=dict(edges_pct=edges.tolist(),counts=hist.tolist())
            matching=[name for name in public_paths(nav) if map_animal_to_spec_id(name.split('_',2)[2])==spec]
            for c,date in enumerate(daily_dates):
                null_values=np.zeros(count) if c==0 else values[c-1]-1
                for name in matching:
                    stats=empirical(float(nav.loc[date,name]-1),null_values)
                    collected.append(dict(season_id=sid,path_id=name,cutoff=date,**stats))
        reference=nav['BENCHMARK_taotie']
        snapshots['P_ALL_0']={date:dict(p05=float(value),median=float(value),p95=float(value)) for date,value in reference.items()}
        settlements['P_ALL_0']={date:snapshots['P_ALL_0'][date] for date in dates}
        save_json(exporter.public_dir/'monkey_timeline.json',snapshots)
        save_json(exporter.public_dir/'monkey_settlement_timeline.json',settlements)
        save_json(exporter.public_dir/'monkey_histograms.json',histograms)
        del control,values
        # Reconstruct meaningful execution diagnostics from full reference paths.
        diag=pd.read_csv(exporter.public_dir/'capital_constraint_diagnostics.csv', float_precision="round_trip")
        for row_i,row in diag.iterrows():
            cid=row['contestant_id'];aid=row['animal_id']
            key=next((key for key in paths if runner.registry.get_anonymous_id(key[0])==cid and key[1]==aid),None)
            if key:
                for field in ('stale_mark_count','rejected_order_count'):
                    diag.loc[row_i,field]=paths[key].diagnostics[field]
        diag.to_csv(exporter.public_dir/'capital_constraint_diagnostics.csv',index=False)
        print(f'[monitoring] {sid}: {len(daily_dates)} NAV dates; actual daily null quantiles complete',flush=True)
    frame=pd.DataFrame(collected)
    for cutoff in sorted(frame.cutoff.unique()):
        indices=frame.index[frame.cutoff==cutoff]
        if len(indices)!=840: raise ValueError('Monitoring family is incomplete')
        for method,values in adjust(frame.loc[indices,'empirical_p_value'].to_numpy()).items():
            frame.loc[indices,{'bonferroni':'bonferroni_p','holm':'holm_p','bh':'bh_q','by':'by_q'}[method]]=values
    frame['family_size']=840
    frame['interpretation']='descriptive_repeated_monitoring'
    frame.to_csv(root/'staging/public/monitoring_statistics.csv',index=False)
    for sid in sids:
        subset=frame[frame.season_id==sid].copy()
        subset.to_csv(datasets[sid]['exporter'].public_dir/'monitoring_statistics.csv',index=False)
        datasets[sid]['monitoring']=subset
    return datasets


def section_data(data,start,end):
    nav=data['nav']; names=public_paths(nav)
    sub=nav.loc[start:end,names]
    returns=(sub.iloc[-1]/sub.iloc[0]-1)*100
    cumulative=(sub.iloc[-1]-1)*100
    mdd=-(sub/sub.cummax()-1).min()*100
    monitoring=data['monitoring']; lookup=monitoring[monitoring.cutoff==end].set_index('path_id')
    rows=[]
    for name in names:
        rows.append(dict(path=name,contestant=name.split('_')[0]+'_'+name.split('_')[1],animal=name.split('_',2)[2],
            period_pct=float(returns[name]),cumulative_pct=float(cumulative[name]),nav=float(sub.iloc[-1][name]),
            period_mdd_pct=float(mdd[name]),raw_p=float(lookup.loc[name,'empirical_p_value']),
            bonferroni_p=float(lookup.loc[name,'bonferroni_p'])))
    metrics=pd.DataFrame(rows)
    return sub,metrics,lookup


def dispatch(data,start,end,title,language='en',append_october=False):
    sub,metrics,lookup=section_data(data,start,end)
    period=metrics.sort_values('period_pct',ascending=False); cumulative=metrics.sort_values('cumulative_pct',ascending=False)
    best,leader=period.iloc[0],cumulative.iloc[0]
    tao=data['nav'].loc[start:end,'BENCHMARK_taotie'];ghost=data['nav'].loc[start:end,'BENCHMARK_ghost_taotie']
    tao_ret=(tao.iloc[-1]/tao.iloc[0]-1)*100;ghost_ret=(ghost.iloc[-1]/ghost.iloc[0]-1)*100
    positive=int((metrics.period_pct>0).sum());raw=int((metrics.raw_p<.05).sum());bonf=int((metrics.bonferroni_p<.05).sum())
    cycles=[c for c in data['runner'].cycles if start<c.settle_date<=end]
    rebalances=sum(c.has_rebalance and c.trade_date>start for c in cycles)
    count=int(lookup.iloc[0].monkey_count)
    market=data.get('market_curve')
    market_ret=(market.loc[end]/market.loc[start]-1)*100 if market is not None else None
    model=metrics.groupby('contestant').agg(mean_pct=('period_pct','mean'),median_pct=('period_pct','median'),
        positive=('period_pct',lambda s:int((s>0).sum())),best_pct=('period_pct','max'),worst_pct=('period_pct','min'),
        mean_mdd_pct=('period_mdd_pct','mean')).reset_index()
    animals=metrics.groupby('animal').agg(mean_pct=('period_pct','mean'),median_pct=('period_pct','median'),
        best_pct=('period_pct','max'),worst_pct=('period_pct','min')).reset_index()
    eagle=metrics[metrics.animal=='eagle-5-1']
    spread=eagle.period_pct.max()-eagle.period_pct.min()
    top_columns=['path','period_pct','cumulative_pct','nav','period_mdd_pct','raw_p','bonferroni_p']
    for f in ('raw_p','bonferroni_p'): period[f]=period[f].map(ptext);cumulative[f]=cumulative[f].map(ptext)
    zh=language=='zh'
    facts=[
        f'{start} → {end}: {len(sub)-1} return sessions, {len(sub)} NAV observations including the reporting anchor; {rebalances} scheduled rebalances.',
        f'Period leader {best.path}: {best.period_pct:+.4f}%; end NAV {best.nav:.6f}.',
        f'Cumulative leader {leader.path}: {leader.cumulative_pct:+.4f}%; end NAV {leader.nav:.6f}.',
        f'{positive}/168 contestant paths gained during this segment; median path return {metrics.period_pct.median():+.4f}%.',
        f'Taotie {tao_ret:+.4f}% for the segment, end NAV {tao.iloc[-1]:.6f}; Ghost scenario {ghost_ret:+.4f}%, NAV {ghost.iloc[-1]:.6f}.',
        f'Cumulative leader raw p={ptext(leader.raw_p)}, Bonferroni p={ptext(leader.bonferroni_p)}; N={count:,} per matched random spec.',
        f'At this cutoff: {raw}/168 raw p<0.05 and {bonf}/168 Bonferroni p<0.05 in this pool, within the visible 840-item family.'
    ]
    if market_ret is not None: facts.insert(4,f'Market index segment return {market_ret:+.4f}%; end normalized NAV {market.loc[end]:.6f}.')
    if zh:
        facts=[f'{start} 至 {end}：{len(sub)-1} 个收益交易日，含报告锚点共 {len(sub)} 个净值观察；{rebalances} 次计划调仓。',
            f'区间第一 {best.path}：{best.period_pct:+.4f}%，期末 NAV {best.nav:.6f}。',
            f'累计第一 {leader.path}：{leader.cumulative_pct:+.4f}%，期末 NAV {leader.nav:.6f}。',
            f'168 条动物路径中 {positive} 条区间盈利；区间收益中位数 {metrics.period_pct.median():+.4f}%。',
            f'Taotie 区间 {tao_ret:+.4f}%，期末 NAV {tao.iloc[-1]:.6f}；Ghost 情景 {ghost_ret:+.4f}%，NAV {ghost.iloc[-1]:.6f}。',
            f'累计领先路径原始 p={ptext(leader.raw_p)}，Bonferroni p={ptext(leader.bonferroni_p)}；对应随机规格 N={count:,}。',
            f'本池截至该日：{raw}/168 原始 p<0.05，{bonf}/168 Bonferroni p<0.05；校正族仍包含全部五池 840 项。']
        if market_ret is not None:facts.insert(4,f'市场指数区间 {market_ret:+.4f}%，期末归一化 NAV {market.loc[end]:.6f}。')
    intro=(f'本篇在统一修复引擎下事后重放，采用旧快照保存的实际周原始信号，行情为本次冻结的现时日线快照。报告窗口锚点 {start}，截止 {end}。全部收益采用净值比率；收益差为百分点。旧版已在私有归档中保留，新版不构成当年事前发布的承诺。' if zh else
        f'This dispatch is a retrospective repair replay using the actual raw weekly signals preserved in legacy checkpoints and a frozen current daily-bar snapshot. Reporting anchor: {start}; cutoff: {end}. Period returns are NAV ratios; differences in returns are percentage points. Legacy artifacts are archived separately. This refreshed document is not evidence of a historical pre-market commitment.')
    text=f'# {title}\n\n{intro}\n\n'+('## ⚡ 战报速读 (TL;DR)' if zh else '## ⚡ TL;DR')+'\n\n'+'\n'.join('- '+f for f in facts)+'\n\n'
    text+=('## 区间与累计排名\n\n区间前十：\n\n' if zh else '## Period and cumulative standings\n\nTop ten for the reporting segment:\n\n')+table(period.head(10)[top_columns])+'\n\n'
    text+=('累计前十（截至本篇截止）：\n\n' if zh else 'Top ten cumulatively through this cutoff:\n\n')+table(cumulative.head(10)[top_columns])+'\n\n'
    text+=('区间后五：\n\n' if zh else 'Bottom five for the segment:\n\n')+table(period.tail(5)[top_columns])+'\n\n'
    text+=('## 六个匿名模型\n\n每个模型包含全部 28 个动物，不按获胜组合筛选。\n\n' if zh else '## Six anonymous contestants\n\nEach row includes all 28 animals; no selection of winning combinations.\n\n')+table(model)+'\n\n'
    text+=('## 全部动物策略\n\n每行汇总六个模型的区间收益；范围体现模型与策略的交互。\n\n' if zh else '## All animal policies\n\nEach row summarizes segment returns across the six contestants; the range describes contestant-policy interaction.\n\n')+table(animals)+'\n\n'
    mechanism=(f'TopK=5/DropN=1 在六模型间的区间收益跨度为 {spread:.4f} 个百分点；仅凭单个优胜路径不能认定集中度有普遍优势。Rabbit 的 DropN 控制每周可替换数量，并不是更高的交易频率。Sloth 的延迟及冷启动现金和 Snail 的暖启动旧信号会同时改变敞口与路径，因此这里只评价完整策略，不将差额归因于纯预测半衰期。Meerkat 分位带与反向 Koala 的表现应结合上表全模型分布阅读。\n\n模型级均值衡量跨动物的一致性，最优行只描述本窗口的实现收益。宽池与窄池的可选集合、费用、整手约束、现金暴露及模型信号截面共同影响结果；这些结果不识别单一宏观原因，也不揭示模型架构。' if zh else
        f'The TopK=5/DropN=1 segment spread across contestants is {spread:.4f} percentage points. A winning concentrated path does not establish a universal concentration advantage. Rabbit DropN changes weekly replacement capacity, not trading frequency. Sloth delay and cold-start cash, and Snail warm-start stale signals, jointly alter exposure and path dependence; these are whole-strategy comparisons, not an identified prediction half-life. Percentile Meerkats and inverted Koala should be read against the full contestant distribution above.\n\nContestant averages describe consistency across animals; the best row describes realized performance in this window. Pool membership, fees, lots, cash exposure and signal cross-sections all contribute to differences across environments. The results do not identify a single macro cause or disclose contestant architecture.')
    text+=('## 机制解释与边界\n\n' if zh else '## Mechanisms and interpretation\n\n')+mechanism+'\n\n'
    method=(f'猴群只按 TopK/DropN 匹配，保留十随机规格和一确定性被动参考，不增加延迟、暖冷启动、反向或分位专用种类。上表 p 使用从开场锚点累计的收益，并非区间收益 p；上尾 k 包含相等，p=(k+1)/(N+1)。N={count:,} 的最小 p 为 {1/(count+1):.8g}，不能写成零。Bonferroni/Holm/BH/BY 另行保存，840 项阈值为 {0.05/840:.8g}，严格小于。当前正式数量下至多 4 个超越可通过 Bonferroni。猴群现金与持仓跨周延续，按每个交易日保存真实净值和分位数，周结值用于报告切段。过去截止与反复日度或周度监测为描述性统计，未对所有历史窗口再次控制联合家族错误，也未计入隐含研究筛选。Monte Carlo 区间只衡量模拟尾概率误差，不增加真实市场样本。\n\n撮合采用当日有限正报价，缺价不卖出注销持仓；估值允许最近有效收盘价并记陈旧次数。成员身份与可负担筛选分离；周五冻结意图，周一撮合。Taotie 使用普通账户资本比例 1.0 与相同分配机制，Ghost 是较低资本粒度摩擦情景，不是无费用纯等权。换手口径为买卖双边成交总额除以周初资产。\n\n本版仍属日线研究：全日成交量只是事后可交易性代理；缺少完整可靠的企业行为、开盘方向限制及容量信息。没有把因子变化猜成分红，也没有混用复权单位与未调整股数来宣称修复总回报。严格执行模式在数据覆盖不足时拒绝运行。' if zh else
        f'Matching uses TopK/DropN only: ten random specifications and one deterministic passive reference. Delay, warm/cold starts, inversion and percentile selection do not introduce extra species. The p values above test cumulative returns from inception, not segment returns. The upper tail includes ties: p=(k+1)/(N+1). At N={count:,}, minimum p is {1/(count+1):.8g}, never zero. Bonferroni/Holm/BH/BY are stored separately. The 840-item raw threshold is {0.05/840:.8g}, with strict inequality; at the formal count, up to four exceedances can pass Bonferroni. The same monkeys retain cash and positions across weeks; actual daily NAV and pointwise quantiles are saved, while weekly settlements define reporting segments. Earlier cutoffs and repeated daily or weekly reviews are descriptive monitoring. Correction does not cover all historical windows jointly or hidden prior research selection. Monte Carlo intervals measure simulation tail uncertainty and add no market history.\n\nExecution requires finite positive same-day quotes; missing-price sells retain the position. Valuation may carry the last valid close with stale-mark counts. Pool membership is separate from affordability. Decision-close intent is frozen before Monday execution. Taotie uses a 1.0 standard-account capital ratio and the same allocation policy. Ghost is a capital-granularity scenario, not a costless equal-weight index. Turnover is gross buys plus gross sells divided by starting assets.\n\nThis remains daily-bar research: full-day volume is a retrospective tradability proxy. Complete verified corporate-action, opening direction-limit and capacity data are unavailable. Factor changes are not guessed into dividend payments, and adjusted prices are not mixed with unchanged nominal shares to claim a total-return repair. Strict execution fails its preflight without required coverage.')
    text+=('## 随机检验与执行口径\n\n' if zh else '## Random-control and execution contract\n\n')+method+'\n\n'
    if append_october:
        sub_oct,oct_metrics,_=section_data(data,'2026-09-30','2026-10-09')
        text+=('## 十月独立附录\n\n9月30日收盘至10月9日包含2个收益交易日；周一休市不补调仓。下表单独报告十月区间，未混入九月收益。\n\n' if zh else '## Separate October appendix\n\nSeptember 30 close to October 9 contains two return sessions. The holiday Monday produces no makeup rebalance. October is reported separately from September.\n\n')+table(oct_metrics.sort_values('period_pct',ascending=False).head(10)[top_columns])+'\n'
    return text.rstrip()+"\n",dict(leader=leader.path,nav=float(leader.nav),return_pct=float(leader.cumulative_pct),period_leader=best.path,period_return_pct=float(best.period_pct),positive=positive,sessions=len(sub)-1,raw=raw,bonferroni=bonf)


def build_dispatches(root,datasets):
    staged=root/'staging'; summaries={}
    for sid,data in datasets.items():
        cfg=data['cfg']; entries=cfg.raw_dict.setdefault('dispatches',{}).setdefault('episodes',[])
        latest_end=data['dates'][-1]
        if not any(str(e.get('date'))==latest_end for e in entries):
            entries.append(dict(id=f"refresh_{latest_end.replace('-','')}",date=latest_end,
                file=f"chronicles/en/{sid}_{latest_end.replace('-','')}.md",tab_label=f"{latest_end} Recalculated"))
        calendar=cfg.raw_dict.get('calendar',cfg.raw_dict.get('horizon',{}))
        calendar['end_date']=latest_end
        cfg.end_date=latest_end
        for entry in entries:
            file=entry['file'];end=entry['date']
            if end=='2026-08-28': start='2026-07-03'
            elif '_m3' in file: start='2026-08-28'
            else:
                prior=[d for d in data['dates'] if d<end]
                start=prior[-1] if prior else cfg.anchor_date
            name=Path(file).name
            title=(f'{sid} — repaired baseline through {end}' if end=='2026-08-28' else f'{sid} — repaired dispatch through {end}')
            text,summary=dispatch(data,start,end,title,append_october='_m3' in file)
            target=staged/file;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text)
            web=staged/'web'/file;web.parent.mkdir(parents=True,exist_ok=True);web.write_text(text)
            # Preserve existing Chinese episode file names and create missing counterparts.
            if sid=='season_01':
                prefix='episodes_01_08_' if end=='2026-08-28' else f"episode_{entry['id'].replace('ep','')}_"
                matches=list((REPO_ROOT/'chronicles/zh').glob(prefix+'*.md'))
                zh_name=matches[0].name if matches else name
            else:
                matches=list((REPO_ROOT/'chronicles/zh').glob(Path(name).stem+'*.md'))
                zh_name=matches[0].name if matches else name
            zh,_=dispatch(data,start,end,title,language='zh',append_october='_m3' in file)
            target=staged/'chronicles/zh'/zh_name;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(zh)
            entry.update(title=title,summary=f"Repaired replay: {summary['sessions']} return sessions; {summary['period_leader']} segment {summary['period_return_pct']:+.2f}%. Cumulative leader {summary['leader']} at NAV {summary['nav']:.4f}.",badge='Recalculated',read_time='8 min read')
        latest_start=data['dates'][-2] if len(data['dates'])>1 else cfg.anchor_date
        _,latest=dispatch(data,latest_start,latest_end,sid)
        summaries[sid]=latest
        d=cfg.raw_dict.setdefault('dispatches',{})
        d['executive']={'tag':'Repaired Research Release','title':f'{sid}: through {latest_end}',
            'window_label':f'{cfg.anchor_date} ~ {latest_end} · {len(data["nav"])} NAV observations · {len(data["nav"])-1} return sessions',
            'nature_label':'Retrospective repair using preserved historical signals; daily-bar execution research.',
            'leader_summary':f"{latest['leader']} leads at NAV {latest['nav']:.4f} ({latest['return_pct']:+.2f}%). October segment leader {latest['period_leader']} at {latest['period_return_pct']:+.2f}%."}
        d['climate']={'tag':'Recalculated Market Review','status_badge':'Released','title':'Recalculated reporting segment',
            'summary':f"{latest_start} ~ {latest_end}: {latest['positive']}/168 contestant paths positive. All statistics use the repaired execution policy and 100,000 matched random controls per spec.",
            'bullets':[f"{latest['raw']}/168 raw cumulative p<0.05 in this pool; {latest['bonferroni']}/168 Bonferroni p<0.05 within the complete 840-item family.",
                'Past dispatches are retrospectively recalculated; historical pre-market commitment is not established.',
                'Daily-bar research lacks complete verified corporate actions and opening direction-limit data.'],
            'decrypt_label':f'All dispatches recalculated through {latest_end}'}
        cfg.raw_dict.setdefault('banner',{})['proof_text']='Repaired daily-bar research: 10 random TopK/DropN specs × 100,000 controls per pool, plus one deterministic passive reference. Complete visible family: 840 comparisons.'
        path=staged/'seasons'/sid/'season_config.yaml';path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(yaml.safe_dump(cfg.raw_dict,sort_keys=False,allow_unicode=True))
    # Draft season retains its future horizon, receives only effective rule configuration.
    for sid in set(SeasonManager.list_seasons())-set(datasets):
        cfg=effective_config(sid)
        path=staged/'seasons'/sid/'season_config.yaml';path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(yaml.safe_dump(cfg.raw_dict,sort_keys=False,allow_unicode=True))
    text='# Recalculated arena dispatches\n\nAll listed reports use the preserved historical raw signals and the unified repaired daily-bar research engine. The formal controls contain 100,000 random paths per TopK/DropN specification, ten random specifications per pool, plus one deterministic passive reference. Historical versions remain in the local evaluation archive.\n\n'
    for path in sorted((staged/'chronicles/en').glob('*.md')):text+=f'- [{path.stem}]({path.name})\n'
    (staged/'chronicles/en/README.md').write_text(text)
    (staged/'chronicles/zh/README.md').write_text(text.replace('Recalculated arena dispatches','重算后的斗技场战报').replace('chronicles/en','chronicles/zh'))
    return summaries


def publish(root,sids,end_date,count):
    from arena.evaluation import family_corrections
    recover_publication(root)
    sids=sorted(sids,key=SeasonManager.season_sort_key)
    registered=SeasonManager.list_seasons()
    # Reusing a staged evaluation must not resurrect removed draft seasons.
    staged_seasons=root/'staging/seasons'
    if staged_seasons.exists():
        for directory in staged_seasons.iterdir():
            if directory.is_dir() and directory.name not in registered:shutil.rmtree(directory)
    family_corrections(root,sids)
    common_sources=['arena/data/market.py','arena/portfolio/engine.py','arena/portfolio/policy.py',
        'arena/portfolio/types.py','arena/portfolio/costs.py','arena/runner/weekly_cycle.py',
        'arena/calendar.py','arena/controls/compact.py','arena/controls/compact_kernel.cpp',
        'arena/benchmarks/index.py','arena/reports/statistics.py',
        'arena/contestants/adapters/historical.py']
    common_sources += [str(p.relative_to(REPO_ROOT)) for p in sorted((REPO_ROOT/'arena/animals').glob('*.py'))]
    source_hashes={name:digest(REPO_ROOT/name) for name in common_sources}
    for sid in sids:
        path=root/'staging/runs'/f'{sid}_run/public/evaluation_manifest.json'
        value=json.loads(path.read_text());value['execution_source_hashes']=source_hashes
        save_json(path,value)
    datasets=build_monitoring(root,sids,count)
    # Obtain independently exported market index curves before composing reports.
    for sid,data in datasets.items():
        output=root/'staging/web/js/data'/f'{sid}.js'
        data['exporter'].export_web_payload(data['cfg'],web_output_path=output,publish_auxiliary=False)
        payload=json.loads(output.read_text().split(f'window.ARENA_SEASONS_DATA["{sid}"] = ',1)[1].rstrip().rstrip(';'))
        curves=payload['nav_timeline']['curves']
        if 'BENCHMARK_market' not in curves: raise ValueError('Market index curve missing')
        data['market_curve']=pd.Series(curves['BENCHMARK_market'],index=payload['nav_timeline']['dates'])
    summaries=build_dispatches(root,datasets)
    # Updated configs reside in the in-memory effective objects until publication.
    outputs=[];index=[]
    for sid,data in datasets.items():
        output=root/'staging/web/js/data'/f'{sid}.js'
        data['exporter'].export_web_payload(data['cfg'],web_output_path=output,publish_auxiliary=False)
        content=output.read_text();outputs.append(content)
        payload=json.loads(content.split(f'window.ARENA_SEASONS_DATA["{sid}"] = ',1)[1].rstrip().rstrip(';'))
        meta=payload['meta']
        index.append(dict(id=sid,title=data['cfg'].title,short_title=data['cfg'].raw_dict.get('short_title',data['cfg'].universe_code),
            status=data['cfg'].status,badge_type='active',period='2026.07 - 2026.10',anchor_date=data['cfg'].anchor_date,
            end_date=end_date,trading_days=len(data['nav']),contestants_count=6,animals_count=28,
            description=data['cfg'].description,dispatches_banner=dict(title='Recalculated research dispatches',link='#dispatches',link_text='Read dispatches'),
            methodology=dict(framework_name='Daily-bar repair research',anchor_spec='Preserved historical weekly signals',
                capital_spec='Normalized NAV; declared standard account and round lots',
                benchmarks_summary='Market index + Taotie + Ghost scenario + 10 × 100,000 random paths + 1 deterministic reference',
                execution_flow='Decision-close frozen intent; Monday execution; closed Mondays skip rebalance')))
        if sid=='season_01':
            legacy='window.ARENA_DATA = '+json.dumps(payload,ensure_ascii=False,allow_nan=False)+';\n'
            (root/'staging/web/js/data/arena_data.js').write_text(legacy)
    for sid in sorted(set(registered)-set(sids),key=SeasonManager.season_sort_key):
        cfg=effective_config(sid)
        index.append(dict(id=sid,title=cfg.title,short_title=cfg.raw_dict.get('short_title',cfg.universe_code),status=cfg.status,
            anchor_date=cfg.anchor_date,end_date=cfg.end_date,trading_days=0,contestants_count=6,animals_count=28,
            description='Draft season; no future observations generated.',badge_type='warning'))
    index.sort(key=lambda value:SeasonManager.season_sort_key(value['id']))
    index_text='window.ARENA_SEASONS_INDEX = '+json.dumps(index,ensure_ascii=False,indent=2)+';\n'
    (root/'staging/web/js/data/seasons_index.js').write_text(index_text)
    bundle='\n'.join(outputs)+legacy+index_text+'window.ARENA_ACTIVE_EVALUATION = '+json.dumps(root.name)+';\n'
    bundle_path=root/'staging/web/js/data/arena_release.js';bundle_path.write_text(bundle)
    html=release_html((REPO_ROOT/'web/index.html').read_text(),f'{root.name}-{digest(bundle_path)[:12]}')
    (root/'staging/web/index.html').write_text(html)
    # Publishing journal keeps backups before every replace. Bundle is the last data commit.
    publish_files=[]
    for base in ('chronicles','seasons','web'):
        publish_files.extend(p for p in (root/'staging'/base).rglob('*') if p.is_file())
    # Existing page keeps its old named data until the complete bundle and loader switch.
    def phase(path):
        rel=path.relative_to(root/'staging')
        if rel==Path('web/index.html'): return 3
        if rel==Path('web/js/data/arena_release.js'): return 2
        if str(rel).startswith('web/js/data/'): return 4
        return 1
    publish_files.sort(key=lambda p:(phase(p),str(p)))
    journal_path=root/'publication_journal.json'
    # A completed earlier publish may have backups under this evaluation ID.
    # Clear them before preparing the new journal, so untouched runs cannot be
    # mistaken for runs moved by the new transaction during recovery.
    old_runs=root/'swapped_runs'
    if old_runs.exists():shutil.rmtree(old_runs)
    journal=dict(evaluation_id=root.name,phase='prepared',files=[],runs=[],cutoff=end_date)
    for path in publish_files:
        rel=path.relative_to(root/'staging');target=REPO_ROOT/rel
        backup=root/'publication_backup'/rel
        if target.exists():backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,backup)
        journal['files'].append(dict(path=str(rel),existed=target.exists(),sha256=digest(path)))
    for sid in sids:
        name=f'{sid}_run'
        journal['runs'].append(dict(name=name,ready=f'.{sid}_{root.name}.ready',existed=(RUNS_DIR/name).exists()))
    save_json(journal_path,journal)
    # Scan ignored staging explicitly, then run the mandatory repository audit.
    from scripts.audit_privacy import scan_file
    public_staging=publish_files+list((root/'staging/public').glob('*'))
    for path in public_staging:
        findings=scan_file(path)
        if findings:
            raise ValueError(f"Staged public privacy audit failed: {path.relative_to(root)}; {len(findings)} rule violations")
    try:
        for item in journal['files']:
            rel=Path(item['path'])
            if phase(root/'staging'/rel)>=2:continue
            atomic_write(REPO_ROOT/rel,(root/'staging'/rel).read_bytes())
        subprocess.run([sys.executable,str(REPO_ROOT/'scripts/audit_privacy.py')],cwd=REPO_ROOT,check=True)
        for item in journal['runs']:
            replace_run(root,item)
        # One complete bundle is committed before the first loader cutover. Existing
        # legacy aliases are updated only after the page reads the atomic bundle.
        for item in journal['files']:
            rel=Path(item['path'])
            if phase(root/'staging'/rel)>=2:
                atomic_write(REPO_ROOT/rel,(root/'staging'/rel).read_bytes())
        subprocess.run([sys.executable,str(REPO_ROOT/'scripts/audit_privacy.py')],cwd=REPO_ROOT,check=True)
        journal['phase']='complete';save_json(journal_path,journal)
        save_json(root/'complete.json',dict(evaluation_id=root.name,cutoff=end_date,seasons=sids,
            random_paths=count*10*len(sids),deterministic_references=len(sids),monkey_nav_frequency='daily',
            bundle_sha256=digest(bundle_path),summaries=summaries))
    except BaseException:
        recover_publication(root)
        raise
    print(f'[publish] {root.name}: {len(sids)} pools, {count*10*len(sids):,} random paths, all dispatches refreshed',flush=True)
