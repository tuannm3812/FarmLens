const {test}=require('node:test');
const assert=require('node:assert/strict');
const v=require('../web/vegetation.js');
const sample={date:'2026-10-07',status:'available',observed_at:'2026-10-06T23:55:27+00:00',green_pct:33,dry_pct:24,bare_pct:42,unmixing_error:8};
const source={status:'cached',stale:false,data:{resolution_m:30,as_of:'2026-10-20',samples:[sample]}};
test('cover chart preserves independent percentages and actual dates',()=>{
 const html=v.render(source);assert.match(html,/33%/);assert.match(html,/24%/);assert.match(html,/42%/);
 assert.match(html,/2026-10-07/);assert.match(html,/30 m/);assert.match(html,/<table/);
});
test('unavailable and excluded samples do not invent percentages or trend segments',()=>{
 assert.doesNotMatch(v.render({status:'offline',data:{samples:[]}}),/33%|cover-track/);
 const html=v.render({...source,data:{...source.data,samples:[{date:'2026-10-01',status:'excluded',reason:'Cloud'},sample]}});
 assert.match(html,/Cloud/);assert.match(html,/Gap/);assert.doesNotMatch(html,/polyline/);
 const stale=v.render({...source,stale:true});assert.match(stale,/stale/i);
});
test('latest incomplete sample is omitted, source text escaped and future values not guessed',()=>{
 const html=v.render({...source,data:{...source.data,samples:[{...sample,green_pct:NaN}]}});
 assert.doesNotMatch(html,/NaN|width:NaN/);assert.match(html,/No usable/);
 assert.match(v.render({status:'offline',warning:'<img>',data:{samples:[]}}),/&lt;img/);
});
test('point changes abort and discard old vegetation responses',async()=>{
 const pending=[],states=[];
 const loader=v.createLoader((url,payload,signal)=>new Promise(resolve=>pending.push({resolve,signal,payload})),r=>states.push(r));
 loader.select({lat:-32.25,lon:148.6});loader.select({lat:-31.95,lon:141.45});
 assert.equal(pending[0].signal.aborted,true);
 pending[0].resolve(source);await Promise.resolve();assert.equal(states.at(-1).status,'loading');
 pending[1].resolve({...source,status:'live'});await Promise.resolve();assert.equal(states.at(-1).status,'live');
 loader.select({lat:-31.95,lon:141.45});assert.equal(pending.length,2);
 loader.cancel();
});
test('partially available offline observations never claim live status',()=>{
 const html=v.render({...source,status:'offline'});assert.match(html,/Partial/);assert.doesNotMatch(html,/>Live ·/);
});
