/* Optional historical water scenarios. No access to the crop-scoring engine. */
(function(root){
 'use strict';
 const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const num=(value,d=0)=>typeof value==='number'&&Number.isFinite(value)?value.toLocaleString('en-AU',{minimumFractionDigits:d,maximumFractionDigits:d}):'—';
 const months=['January','February','March','April','May','June','July','August','September','October','November','December'];
 const link=source=>typeof source.url==='string'&&source.url.startsWith('https://')?`<a href="${esc(source.url)}" target="_blank" rel="noreferrer">${esc(source.title)} ↗</a>`:esc(source.title);
 function requestGate(){
  let generation=0,controller=null;
  const invalidate=()=>{generation++;controller?.abort();};
  return {invalidate,begin(){invalidate();controller=new AbortController();const version=generation;return {signal:controller.signal,current:()=>version===generation};}};
 }
 function renderResult(response){
  const a=response.assessment,s=response.source;
  const source=`<p class="water-source"><span class="data-tag">${esc(s.status.toUpperCase())}${s.stale?' · STALE':''}</span> ${esc(s.source)}<br>Retrieved (UTC): ${esc(s.fetched_at||'Unavailable')}${s.warning?`<br>${esc(s.warning)}`:''}</p>`;
  if(a.status!=='available')return `<div class="notice"><b>Water assessment unavailable</b><p>${esc(a.reason)}</p></div>${source}`;
  const i=a.inputs,summary=a.summary;
  const range=(v,unit,d=0)=>`${num(v.p10,d)}–${num(v.p90,d)} ${unit}`;
  const metric=(title,key,unit,d=0)=>`<div class="water-metric"><span>${title}</span><b>${num(summary[key].median,d)}<small> ${unit}</small></b><small>${range(summary[key],unit,d)}</small></div>`;
  const unknown=i.supply_ml_ha===null;
  const supply=unknown?'<b>Supply not entered</b><p>Enter irrigation supply to estimate the remaining gap. Availability is unassessed.</p>':`<b>${i.irrigation==='rainfed'?'Rainfed · no irrigation supplied':`Supply entered: ${num(i.supply_ml_ha,2)} ML/ha`}</b><p>Remaining shortfall: <strong>${num(summary.remaining_shortfall_mm.median)} mm</strong> median (${range(summary.remaining_shortfall_mm,'mm')}).</p><p>${a.seasons_with_shortfall} of 10 past seasons have a modelled gap. This does not predict future risk or confirm suitability.</p>`;
  const highest=Math.max(1,...a.seasons.map(row=>row.net_irrigation_mm));
  const seasonBars=a.seasons.map(row=>`<div class="water-year"><span>${row.year}</span><span class="water-year-track" aria-hidden="true"><i style="width:${Math.max(0,Math.min(100,row.net_irrigation_mm/highest*100))}%"></i></span><b>${num(row.net_irrigation_mm)} mm</b></div>`).join('');
  const table=a.seasons.map(row=>`<tr><th scope="row">${esc(row.start_date)}<br>${esc(row.end_date)}</th><td>${num(row.demand_mm)}</td><td>${num(row.rainfall_mm)}</td><td>${num(row.rain_retained_mm)}</td><td>${num(row.net_irrigation_mm)}</td><td>${num(row.gross_irrigation_ml_ha,2)}</td><td>${num(row.remaining_shortfall_mm)}</td></tr>`).join('');
  return `<div class="water-result-heading"><div><span class="eyebrow">HISTORICAL WATER SCENARIO</span><h3>${esc(a.profile.name)} · ${months[i.sowing_month-1]} sowing</h3></div><span class="water-pilot">${s.stale?'Stale history':'10 past seasons'}</span></div>
   <p class="water-caption">Sown 1 ${months[i.sowing_month-1]} · ${i.stages.reduce((x,y)=>x+y,0)} days · ${a.seasons[0].year}–${a.seasons.at(-1).year} start years. These are historical scenarios, not a forecast.</p>
   ${!a.within_broad_sowing_window?'<div class="notice">Outside this crop’s broad demo sowing window. This water calculation does not establish a suitable sowing date.</div>':''}
   <div class="water-metrics">${metric('Median demand','demand_mm','mm')}${metric('Rain retained','rain_retained_mm','mm')}${metric('Additional net water','net_irrigation_mm','mm')}</div>
   <p class="water-caption">Medians with 10th–90th percentile ranges from ten seasons, not forecast or confidence limits. Separate medians may not add up.</p>
   <div class="water-gross"><div><span>Estimated gross irrigation</span><b>${num(summary.gross_irrigation_ml_ha.median,2)} <small>ML/ha</small></b></div><p>${range(summary.gross_irrigation_ml_ha,'ML/ha',2)} historical range<br>At your ${num(i.efficiency_pct)}% efficiency assumption</p></div>
   <div class="water-supply ${unknown?'water-unassessed':''}">${supply}</div>
   <details class="water-history"><summary>How the seasons vary</summary><p class="water-caption">Additional net water before irrigation supply; each bar is one historical growing season.</p>${seasonBars}<div class="water-table-wrap" tabindex="0" role="region" aria-label="Historical water values, scroll horizontally"><table><caption>Season dates and water totals. All columns are mm except gross irrigation (ML/ha). A dash means unassessed.</caption><thead><tr><th scope="col">Start / end</th><th scope="col">Demand</th><th scope="col">Rain</th><th scope="col">Retained</th><th scope="col">Net need</th><th scope="col">Gross ML/ha</th><th scope="col">Remaining</th></tr></thead><tbody>${table}</tbody></table></div></details>
   <details class="water-method"><summary>Assumptions, method & sources</summary><p><b>Soil water buffer:</b> ${num(i.soil_buffer_mm)} mm; starting water ${num(i.starting_water_mm)} mm. These are scenario inputs for readily available storage before stress, not measured soil moisture or total plant-available capacity. They are not derived from SLGA.</p><p>Rain infiltration ${num(i.rain_capture_pct)}%; irrigation efficiency ${num(i.efficiency_pct)}%. Growth stages ${i.stages.join(' / ')} days. Kc initial / mid / end: ${a.profile.kc.map(v=>num(v,2)).join(' / ')}.</p><p>${esc(a.profile.coefficient_note)} ${esc(a.profile.timing_note)}</p><p>Daily demand = reference evapotranspiration × crop coefficient. Rain fills the entered buffer up to capacity, then daily demand draws it down. Shortfalls accumulate when demand exceeds that store; later rain cannot erase an earlier gap. Gross irrigation = net shortfall ÷ efficiency; 100 mm = 1 ML/ha.</p><p>This simplified balance assumes fixed usable storage and immediate water delivery. It does not model root growth, stress response, crop failure, capillary rise, salinity, waterlogging or irrigation timing constraints. Rain retained can include water left in storage at harvest. Wheat and barley share generic coefficients and timing, so identical inputs produce identical water estimates.</p><p>All three crops can be compared here even if absent from your shortlist. The crop scores and NSW checks remain separate. Soil tests, cultivar timing and actual water access still need local review.</p>${a.sources.map(source=>`<p>${link(source)}</p>`).join('')}${s.grid?`<p>Weather grid returned: ${num(s.grid.latitude,3)}, ${num(s.grid.longitude,3)}. ERA5 reanalysis is modelled weather, not a paddock weather station.</p>`:''}${source}</details>
   <p class="water-caption">Indicative only. Check with a local agronomist.</p>`;
 }
 function mount(metadata,api){
  const $=id=>document.getElementById(id),profiles=metadata.profiles,defaults=metadata.defaults;
  const gate=requestGate();let context=null,lastPoint=null;
  const field=(id,label,value,min,max,step=1)=>`<label for="wf-${id}">${label}<input id="wf-${id}" type="number" min="${min}" max="${max}" step="${step}" value="${value}" required></label>`;
  $('water-form-host').innerHTML=`<form id="water-form"><div class="water-fields water-primary-fields"><label for="wf-crop">Crop<select id="wf-crop">${Object.entries(profiles).map(([id,p])=>`<option value="${esc(id)}">${esc(p.name)}</option>`).join('')}</select></label><label for="wf-month">Sowing month<select id="wf-month">${months.map((name,n)=>`<option value="${n+1}" ${n===4?'selected':''}>${name}</option>`).join('')}</select></label></div>
   <p class="water-caption">Assumes sowing on day 1 of the month in each past year.</p>
   <div id="water-supply-entry"><label for="wf-supply">Available irrigation · ML/ha<input id="wf-supply" type="number" min="0" max="30" step="0.01" placeholder="Unknown — optional" aria-describedby="water-supply-help"></label><p id="water-supply-help" class="water-caption">Seasonal gross supply: total ML ÷ irrigated hectares. Blank = unknown; 0 = none.</p></div>
   <p id="water-mode-note" class="water-caption"></p>
   <details class="water-assumptions"><summary>Edit scenario assumptions <span id="water-assumption-brief"></span></summary><p class="water-caption">Illustrative defaults, not measurements. Replace with farm or adviser estimates.</p><div class="water-fields">
    ${field('buffer','Soil water buffer · mm',defaults.soil_buffer_mm,1,400)}${field('starting','Water at sowing · mm',defaults.starting_water_mm,0,400)}${field('capture','Rain infiltration · %',defaults.rain_capture_pct,0,100)}${field('efficiency','Irrigation efficiency · %',defaults.efficiency_pct,10,100)}</div>
   <p class="water-caption">Buffer means readily available root-zone storage before stress, not total plant-available water. Starting water cannot exceed the buffer.</p><h4>Growth stages · days</h4><div class="water-fields water-stage-fields">${['Initial','Development','Mid-season','Late-season'].map((label,n)=>field(`stage-${n}`,label,profiles.wheat.stages[n],5,180)).join('')}</div><p id="water-timing-note" class="water-caption"></p><button type="button" id="water-reset" class="text-button">Reset illustrative assumptions</button></details>
   <p class="water-caption water-default-note">Uses illustrative soil, rain and timing assumptions. Scenario only; not an irrigation prescription.</p><div class="water-actions"><button type="submit" class="primary" id="water-calculate" disabled>Calculate water scenario</button><span id="water-location" class="water-caption"></span></div></form>`;
  const form=$('water-form');
  // Native validity checks run before submit, including for fields in closed details.
  form.addEventListener('invalid',event=>{
   const details=event.target.closest('details');if(details)details.open=true;
   $('water-status').textContent=event.target.validationMessage;
  },true);
  function summary(){
   $('water-assumption-brief').textContent=`${$('wf-buffer').value||'—'} mm buffer · ${$('wf-starting').value||'—'} mm at sowing`;
   $('water-timing-note').textContent=profiles[$('wf-crop').value].timing_note;
  }
  function invalidate(message='Inputs changed. Recalculate to update.'){
   gate.invalidate();$('water-results').replaceChildren();$('water-status').textContent=message;
   $('water-calculate').disabled=!context;$('water-calculate').textContent='Calculate water scenario';
  }
  function stages(){profiles[$('wf-crop').value].stages.forEach((days,n)=>{$(`wf-stage-${n}`).value=days;});summary();}
  function reset(){
   for(const [id,key] of [['buffer','soil_buffer_mm'],['starting','starting_water_mm'],['capture','rain_capture_pct'],['efficiency','efficiency_pct']])$(`wf-${id}`).value=defaults[key];
   $('wf-supply').value='';$('wf-starting').setCustomValidity('');stages();
  }
  form.addEventListener('input',()=>{ $('wf-starting').setCustomValidity('');invalidate();summary(); });
  $('wf-crop').addEventListener('change',stages);
  $('water-reset').onclick=()=>{reset();invalidate('Illustrative assumptions restored. Calculate to compare.');};
  form.addEventListener('submit',async event=>{
   event.preventDefault();if(!context)return;
   $('wf-starting').setCustomValidity(Number($('wf-starting').value)>Number($('wf-buffer').value)?'Starting water cannot exceed the soil water buffer.':'');
   if(!form.reportValidity())return;
   const value=id=>$(`wf-${id}`).value===''?null:Number($(`wf-${id}`).value);
   const payload={lat:context.lat,lon:context.lon,cache_only:context.cache_only,irrigation:context.irrigation,
    crop_id:$('wf-crop').value,sowing_month:value('month'),stages:[0,1,2,3].map(n=>value(`stage-${n}`)),
    soil_buffer_mm:value('buffer'),starting_water_mm:value('starting'),rain_capture_pct:value('capture'),efficiency_pct:value('efficiency'),
    supply_ml_ha:context.irrigation==='rainfed'?0:value('supply')};
   const request=gate.begin();$('water-results').replaceChildren();$('water-status').textContent='Comparing ten complete growing seasons…';
   $('water-calculate').disabled=true;$('water-calculate').textContent='Calculating…';
   const timeout=setTimeout(()=>{if(request.current())invalidate('The water request timed out. Try cached data or calculate again.');},60000);
   try{const response=await api('/api/water',payload,request.signal);if(!request.current())return;
    $('water-results').innerHTML=renderResult(response);$('water-status').textContent=response.assessment.status==='available'?'Water scenario ready. Crop scores are unchanged.':'Water history is unavailable; no estimate substituted.';
   }catch(error){if(request.current())$('water-status').textContent=error.message==='Failed to fetch'?'Could not reach FarmLens. Check the local server and try again.':error.message;}
   finally{clearTimeout(timeout);if(request.current()){$('water-calculate').disabled=!context;$('water-calculate').textContent='Calculate water scenario';}}
  });
  summary();
  return {setContext(next){
   context=next;invalidate(next?'Choose a crop and review the assumptions, then calculate.':'Select a valid NSW point to calculate a water scenario.');
   if(!next){$('water-location').textContent='';return;}
   const point=`${next.lat},${next.lon}`;
   if(lastPoint!==null&&lastPoint!==point){reset();$('water-status').textContent='New location: land-specific water assumptions have been reset.';}
   lastPoint=point;
   if(next.mode==='season')$('wf-month').value=next.month;
   $('wf-supply').disabled=next.irrigation==='rainfed';$('water-supply-entry').hidden=next.irrigation==='rainfed';
   $('water-mode-note').textContent=next.irrigation==='rainfed'?'Rainfed: no irrigation supplied. Estimates any additional water gap.':'Irrigated: confirm supply and delivery reliability locally.';
   $('water-location').textContent=`${next.name}${next.cache_only?' · cached data only':''}`;
  }};
 }
 const api={renderResult,requestGate,mount};
 if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.FarmLensWater=api;
})(typeof globalThis!=='undefined'?globalThis:this);
