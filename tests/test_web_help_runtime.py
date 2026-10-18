"""Existing field-guide links, hover lifecycle and browser storage boundaries."""
import subprocess

import pytest

from arena.config import REPO_ROOT


@pytest.mark.parametrize('entry', [
    'drawer_term_targets', 'drawer_categories', 'drawer_search', 'glossary_aliases',
    'glossary_boundaries', 'anonymous_descriptions', 'tooltip_lifecycle',
    'tooltip_position', 'storage_denied', 'invalid_theme',
])
def test_help_runtime(entry):
    program = r'''
const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');
const nodes=new Map(),timers=new Map(),frames=[];let serial=0;
function node(id){
 if(!nodes.has(id)){
  const classes=new Set();
  nodes.set(id,{id,innerHTML:'',textContent:'',style:{display:'none'},attributes:{},events:{},isConnected:true,
   classList:{add:name=>classes.add(name),remove:name=>classes.delete(name),contains:name=>classes.has(name)},
   setAttribute(name,value){this.attributes[name]=value;},getAttribute(name){return this.attributes[name]??null;},
   addEventListener(name,callback){this.events[name]=callback;},querySelectorAll(){return[];},
   querySelector(selector){return node(selector.slice(1));},scrollIntoView(){},
   getBoundingClientRect(){return{left:50,top:100,bottom:120,width:120,height:40};}});
 }
 return nodes.get(id);
}
global.window={location:{hash:'',search:'',href:'https://arena.invalid/'},innerWidth:1000,scrollX:0,scrollY:0,pageXOffset:0,pageYOffset:0,addEventListener(){}};
global.document={readyState:'loading',addEventListener(){},getElementById:node,documentElement:node('html')};
global.setTimeout=callback=>{timers.set(++serial,callback);return serial;};
global.clearTimeout=id=>timers.delete(id);
global.requestAnimationFrame=callback=>{frames.push(callback);};
function flush(){const callbacks=[...timers.values()];timers.clear();callbacks.forEach(callback=>callback());}
for(const file of ['data/arena_release','adapter','components/glossary_service','components/spec_drawer','components/tooltip_manager','app'])vm.runInThisContext(fs.readFileSync('web/js/'+file+'.js','utf8'));
const seasons=Object.keys(window.ARENA_SEASONS_DATA);
function pool(sid){window.arenaAdapter=new window.ArenaDataAdapter(structuredClone(window.ARENA_SEASONS_DATA[sid]));return window.arenaAdapter;}
function drawer(){const view=window.ArenaSpecDrawer;view.drawerEl=node('drawer');view.fabEl=node('fab');view.isOpen=true;view.activeCategory='All';view.searchQuery='';return view;}
const checks={
 drawer_term_targets(){
  for(const sid of seasons){
   const adapter=pool(sid),view=drawer();
   const terms=[...adapter.getAllAnimals().map(a=>[a.id,'Zoo Animals']),['topk','Metrics'],['dropn','Metrics'],['monkey_percentile','Metrics'],['market','Benchmarks'],['CONTESTANT_G','Contestants']];
   for(const [term,category] of terms){
    view.isOpen=true;view.openTerm(term);
    assert(view.isOpen,'Inspecting a term closed the existing drawer');
    assert.equal(view.activeCategory,category,'The term targeted a category without its card');
    const resolved=window.ArenaGlossaryService.lookup(term);
    assert(node('arena-drawer-content').innerHTML.includes('id="spec-card-'+resolved.id+'"'));
   }
  }
 },
 drawer_categories(){
  pool(seasons[0]);const view=drawer();
  for(const [input,expected] of [['contestants','Contestants'],['animals','Zoo Animals'],['benchmarks','Benchmarks'],['metrics','Metrics']]){
   view.isOpen=false;view.openCategory(input);
   assert.equal(view.activeCategory,expected);assert(view.isOpen);
   assert(!node('arena-drawer-content').innerHTML.includes('No matching'));
   view.toggle(input);assert(!view.isOpen,'The existing same-category toggle stopped closing');
  }
 },
 drawer_search(){
  pool(seasons[0]);const view=drawer();view.searchQuery='<unmatched>&"';view.renderContent();
  const html=node('arena-drawer-content').innerHTML;
  assert(html.includes('&lt;unmatched&gt;&amp;&quot;'));assert(!html.includes('<unmatched>'));
 },
 glossary_aliases(){
  pool(seasons[0]);const glossary=window.ArenaGlossaryService;
  assert.equal(glossary.lookup('metric_monkey_percentile').id,'monkey_percentile');
  assert.equal(glossary.lookup('whale_shark').id,'whale-shark');
  assert.equal(glossary.lookup('turtle-22-3').id,'turtle');
 },
 glossary_boundaries(){
  pool(seasons[0]);
  for(const key of ['__proto__','constructor','toString',null,23,{}])assert.equal(window.ArenaGlossaryService.lookup(key),null);
 },
 anonymous_descriptions(){
  for(const sid of seasons){
   const adapter=pool(sid),dict=window.ArenaGlossaryService.getDictionary();
   for(const participant of adapter.getAllContestants()){
    const description=dict.contestants[participant.id];
    assert(description.tooltip.includes(description.name));
    assert(description.details.includes('Observation anchor: '+(participant.observation_start||adapter.getNavDates()[0])));
   }
  }
 },
 tooltip_lifecycle(){
  pool(seasons[0]);const view=window.ArenaTooltip;view.container=node('popover');
  const known=node('known');known.setAttribute('data-tooltip-term','nav');
  view.scheduleShow(known);flush();assert.equal(view.container.style.display,'block');
  const unknown=node('unknown');unknown.setAttribute('data-tooltip-term','unavailable-term');
  view.scheduleShow(unknown);flush();assert.equal(view.container.style.display,'none','An unknown term kept the previous explanation');
  view.scheduleShow(known);known.isConnected=false;flush();assert.equal(view.container.style.display,'none','A detached link opened a stale tooltip');
  known.isConnected=true;view.scheduleShow(known);flush();view.hide();frames.splice(0).forEach(callback=>callback());
  assert(!view.container.classList.contains('visible'),'A delayed animation revived a hidden tooltip');
  const fallback=node('fallback');fallback.setAttribute('data-tooltip-term','unavailable-term');fallback.setAttribute('title','<plain title>');
  view.scheduleShow(fallback);flush();assert(view.container.innerHTML.includes('&lt;plain title&gt;'));
 },
 tooltip_position(){
  const view=window.ArenaTooltip;view.container=node('popover');window.innerWidth=80;
  view.position(node('anchor'));assert(parseFloat(view.container.style.left)>=10,'A wide tooltip was clamped outside the left viewport edge');
 },
 storage_denied(){
  let rendered=0;global.localStorage={getItem(){throw Error('storage unavailable');},setItem(){throw Error('storage unavailable');}};
  window.ArenaApp.handleRouting=()=>rendered++;
  assert.doesNotThrow(()=>window.ArenaApp.initTheme());
  assert.equal(document.documentElement.getAttribute('data-theme'),'dark');
  assert.doesNotThrow(()=>node('theme-toggle-btn').events.click());
  assert.equal(document.documentElement.getAttribute('data-theme'),'light');assert.equal(rendered,1);
 },
 invalid_theme(){
  global.localStorage={getItem(){return 'invalid-theme';},setItem(){}};window.ArenaApp.initTheme();
  assert.equal(document.documentElement.getAttribute('data-theme'),'dark');
 }
};
checks[process.argv[1]]();
'''
    completed = subprocess.run(['node', '-e', program, entry], cwd=REPO_ROOT,
                               capture_output=True, text=True, timeout=30)
    assert completed.returncode == 0, completed.stderr
