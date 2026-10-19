"""Identity colors survive pool, metric, selection, slot and theme changes."""
import subprocess

import pytest

from arena.config import REPO_ROOT


@pytest.mark.parametrize('entry', ['curves', 'panorama', 'fingerprints', 'comparison', 'palette', 'heatmap_labels'])
def test_color_contract(entry):
    program = r'''
const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');
let theme='dark';const nodes=new Map(),options=new Map();
const node=id=>{if(!nodes.has(id))nodes.set(id,{id,innerHTML:'',style:{},addEventListener(){},
 querySelectorAll(){return[];},querySelector(){return null;}});return nodes.get(id);};
global.window={addEventListener(){}};
global.document={getElementById:node,querySelectorAll(){return[];},documentElement:{getAttribute(){return theme;}}};
global.setTimeout=cb=>cb();
global.echarts={getInstanceByDom(){return null;},init(dom){return{
 setOption(option){options.set(dom.id,option);},resize(){},on(){},off(){}};},graphic:{LinearGradient:function(){}}};
for(const file of ['data/arena_release','adapter','components/charts','views/decision_audit','views/contestant_detail'])
 vm.runInThisContext(fs.readFileSync('web/js/'+file+'.js','utf8'));
const colors=window.ArenaColors,charts=window.ArenaCharts;
const paint=series=>series.lineStyle?.color||series.itemStyle?.color||series.color;
function samePaint(series,expected){
 assert.equal(paint(series),expected,'Stroke changed identity: '+series.name);
 if(series.itemStyle?.color)assert.equal(series.itemStyle.color,expected,'Legend and stroke disagree');
}
function benchmarkPaint(series){
 for(const s of series){
  const role=s.benchmarkKey||(/ghost/i.test(s.name)?'ghost':/taotie|executable passive/i.test(s.name)?'taotie'
   :s.name.includes(window.arenaAdapter.getMarketBenchmarkName())?'market':null);
  if(role)samePaint(s,colors.semantic()[role]);
 }
}
function contrast(hex,bg){
 const luminance=c=>[1,3,5].map(i=>parseInt(c.slice(i,i+2),16)/255)
  .map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4)
  .reduce((sum,v,i)=>sum+v*[.2126,.7152,.0722][i],0);
 const a=luminance(hex),b=luminance(bg);return(Math.max(a,b)+.05)/(Math.min(a,b)+.05);
}
const observed=new Map();
for(const source of Object.values(window.ARENA_SEASONS_DATA))for(theme of ['dark','light']){
 const adapter=window.arenaAdapter=new window.ArenaDataAdapter(source),baseline=JSON.stringify(adapter.paths);
 const dates=adapter.getNavDates(),taotie=adapter.getBenchmarkTaotieCurve(),market=adapter.getBenchmarkCsi300Curve();
 const animals=adapter.getAllAnimals().map(a=>a.id),participants=adapter.getAllContestants().map(c=>c.id);
 const references=()=>colors.semantic();
 const checks={
  heatmap_labels(){
   let background=null;
   const init=echarts.init;
   echarts.init=dom=>{const chart=init(dom);chart.getModel=()=>({getSeriesByIndex(){return{
    getData(){return{getItemVisual(){return{fill:background};}};}};}});return chart;};
   for(const metric of ['total_return_pct','percentile_rank','max_drawdown_pct','sharpe_ratio']){
    charts.renderHeatmap('matrix',adapter.matrix,metric);
    const option=options.get('matrix'),label=option.series[0].label;
    const cell=option.series[0].data.find(d=>Array.isArray(d));
    const backgrounds=[...option.visualMap.inRange.color];
    for(let v=0;v<=255;v++)backgrounds.push('rgb('+[v,v,v].join(',')+')');
    for(background of backgrounds){
     const formatted=label.formatter({data:cell,value:cell,dataIndex:0});
     const match=formatted.match(/^\{(dark|light)\|(.+)\}$/);assert(match,'Heatmap label has no adaptive text style');
     const hex=background.startsWith('#')?background:'#'+background.match(/\d+/g).map(v=>Number(v).toString(16).padStart(2,'0')).join('');
     assert(contrast(hex,label.rich[match[1]].color)>=4.5,'The actual cell color obscures its numeric label');
     assert.equal(match[2],window.formatNumber(cell[2],metric==='percentile_rank'?0:1),'Contrast correction changed the displayed metric');
    }
   }
   echarts.init=init;
  },
  curves(){
   for(const cid of ['CONTESTANT_A','CONTESTANT_G'])for(const metric of ['nav','drawdown','excess_csi300']){
    const paths=animals.map(id=>adapter.getPath(cid+'_'+id));
    charts.renderMultiAnimalCurves('profile',dates,paths,taotie,market,metric);
    benchmarkPaint(options.get('profile').series);
    const all=options.get('profile').series.slice(0,paths.length);
    for(const [i,path]of paths.entries()){
     const expected=paint(all[i]);assert.equal(expected,colors.animal(path.animal_id));
     charts.renderEquityCurves('detail',dates,path,taotie,market,null,metric);
     const line=options.get('detail').series.find(s=>s.name.includes(path.path_id)||s.name===cid);
     samePaint(line,expected);
     benchmarkPaint(options.get('detail').series);
    }
    for(const subset of [[...paths].reverse(),paths.slice(5,12),[paths[0]]]){
     charts.renderMultiAnimalCurves('profile',dates,subset,taotie,market,metric);
     options.get('profile').series.slice(0,subset.length).forEach((s,i)=>samePaint(s,colors.animal(subset[i].animal_id)));
    }
   }
   for(const metric of ['nav','drawdown','excess_csi300'])for(const animal of animals){
    const paths=participants.map(cid=>adapter.getPath(cid+'_'+animal));
    for(const subset of [paths,[...paths].reverse(),paths.slice(3)]){
     charts.renderCrossModelAnimalCurves('zoo',dates,subset,taotie,market,metric);
     options.get('zoo').series.slice(0,subset.length).forEach((s,i)=>samePaint(s,colors.subject(subset[i].contestant_id)));
    }
   }
   const mixed=['CONTESTANT_A','CONTESTANT_G'].flatMap(cid=>animals.slice(0,4).map(a=>adapter.getPath(cid+'_'+a)));
   for(const metric of ['nav','drawdown','excess_csi300']){
    charts.renderCrossModelAnimalCurves('mixed',dates,mixed,taotie,market,metric);
    const lines=options.get('mixed').series;
    mixed.forEach((p,i)=>samePaint(lines[i],colors.animal(p.animal_id)));
    assert.notDeepEqual(lines[0].lineStyle.type,lines[4].lineStyle.type,'Same animal across models lost its secondary identity');
   }
   charts.renderScatter('scatter',adapter.getAllPaths());
   const scatter=options.get('scatter').series[0];
   for(const data of scatter.data)assert.equal(scatter.itemStyle.color({data}),colors.animal(data[3].animal_id));
  },
  panorama(){
   for(const focus of ['all',...participants])for(const cohort of ['top5','robot','sloth','snail','eagle','turnover','koala']){
    const normal=adapter.getMacroPanoramaData('nav',cohort,focus),candidates=normal.seriesList.filter(s=>s.path);
    const paints=new Map(candidates.map(s=>[s.id,s.color]));
    for(const metric of ['nav','drawdown','excess_csi300','excess_taotie','excess_ghost']){
     const data=adapter.getMacroPanoramaData(metric,cohort,focus);
     charts.renderMacroPanorama('panorama',data);
     options.get('panorama').series.forEach((s,i)=>{
      const item=data.seriesList[i];samePaint(s,item.path?paints.get(item.id):colors.subject(item.id));
      if(item.path){
       const peers=candidates.filter(c=>c.path.animal_id===item.path.animal_id);
       if(new Set(candidates.map(c=>c.path.animal_id)).size>1&&new Set(peers.map(c=>c.path.contestant_id)).size>1)
        assert.deepEqual(s.lineStyle.type,colors.modelLine(item.path.contestant_id));
      }
     });
    }
   }
  },
  fingerprints(){
   for(const cid of participants){
    const fp=adapter.getContestantFingerprints(cid);
    charts.renderFingerprintGroup('delay','turnover','breadth','direction',fp);
    for(const [i,family]of ['sloth','snail'].entries())options.get('delay').series[i].data.forEach((d,j)=>{
     if(d!==null)assert.equal(d.itemStyle.color,colors.animal(j?family+'-'+j:'robot'));
    });
    const bars=options.get('turnover').series[0];
    fp.turnoverData.forEach((d,i)=>assert.equal(bars.itemStyle.color({dataIndex:i}),colors.animal(d.animal_id)));
    options.get('breadth').series[0].data.forEach((d,i)=>{
     if(d!==null)assert.equal(d.itemStyle.color,fp.breadthData[i].subject_id?references().taotie:colors.animal(fp.breadthData[i].animal_id));
    });
    const direction=options.get('direction').series[0].data;
    assert.equal(direction[0].itemStyle.color,colors.animal('robot'));
    assert.equal(direction[1].itemStyle.color,colors.animal('koala'));
    assert.equal(direction[2].itemStyle.color,references().spread);
    window.ContestantDetailView.render('root',cid);
    const deciles=options.get('chart-fingerprint-meerkat').series[0];
    deciles.data.forEach((d,i)=>assert.equal(d.itemStyle.color,colors.animal('meerkat-'+(i+1)*10)));
   }
   const path=adapter.getPath('CONTESTANT_A_koala');
   charts.renderMonkeyDistribution('null',{colony_size:100000},path.total_return_pct,50,.5,path.animal_id);
   const distribution=options.get('null').series[0];
   assert.equal(distribution.itemStyle.borderColor,references().monkey);
   assert.equal(distribution.markLine.lineStyle.color,colors.animal('koala'));
  },
  comparison(){
   const view=window.DecisionAuditView;
   view.activePreset='custom';view.slotC='BENCHMARK_taotie';view.start=null;view.end=null;
   for(const ids of [['CONTESTANT_G','CONTESTANT_A'],['CONTESTANT_A','CONTESTANT_G']]){
    [view.slotA,view.slotB]=ids;view.render('root');
    const option=options.get('chart-archaeology-trajectory');
    assert(option,'Comparison did not render');
    [ids[0],ids[1],view.slotC].forEach((id,i)=>samePaint(option.series[i],colors.subject(id)));
    samePaint(option.series[3],references().spread);
    for(const id of [...ids,view.slotC])assert(node('root').innerHTML.includes('--subject-color:'+colors.subject(id)));
   }
  },
  palette(){
   const animalColors=animals.map(id=>colors.animal(id));
   assert.equal(new Set(animalColors).size,animals.length,'Distinct animals share a color');
   const modelIds=[...participants,'CONTESTANT_H','CONTESTANT_AA'];
   const modelColors=modelIds.map(id=>colors.subject(id));
   assert.equal(new Set(modelColors).size,modelIds.length,'Future branches collide with an existing participant');
   for(const participant of adapter.getAllContestants())for(const label of [participant.display_name,participant.anonymous_name].filter(Boolean))
    assert.equal(colors.subject(label),colors.subject(participant.id),'An alternate label changed participant color');
   for(const id of [...animals,...modelIds]){
    const color=animals.includes(id)?colors.animal(id):colors.subject(id),key=theme+'/'+id;
    assert.match(color,/^#[a-f0-9]{6}$/i);
    assert(contrast(color,theme==='light'?'#ffffff':'#0f172a')>=3,'Identity stroke is too faint: '+id);
    if(observed.has(key))assert.equal(color,observed.get(key),'Changing pool changed identity color');
    observed.set(key,color);
   }
   for(const key of ['market','taotie','ghost','monkey','spread'])assert(contrast(references()[key],theme==='light'?'#ffffff':'#0f172a')>=3);
   const css=fs.readFileSync('web/css/variables.css','utf8').split('[data-theme="light"]')[theme==='light'?1:0];
   for(const [key,token]of Object.entries({market:'benchmark-market',taotie:'benchmark-taotie',ghost:'benchmark-ghost',monkey:'benchmark-monkey',spread:'chart-spread'}))
    assert.equal(references()[key],css.match(new RegExp('--'+token+':\\s*(#[a-f0-9]+)'))[1],'Canvas fallback disagrees with CSS swatches');
  }
 };
 checks[process.argv[1]]();
 assert.equal(JSON.stringify(adapter.paths),baseline,'Color rendering mutated published metrics');
}
'''
    result = subprocess.run(
        ['node', '-e', program, entry], cwd=REPO_ROOT,
        capture_output=True, text=True, timeout=45,
    )
    assert result.returncode == 0, result.stderr
