const test=require('node:test');
const assert=require('node:assert/strict');
const {createResolver}=require('../web/location.js');

test('rapid pin selections look up only the latest point without moving it',async t=>{
 t.mock.timers.enable({apis:['setTimeout']});
 const calls=[],states=[];
 const resolver=createResolver(async(path,payload)=>{calls.push({path,payload});return {data:{name:'Dubbo, NSW',kind:'locality'},status:'cached'};},state=>states.push(state));
 const point={lat:-32.2569,lon:148.6011};
 resolver.select({lat:-31.95,lon:141.45},false);resolver.select(point,true);
 t.mock.timers.tick(450);await Promise.resolve();
 assert.deepEqual(calls,[{path:'/api/reverse',payload:{...point,cache_only:true}}]);
 assert.equal(states.at(-1).name,'Dubbo, NSW');
 assert.equal(states.at(-1).status,'resolved');
 assert.deepEqual(point,{lat:-32.2569,lon:148.6011});
});

test('a late name response cannot rename a new pin or preset',async t=>{
 t.mock.timers.enable({apis:['setTimeout']});
 const requests=[],states=[];
 const resolver=createResolver((path,payload,signal)=>new Promise(resolve=>requests.push({resolve,signal})),state=>states.push(state));
 resolver.select({lat:-32.26,lon:148.6},false);t.mock.timers.tick(450);
 resolver.select({lat:-31.95,lon:141.45},false);t.mock.timers.tick(450);
 requests[0].resolve({data:{name:'Dubbo, NSW'},status:'live'});await Promise.resolve();
 assert.equal(requests[0].signal.aborted,true);
 assert.equal(states.at(-1).status,'loading');
 resolver.cancel();requests[1].resolve({data:{name:'Broken Hill, NSW'},status:'live'});await Promise.resolve();
 assert.equal(states.filter(s=>s.status==='resolved').length,0);
});

test('network and missing-name responses keep coordinates as the honest fallback',async t=>{
 t.mock.timers.enable({apis:['setTimeout']});
 for(const response of [null,{data:{name:null},status:'offline'}]){
  const states=[];
  const resolver=createResolver(async()=>{if(response===null)throw new Error('Network unavailable');return response;},s=>states.push(s));
  resolver.select({lat:-32.26,lon:148.6},true);t.mock.timers.tick(450);await Promise.resolve();
  assert.equal(states.at(-1).status,'unavailable');
  assert.equal(states.at(-1).name,null);
 }
});
