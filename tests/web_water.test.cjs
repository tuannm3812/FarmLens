const {test}=require('node:test');
const assert=require('node:assert/strict');
const w=require('../web/water.js');

const stats=(n)=>({median:n,p10:n/2,p90:n*1.5});
function response(supply=null){return {source:{status:'cached',stale:false,source:'Open-Meteo',fetched_at:'2026-10-20T00:00:00Z',warning:'',grid:{latitude:-32.25,longitude:148.5}},assessment:{status:'available',stale:false,profile:{name:'Wheat',coefficient_note:'Spring proxy',timing_note:'Illustrative',kc:[.3,1.15,.25]},inputs:{crop_id:'wheat',sowing_month:5,stages:[20,30,60,40],soil_buffer_mm:100,starting_water_mm:50,rain_capture_pct:80,efficiency_pct:80,irrigation:'irrigated',supply_ml_ha:supply},summary:{demand_mm:stats(300),rain_retained_mm:stats(200),net_irrigation_mm:stats(60),gross_irrigation_ml_ha:stats(.75),remaining_shortfall_mm:supply===null?null:stats(60)},season_count:10,seasons_with_shortfall:supply===null?null:10,within_broad_sowing_window:true,notice:'Historical scenario only.',sources:[],seasons:[{year:2025,start_date:'2025-05-01',end_date:'2025-09-27',demand_mm:300,rainfall_mm:220,rain_retained_mm:200,net_irrigation_mm:60,gross_irrigation_ml_ha:.75,remaining_shortfall_mm:supply===null?null:60}]}};}

test('unknown supply stays unassessed while an explicit zero reports the shortfall',()=>{
 assert.match(w.renderResult(response()),/Supply not entered/);
 assert.doesNotMatch(w.renderResult(response()),/0 of 10/);
 const zero=w.renderResult(response(0));
 assert.match(zero,/10 of 10/);
 assert.match(zero,/Remaining shortfall/);
 assert.match(zero,/0\.00 ML\/ha/);
});

test('missing history gives no numeric water recommendation and stale history is labelled',()=>{
 const missing=response();missing.assessment.status='unavailable';missing.assessment.reason='No valid history';missing.assessment.summary=null;
 assert.match(w.renderResult(missing),/No valid history/);
 assert.doesNotMatch(w.renderResult(missing),/Median demand/);
 const stale=response();stale.source.stale=true;stale.assessment.stale=true;
 assert.match(w.renderResult(stale),/STALE/);
 assert.match(w.renderResult(stale),/not a forecast/i);
});

test('water rendering escapes text and never renders unsafe source links',()=>{
 const data=response();data.assessment.profile.name='<img src=x onerror=alert(1)>';
 data.assessment.sources=[{title:'Bad <source>',url:'javascript:alert(1)'}];
 const html=w.renderResult(data);
 assert.match(html,/&lt;img/);
 assert.doesNotMatch(html,/<img|href="javascript/);
 assert.match(html,/10th–90th/);
 assert.match(html,/Soil water buffer/);
});

test('superseded requests cannot publish even if transport ignores cancellation',()=>{
 const gate=w.requestGate();
 const old=gate.begin();const latest=gate.begin();
 assert.equal(old.signal.aborted,true);
 assert.equal(old.current(),false);assert.equal(latest.current(),true);
 gate.invalidate();assert.equal(latest.current(),false);assert.equal(latest.signal.aborted,true);
});
