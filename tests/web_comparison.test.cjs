const test=require('node:test');
const assert=require('node:assert/strict');
const {buildComparison,renderRadar}=require('../web/comparison.js');
const scores={temperature:100,rainfall:80,ph:70,frost:60,fire:null,texture:90,carbon:84};
const crop={id:'canola',name:'Canola',subscores:scores};
test('missing factors remain gaps without fabricated zero scores',()=>{
 const model=buildComparison([crop],['canola']);
 assert.equal(model.series[0].values[4],null);
 assert.equal(model.series[0].complete,false);
 assert.equal(model.series[0].segments.length,5);
 assert.ok(model.series[0].segments.every(([a,b])=>a!==4&&b!==4));
 const svg=renderRadar(model,360);
 assert.ok(!svg.includes('<polygon'));
 assert.ok(svg.includes('Unassessed'));
});
test('real zero is assessed and full series may close',()=>{
 const model=buildComparison([{...crop,subscores:{...scores,fire:0}}],['canola']);
 assert.equal(model.series[0].values[4],0);assert.equal(model.series[0].complete,true);
 assert.equal(model.series[0].segments.length,7);
});
test('selection excludes unwanted series and handles none',()=>{
 const crops=[crop,{...crop,id:'oats',name:'Oats'}];
 assert.deepEqual(buildComparison(crops,['oats']).series.map(s=>s.id),['oats']);
 assert.deepEqual(buildComparison(crops,[]).series,[]);
});
test('non-finite and out-of-domain values stay unassessed; labels are escaped',()=>{
 const model=buildComparison([{...crop,name:'<crop>',subscores:{...scores,ph:NaN,carbon:101}}],['canola']);
 assert.equal(model.series[0].values[2],null);assert.equal(model.series[0].values[6],null);
 assert.ok(!renderRadar(model,360).includes('<crop>'));
});
