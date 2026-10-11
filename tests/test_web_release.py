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
function node(id){if(!nodes.has(id))nodes.set(id,{innerHTML:'',addEventListener(){},querySelectorAll(){return[];},classList:{toggle(){},add(){},remove(){}}});return nodes.get(id);}
global.window={addEventListener(){}};
global.document={documentElement:{getAttribute(){return'dark';}},getElementById:node,querySelectorAll(){return[];},querySelector(){return node('query');}};
global.setTimeout=cb=>{cb();return 0;};
global.echarts={getInstanceByDom(){return null;},init(){return {setOption(){},resize(){},getOption(){return{series:[]};},on(){}};},graphic:{LinearGradient:function(){}}};
for(const file of ['web/js/data/arena_release.js','web/js/adapter.js','web/js/components/charts.js','web/js/views/methodology.js','web/js/views/path_detail.js'])vm.runInThisContext(fs.readFileSync(file,'utf8'));
const results=[];
for(const [sid,data] of Object.entries(window.ARENA_SEASONS_DATA)){
 if(data.meta.evaluation_id!==window.ARENA_ACTIVE_EVALUATION)throw Error('mixed generations');
 if(data.nav_timeline.dates.at(-1)!==data.meta.cutoff)throw Error('cutoff differs');
 for(const values of Object.values(data.nav_timeline.curves))if(values[0]!==1)throw Error('anchor differs');
 const tested=data.paths.filter(p=>p.test_status==='random_control');
 if(tested.length!==168)throw Error('comparison coverage differs');
 for(const p of tested){
  if(p.empirical_p_value!==(p.exceedance_count+1)/(p.monkey_count+1))throw Error('p precision or count differs');
  if(p.is_statistically_significant!==(p.empirical_p_value<.05))throw Error('flag differs');
 }
 if(data.paths.filter(p=>p.test_status==='not_applicable').some(p=>p.empirical_p_value!==null))throw Error('reference has random p');
 window.arenaAdapter=new window.ArenaDataAdapter(data);
 window.MethodologyView.render('root');
 window.PathDetailView.render('root',tested[0].path_id);
 window.PathDetailView.render('root',data.paths.find(p=>p.animal_id==='ghost_taotie').path_id);
 results.push({sid,paths:data.paths.length,tests:tested.length,count:tested[0].monkey_count});
}
console.log(JSON.stringify(results));
'''
    completed=subprocess.run(['node','-e',program],cwd=REPO_ROOT,capture_output=True,text=True)
    assert completed.returncode==0,completed.stderr
    results=json.loads(completed.stdout)
    assert len(results)==5
    assert all(result['paths']==170 and result['tests']==168 and result['count']>=16800 for result in results)
