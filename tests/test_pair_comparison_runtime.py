"""Exercise the actual browser adapter and comparison view using synthetic NAV."""
import subprocess

from arena.config import REPO_ROOT


def test_presets_follow_declared_branch_metadata():
    program=r'''
const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');global.window={};
vm.runInThisContext(fs.readFileSync('web/js/adapter.js','utf8'));
const participants=[['A',null,null],['C',null,null],['G','A','2026-10-09'],['H','G','2026-10-14'],
 ['I','C','2026-10-09'],['J','I','2026-10-14'],['K','C','2026-11-01']].map(([id,parent,start])=>({
 contestant_id:'CONTESTANT_'+id,retrained_from:parent?'CONTESTANT_'+parent:null,observation_start:start}));
const legacy={id:'legacy_case'};
const adapter=new window.ArenaDataAdapter({meta:{cutoff:'2026-10-16'},contestants:participants,decision_forks:[legacy]});
const presets=adapter.getComparisonPresets();
assert.deepEqual(presets.map(p=>p.title||p.id),['A / G','G / H','A / H','C / I','I / J','C / J','legacy_case']);
assert(!presets.some(p=>p.chosen_contestant_id==='CONTESTANT_K'),'An unadmitted branch acquired a preset');
assert.equal(presets.find(p=>p.title==='C / J').decision_date,'2026-10-14');
participants[0].retrained_from='CONTESTANT_H';
const cyclic=new window.ArenaDataAdapter({meta:{cutoff:'2026-10-16'},contestants:participants}).getComparisonPresets();
assert(cyclic.length<participants.length**2);assert(cyclic.every(p=>p.chosen_contestant_id!==p.rejected_contestant_id));
'''
    result=subprocess.run(['node','-e',program],cwd=REPO_ROOT,capture_output=True,text=True,timeout=10)
    assert result.returncode==0,result.stderr


def test_pair_comparison_runtime_and_late_entry():
    program=r'''
const fs=require('fs'),vm=require('vm');
const nodes=new Map();
const node=id=>{if(!nodes.has(id))nodes.set(id,{innerHTML:'',addEventListener(){},querySelectorAll(){return[];},querySelector(){return null;}});return nodes.get(id);};
global.window={};global.document={getElementById:node};global.setTimeout=cb=>cb();
for(const file of ['web/js/adapter.js','web/js/components/charts.js','web/js/views/decision_audit.js'])vm.runInThisContext(fs.readFileSync(file,'utf8'));
const dates=['2026-10-09','2026-10-12','2026-10-13','2026-10-14'];
const contestants=['A','G','H'].map(c=>({contestant_id:'CONTESTANT_'+c,observation_start:c==='H'?dates[2]:c==='G'?dates[0]:null}));
const paths=contestants.map(c=>({...c,path_id:c.contestant_id+'_robot',animal_id:'robot'}));
const curves={CONTESTANT_A_robot:[2,2.2,2.1,2.15],CONTESTANT_G_robot:[1,1.2,1.1,1.16],CONTESTANT_H_robot:[null,null,1,.98]};
window.arenaAdapter=new window.ArenaDataAdapter({meta:{season_id:'synthetic',cutoff:dates.at(-1)},contestants,paths,nav_timeline:{dates,curves}});
const adapter=window.arenaAdapter;
const result=adapter.getPairComparison('CONTESTANT_A','CONTESTANT_G');
if(Math.abs(result.spread[2]-5)>1e-9||result.reference[0]!==1||result.candidate[0]!==1)throw Error('common anchor or pp differs');
const late=adapter.getPairComparison('CONTESTANT_G','CONTESTANT_H');
if(late.start!==dates[2]||late.sessions!==1)throw Error('late participant window differs');
let failed=false;try{adapter.getPairComparison('CONTESTANT_G','CONTESTANT_H','robot',dates[0]);}catch(_){failed=true;}
if(!failed)throw Error('missing history was accepted');
const three=adapter.getComparisonWindow(['CONTESTANT_A','CONTESTANT_G','CONTESTANT_H']);
if(three.start!==dates[2]||three.profiles.some(p=>p.curve[0]!==1||p.nullCourt!=='N/A · selected window'))throw Error('third subject failed to align all cards');
const previous=adapter.getComparisonWindow(['CONTESTANT_A','CONTESTANT_G'],'robot',dates[0],dates[1]);
if(Math.abs(previous.profiles[1].totalReturnPct-20)>1e-9||previous.dates.length!==2)throw Error('historical cutoff borrowed latest metrics');
let plotted;window.ArenaCharts.renderCustomArchaeology=(id,dates,profiles)=>{plotted={dates,profiles};};
window.DecisionAuditView.render('root');
if(!node('root').innerHTML.includes('slot-c-select')||!node('root').innerHTML.includes('Cross-Handler')||plotted.profiles[0].name!=='CONTESTANT_G'||plotted.profiles[1].name!=='CONTESTANT_A')throw Error('original workbench and default preset differ');
window.DecisionAuditView.slotC='CONTESTANT_H';window.DecisionAuditView.render('root');
if(plotted.dates[0]!==dates[2]||window.DecisionAuditView.window.sessions!==1)throw Error('third slot window mismatch');
window.DecisionAuditView.start=dates[0];window.DecisionAuditView.render('root');
if(!node('root').innerHTML.includes('common observation anchor')||node('root').innerHTML.includes('kpi-value'))throw Error('invalid window silently retained scores');
curves.CONTESTANT_G_robot[3]=null;
failed=false;try{adapter.getComparisonWindow(['CONTESTANT_A','CONTESTANT_G']);}catch(_){failed=true;}
if(!failed)throw Error('window hole accepted');
curves.CONTESTANT_G_robot[3]=1.16;curves.CONTESTANT_G_robot[0]=null;
failed=false;try{adapter.getComparisonWindow(['CONTESTANT_A','CONTESTANT_G']);}catch(_){failed=true;}
if(!failed)throw Error('missing declared anchor was silently moved forward');
if(adapter.getComparisonWindow(['CONTESTANT_A','CONTESTANT_G'],'robot',dates[1]).start!==dates[1])throw Error('explicit later window rejected');
'''
    result=subprocess.run(['node','-e',program],cwd=REPO_ROOT,capture_output=True,text=True)
    assert result.returncode==0,result.stderr
