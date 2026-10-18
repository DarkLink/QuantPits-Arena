"""Runtime verification of the complete website generation and real view paths."""
import json
import subprocess
from arena.config import REPO_ROOT


def test_release_contract_and_view_runtime():
    html=(REPO_ROOT/'web/index.html').read_text()
    assert html.count('src="js/data/arena_release.js')==1
    program=r'''
const fs=require('fs');const vm=require('vm');
const nodes=new Map();
function node(id){if(!nodes.has(id))nodes.set(id,{innerHTML:'',addEventListener(){},querySelectorAll(){return[];},querySelector(){return null;},classList:{toggle(){},add(){},remove(){},contains(){return true;}}});return nodes.get(id);}
global.window={addEventListener(){},location:{search:'',hash:'',href:'https://arena.invalid/'}};
global.document={readyState:'loading',addEventListener(){},documentElement:{getAttribute(){return'dark';}},getElementById:node,querySelectorAll(){return[];},querySelector(){return node('query');}};
global.setTimeout=cb=>{cb();return 0;};
global.echarts={getInstanceByDom(){return null;},init(){return {setOption(option){global.lastChart=option;},resize(){},getOption(){return{series:[]};},on(){}};},graphic:{LinearGradient:function(){}}};
for(const file of ['web/js/data/arena_release.js','web/js/adapter.js','web/js/components/charts.js','web/js/views/methodology.js','web/js/views/path_detail.js','web/js/views/contestant_detail.js','web/js/views/decision_audit.js','web/js/views/leaderboard_view.js','web/js/app.js'])vm.runInThisContext(fs.readFileSync(file,'utf8'));
const expected=['season_01','season_csi300','season_csi500','season_csi800','season_csi1000'];
if(JSON.stringify(window.ARENA_SEASONS_INDEX.map(s=>s.id))!==JSON.stringify(expected))throw Error('season order differs');
if(JSON.stringify(Object.keys(window.ARENA_SEASONS_DATA))!==JSON.stringify(expected))throw Error('bundle order differs');
if(JSON.stringify(window.ARENA_SEASONS_INDEX.map(s=>s.short_title))!==JSON.stringify(['csirun300','CSI300','CSI500','CSI800','CSI1000']))throw Error('season labels differ');
if(window.ARENA_SEASONS_INDEX.some(s=>s.status!=='ACTIVE'))throw Error('retired or inactive season visible');
if(window.ArenaApp.normalizeSeasonId('season_02')!==null||window.ArenaApp.normalizeSeasonId('csirun300')!=='season_01')throw Error('season aliases differ');
window.ArenaApp.initSeasonSelector();
const dropdownIds=[...node('season-dropdown').innerHTML.matchAll(/data-season-id="([^"]+)"/g)].map(m=>m[1]);
if(JSON.stringify(dropdownIds)!==JSON.stringify(expected)||node('current-season-label').textContent!=='csirun300')throw Error('dropdown order or default differs');
const results=[];
for(const [sid,data] of Object.entries(window.ARENA_SEASONS_DATA)){
 if(data.meta.evaluation_id!==window.ARENA_ACTIVE_EVALUATION)throw Error('mixed generations');
 if(data.nav_timeline.dates.at(-1)!==data.meta.cutoff)throw Error('cutoff differs');
 if(data.meta.monkey_nav_frequency!=='daily')throw Error('monkey frequency differs');
 for(const [id,values] of Object.entries(data.nav_timeline.curves)){
  const first=values.findIndex(v=>v!==null);
  if(first<0||values[first]!==1||values.slice(first).some(v=>!Number.isFinite(v)))throw Error('anchor or coverage differs');
  const path=data.paths.find(p=>p.path_id===id);
  if(path?.observation_start && data.nav_timeline.dates[first]!==path.observation_start)throw Error('observation anchor differs');
 }
 const tested=data.paths.filter(p=>p.test_status==='random_control');
 if(tested.length!==168)throw Error('comparison coverage differs');
 for(const p of tested){
  if(p.empirical_p_value!==(p.exceedance_count+1)/(p.monkey_count+1))throw Error('p precision or count differs');
  if(p.is_statistically_significant!==(p.empirical_p_value<.05))throw Error('flag differs');
 }
 if(data.paths.filter(p=>p.test_status==='not_applicable').some(p=>p.empirical_p_value!==null))throw Error('reference has random p');
 window.arenaAdapter=new window.ArenaDataAdapter(data);
 window.MethodologyView.render('root');
 const dates=data.nav_timeline.dates;
 for(const dist of data.monkey_null_distributions){
  const quantiles=dist.daily_quantiles;
  if(Object.keys(quantiles).length!==dates.length)throw Error('daily monkey coverage differs');
  for(const date of dates){
   const q=quantiles[date];
   if(!q||![q.p05,q.median,q.p95].every(Number.isFinite)||q.p05>q.median||q.median>q.p95)throw Error('invalid daily quantiles');
  }
  if(Object.values(quantiles[dates[0]]).some(v=>v!==1))throw Error('monkey anchor differs');
 }
 const dist=window.arenaAdapter.getMonkeyDistribution(tested[0].strategy_spec);
 window.ArenaCharts.renderEquityCurves('root',dates,tested[0],window.arenaAdapter.getBenchmarkTaotieCurve(),window.arenaAdapter.getBenchmarkCsi300Curve(),dist,'nav');
 const monkeys=lastChart.series.filter(s=>s.name.startsWith('Monkey '));
 if(monkeys.length!==3||monkeys.some(s=>s.type!=='line'||s.data.length!==dates.length||!s.data.every(Number.isFinite)||s.smooth!==false))throw Error('daily monkey lines differ');
 const day=dates.indexOf('2026-07-07');
 if(day<0)throw Error('non-rebalance test day missing');
 const tooltip=lastChart.tooltip.formatter(monkeys.map(s=>({axisValue:dates[day],seriesName:s.name,value:s.data[day],dataIndex:day,color:s.color})));
 if(!tooltip.includes('Monkey Median')||tooltip.includes('null')||tooltip.includes('undefined'))throw Error('non-rebalance tooltip differs');
 window.PathDetailView.render('root',tested[0].path_id);
 window.PathDetailView.render('root',data.paths.find(p=>p.animal_id==='ghost_taotie').path_id);
 const observers=data.paths.filter(p=>p.observation_start);
 if(observers.length){
  const retrained=data.contestants.find(c=>c.contestant_id==='CONTESTANT_G');
  if(retrained.retrained_from!=='CONTESTANT_A'||retrained.retraining_context.information_cutoff!=='2026-10-09'||retrained.retraining_context.first_execution!=='2026-10-12')throw Error('public retraining introduction is missing');
  if(observers.some(p=>p.empirical_p_value!==null||p.is_statistically_significant!==null||p.full_season_eligible!==false||p.test_status!=='observation'))throw Error('observer has cumulative inference');
  const observer=observers.find(p=>p.animal_id==='robot');
  window.PathDetailView.render('root',observer.path_id);
  window.ContestantDetailView.render('root',observer.contestant_id);
  if(!node('root').innerHTML.includes('Participant Background')||!node('root').innerHTML.includes('Five Behavioral')||node('root').innerHTML.includes('Failed to load'))throw Error('shared contestant layout differs');
  if(!node('root').innerHTML.includes('Retrained from CONTESTANT_A')||node('root').innerHTML.includes('Burial Annualized Return'))throw Error('retraining introduction or unavailable legacy metrics differ');
  for(const metric of ['nav','drawdown','excess_csi300']){
   window.ArenaCharts.renderMultiAnimalCurves('root',dates,observers,window.arenaAdapter.getBenchmarkTaotieCurve(),window.arenaAdapter.getBenchmarkCsi300Curve(),metric);
   if(lastChart.xAxis.data[0]!==observer.observation_start||lastChart.series.some(s=>s.data.length!==lastChart.xAxis.data.length||s.data.some(v=>!Number.isFinite(v))||s.data[0]!== (metric==='nav'?1:0)))throw Error('observation profile benchmark window differs');
  }
  window.DecisionAuditView.start=null;window.DecisionAuditView.end=null;
  window.DecisionAuditView.activePreset=null;window.DecisionAuditView.slotC='';
  window.DecisionAuditView.render('root');
  if(!node('root').innerHTML.includes('slot-c-select')||lastChart.series.length!==3||lastChart.xAxis[0].data[0]!==observer.observation_start)throw Error('real comparison workbench differs');
  window.DecisionAuditView.slotC='BENCHMARK_taotie';window.DecisionAuditView.render('root');
  if(lastChart.series.length!==4||lastChart.series.slice(0,3).some(s=>s.data[0]!==1)||lastChart.yAxis[1].name!=='Spread (pp)')throw Error('third benchmark slot differs');
  window.DecisionAuditView.slotA='CONTESTANT_B';window.DecisionAuditView.slotB='CONTESTANT_A';window.DecisionAuditView.render('root');
  if(lastChart.xAxis[0].data[0]!==dates[0]||lastChart.series[0].data.length!==dates.length)throw Error('original full-season comparison was lost');
 }
 window.LeaderboardView.render('root');
 results.push({sid,paths:data.paths.length,expectedPaths:data.contestants.length*28+2,tests:tested.length,count:tested[0].monkey_count,daily:dates.length});
}
console.log(JSON.stringify(results));
'''
    completed=subprocess.run(['node','-e',program],cwd=REPO_ROOT,capture_output=True,text=True)
    assert completed.returncode==0,completed.stderr
    results=json.loads(completed.stdout)
    assert len(results)==5
    assert all(result['paths']==result['expectedPaths'] and result['tests']==168 and result['count']==100000 for result in results)
    assert len({result['daily'] for result in results})==1
