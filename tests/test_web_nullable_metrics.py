"""Exercise published nullable metrics through view and deferred tooltip callbacks."""
import subprocess

import pytest

from arena.config import REPO_ROOT


@pytest.mark.parametrize('entry', ['matrix', 'scatter', 'panorama', 'details', 'table', 'formatting'])
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
 'js/views/landing.js','js/views/overview.js','js/views/leaderboard_view.js',
 'js/views/path_detail.js','js/views/contestant_detail.js','js/views/decision_audit.js',
 'js/views/methodology.js','js/views/disclaimer.js']) vm.runInThisContext(fs.readFileSync('web/'+file,'utf8'));
function safeText(text, context = '') {
 assert(!/NaN|Infinity|undefined|>\s*null\s*</.test(text), 'Invalid value exposed by the view: '+context);
 assert(!/Error Loading|Failed to render/.test(text), 'The view swallowed a runtime exception');
}
const checks = {
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
   assert.equal(option.yAxis.data.length, data.contestants.filter(c => !c.observation_start).length);
   window.ArenaCharts.renderHeatmap('nullable-matrix', {...window.arenaAdapter.matrix,
    rows:data.contestants.map(c => c.contestant_id)}, metric);
   const extended = charts.get('nullable-matrix');
   for (const cell of extended.series[0].data) {
    const value = cell.value || cell;
    const params = {data:cell, value};
    const tooltip = extended.tooltip.formatter(params);
    const label = cell.label?.formatter || extended.series[0].label.formatter(params);
    safeText(tooltip); safeText(String(label));
    const path = window.arenaAdapter.getPath(value[3]);
    if (path.observation_start) {
     assert.equal(value[2], null, 'A later entrant received a full-season heatmap score');
     assert.equal(label, 'N/A');
     assert(tooltip.includes(path.observation_start));
    }
   }
  }
 },
 panorama(data) {
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
     for (const series of option.series) {
      assert.equal(series.data.length, option.xAxis.data.length);
      assert(series.data.every(Number.isFinite));
      assert.equal(series.data[0], metric === 'nav' ? 1 : 0);
      const path = data.paths.find(p => p.path_id === series.name);
      if (path) {
       const first = data.nav_timeline.dates.indexOf(start);
       const values = data.nav_timeline.curves[path.path_id].slice(first);
       const nav = values.map(v => v / values[0]); let peak = 1;
       const referenceId = {excess_taotie:'BENCHMARK_taotie', excess_ghost:'BENCHMARK_ghost_taotie', excess_csi300:'BENCHMARK_csi300'}[metric];
       const reference = referenceId && data.nav_timeline.curves[referenceId].slice(first);
       const expected = nav.map((v,i) => {peak = Math.max(peak,v); return metric === 'nav' ? v : metric === 'drawdown' ? (v/peak-1)*100 : (v-reference[i]/reference[0])*100;});
       assert(series.data.every((v,i) => Math.abs(v-expected[i]) < 0.011), 'Panorama values use a different benchmark anchor');
      }
     }
     for (const day of [0, option.xAxis.data.length-1]) safeText(option.tooltip.formatter(
      option.series.map(s => ({axisValue:option.xAxis.data[day],seriesName:s.name,value:s.data[day],color:'#fff'}))));
     assert(option.tooltip.formatter([{axisValue:start,seriesName:'Unavailable',value:null,color:'#fff'}]).includes('N/A'));
    }
   }
  }
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
  for (const key of ['final_nav','max_drawdown_pct','actual_holdings_mean','target_holdings_mean','mean_cash_ratio','mean_cash_ratio_pct','unaffordable_buy_ratio']) path[key] = null;
  window.PathDetailView.render('root', path.path_id); safeText(node('root').innerHTML);
  assert(node('root').innerHTML.includes('N/A'));
 },
 table(data) {
  window.LeaderboardView.activeTab = 'table';
  for (const mode of ['return','vs_taotie','vs_ghost','vs_csi300']) {
   window.LeaderboardView.viewMode = mode; window.LeaderboardView.render('root');
   safeText(node('leaderboard-tbody').innerHTML);
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
