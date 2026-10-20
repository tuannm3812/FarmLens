const test=require('node:test');
const assert=require('node:assert/strict');
const ui=require('../web/overview.js');
const days=Array.from({length:7},(_,i)=>({date:`2026-10-${20+i}`,rainfall_mm:i,min_temperature_c:6,max_temperature_c:22,weather_code:i?null:0}));
const forecast={status:'cached',stale:false,data:{start_date:days[0].date,end_date:days[6].date,rainfall_mm:21,min_temperature_c:6,max_temperature_c:22,days}};
test('forecast renders seven actual dates and unknown codes without guessed sunshine',()=>{
 const html=ui.weather(forecast);
 assert.equal((html.match(/class="forecast-day"/g)||[]).length,7);
 assert.equal((html.match(/Clear sky/g)||[]).length,1);
 assert.equal((html.match(/Conditions unavailable/g)||[]).length,6);
 assert.match(html,/20–26 Oct 2026/);assert.match(html,/21 mm/);
 assert.match(ui.weather({...forecast,data:{...forecast.data,days:days.slice(1)}}),/Daily detail unavailable/);
});
test('stale or missing weather never issues current frost or heat flags',()=>{
 const hot={...forecast,data:{...forecast.data,min_temperature_c:-2,max_temperature_c:36}};
 assert.match(ui.weather(hot),/Frost &amp; heat flags/);
 const stale=ui.weather({...hot,stale:true});
 assert.match(stale,/Saved outlook/);assert.doesNotMatch(stale,/Frost &amp; heat flags/);
 assert.match(stale,/Refresh before use/);
 const unavailable=ui.weather({status:'offline',data:{}});
 assert.match(unavailable,/Outlook unavailable/);assert.doesNotMatch(unavailable,/forecast-day/);
});
test('land snapshot preserves missing data, carbon units and dated pixel context',()=>{
 const cover={status:'live',data:{class_code:111,label:'Cultivated vegetation',year:2025,resolution_m:30}};
 const html=ui.land({status:'cached',data:{ph:6.2,soc_g_kg:13,clay_pct:12,sand_pct:70}},cover);
 assert.match(html,/1.30%/);assert.match(html,/2025 · 30 m pixel/);assert.match(html,/Sandy/);
 assert.match(html,/not a farm boundary/);
 assert.match(ui.land({status:'offline',data:{}},{status:'offline',data:{}}),/Land cover unavailable/);
 assert.doesNotMatch(ui.land({data:{}},cover),/0\.00%/);
 assert.doesNotMatch(ui.land({data:{}},{...cover,data:{...cover.data,label:'<script>x</script>'}}),/<script>/);
});
test('snapshot leaves inconsistent or negative soil fractions unassessed',()=>{
 for(const [clay_pct,sand_pct] of [[20,80.2],[-1,70],[30,-1]]){
  const html=ui.land({status:'cached',data:{clay_pct,sand_pct}},{status:'offline',data:{}});
  assert.match(html,/<dd>Unassessed<\/dd>/);
 }
 assert.match(ui.land({data:{clay_pct:20,sand_pct:80}}),/<dd>Sandy<\/dd>/);
});
test('monthly chart requires all twelve valid months and includes numeric table',()=>{
 const source={status:'cached',data:{period:'2016–2025',years:10,monthly:Array.from({length:12},(_,i)=>({month:i+1,rainfall_mm:i*10,temperature_c:i+5}))}};
 const html=ui.climate(source);
 assert.match(html,/role="img"/);assert.match(html,/<table>/);assert.match(html,/2016–2025/);assert.match(html,/December/);
 assert.doesNotMatch(ui.climate({...source,status:'offline'}),/<svg/);
 assert.doesNotMatch(ui.climate({...source,data:{...source.data,monthly:source.data.monthly.slice(1)}}),/<svg/);
 assert.doesNotMatch(ui.climate({...source,data:{...source.data,monthly:source.data.monthly.map(m=>({...m,rainfall_mm:-1}))}}),/<svg/);
});
test('cover loader guards late responses and reuses scenario-only context',async()=>{
 const pending=[],states=[];
 const loader=ui.createCoverLoader((path,payload,signal)=>new Promise(resolve=>pending.push({resolve,path,payload,signal})),s=>states.push(s));
 const p={lat:-32.2569,lon:148.6011,cache_only:false};
 loader.select(p);loader.select({...p,mode:'season'});assert.equal(pending.length,1);
 loader.select({...p,lat:-31.95,cache_only:true});assert.equal(pending[0].signal.aborted,true);
 pending[0].resolve({status:'live',data:{label:'Wrong place'}});await Promise.resolve();
 assert.equal(states.at(-1).status,'loading');
 pending[1].resolve({status:'offline',data:{}});await Promise.resolve();assert.equal(states.at(-1).status,'offline');
 assert.equal(pending[1].payload.cache_only,true);
 loader.select({...p,lat:-31.95,cache_only:true},{refresh:true});assert.equal(pending.length,3);
});

test('compact land card keeps class icons, observed dates and land-use cautions',()=>{
 const soil={data:{}},base={status:'cached',data:{class_code:111,label:'Cultivated vegetation',year:2025,resolution_m:30}};
 const cultivated=ui.land(soil,base);
 assert.match(cultivated,/icons\/land.svg#cultivated/);assert.match(cultivated,/2025 · 30 m pixel/);
 const built=ui.land(soil,{...base,data:{...base.data,class_code:215,label:'Artificial surfaces'}});
 assert.match(built,/This pixel maps built surfaces/);
 const offline=ui.land(soil,{...base,status:'offline'});
 assert.match(offline,/Land cover unavailable/);assert.match(offline,/icons\/land.svg#unknown/);
});
