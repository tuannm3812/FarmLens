/* Only the last assessed selection lives in this tab; never store report or budget data. */
(function(root){
 'use strict';
 const defaults=()=>({mode:'explore',month:5,irrigation:'rainfed',category:null,drainage:'unknown',cache_only:false});
 function clean(point,scenario){
  if(!point||!scenario||typeof point.name!=='string'||!point.name.trim()||point.name.length>250||
   typeof point.lat!=='number'||!Number.isFinite(point.lat)||point.lat < -37.6||point.lat > -28||
   typeof point.lon!=='number'||!Number.isFinite(point.lon)||point.lon < 140.9||point.lon > 153.7||
   !['explore','season'].includes(scenario.mode)||!Number.isInteger(scenario.month)||scenario.month<1||scenario.month>12||
   !['rainfed','irrigated'].includes(scenario.irrigation)||![null,'annual','perennial','pasture'].includes(scenario.category)||
   !['unknown','well_drained','poorly_drained'].includes(scenario.drainage)||typeof scenario.cache_only!=='boolean')return null;
  return {point:{name:point.name,lat:point.lat,lon:point.lon},scenario:{mode:scenario.mode,month:scenario.month,irrigation:scenario.irrigation,category:scenario.category,drainage:scenario.drainage,cache_only:scenario.cache_only}};
 }
 function read(raw,presets,hash){
  const preset=presets.find(p=>'#'+p.name.toLowerCase().replaceAll(' ','-')===hash);
  if(preset)return clean(preset,defaults());
  try{
   const stored=JSON.parse(raw),value=stored?.version===1?clean(stored.point,stored.scenario):null;
   if(value){const known=presets.find(p=>p.lat===value.point.lat&&p.lon===value.point.lon);value.point.name=known?.name||'Selected NSW point';}
   return value;
  }catch{return null;}
 }
 function encode(point,scenario){const value=clean({...point,name:'Selected NSW point'},scenario);return value?JSON.stringify({version:1,...value}):null;}
 const api={read,encode};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.FarmLensNavigation=api;
})(typeof globalThis!=='undefined'?globalThis:this);
