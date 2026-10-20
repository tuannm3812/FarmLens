const {test}=require('node:test');
const assert=require('node:assert/strict');
const nav=require('../web/navigation.js');
const presets=[{name:'Dubbo',lat:-32.2569,lon:148.6011},{name:'Coffs Harbour',lat:-30.2963,lon:153.1135}];
const scenario={mode:'season',month:7,irrigation:'irrigated',category:'annual',drainage:'well_drained',cache_only:true};
test('returning to explorer retains a point and scenario, excluding unrelated data',()=>{
 const raw=nav.encode({...presets[0],secret:'ignored'}, {...scenario,api_key:'ignored',budget:{yield:5}});
 const got=nav.read(raw,presets,'');
 assert.deepEqual(got,{point:presets[0],scenario});assert.doesNotMatch(raw,/secret|api_key|budget/);
});
test('a named demo link overrides saved land and starts a fresh scenario',()=>{
 const got=nav.read(nav.encode(presets[0],scenario),presets,'#coffs-harbour');
 assert.deepEqual(got.point,presets[1]);assert.equal(got.scenario.irrigation,'rainfed');assert.equal(got.scenario.drainage,'unknown');
});
test('corrupt, invalid or obsolete saved selections never restore',()=>{
 const raw=nav.encode(presets[0],scenario);
 for(const invalid of ['{broken','null','[]',raw.replace('"month":7','"month":13'),raw.replace('"lat":-32.2569','"lat":"-32"'),raw.replace('"irrigated"','"invented"'),raw.replace('"version":1','"version":99')])assert.equal(nav.read(invalid,presets,''),null);
 assert.equal(nav.read('',presets,'#unrecognised'),null);
});
test('searched address labels are not retained with the selected coordinates',()=>{
 const searched={name:'123 Private Road, Farmhouse, NSW',lat:-32.26,lon:148.61};
 const raw=nav.encode(searched,scenario);
 assert.doesNotMatch(raw,/Private Road|Farmhouse/);
 assert.deepEqual(nav.read(raw,presets,'').point,{name:'Selected NSW point',lat:-32.26,lon:148.61});
 const legacy=JSON.stringify({version:1,point:searched,scenario});
 assert.equal(nav.read(legacy,presets,'').point.name,'Selected NSW point');
});
