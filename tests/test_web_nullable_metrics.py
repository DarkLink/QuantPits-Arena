"""Exercise published nullable metrics through view and deferred tooltip callbacks."""
import subprocess

import pytest

from arena.config import REPO_ROOT


@pytest.mark.parametrize('entry', ['matrix', 'scatter', 'panorama', 'benchmark_anchors', 'late_entry', 'curve_tooltips', 'observation_gaps', 'fingerprints', 'details', 'table', 'formatting'])
def test_nullable_view_runtime(entry):
    program = r'''
const fs = require('fs'), vm = require('vm'), assert = require('assert/strict');
const nodes = new Map(), charts = new Map();
function node(id) {
 if (!nodes.has(id)) nodes.set(id, {id, innerHTML:'', textContent:'', style:{}, addEventListener(){},
  querySelectorAll(){return [];}, querySelector(){return null;},
  classList:{toggle(){}, add(){}, remove(){}, contains(){return true;}}});
 return nodes.get(id);
}
global.window = {addEventListener(){}, location:{hash:'', search:'', href:'https://arena.invalid/'}};
global.document = {readyState:'loading', addEventListener(){}, getElementById:node,
 documentElement:{getAttribute(){return 'dark';}}, querySelectorAll(){return [];}, querySelector(){return null;}};
global.setTimeout = callback => {callback(); return 0;};
global.echarts = {getInstanceByDom(){return null;}, init(dom){return {
 setOption(option){charts.set(dom.id, option);}, resize(){}, on(){}, off(){},
 getOption(){return {series:[]};}};}, graphic:{LinearGradient:function(){}}};
for (const file of ['js/data/arena_release.js','js/adapter.js','js/components/charts.js',
 'js/views/landing.js','js/views/overview.js','js/views/leaderboard_view.js','js/views/animals_view.js',
 'js/views/path_detail.js','js/views/contestant_detail.js','js/views/decision_audit.js',
 'js/views/methodology.js','js/views/disclaimer.js']) vm.runInThisContext(fs.readFileSync('web/'+file,'utf8'));
function safeText(text, context = '') {
 assert(!/NaN|Infinity|undefined|>\s*null\s*</.test(text), 'Invalid value exposed by the view: '+context);
 assert(!/Error Loading|Failed to render/.test(text), 'The view swallowed a runtime exception');
}
const checks = {
 curve_tooltips(data) {
  const adapter=window.arenaAdapter,dates=adapter.getNavDates();
  for(const cid of ['CONTESTANT_A','CONTESTANT_G'])for(const metric of ['nav','drawdown','excess_csi300']){
   const path=adapter.getPath(cid+'_robot'),taotie=adapter.getBenchmarkTaotieCurve(),market=adapter.getBenchmarkCsi300Curve();
   for(const render of [()=>window.ArenaCharts.renderEquityCurves('tooltip-curve',dates,path,taotie,market,null,metric),
    ()=>window.ArenaCharts.renderMultiAnimalCurves('tooltip-curve',dates,[path],taotie,market,metric)]){
    render();const option=charts.get('tooltip-curve');
    const tooltip=value=>option.tooltip.valueFormatter?option.tooltip.valueFormatter(value):option.tooltip.formatter([{axisValue:dates.at(-1),seriesName:cid,value,color:'#fff'}]);
    for(const value of [null,undefined,NaN,Infinity,-Infinity]){
     const text=tooltip(value);safeText(text,'curve tooltip');assert(text.includes('N/A'),'Missing curve values were not labeled N/A');
    }
    for(const value of [0,1.23456,-1.23456]){
     const expected=metric==='nav'?value.toFixed(4):metric==='drawdown'?value.toFixed(2)+'%':(value>=0?'+':'')+value.toFixed(2)+' pp';
     assert(tooltip(value).includes(expected),'Curve tooltip units or precision differ across observation participants');
    }
   }
  }
 },
 observation_gaps(data) {
  const adapter=window.arenaAdapter,dates=adapter.getNavDates(),path=adapter.getPath('CONTESTANT_G_robot');
  const first=dates.indexOf(path.observation_start);
  const modes=['nav','drawdown','excess_csi300'],baseline=new Map();
  const draw=metric=>window.ArenaCharts.renderEquityCurves('gaps',dates,path,adapter.getBenchmarkTaotieCurve(),adapter.getBenchmarkCsi300Curve(),null,metric);
  for(const metric of modes){draw(metric);baseline.set(metric,charts.get('gaps'));}
  for(const id of [path.path_id,'BENCHMARK_taotie','BENCHMARK_csi300','BENCHMARK_ghost_taotie']){
   const curve=adapter.getNavCurve(id),original=[...curve];
   for(const [day,value] of [[first,null],[first,0],[first+1,null]]){
    curve[day]=value;
    for(const metric of modes){
     draw(metric);
     const option=charts.get('gaps');
     assert.equal(option.xAxis.data[0],path.observation_start,'A missing anchor silently moved the observation period');
     for(const [i,series] of option.series.entries()){
      assert.equal(series.data.length,dates.length-first,'A missing point shifted the timeline');
      assert(series.data.every(v=>v===null||Number.isFinite(v)),'The chart divided by an unavailable or zero anchor');
      const seriesId={market:'BENCHMARK_csi300',taotie:'BENCHMARK_taotie',ghost:'BENCHMARK_ghost_taotie'}[series.benchmarkKey]||path.path_id;
      const affected=seriesId===id||metric==='excess_csi300'&&id==='BENCHMARK_csi300';
      if(affected){
       assert.equal(series.data[day-first],null,'The chart manufactured a value for an unavailable observation');
       if(day===first)assert(series.data.every(v=>v===null),'A missing anchor was silently replaced with a later NAV');
      } else assert.deepEqual(series.data,baseline.get(metric).series[i].data,'A missing point changed an unrelated curve');
     }
    }
    window.PathDetailView.render('root',path.path_id);safeText(node('root').innerHTML,'path benchmark card');
    for(const metric of modes){
     window.ArenaCharts.renderMultiAnimalCurves('profile-gaps',dates,[path],adapter.getBenchmarkTaotieCurve(),adapter.getBenchmarkCsi300Curve(),metric);
     const option=charts.get('profile-gaps');
     assert.equal(option.xAxis.data[0],path.observation_start);
     for(const series of option.series){
      assert.equal(series.data.length,dates.length-first);
      assert(series.data.every(v=>v===null||Number.isFinite(v)),'A profile chart manufactured a value from a missing observation');
     }
    }
    window.ContestantDetailView.render('root',path.contestant_id);safeText(node('root').innerHTML,'profile benchmark coverage');
    Object.assign(window.AnimalsView,{comparisonMode:'multi',activeFocusModel:path.contestant_id,selectedAnimalIds:['robot'],activeMetric:'nav'});
    window.AnimalsView.render('root');safeText(node('root').innerHTML,'Zoo benchmark coverage');
    curve.splice(0,curve.length,...original);
   }
  }
 },
 fingerprints(data) {
  for(const cid of ['CONTESTANT_A','CONTESTANT_G']){
   const sample=structuredClone(data),missing=['robot','rabbit-1','eagle-5-1','koala','meerkat-30'];
   sample.paths=sample.paths.filter(p=>p.contestant_id!==cid||!missing.includes(p.animal_id));
   sample.paths.find(p=>p.path_id===cid+'_rabbit-2').total_return_pct=0;
   const untested=sample.paths.find(p=>p.path_id===cid+'_turtle');untested.empirical_p_value=null;untested.p_value=null;
   const adapter=window.arenaAdapter=new window.ArenaDataAdapter(sample),fp=adapter.getContestantFingerprints(cid);
   assert.equal(fp.turnoverData[1].return,null,'A missing baseline was presented as a flat return');
   assert.equal(fp.turnoverData[2].return,null);assert.equal(fp.turnoverData[3].return,0,'A measured zero was hidden');
   assert.equal(fp.breadthData[0].return,null);assert.equal(fp.meerkatData[2].return,null);
   assert.deepEqual(fp.directionData,{robot:null,koala:null,spread:null},'A direction spread was manufactured from missing returns');
   window.ContestantDetailView.render('root',cid);const html=node('root').innerHTML;safeText(html);
   assert(/Baseline Handler \(Robot\)[\s\S]*?>\s*N\/A\s*<\/div>/.test(html),'The profile reports a zero baseline for an unavailable handler');
   assert(html.includes(`Across ${sample.paths.filter(p=>p.contestant_id===cid).length} available handlers`));
   if(cid==='CONTESTANT_A'){
    const tested=sample.paths.filter(p=>p.contestant_id===cid&&Number.isFinite(p.empirical_p_value));
    assert(html.includes(`${tested.filter(p=>p.empirical_p_value<.05).length} / ${tested.length}`),'Missing tests were included in the significance denominator');
   }
   assert.equal(charts.get('chart-fingerprint-turnover').series[0].data[1],null);
  }
 },
 scatter(data) {
  const path = data.paths.find(p => p.contestant_id === 'CONTESTANT_A');
  path.sharpe_ratio = null; path.empirical_p_value = null; path.p_value = null;
  const formatPValue = window.formatPValue, formatPercentile = window.formatPercentile;
  window.formatPValue = undefined; window.formatPercentile = undefined;
  window.ArenaCharts.renderScatter('scatter', data.paths);
  const option = charts.get('scatter');
  for (const point of option.series[0].data) safeText(option.tooltip.formatter({data:point}));
  assert(option.tooltip.formatter({data:option.series[0].data.find(point => point[3] === path)}).includes('N/A'));
  window.formatPValue = formatPValue; window.formatPercentile = formatPercentile;
 },
 matrix(data) {
  const view = window.LeaderboardView;
  view.activeTab = 'matrix'; view.render('root');
  for (const metric of ['total_return_pct','percentile_rank','max_drawdown_pct','sharpe_ratio']) {
   view.changeMatrixMetric(metric);
   const option = charts.get('chart-leaderboard-matrix');
   assert.deepEqual(option.yAxis.data, window.arenaAdapter.getAllContestants().map(c => c.id),
    'The actual HeatMap view omitted an admitted participant');
   assert.equal(option.series[0].data.length, option.yAxis.data.length * option.xAxis.data.length);
   for (const cell of option.series[0].data) {
    const value = cell.value || cell;
    const params = {data:cell, value};
    const tooltip = option.tooltip.formatter(params);
    const label = cell.label?.formatter || option.series[0].label.formatter(params);
    safeText(tooltip); safeText(String(label));
    const path = window.arenaAdapter.getPath(value[3]);
    if (path.observation_start) {
     const expected = path[metric];
     assert.equal(value[2], Number.isFinite(expected) ? expected : null,
      'An available observation-period metric was hidden');
     if (!Number.isFinite(expected)) assert.equal(label, 'N/A');
     assert(tooltip.includes(path.observation_start));
     assert(option.yAxis.axisLabel.formatter(path.contestant_id).includes(path.observation_start),
      'A later entrant has no visible period label');
    }
   }
  }
 },
 panorama(data) {
  const original = JSON.stringify(data.nav_timeline);
  window.OverviewView.render('root'); safeText(node('root').innerHTML);
  for (const focus of ['all','CONTESTANT_A','CONTESTANT_G']) {
   window.OverviewView.activeFocusModel = focus;
   for (const group of ['top5','robot','eagle','sloth','snail','turnover','koala']) {
    window.OverviewView.activeFilterGroup = group;
    for (const metric of ['nav','drawdown','excess_taotie','excess_ghost','excess_csi300']) {
     window.OverviewView.activeMetricMode = metric; window.OverviewView.updatePanoramaChart();
     const option = charts.get('chart-arena-panorama');
     const start = focus === 'CONTESTANT_G' ? '2026-10-09' : data.nav_timeline.dates[0];
     assert.equal(option.xAxis.data[0], start, 'Panorama mixes participant observation windows');
     assert(node('panorama-observation-window').textContent.includes(start));
     const selected = data.paths.filter(p => p.contestant_id !== 'BENCHMARK' && (focus === 'all' || p.contestant_id === focus));
     const groups = {robot:p=>p.animal_id==='robot', eagle:p=>p.animal_id.startsWith('eagle'),
      sloth:p=>p.animal_id.startsWith('sloth'), snail:p=>p.animal_id.startsWith('snail'),
      turnover:p=>p.animal_id.startsWith('rabbit')||p.animal_id==='turtle', koala:p=>p.animal_id==='koala'};
     const expectedPaths = group === 'top5'
      ? selected.filter(p => focus !== 'all' || p.full_season_eligible !== false).sort((a,b)=>b.total_return_pct-a.total_return_pct).slice(0,6)
      : selected.filter(groups[group]);
     assert.deepEqual(option.series.filter(s => !s.name.includes('Taotie') && s.name.startsWith('CONTESTANT_')).map(s=>s.name),
      expectedPaths.map(p=>p.path_id), 'A panorama cohort silently omitted matching participants or handlers');
     for (const series of option.series) {
      assert.equal(series.data.length, option.xAxis.data.length);
      assert(series.data.every(v=>v===null||Number.isFinite(v)));
      const path = data.paths.find(p => p.path_id === series.name);
      if (path) {
       const first = data.nav_timeline.dates.indexOf(start);
       const values = data.nav_timeline.curves[path.path_id].slice(first);
       const anchor = values.findIndex(Number.isFinite), base = values[anchor];
       const nav = values.map(v => v===null?null:v/base); let peak = 1;
       const referenceId = {excess_taotie:'BENCHMARK_taotie', excess_ghost:'BENCHMARK_ghost_taotie', excess_csi300:'BENCHMARK_csi300'}[metric];
       const reference = referenceId && data.nav_timeline.curves[referenceId].slice(first);
       const expected = nav.map((v,i) => {if(v===null)return null;peak = Math.max(peak,v); return metric === 'nav' ? v : metric === 'drawdown' ? (v/peak-1)*100 : (v-reference[i]/reference[anchor])*100;});
       assert(series.data.every((v,i) => expected[i]===null?v===null:Number.isFinite(v)&&Math.abs(v-expected[i]) < 0.011), 'Panorama values use a different benchmark anchor');
       assert.equal(series.connectNulls, false);
       assert.equal(series.data[anchor], metric==='nav'?1:0);
       if(metric==='nav')assert.deepEqual(series.data, values, 'Panorama changed the published NAV history');
      } else {
       assert.equal(series.data[0], metric === 'nav' ? 1 : 0);
      }
     }
     for (const day of [0, option.xAxis.data.length-1]) safeText(option.tooltip.formatter(
      option.series.map(s => ({axisValue:option.xAxis.data[day],seriesName:s.name,value:s.data[day],color:'#fff'}))));
     assert(option.tooltip.formatter([{axisValue:start,seriesName:'Unavailable',value:null,color:'#fff'}]).includes('N/A'));
    }
   }
  }
  assert.equal(JSON.stringify(data.nav_timeline),original);
 },
 benchmark_anchors(data) {
  const adapter=window.arenaAdapter,dates=adapter.getNavDates();
  for(const participant of adapter.getAllContestants()){
   const path=adapter.getPath(participant.id+'_robot'),curve=adapter.getNavCurve(path.path_id);
   const first=dates.indexOf(path.observation_start||dates[0]);
   for(const [method,reference] of [['getPathExcessTaotie','BENCHMARK_taotie'],['getPathExcessGhostTaotie','BENCHMARK_ghost_taotie'],['getPathExcessMarket','BENCHMARK_csi300']]){
    const values=adapter[method](path.path_id),benchmark=adapter.getNavCurve(reference);
    assert.equal(values.length,dates.length);
    assert(values.slice(0,first).every(v=>v===null),'Missing pre-entry NAV was treated as zero');
    assert.equal(values[first],0,'Excess did not start at the participant entry');
    for(let i=first;i<dates.length;i++)assert(Math.abs(values[i]-(curve[i]-benchmark[i]/benchmark[first])*100)<.011);
   }
  }
  const left=adapter.getNavCurve('CONTESTANT_A_robot'),right=adapter.getNavCurve('CONTESTANT_G_robot');
  const first=dates.indexOf(adapter.getPath('CONTESTANT_G_robot').observation_start);
  const spread=adapter.getSpreadCurve('CONTESTANT_A_robot','CONTESTANT_G_robot');
  assert(spread.slice(0,first).every(v=>v===null),'A spread invented values before both paths were observed');
  assert.equal(spread[first],0,'Spread curves use different anchors');
  for(let i=first;i<dates.length;i++)assert(Math.abs(spread[i]-(left[i]/left[first]-right[i]/right[first])*100)<.011);
 },
 late_entry(data) {
  const dates=data.nav_timeline.dates,start=dates.at(-3),cid='CONTESTANT_H';
  const participant={...data.contestants.find(c=>c.contestant_id==='CONTESTANT_G'),id:cid,contestant_id:cid,observation_start:start};
  const path={...data.paths.find(p=>p.path_id==='CONTESTANT_G_robot'),contestant_id:cid,path_id:cid+'_robot',observation_start:start,
   total_return_pct:-1,final_nav:.99,max_drawdown_pct:(1-.99/1.005)*100};
  data.contestants.push(participant);data.paths.push(path);
  data.nav_timeline.curves[path.path_id]=dates.map((_,i)=>i<dates.length-3?null:[1,1.005,.99][i-dates.length+3]);
  window.arenaAdapter=new window.ArenaDataAdapter(data);
  const all=window.arenaAdapter.getMacroPanoramaData('nav','robot','all');
  assert.deepEqual(all.dates,dates,'The newest entrant shortened older histories');
  assert.deepEqual(all.seriesList.filter(s=>s.type==='candidate').map(s=>s.path.contestant_id).sort(),data.contestants.map(c=>c.id).sort());
  for(const series of all.seriesList.filter(s=>s.type==='candidate'))assert.deepEqual(series.data,data.nav_timeline.curves[series.id]);
  const focused=window.arenaAdapter.getMacroPanoramaData('nav','robot',cid);
  assert.equal(focused.dates[0],start,'The focused branch used another participant entry');
  assert(focused.seriesList.every(s=>s.data[0]===1));
  const excess=window.arenaAdapter.getPathExcessMarket(path.path_id),first=dates.indexOf(start);
  const reference=window.arenaAdapter.getBenchmarkCsi300Curve(),curve=data.nav_timeline.curves[path.path_id];
  assert(excess.slice(0,first).every(v=>v===null));assert.equal(excess[first],0);
  for(let i=first;i<dates.length;i++)assert(Math.abs(excess[i]-(curve[i]-reference[i]/reference[first])*100)<.011);
  const spread=window.arenaAdapter.getSpreadCurve('CONTESTANT_G_robot',path.path_id);
  assert(spread.slice(0,first).every(v=>v===null));assert.equal(spread[first],0);
  const anchorValue=curve[first];curve[first]=null;
  assert(window.arenaAdapter.getPathExcessMarket(path.path_id).every(v=>v===null),'A missing declared entry was silently moved forward');
  assert(window.arenaAdapter.getSpreadCurve('CONTESTANT_G_robot',path.path_id).every(v=>v===null));
  curve[first]=anchorValue;
  window.LeaderboardView.activeTab='matrix';window.LeaderboardView.render('root');
  assert(charts.get('chart-leaderboard-matrix').yAxis.data.includes(cid),'A later retraining branch was omitted from HeatMap');
  window.AnimalsView.comparisonMode='single';window.AnimalsView.activeAnimalId='robot';window.AnimalsView.render('root');
  safeText(node('root').innerHTML);
  assert.deepEqual(charts.get('animal-cross-model-chart').xAxis.data,dates);
  assert(node('root').innerHTML.includes(`data-zoo-path="${path.path_id}" data-observation-start="${start}"`));
 },
 details(data) {
  for (const view of [window.LandingView, window.MethodologyView, window.DisclaimerView]) {
   view.render('root'); safeText(node('root').innerHTML);
  }
  for (const contestant of data.contestants) {
   window.ContestantDetailView.render('root', contestant.contestant_id); safeText(node('root').innerHTML);
  }
  for (const path of data.paths) {
   window.PathDetailView.render('root', path.path_id); safeText(node('root').innerHTML, path.path_id);
   const anchor = path.observation_start || data.nav_timeline.dates[0];
   assert(node('root').innerHTML.includes('Base 1.0000 on '+anchor), 'Path NAV anchor is mislabeled');
   const distribution = charts.get('chart-path-monkey-dist');
   if (!path.observation_start && distribution) {
    for (const series of distribution.series) {
     if (series.tooltip?.formatter) safeText(series.tooltip.formatter({}));
     for (const line of series.markLine?.data || []) if (line.label?.formatter) safeText(line.label.formatter({}));
    }
   }
   for (const metric of ['nav','drawdown','excess_csi300']) {
    window.ArenaCharts.renderEquityCurves('curve', data.nav_timeline.dates, path,
     window.arenaAdapter.getBenchmarkTaotieCurve(), window.arenaAdapter.getBenchmarkCsi300Curve(), null, metric);
    const option = charts.get('curve');
    if (path.observation_start) {
     assert.equal(option.xAxis.data[0], anchor);
     assert(option.series.every(s => s.data[0] === (metric === 'nav' ? 1 : 0)));
    }
   }
  }
  const path = data.paths.find(p => p.contestant_id === 'CONTESTANT_G' && p.animal_id === 'robot');
  window.PathDetailView.render('root',path.path_id);
  assert(!node('root').innerHTML.includes('Deterministic or unmatched reference'), 'An observation participant was mislabeled as a reference');
  for (const key of ['final_nav','max_drawdown_pct','actual_holdings_mean','target_holdings_mean','mean_cash_ratio','mean_cash_ratio_pct','unaffordable_buy_ratio']) path[key] = null;
  window.PathDetailView.render('root', path.path_id); safeText(node('root').innerHTML);
  assert(node('root').innerHTML.includes('N/A'));
 },
 table(data) {
  window.LeaderboardView.activeTab = 'table';
  for (const mode of ['return','vs_taotie','vs_ghost','vs_csi300']) {
   window.LeaderboardView.viewMode = mode; window.LeaderboardView.render('root');
   const html=node('leaderboard-tbody').innerHTML;safeText(html);
   for(const path of data.paths.filter(p=>p.contestant_id!=='BENCHMARK')){
    const row=html.split('<tr').find(row=>row.includes(`pathId: '${path.path_id}'`));
    assert(row,'Leaderboard omitted a participant');
    const reference={vs_taotie:'BENCHMARK_taotie',vs_ghost:'BENCHMARK_ghost_taotie',vs_csi300:'BENCHMARK_csi300'}[mode];
    if(reference){
     const values=window.arenaAdapter.getNavCurve(reference),first=data.nav_timeline.dates.indexOf(path.observation_start||data.nav_timeline.dates[0]);
     const fullSeason={vs_taotie:()=>window.arenaAdapter.getTaotieReturn(),vs_ghost:()=>window.arenaAdapter.getGhostTaotieReturn(),vs_csi300:()=>window.arenaAdapter.getCsi300Return()};
     const expected=path.total_return_pct-(path.observation_start?(values.at(-1)/values[first]-1)*100:fullSeason[mode]());
     assert(row.includes(`${expected>=0?'+':''}${expected.toFixed(2)} pp`),'The excess-return column shows an absolute return or uses the full-season benchmark for a later entrant');
    }
   }
  }
  const originals = data.paths.filter(p => p.contestant_id === 'CONTESTANT_A');
  originals[0].sharpe_ratio = null; originals[1].sharpe_ratio = 0;
  window.ArenaFilters = {currentFilters:{contestantId:'CONTESTANT_A'}};
  window.LeaderboardView.sortField = 'sharpe_ratio';
  for (const ascending of [true,false]) {
   window.LeaderboardView.sortAsc = ascending; window.LeaderboardView.renderTableBody();
   const html = node('leaderboard-tbody').innerHTML; safeText(html);
   const ids = [...html.matchAll(/pathId: '([^']+)'/g)].map(m => m[1]);
   assert.equal(ids.at(-1), originals[0].path_id, 'Missing Sharpe sorted as zero');
   const zeroRow = html.split('<tr').find(row => row.includes(originals[1].path_id));
   assert(zeroRow.includes('>0.00<'), 'A measured zero Sharpe was hidden');
  }
  delete window.ArenaFilters;
 },
 formatting(data) {
  for (const invalid of [null,undefined,NaN,Infinity,-Infinity]) {
   assert.equal(window.formatNumber(invalid), 'N/A');
   assert.equal(window.formatPValue(invalid), 'N/A');
   assert.equal(window.formatPercentile(invalid), 'N/A');
   assert.equal(window.arenaAdapter.formatPValue(invalid), 'N/A');
   assert.equal(window.arenaAdapter.formatPercentile(invalid), 'N/A');
  }
  assert.equal(window.formatNumber(0), '0.00');
  assert.equal(window.formatNumber(0, 1, '%'), '0.0%');
  const contestant = data.contestants[0];
  for (const value of [null,0]) {
   for (const key of ['historical_sys_ann_return_pct','historical_is_return_pct','historical_is_mdd_pct','historical_is_sharpe']) contestant[key] = value;
   window.ContestantDetailView.render('root', contestant.contestant_id); const html = node('root').innerHTML;
   safeText(html);
   assert(html.includes(value === null ? 'Historical Sharpe: <b>N/A</b>' : 'Historical Sharpe: <b>0.00</b>'));
  }
  const adapter = new window.ArenaDataAdapter({contestants:[{contestant_id:'CONTESTANT_A'}]});
  assert.equal(adapter.getContestant('CONTESTANT_A').historical_is_sharpe, null);
  assert.equal(adapter.getContestant('CONTESTANT_A').historical_is_return_pct, null);
  assert.equal(adapter.getTaotieReturn(), null);
  assert.equal(adapter.getMarketBenchmarkReturn(), null);
  assert.equal(adapter.getGhostTaotieReturn(), null);
  for (const key of ['taotie_return_pct','market_benchmark_return_pct','csi300_return_pct']) window.arenaAdapter.metadata[key] = null;
  const taotie = data.nav_timeline.curves.BENCHMARK_taotie;
  assert.equal(window.arenaAdapter.getTaotieReturn(), (taotie.at(-1)/taotie[0]-1)*100);
  window.OverviewView.render('root'); safeText(node('root').innerHTML);
  window.LeaderboardView.render('root'); safeText(node('root').innerHTML);
 }
};
for (const source of Object.values(window.ARENA_SEASONS_DATA)) {
 const data = structuredClone(source);
 window.arenaAdapter = new window.ArenaDataAdapter(data);
 checks[process.argv[1]](data);
}
'''
    completed = subprocess.run(['node', '-e', program, entry], cwd=REPO_ROOT,
                               capture_output=True, text=True, timeout=30)
    assert completed.returncode == 0, completed.stderr
