"""Run real view callbacks with reused charts, deferred timers and reordered fetches."""
import subprocess

import pytest

from arena.config import REPO_ROOT


@pytest.mark.parametrize('entry', [
    'benchmark_switches', 'deferred_paths', 'deferred_profiles', 'deferred_routes',
    'dispatch_race', 'dispatch_participants', 'resizing', 'season_selection', 'focused_pool_change', 'routing_inputs', 'summary_counts', 'participation_counts', 'filter_reset', 'comparison_tie', 'matrix_filters',
    'zoo_route_state', 'comparison_route_state',
])
def test_interaction_runtime(entry):
    program = r'''
const fs=require('fs'), vm=require('vm'), assert=require('assert/strict');
const nodes=new Map(), instances=new Map(), timers=new Map(), listeners=new Map();
let timerId=0;
function node(id){
 if(!nodes.has(id))nodes.set(id,{id,innerHTML:'',textContent:'',style:{},isConnected:true,
  nodeType:1,tagName:'DIV',childNodes:[],events:{},classList:{toggle(){},add(){},remove(){},contains(){return true;}},
  addEventListener(name,callback){this.events[name]=callback;},setAttribute(){},remove(){this.isConnected=false;},
  querySelectorAll(){return[];},querySelector(selector){return selector.startsWith('#')?node(selector.slice(1)):null;},contains(other){return this===other;}});
 return nodes.get(id);
}
function location(url){window.location=new URL(url);}
function flush(reverse=false){const pending=[...timers.values()];timers.clear();if(reverse)pending.reverse();pending.forEach(cb=>cb());}
global.window={addEventListener(event,callback){if(!listeners.has(event))listeners.set(event,[]);listeners.get(event).push(callback);},scrollTo(){},history:{replaceState(_,__,url){location(url);}}};
location('https://arena.invalid/?season=season_01#overview');
global.document={readyState:'loading',addEventListener(){},getElementById:node,
 createElement(tag){return node('created-'+tag+'-'+(++timerId));},
 documentElement:{getAttribute(){return'dark';}},querySelectorAll(){return[];},querySelector(){return null;}};
global.Node={TEXT_NODE:3,ELEMENT_NODE:1};
global.setTimeout=callback=>{timers.set(++timerId,callback);return timerId;};
global.clearTimeout=id=>timers.delete(id);
global.echarts={getInstanceByDom:dom=>instances.get(dom),init(dom){
 const chart={option:{},resizes:0,disposed:false,getDom(){return dom;},isDisposed(){return this.disposed;},
  setOption(option,replace){this.option=replace?option:{...this.option,...option,legend:option.legend?{...this.option.legend,...option.legend}:this.option.legend};},
  getOption(){return{...this.option,legend:[this.option.legend||{}]};},
  resize(){assert(!this.disposed);this.resizes++;},dispose(){this.disposed=true;instances.delete(dom);},on(){},off(){}};
 instances.set(dom,chart);return chart;},graphic:{LinearGradient:function(){}}};
for(const name of ['data/arena_release','adapter','components/charts','components/filters',
 'views/overview','views/leaderboard_view','views/animals_view','views/contestant_detail',
 'views/path_detail','views/decision_audit','views/dispatches','app'])vm.runInThisContext(fs.readFileSync('web/js/'+name+'.js','utf8'));
const seasons=Object.keys(window.ARENA_SEASONS_DATA);
function pool(id){window.arenaAdapter=new window.ArenaDataAdapter(structuredClone(window.ARENA_SEASONS_DATA[id]));return window.arenaAdapter;}
function option(id){return instances.get(node(id))?.option;}
const checks={
 zoo_route_state(){
  for(const sid of seasons){
   const adapter=pool(sid),view=window.AnimalsView;
   location('https://arena.invalid/?season='+sid+'#animals/robot');
   Object.assign(view,{comparisonMode:'single',activeCategory:'All',activeAnimalId:'robot'});
   const container=node('view-animals'),original=container.querySelectorAll;
   const button=node('category-lag');button.getAttribute=()=> 'Execution Lag';
   container.querySelectorAll=selector=>selector==='.animal-cat-btn'?[button]:[];
   window.ArenaApp.handleRouting();flush();
   button.events.click({currentTarget:button});flush();
   const selected=view.activeAnimalId;
   assert.equal(adapter.getAllAnimals().find(a=>a.id===selected).category,'Execution Lag');
   assert.equal(window.ArenaApp.parseHash().params.animalId,selected,'Category selection left the old animal in the URL');
   window.ArenaApp.handleRouting();flush();
   assert.equal(view.activeAnimalId,selected,'A theme rerender reverted the selected animal');
   location('https://arena.invalid/?season='+sid+'#animals/koala');
   window.ArenaApp.handleRouting();flush();
   assert.equal(view.activeCategory,adapter.getAllAnimals().find(a=>a.id==='koala').category);
   assert(container.innerHTML.includes('value="koala" selected'),'The direct link disagrees with the selected dropdown');
   location('https://arena.invalid/?season='+sid+'#animals/robot?mode=multi&modelFocus=CONTESTANT_G');
   window.ArenaApp.handleRouting();flush();
   view.comparisonMode='single';view.activeFocusModel='CONTESTANT_A';view.render('view-animals');flush();
   window.ArenaApp.handleRouting();flush();
   assert.equal(view.comparisonMode,'single','An old mode parameter overrode the current selection');
   assert.equal(view.activeFocusModel,'CONTESTANT_A','An old focus parameter overrode the current selection');
   assert.equal(window.location.search,'?season='+sid);
   container.querySelectorAll=original;
  }
 },
 comparison_route_state(){
  for(const sid of seasons){
   const adapter=pool(sid),view=window.DecisionAuditView,preset=adapter.getComparisonPresets()[0].id;
   Object.assign(view,{activePreset:null,start:null,end:null,season:null});
   location('https://arena.invalid/?season='+sid+'#decision-audit/'+preset+'?animalId=robot');
   window.ArenaApp.handleRouting();flush();
   node('comparison-start').events.change({target:{value:'2026-10-13'}});flush();
   window.ArenaApp.handleRouting();flush();
   assert.equal(view.window.start,'2026-10-13','A preset link reset the selected dates during a theme rerender');
   node('slot-b-select').events.change({target:{value:'CONTESTANT_B'}});flush();
   assert(!window.ArenaApp.parseHash().params.forkId,'A custom comparison retained a stale preset URL');
   window.ArenaApp.handleRouting();flush();
   assert.equal(view.slotB,'CONTESTANT_B','A theme rerender restored the old preset participant');
   node('archaeology-animal-select').events.change({target:{value:'koala'}});flush();
   window.ArenaApp.handleRouting();flush();
   assert.equal(view.activeAnimalId,'koala','A stale animal query overrode the comparison selection');
   assert.equal(window.location.search,'?season='+sid);
   view.applyPreset(preset,adapter.getComparisonPresets());view.render('view-decision-audit');flush();
   assert.equal(window.ArenaApp.parseHash().params.forkId,preset,'Selecting a preset left the custom URL active');
  }
 },
 benchmark_switches(){
  for(const sid of seasons){
   const adapter=pool(sid),dates=adapter.getNavDates();
   for(const cid of ['CONTESTANT_A','CONTESTANT_G'])for(const metric of ['nav','drawdown','excess_csi300']){
    const path=adapter.getPath(cid+'_robot');
    window.ArenaCharts.renderEquityCurves('curve',dates,path,adapter.getBenchmarkTaotieCurve(),adapter.getBenchmarkCsi300Curve(),null,metric);
    const chart=instances.get(node('curve'));
    assert(chart.option.series.some(s=>s.name.includes('Ghost')), 'Ghost reference disappeared for an observation participant');
    for(const key of ['market','taotie','ghost']){
     window.ArenaCharts.toggleBenchmark('curve',key,false);
     const selected=chart.option.legend.selected;
     assert.equal(Object.values(selected).filter(value=>value===false).length,1,'A benchmark toggle affected multiple references');
     window.ArenaCharts.toggleBenchmark('curve',key,true);
    }
    if(metric==='excess_csi300')assert(chart.option.yAxis.name.includes('pp'));
   }
  }
 },
 deferred_paths(){
  for(const sid of seasons){
   pool(sid);window.PathDetailView.render('root','CONTESTANT_A_robot');
   window.PathDetailView.render('root','CONTESTANT_G_robot');flush(true);
   assert(option('chart-path-equity-curves').series.some(s=>s.name==='CONTESTANT_G'));
   assert(!option('chart-path-equity-curves').series.some(s=>s.name.includes('CONTESTANT_A')),'An old path overwrote the current path');
  }
 },
 deferred_profiles(){
  for(let i=0;i<seasons.length;i++){
   pool(seasons[i]);window.ContestantDetailView.render('root','CONTESTANT_G');
   const adapter=pool(seasons[(i+1)%seasons.length]);window.ContestantDetailView.render('root','CONTESTANT_G');flush(true);
   const expected=adapter.getPath('CONTESTANT_G_robot').total_return_pct.toFixed(2);
   assert(option('chart-contestant-multi-curves').series[0].name.includes(expected),'A previous pool supplied the current chart labels');
  }
 },
 deferred_routes(){
  pool(seasons[0]);location('https://arena.invalid/#path/CONTESTANT_G_robot');window.ArenaApp.handleRouting();
  location('https://arena.invalid/#overview');window.ArenaApp.handleRouting();flush(true);
  assert(!instances.has(node('chart-path-equity-curves')),'A hidden route recreated an abandoned chart');
  assert(instances.has(node('chart-arena-panorama')));
 },
 async dispatch_race(){
  const adapter=pool(seasons[0]);
  const episodes=adapter.getDispatchesData().episodes.filter(ep=>ep.file).slice(0,2);
  assert.equal(episodes.length,2);
  const requests=[];
  global.fetch=()=>new Promise(resolve=>requests.push(resolve));window.marked={parse:text=>text};
  window.DispatchesView.currentEpisode=episodes[0].id;
  const old=window.DispatchesView.loadArticle(episodes[0].id);
  window.DispatchesView.currentEpisode=episodes[1].id;
  const current=window.DispatchesView.loadArticle(episodes[1].id);
  requests[1]({ok:true,text:async()=>'<p>current article</p>'});await current;
  requests[0]({ok:true,text:async()=>'<p>stale article</p>'});await old;
  assert(node('dispatch-article-body').innerHTML.includes('current article'),'An older fetch replaced the selected episode');
  assert(!node('dispatch-article-body').innerHTML.includes('stale article'));
 },
 dispatch_participants(){
  const createElement=document.createElement;
  document.createElement=tag=>({nodeType:Node.ELEMENT_NODE,tagName:tag.toUpperCase(),childNodes:[],
   querySelectorAll(){return[];},
   classList:{contains(){return false;}},
   set innerHTML(text){this.childNodes=[{nodeType:Node.TEXT_NODE,nodeValue:text,parentNode:this}];},
   get innerHTML(){return this.childNodes.map(child=>child.nodeValue??child.innerHTML).join('');},
   replaceChild(next,previous){this.childNodes[this.childNodes.indexOf(previous)]=next;}});
  for(const suffix of ['A','G','H','AA']){
   const contestant='CONTESTANT_'+suffix,path=contestant+'_eagle-11-2';
   const decorated=window.DispatchesView.decorateArticle(`${contestant} follows ${path}.`);
   assert(decorated.includes(`data-tooltip-term="${contestant}"`),'Dispatch glossary omitted an admitted participant');
   assert(decorated.includes(`data-tooltip-term="${path}"`),'A complete path identifier was split into separate terms');
  }
  document.createElement=createElement;
 },
 resizing(){
  const adapter=pool(seasons[0]);
  for(let i=0;i<25;i++)window.ArenaCharts.renderScatter('chart',adapter.getAllPaths());
  assert.equal(listeners.get('resize')?.length,1,'Redraws accumulated window resize handlers');
  const chart=instances.get(node('chart'));listeners.get('resize').forEach(cb=>cb());assert.equal(chart.resizes,1);
  window.ArenaCharts.disposeAll();listeners.get('resize').forEach(cb=>cb());
  assert(chart.disposed);assert.equal(chart.resizes,1);
 },
 season_selection(){
  pool(seasons[0]);window.ArenaApp.currentSeasonId=seasons[0];
  const target='season_csi500',original=window.ARENA_SEASONS_DATA[target];
  const smaller=structuredClone(original);smaller.contestants=smaller.contestants.filter(c=>c.contestant_id!=='CONTESTANT_G');
  smaller.paths=smaller.paths.filter(p=>p.contestant_id!=='CONTESTANT_G');window.ARENA_SEASONS_DATA[target]=smaller;
  window.ArenaFilters.currentFilters.contestantId='CONTESTANT_G';window.ArenaFilters.currentFilters.search='" <search> &';
  window.ArenaApp.switchSeason('csi500');
  assert.equal(window.ArenaApp.currentSeasonId,target);
  assert.equal(window.location.search,'?season='+target,'Season aliases were written back into the URL');
  assert.equal(window.ArenaFilters.currentFilters.contestantId,'ALL','A stale model filter remained selected');
  const html=node('global-filters-container').innerHTML;
  assert(html.includes('&quot; &lt;search&gt; &amp;'));assert(!html.includes('value="CONTESTANT_G"'));
  delete window.ARENA_SEASONS_DATA.season_csi800;
  window.ArenaApp.switchSeason('season_csi800');
  assert.equal(window.ArenaApp.currentSeasonId,target,'The label switched while the previous pool data stayed active');
  assert.equal(window.arenaAdapter.getCurrentSeasonMeta().id,target);
 },
 focused_pool_change(){
  for(const sid of seasons){
   const data=structuredClone(window.ARENA_SEASONS_DATA[sid]);
   data.contestants=data.contestants.filter(c=>c.contestant_id!=='CONTESTANT_G');
   data.paths=data.paths.filter(p=>p.contestant_id!=='CONTESTANT_G');
   window.arenaAdapter=new window.ArenaDataAdapter(data);
   window.OverviewView.activeFocusModel='CONTESTANT_G';window.OverviewView.activeFilterGroup='robot';
   window.OverviewView.render('root');flush();
   assert.equal(window.OverviewView.activeFocusModel,'all','A stale panorama focus hid the new pool participants');
   assert(option('chart-arena-panorama').series.some(s=>s.name==='CONTESTANT_A_robot'));
   Object.assign(window.AnimalsView,{activeFocusModel:'CONTESTANT_G',comparisonMode:'multi',selectedAnimalIds:['robot']});
   window.AnimalsView.render('root');flush();
   assert.equal(window.AnimalsView.activeFocusModel,'all','A stale Zoo focus hid the new pool participants');
   assert(option('animal-cross-model-chart').series.some(s=>s.name.startsWith('CONTESTANT_A')));
   pool(sid);window.OverviewView.activeFocusModel='CONTESTANT_G';window.OverviewView.render('root');flush();
   assert.equal(window.OverviewView.activeFocusModel,'CONTESTANT_G','An available participant selection was discarded');
  }
 },
 routing_inputs(){
  pool(seasons[0]);
  location('https://arena.invalid/#intro');
  assert.equal(window.ArenaApp.parseHash().route,'landing','The exhibition link no longer opens the existing landing page');
  location('https://arena.invalid/#contestant-detail/CONTESTANT_G');
  assert.equal(window.ArenaApp.parseHash().params.contestantId,'CONTESTANT_G');
  location('https://arena.invalid/#path/%E0%A4%A');assert.doesNotThrow(()=>window.ArenaApp.handleRouting());
  assert.equal(window.arenaAdapter.getContestant('UNAVAILABLE'),null,'An unknown participant silently resolved to A');
  window.ContestantDetailView.render('root','UNAVAILABLE');assert(node('root').innerHTML.includes('No contestant found'));
  window.PathDetailView.render('root','<unavailable>');
  assert(node('root').innerHTML.includes('&lt;unavailable&gt;'));assert(!node('root').innerHTML.includes('"<unavailable>"'));
  window.PathDetailView.render('root','BENCHMARK_taotie');assert(!node('root').innerHTML.includes('Model Profile ('));
 },
 summary_counts(){
  const adapter=pool(seasons[0]),paths=adapter.getAllPaths().filter(p=>p.contestant_id!=='BENCHMARK'&&p.full_season_eligible!==false);
  paths.forEach(p=>p.sharpe_ratio=null);paths[0].empirical_p_value=null;
  const tested=paths.filter(p=>Number.isFinite(p.empirical_p_value));
  const significant=tested.filter(p=>p.empirical_p_value<.05).length;
  const kpis=adapter.getGlobalKPIs();
  assert.equal(kpis.bestSharpe,null);assert.equal(kpis.statSignificantPct,(100*significant/tested.length).toFixed(1)+'%');
 },
 participation_counts(){
  for(const sid of seasons){
   const adapter=pool(sid),baseline=adapter.getGlobalKPIs(),data=adapter.raw;
   assert.equal(baseline.totalPaths,196,'The participant total omitted observation branches or counted benchmark paths');
   assert.equal(baseline.fullSeasonPaths,168);assert.equal(baseline.observationPaths,28);
   assert.equal(baseline.referencePaths,2);assert.equal(baseline.contestantCount,7);assert.equal(baseline.testedPaths,168);
   window.OverviewView.render('root');
   assert(node('root').innerHTML.includes('data-path-count="196"'));
   assert(node('root').innerHTML.includes('168 full-season + 28 observation'));
   const child={...data.contestants.find(c=>c.id==='CONTESTANT_G'),id:'CONTESTANT_H',contestant_id:'CONTESTANT_H',observation_start:'2026-11-01',retrained_from:'CONTESTANT_G'};
   data.contestants.push(child);
   const rows=data.paths.filter(p=>p.contestant_id==='CONTESTANT_G').map(p=>({...p,contestant_id:'CONTESTANT_H',path_id:p.path_id.replace('CONTESTANT_G','CONTESTANT_H'),observation_start:child.observation_start}));
   data.paths.push(...rows);
   assert.equal(adapter.getGlobalKPIs().totalPaths,196,'A future participant was counted before admission');
   child.observation_start='2026-10-14';rows.forEach(p=>p.observation_start=child.observation_start);
   const expanded=adapter.getGlobalKPIs();
   assert.equal(expanded.totalPaths,224);assert.equal(expanded.observationPaths,56);assert.equal(expanded.contestantCount,8);
   assert.equal(expanded.fullSeasonPaths,168);assert.equal(expanded.testedPaths,168);
   for(const key of ['topReturn','medianReturn','bestSharpe','statSignificantCount','statSignificantPct'])assert.equal(expanded[key],baseline[key],'A new branch changed full-season statistics');
   window.OverviewView.render('root');assert(node('root').innerHTML.includes('data-path-count="224"'));
   for(const [parent,id] of [['C','I'],['D','J'],['E','K'],['F','L']]){
    data.contestants.push({...child,id:'CONTESTANT_'+id,contestant_id:'CONTESTANT_'+id,retrained_from:'CONTESTANT_'+parent});
    data.paths.push(...rows.map(p=>({...p,contestant_id:'CONTESTANT_'+id,path_id:p.path_id.replace('CONTESTANT_H','CONTESTANT_'+id)})));
   }
   const families=adapter.getGlobalKPIs();assert.equal(families.totalPaths,336);assert.equal(families.contestantCount,12);assert.equal(families.testedPaths,168);
   assert.equal(families.fullSeasonPaths,168);assert.equal(families.observationPaths,168);
   const onlyObserved=structuredClone(data);onlyObserved.paths=onlyObserved.paths.filter(p=>p.contestant_id==='CONTESTANT_G'||p.contestant_id==='BENCHMARK');
   window.arenaAdapter=new window.ArenaDataAdapter(onlyObserved);const observed=window.arenaAdapter.getGlobalKPIs();
   assert.equal(observed.totalPaths,28);assert.equal(observed.fullSeasonPaths,0);assert.equal(observed.topReturn,null);assert.equal(observed.statSignificantPct,'N/A');
  }
 },
 filter_reset(){
  pool(seasons[0]);window.ArenaFilters.render('filters');
  node('filter-search').events.input({target:{value:'pending search'}});
  window.ArenaFilters.reset();flush();assert.equal(window.ArenaFilters.currentFilters.search,'');
  node('filter-search').events.input({target:{value:'across pools'}});
  window.ArenaApp.switchSeason('csi500');flush();
  assert.equal(window.ArenaFilters.currentFilters.search,'across pools');
  assert(node('global-filters-container').innerHTML.includes('value="across pools"'));
 },
 comparison_tie(){
  pool(seasons[0]);
  Object.assign(window.DecisionAuditView,{activePreset:'custom',slotA:'CONTESTANT_A',slotB:'CONTESTANT_A',slotC:'',start:null,end:null});
  window.DecisionAuditView.render('root');flush();
  assert(node('root').innerHTML.includes('Equal return'));
  assert(!node('root').innerHTML.includes('Slot A Outperformed'));
 },
 matrix_filters(){
  pool(seasons[0]);window.LeaderboardView.render('root');
  window.LeaderboardView.switchTab('matrix');
  assert.equal(node('global-filters-container').style.display,'none');
  window.LeaderboardView.switchTab('table');
  assert.equal(node('global-filters-container').style.display,'block');
 }
};
(async()=>{await checks[process.argv[1]]();})().catch(error=>{console.error(error);process.exitCode=1;});
'''
    completed = subprocess.run(['node', '-e', program, entry], cwd=REPO_ROOT,
                               capture_output=True, text=True, timeout=30)
    assert completed.returncode == 0, completed.stderr
