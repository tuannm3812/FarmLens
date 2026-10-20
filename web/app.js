'use strict';
const $ = id => document.getElementById(id);
const paths={budget:'<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 7h8M8 11h2m4 0h2M8 15h2m4 0h2M8 18h2m4 0h2"/>',land:'<path d="M3 19 12 3l9 16H3Zm4 0 5-9 5 9m-7 0 2-4 2 4"/>',pin:'<path d="M19 10c0 5-7 11-7 11S5 15 5 10a7 7 0 1 1 14 0Z"/><circle cx="12" cy="10" r="2.5"/>',search:'<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>',arrow:'<path d="M4 12h16m-6-6 6 6-6 6"/>',expand:'<path d="M8 3H3v5m13-5h5v5M3 16v5h5m13-5v5h-5"/>',refresh:'<path d="M20 8a8 8 0 1 0 0 8M20 3v5h-5"/>',soil:'<path d="m3 7 9-4 9 4-9 4-9-4Zm0 5 9 4 9-4M3 17l9 4 9-4"/>',rain:'<path d="M6 14a4 4 0 1 1 0-8 6 6 0 0 1 11-1 4.5 4.5 0 0 1 1 9M8 17l-1 3m6-3-1 3m6-3-1 3"/>',temp:'<path d="M9 14V5a3 3 0 0 1 6 0v9a5 5 0 1 1-6 0ZM12 8v10"/>',crop:'<path d="M12 22V5m0 7C7 12 4 9 4 5c5 0 8 3 8 7Zm0 6c5 0 8-3 8-7-5 0-8 3-8 7Zm0-11c4 0 6-2 6-6-4 0-6 2-6 6Z"/>',book:'<path d="M12 6v15M3 3l9 3 9-3v15l-9 3-9-3V3Z"/>',info:'<circle cx="12" cy="12" r="9"/><path d="M12 11v6m0-10v.5"/>',close:'<path d="m6 6 12 12M6 18 18 6"/>',compare:'<path d="M12 3 21 9l-3 11H6L3 9l9-6Zm0 0v17M3 9l15 11M21 9 6 20"/>',spark:'<path d="m12 3 2.5 6.5L21 12l-6.5 2.5L12 21l-2.5-6.5L3 12l6.5-2.5L12 3Z"/>',chevron:'<path d="m6 9 6 6 6-6"/>'};
function icon(name,extra=''){return `<svg class="${extra}" viewBox="0 0 24 24" aria-hidden="true">${paths[name]||paths.info}</svg>`;}
document.querySelectorAll('[data-icon]').forEach(el=>el.innerHTML=icon(el.dataset.icon));
const escapeHTML=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const number=(value,d=1)=>typeof value==='number'&&Number.isFinite(value)?value.toLocaleString('en-AU',{maximumFractionDigits:d,minimumFractionDigits:d}):'—';
const ui=FarmLensPresentation;
const names={temperature:'Temperature',rainfall:'Rainfall',ph:'Soil pH',frost:'Frost proxy',fire:'Fire exposure',texture:'Texture fit',carbon:'Organic carbon'};
const state={point:{name:'Dubbo',lat:-32.2569,lon:148.6011},pointValid:null,mode:'explore',version:0,response:null,controller:null,assets:{}};
let map=null,marker=null,waterPlanner=null,budgetPlanner=null,vegetationPanel=null,imageryPanel=null,companion=null;
let searchVersion=0,searchController=null;
let coverSource=null;
const overviewUI=FarmLensOverview;
function renderLand(){
 $('land-snapshot').innerHTML=overviewUI.land(state.response?.data.soil,coverSource);
}
const coverLoader=overviewUI.createCoverLoader(api,result=>{coverSource=result;renderLand();});
const monthNames=['January','February','March','April','May','June','July','August','September','October','November','December'];
$('month').innerHTML=monthNames.map((n,i)=>`<option value="${i+1}" ${i===4?'selected':''}>${n}</option>`).join('');
function scenario(extra={}){return {lat:state.point.lat,lon:state.point.lon,mode:state.mode,month:Number($('month').value),irrigation:$('water').value,category:$('category').value||null,drainage:$('drainage').value,cache_only:$('cache-only').checked,...extra};}
async function api(path,payload,signal){const response=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload),signal});const body=await response.json();if(!response.ok){const error=new Error(body.error||'Unable to complete this request');error.status=response.status;throw error;}return body;}
const placeResolver=FarmLensLocation.createResolver(api,label=>{
 state.point.name=label.name||'Selected NSW point';state.point.labelNote=label.note;updateSelection();
 if(state.response&&$('budget-location'))$('budget-location').textContent=state.point.name;
 if(state.response&&$('water-location'))$('water-location').textContent=`${state.point.name}${$('cache-only').checked?' · cached data only':''}`;
});
function status(text,error=false,loading=false){$('status').textContent=text;$('status').className='status'+(error?' error':'')+(loading?' loading':'');}
function selectTab(evidence){$('shortlist-view').hidden=evidence;$('evidence-view').hidden=!evidence;$('shortlist-tab').setAttribute('aria-selected',String(!evidence));$('evidence-tab').setAttribute('aria-selected',String(evidence));$('shortlist-tab').tabIndex=evidence?-1:0;$('evidence-tab').tabIndex=evidence?0:-1;}
$('shortlist-tab').onclick=()=>selectTab(false);$('evidence-tab').onclick=()=>selectTab(true);
document.querySelectorAll('[role=tab]').forEach(button=>button.onkeydown=e=>{if(['ArrowRight','ArrowLeft','Home','End'].includes(e.key)){e.preventDefault();const show=e.key==='Home'?false:e.key==='End'?true:button.id==='shortlist-tab';selectTab(show);$(show?'evidence-tab':'shortlist-tab').focus();}});
$('method-button').onclick=()=>$('method').showModal();$('close-method').onclick=()=>$('method').close();
$('method').onclick=e=>{if(e.target===$('method')){const r=$('method').getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)$('method').close();}};
function mapPin(){if(!map)return;if(marker){marker.remove();marker=null;}if(state.pointValid===false)return;marker=L.marker([state.point.lat,state.point.lon],{icon:L.divIcon({className:'',html:`<div class="map-marker">${icon('pin')}</div>`,iconSize:[38,38],iconAnchor:[19,19]}),title:state.point.name}).addTo(map);}
function updateSelection(){
 $('location-name').textContent=state.pointValid===false?'Choose a NSW land point':state.point.name;
 $('location-name').title=state.point.name;
 $('report-location').textContent=state.pointValid===false?'Choose a NSW land point':state.point.name;
 $('report-location').title=state.point.name;
 $('coordinates').textContent=`${number(state.point.lat,4)}, ${number(state.point.lon,4)}${state.pointValid===false?' · rejected':''}`;
 const note=state.pointValid===false?'':state.point.labelNote||'';
 $('location-note').textContent=note;$('location-note').hidden=!note;
 $('report-subtitle').textContent=state.point.lookupName&&state.pointValid!==false?`${number(state.point.lat,4)}, ${number(state.point.lon,4)} · ${note||'Selected map point.'}`:'Climate, soil and crop fit.';
 document.querySelectorAll('[data-preset]').forEach(b=>b.classList.toggle('active',b.dataset.preset===state.point.name));
 mapPin();
}
function clearSearch(){searchVersion++;searchController?.abort();$('search-results').hidden=true;$('search-results').replaceChildren();$('search-status').textContent='';}
function selectPoint(point,zoom){
 clearSearch();placeResolver.cancel();const changed=point.lat!==state.point.lat||point.lon!==state.point.lon;state.point={...point};state.pointValid=null;if(changed)$('drainage').value='unknown';updateSelection();
 if(point.lookupName)placeResolver.select(point,$('cache-only').checked);
 if(map&&zoom)map.setView([point.lat,point.lon],zoom);if(matchMedia('(max-width:900px)').matches){setMapCollapsed(true);$('report').focus({preventScroll:true});}analyze();
}
$('address').oninput=clearSearch;
function fitNSW(){if(map)map.fitBounds([[-37.6,140.9],[-28.1,153.7]],{padding:[20,20]});}
$('reset-map').onclick=fitNSW;
function metric(label,value,ico,context=""){return `<div class="mini-metric"><span>${icon(ico)}${label}</span><b>${value}</b><small class="metric-context">${escapeHTML(context)}</small></div>`;}
function sourceStatus(source){return source.status.toUpperCase()+(source.stale?' · STALE':'');}
function localChecks(crop){
 const guidance=crop.guidance;
 if(!guidance)return '<p class="scenario-help">Local agronomic checks remain unassessed. This screen is not NSW validation.</p>';
 const labels={met:'Check met · not validation',not_assessed:'Not assessed',conflict:'Conflict'};
 return `<p>${escapeHTML(guidance.summary)}</p><ul class="local-checks">${guidance.checks.map(check=>`<li><b>${labels[check.status]||'Not assessed'}</b> · ${escapeHTML(check.message)}<br><a href="${escapeHTML(check.source_url)}" target="_blank" rel="noreferrer">${escapeHTML(check.source_title)} ↗</a></li>`).join('')}</ul><p class="scenario-help">Meeting one check does not validate the crop or this location.</p>`;
}
function updateScenarioSummary(){
 const mode=state.mode==='season'?`Plant in ${monthNames[Number($('month').value)-1]}`:'Explore';
 const water=$('water').value==='rainfed'?'Rainfed':'Irrigation unverified';
 const category=state.mode==='season'?'Annual crops':$('category').selectedOptions[0].textContent;
 const drainage={unknown:'Drainage unknown',well_drained:'Reported well drained',poorly_drained:'Reported poor drainage'}[$('drainage').value];
 $('scenario-summary').textContent=[mode,water,category,drainage].join(' · ');
 $('water-help').textContent=$('water').value==='rainfed'?'Rainfed uses rainfall only. The water planner estimates seasonal shortfalls separately.':'Irrigation is your scenario input; supply is unverified. Compare an allocation in the water planner. Rainfall scores use annual totals.';
}
function setMapCollapsed(value){
 document.querySelector('.workspace').classList.toggle('map-collapsed',value);
 $('map-toggle').setAttribute('aria-expanded',String(!value));
 $('map-toggle').children[1].textContent=value?'Show map & search':'Hide map & search';
 if(!value&&map)requestAnimationFrame(()=>map.invalidateSize());
}
$('map-toggle').onclick=()=>setMapCollapsed($('map-toggle').getAttribute('aria-expanded')==='true');
$('close-crop').onclick=()=>$('crop-detail').close();
$('crop-detail').addEventListener('close',()=>{state.detailCropId=null;});
function cropReason(crop){
 const assessed=Object.entries(crop.subscores).filter(([,v])=>v!=null).sort((a,b)=>b[1]-a[1]);
 if(crop.zero_capped)return 'An assessed factor scores zero.';
 if(!assessed.length)return 'Too little evidence to assess.';
 const [key,value]=assessed[0];return value===100?`${names[key]}: within the broad preferred range.`:`Strongest factor: ${names[key].toLowerCase()} (${number(value,0)}/100).`;
}
function renderCropCards(r){
 $('crops').innerHTML=r.top_three.map(crop=>{
  const score=ui.scoreState(crop),weak=crop.subscores[crop.weakest_factor];
  const reason=crop.zero_capped?'Zero-factor cap · maximum 20/100':weak===100?'All assessed factors score 100':`Weakest: ${names[crop.weakest_factor]} · ${number(weak,0)}/100`;
  return `<button type="button" class="crop-card" data-crop="${escapeHTML(crop.id)}" aria-haspopup="dialog" aria-label="View ${escapeHTML(crop.name)} details" aria-describedby="crop-summary-${escapeHTML(crop.id)} crop-score-${escapeHTML(crop.id)}"><span class="crop-icon">${ui.cropIcon(crop.id)}</span><span class="crop-title" id="crop-summary-${escapeHTML(crop.id)}"><b>${escapeHTML(crop.name)}</b>${ui.tags(crop)}<span class="crop-reason">${escapeHTML(cropReason(crop))}</span><span class="crop-risk ${weak===100?'all-preferred':''}">${escapeHTML(reason)}</span></span><span class="crop-score score-${score.tone}" id="crop-score-${escapeHTML(crop.id)}">${number(crop.total,0)}<small>Screening / 100</small><span class="score-label">${score.label}</span></span>${icon('chevron','chevron')}</button>`;
 }).join('');
 $('crops').querySelectorAll('[data-crop]').forEach(button=>button.onclick=()=>openCrop(button.dataset.crop));
 if(r.guidance_excluded?.length){const button=document.createElement('button');button.className='guidance-link';button.textContent=`${r.guidance_excluded.length} withheld by NSW checks · View reasons`;button.onclick=()=>{selectTab(true);$('evidence-tab').focus();const details=$('evidence').querySelector('[data-exclusions]');if(details){details.open=true;details.scrollIntoView({block:'start',behavior:'auto'});}};$('crops').append(button);}
}
function explanationMarkup(crop){
 const explanation=state.explanation,row=explanation?.entries.find(e=>e.id===crop.id);
 if(!row)return '';
 return `<section class="explanation-card"><h3>Why this candidate?</h3><p>${escapeHTML(row.why)}</p><p><b>Watch:</b> ${escapeHTML(row.risk)}</p><p class="scenario-help">${escapeHTML(explanation.source)} · ${escapeHTML(explanation.notice)}</p>${row.local_cautions?.length?`<div class="local-cautions"><b>Local checks</b><ul>${row.local_cautions.map(caution=>`<li>${escapeHTML(typeof caution==='string'?caution:caution.message)}</li>`).join('')}</ul></div>`:''}<p>${escapeHTML(explanation.disclaimer)}</p></section>`;
}
function openCrop(id){
 const crop=state.response?.result.top_three.find(c=>c.id===id);if(!crop)return;
 state.detailCropId=id;renderCropDetail(crop);if(!$('crop-detail').open)$('crop-detail').showModal();
}
function renderCropDetail(crop){
 const s=state.response.data.soil.data,sub=crop.subscores,ctx=crop.soil_context,weak=crop.weakest_factor,score=ui.scoreState(crop);
 const textureName={light:'Sandy / light',medium:'Medium',heavy:'Clay-rich',organic:'Organic'}[ctx?.group]||'Unassessed';
 const texture=sub.texture==null?'Texture fit unassessed.':sub.texture===100?'Within the broad texture preference.':sub.texture===70?'Within the listed tolerance.':'Outside the listed texture preferences.';
 const weakText=crop.zero_capped?`${names[weak]} reaches an absolute proxy limit (0/100), capping the total at 20.`:sub[weak]===100?'All assessed factors score 100. Local constraints still need checking.':`${names[weak]} is the weakest assessed factor (${number(sub[weak],0)}/100).`;
 const factors=Object.entries(sub).map(([key,value])=>{
  const factor=ui.factorState(value,key),lowest=key===weak&&value<100;
  return `<div class="factor-row factor-${factor.tone}${lowest?' is-weakest':''}"><div class="factor-name"><span>${names[key]}</span><small>${lowest?'Weakest · ':''}${factor.label}</small></div><div class="bar" aria-hidden="true"><i style="width:${value??0}%"></i></div><strong>${value==null?'Unassessed':number(value,0)}</strong></div>`;
 }).join('');
 $('crop-detail-content').innerHTML=`<div class="detail-heading"><span class="crop-icon">${ui.cropIcon(crop.id)}</span><div><h2 id="detail-title">${escapeHTML(crop.name)}</h2>${ui.tags(crop)}</div></div>${ui.photoMarkup(crop,state.assets[crop.id])}<div class="detail-fit"><div><span class="eyebrow">CLIMATE & SOIL FIT</span><p>${escapeHTML(cropReason(crop))}</p><span class="detail-badge">Local checks required</span></div><div class="crop-score score-${score.tone}">${number(crop.total,0)}<small>Screening / 100</small><span class="score-label">${score.label}</span></div></div><p class="screening-context">Modelled climate and soil fit. No prediction of yield or success.</p>${explanationMarkup(crop)}<div class="risk"><b>What to watch</b>${escapeHTML(weakText)}${sub.fire==null?' Fire exposure remains unassessed.':''}</div><div class="soil-fit-grid"><section><span class="eyebrow">SOIL TEXTURE</span><h3>${textureName}</h3><span class="data-tag">Modelled · 0–30 cm</span><p>${texture}</p><small>Texture alone does not confirm drainage.</small></section><section><span class="eyebrow">ORGANIC CARBON</span><h3>${number(s.soc_g_kg==null?null:s.soc_g_kg/10,2)}<small>%</small></h3><span class="data-tag">Modelled · 0–30 cm</span><p>Soil condition indicator; nutrients unassessed.</p></section></div><details class="soil-calculation"><summary>How soil affects this score</summary><p>Sand ${number(s.sand_pct)}% · clay ${number(s.clay_pct)}%. Texture uses a broad light / medium / heavy grouping, not a full texture classification.</p><p>Carbon contributes ${number(state.response.weights.carbon*100,0)}% of the configured weight. Its ${sub.carbon==null?'unassessed':number(sub.carbon,0)+'/100'} factor uses an experimental shared curve; it is not a crop-specific fertility grade or target.</p></details><h3>Factor scores</h3><p class="factor-intro">0–100 per factor · weighted total.</p>${factors}<p class="crop-notes">${escapeHTML(crop.notes)}</p><details class="guidance"><summary>NSW checks & sources</summary>${localChecks(crop)}</details><div class="crop-foot"><span>${number(crop.assessed_weight_pct,0)}% of weights assessed</span><a href="${escapeHTML(crop.source_url)}" target="_blank" rel="noreferrer">Crop requirements ↗</a></div>${crop.season_context?`<p class="scenario-help">Historical growing months: ${crop.season_context.months.map(m=>monthNames[m-1]).join(', ')}.<br>${number(crop.season_context.temperature_c)}°C · ${number(crop.season_context.rainfall_mm,0)} mm · ${number(crop.season_context.frost_days)} frost days per growing period, averaged across years. Annual rainfall remains the rainfall score input.</p>`:''}<p class="scenario-help">Modelled water pH, 0–30 cm; not a calcium-chloride soil test. Indicative only. Check with a local agronomist.</p>`;
 const photo=$('crop-detail-content').querySelector('[data-crop-photo]');
 if(photo){const fail=()=>{photo.hidden=true;photo.parentElement.querySelector('.photo-fallback').hidden=false;};photo.addEventListener('error',fail,{once:true});if(photo.complete&&!photo.naturalWidth)fail();}
}
function drawComparison(){
 const crops=state.response?.result.top_three||[],selected=Array.from($('comparison-options').querySelectorAll('input:checked')).map(input=>input.value);
 const model=FarmLensComparison.buildComparison(crops,selected);
 $('radar').innerHTML=model.series.length?FarmLensComparison.renderRadar(model,$('radar').clientWidth||450):'<p class="scenario-help">Select a crop to compare.</p>';
 $('comparison-table').innerHTML=model.series.length?`<table><caption>Rounded to one decimal. Unweighted factors; totals use the published weights. Unassessed is not zero.</caption><thead><tr><th scope="col">Factor</th>${model.series.map(s=>`<th scope="col">${escapeHTML(s.name)}</th>`).join('')}</tr></thead><tbody>${model.axes.map(([key,label],i)=>`<tr><th scope="row">${label}</th>${model.series.map(s=>`<td>${s.values[i]==null?'Unassessed':number(s.values[i],1)}</td>`).join('')}</tr>`).join('')}</tbody></table>`:'';
}
function resetComparison(crops){
 $('comparison').hidden=!crops.length;$('comparison-options').innerHTML=crops.map((crop,i)=>`<label><input type="checkbox" value="${escapeHTML(crop.id)}" checked><svg class="series-${i}" viewBox="0 0 25 12" aria-hidden="true"><path d="M1 6h23" stroke="currentColor" stroke-width="2" ${i===1?'stroke-dasharray="6 4"':i===2?'stroke-dasharray="2 4"':''}/></svg>${escapeHTML(crop.name)}</label>`).join('');
 $('comparison-options').querySelectorAll('input').forEach(input=>input.onchange=drawComparison);drawComparison();
}
$('comparison').addEventListener('toggle',()=>{if($('comparison').open)drawComparison();});
new ResizeObserver(()=>{if($('comparison').open)drawComparison();}).observe($('radar'));

$('open-water-panel').onclick=()=>{selectTab(false);$('water-panel').open=true;$('water-panel').scrollIntoView({block:'start',behavior:'auto'});$('wf-crop')?.focus({preventScroll:true});};
function render(data){
 state.response=data;const {result:r}=data,c=data.data.climate.data,s=data.data.soil.data,f=data.data.forecast.data;
 state.pointValid=true;updateSelection();
 imageryPanel?.setContext({...state.point,cache_only:$('cache-only').checked});
 companion?.setContext(data);
 try{const saved=FarmLensNavigation.encode(state.point,scenario());if(saved)sessionStorage.setItem('farmlens.selection.v1',saved);}catch{/* Storage may be disabled; exploration still works. */}
 budgetPlanner?.setContext({...state.point,irrigation:$('water').value});
 vegetationPanel?.setContext({...state.point,cache_only:$('cache-only').checked});
 waterPlanner?.setContext({...state.point,mode:state.mode,month:Number($('month').value),irrigation:$('water').value,cache_only:$('cache-only').checked});
 const provisional=r.evidence_quality.includes('provisional');
 status(s.ph==null?'Soil evidence unavailable. Choose a cached preset or refresh.':`${provisional?'Provisional inputs':'Modelled evidence'} · ${c.period} climate · 0–30 cm soil`,s.ph==null||provisional);
 const climateNotice=data.data.climate.status==='offline'?'<div class="notice">Offline climate estimates · regional demonstration values, not observations at this point.</div>':'';
 const notice=!r.ranked.length?`<div class="empty"><b>No candidates in this scenario.</b><br>${r.guidance_excluded?.length?'Known inputs conflict with local guidance. Review the source-linked exclusions in Data & sources.':'Check soil pH and monthly climate availability, crop filters, or planting month.'}</div>`:!r.has_strong_match?'<div class="notice"><b>No strong match in this scenario.</b><br>Top candidates fall below the screening threshold or reach an absolute limit.</div>':'';
 $('overview').innerHTML=`${climateNotice}${notice}<div class="section-label"><h2>${r.top_three.length} crop candidates</h2><span>Local checks required</span></div>`;
 renderLand();
 $('outlook').innerHTML=overviewUI.weather(data.data.forecast);
 $('seasonal-chart').innerHTML=overviewUI.climate(data.data.climate);
 $('climate-summary').textContent=`${number(c.annual_rainfall_mm,0)} mm/year · ${number(c.annual_temperature_c)}°C mean · ${c.period}`;
 renderCropCards(r);resetComparison(r.top_three);
 $('explain').disabled=false;
 $('method-weights').innerHTML='<div class="weights">'+Object.entries(data.weights).map(([key,value])=>`<span>${names[key]} ${number(value*100,0)}%</span>`).join('')+'</div>';
 const ph=s.properties?.ph,soilRows=Object.entries(s.properties||{}).flatMap(([key,prop])=>prop.depths.map(d=>`<tr><td>${{ph:'pH (water)',clay_pct:'Clay %',sand_pct:'Sand %',soc_g_kg:'Carbon g/kg'}[key]}</td><td>${escapeHTML(d.depth_cm)}</td><td>${number(d.value,2)}</td><td>${number(d.lower,2)}–${number(d.upper,2)}</td></tr>`));
 const warnings=r.warnings.map(w=>`<p>${escapeHTML(w)}</p>`).join('');
 $('evidence').innerHTML=`<div class="evidence-block"><h3>${icon('soil')} Australian soil</h3><span class="badge">${escapeHTML(sourceStatus(data.data.soil))} · SLGA / CSIRO / TERN</span><p>pH (water) ${number(s.ph,2)} · clay ${number(s.clay_pct)}% · sand ${number(s.sand_pct)}%<br>Organic carbon ${number(s.soc_g_kg)} g/kg (${number(s.soc_g_kg==null?null:s.soc_g_kg/10,2)}%).<br>Modelled ~90 m grid, thickness-weighted 0–30 cm. A local soil test may change the shortlist. pH is an arithmetic screening average, not a calcium-chloride result.</p>${ph?.lower!=null?`<p>pH uncertainty envelope: ${number(ph.lower,2)}–${number(ph.upper,2)}. The averaged layer bounds are not a joint confidence interval.</p>`:''}<details><summary>Depth profiles and source records</summary><table><thead><tr><th>Property</th><th>Depth cm</th><th>Value</th><th>Bounds</th></tr></thead><tbody>${soilRows.join('')}</tbody></table>${Object.entries(s.properties||{}).map(([key,p])=>`<p><a href="${escapeHTML(p.service)}" target="_blank" rel="noreferrer">${escapeHTML(key)} source ↗</a><br>${escapeHTML(p.status)}${p.stale?' · STALE':''} · ${escapeHTML(p.fetched_at||'Unavailable')}<br>${escapeHTML(p.warning)}</p>`).join('')}</details></div><div class="evidence-block"><h3>${icon('rain')} Climate & frost</h3><span class="badge">${escapeHTML(sourceStatus(data.data.climate))} · OPEN-METEO</span><p>${c.period} historical reanalysis · ${number(c.annual_rainfall_mm,0)} mm annual rain · ${number(c.annual_temperature_c)}°C mean temperature.<br>Coldest-month mean minimum ${number(c.coldest_month_min_c)}°C. Monthly means can conceal individual frosts.<br>Driest three months: ${number(c.driest_three_months_mm,0)} mm.</p><p>${escapeHTML(data.data.climate.warning)}</p><p>Retrieved (UTC): ${escapeHTML(data.data.climate.fetched_at||'Not retrieved')}</p><a class="source-link" href="https://open-meteo.com/en/docs/historical-weather-api" target="_blank" rel="noreferrer">Open-Meteo methodology ↗</a></div><div class="evidence-block"><h3>${icon('info')} Fire history</h3><p>${escapeHTML(data.data.fire.data.note)}</p><span class="badge">${escapeHTML(sourceStatus(data.data.fire))}</span><p>Retrieved (UTC): ${escapeHTML(data.data.fire.fetched_at||'Not retrieved')}</p></div><div class="evidence-block"><h3>${icon('book')} How to read this report</h3>${warnings}<p>Soil texture and carbon penalties are uncalibrated demo assumptions. The sand/clay grouping is broad; it is not a USDA class. Carbon is a shared condition factor, not crop-specific nutrient sufficiency.</p><details data-exclusions><summary>Excluded by local guidance (${(r.guidance_excluded||[]).length})</summary>${(r.guidance_excluded||[]).map(crop=>`<article class="guidance-exclusion"><h4>${escapeHTML(crop.name)} · local conflict</h4><p>${escapeHTML(crop.notes)}</p>${localChecks(crop)}</article>`).join('')||'<p>No local guidance conflicts identified. Unknown checks still require assessment.</p>'}</details><details><summary>All crop exclusions</summary>${Object.entries(r.excluded).map(([id,reason])=>`<p><b>${escapeHTML(id)}</b>: ${escapeHTML(reason)}</p>`).join('')}</details><p>NSW outline: ABS 2021, CC BY 4.0. Simplified boundary; not a parcel survey.</p></div>`;
}
async function analyze(extra={}){
 imageryPanel?.setContext(null);companion?.setContext(null);
 waterPlanner?.setContext(null);budgetPlanner?.setContext(null);vegetationPanel?.setContext(null);
 updateScenarioSummary();state.explanation=null;state.detailCropId=null;if($('crop-detail').open)$('crop-detail').close();$('comparison').hidden=true;$('outlook').innerHTML='';
 const version=++state.version;state.controller?.abort();state.controller=new AbortController();state.response=null;
 coverLoader.select(scenario(),{refresh:!!extra.refresh});renderLand();
 $('outlook').innerHTML='<div class="overview-card overview-empty">Loading seven-day weather…</div>';$('seasonal-chart').innerHTML='';$('climate-summary').textContent='Loading historical climate…';
 $('explain').disabled=true;$('explanations').innerHTML='';$('overview').innerHTML='';$('evidence').innerHTML='';$('crops').innerHTML='<div class="skeleton"></div><div class="skeleton"></div><div class="skeleton"></div>';
 status(`Checking ${state.point.name}: climate, Australian soil and local crop checks…`,false,true);
 try{const result=await api('/api/analyze',scenario(extra),state.controller.signal);if(version===state.version)render(result);}
 catch(error){if(version!==state.version)return;if(error.status===400&&state.pointValid!==true){state.pointValid=false;updateSelection();}status(error.message,true);$('outlook').innerHTML=overviewUI.weather(null);$('climate-summary').textContent='Historical climate unavailable';$('crops').innerHTML='<div class="empty">The selected location could not be assessed. Select a NSW demo location, enable cached data only, or retry.</div>';}
}
document.querySelectorAll('[data-mode]').forEach(button=>button.onclick=()=>{state.mode=button.dataset.mode;document.querySelectorAll('[data-mode]').forEach(b=>{b.classList.toggle('active',b===button);b.setAttribute('aria-pressed',String(b===button));});$('month-label').hidden=state.mode!=='season';$('season-help').hidden=state.mode!=='season';$('category-label').hidden=state.mode==='season';analyze();});
['water','category','month','cache-only','drainage'].forEach(id=>$(id).onchange=()=>analyze());
$('cache-only').onchange=()=>{if(state.point.lookupName)placeResolver.select(state.point,$('cache-only').checked);analyze();};
$('refresh').onclick=()=>analyze({refresh:true});$('fire').onclick=()=>analyze({load_fire:true});
async function explainShortlist(){
 const version=state.version;if(!state.response)return;$('explain').disabled=true;$('explanations').textContent='Explaining the assessed factors…';
 try{const data=await api('/api/explain',scenario({cache_only:true,fingerprint:state.response.fingerprint}));if(version!==state.version)return;state.explanation=data.explanation;$('explanations').innerHTML='<p class="scenario-help">Explanations are ready in each crop profile. '+escapeHTML(data.explanation.notice)+'</p>';const first=state.detailCropId||data.result.top_three[0]?.id;if(first)openCrop(first);}
 catch(error){if(version===state.version)$('explanations').textContent=(error.message==='Failed to fetch'?'Could not reach FarmLens. Check the local server and try Explain again.':error.message);}
 finally{if(version===state.version)$('explain').disabled=!state.response;}
}
$('explain').onclick=()=>companion?.open();
$('search-form').onsubmit=async event=>{
 event.preventDefault();clearSearch();const query=$('address').value.trim();
 if(query.length<2){$('search-status').textContent='Enter at least two characters.';return;}
 const version=searchVersion;searchController=new AbortController();$('search-results').hidden=false;$('search-results').textContent='Searching Australian places…';$('search-status').textContent='Searching Australian places…';
 try{const result=await api('/api/search',{query},searchController.signal);if(version!==searchVersion)return;const matches=result.data.matches;$('search-results').replaceChildren();
 if(!matches.length){const message=result.warning||'No NSW matches found.';$('search-results').textContent=message;$('search-status').textContent=message;return;}
 $('search-status').textContent=`${matches.length} NSW places found. Choose a result below.`;
 matches.forEach(match=>{const b=document.createElement('button');b.type='button';b.textContent=match.name;b.onclick=()=>selectPoint(match,9);$('search-results').append(b);});
 }catch(error){if(version===searchVersion){$('search-results').textContent=error.message;$('search-status').textContent=error.message;}}
};
async function init(){
 fetch('/assets/crops/manifest.json').then(r=>{if(!r.ok)throw new Error('No photo catalogue');return r.json();}).then(manifest=>{state.assets=manifest.crops||{};if(state.detailCropId){const crop=state.response?.result.top_three.find(c=>c.id===state.detailCropId);if(crop)renderCropDetail(crop);}}).catch(()=>{});
 try{const response=await fetch('/api/bootstrap');if(!response.ok)throw new Error('Backend unavailable');const config=await response.json();
 let saved=null;try{saved=sessionStorage.getItem('farmlens.selection.v1');}catch{}
 const restored=FarmLensNavigation.read(saved,config.presets,location.hash);
 if(restored){state.point=restored.point;state.mode=restored.scenario.mode;const values=restored.scenario;
  $('month').value=values.month;$('water').value=values.irrigation;$('category').value=values.category||'';$('drainage').value=values.drainage;$('cache-only').checked=values.cache_only;
  document.querySelectorAll('[data-mode]').forEach(b=>{b.classList.toggle('active',b.dataset.mode===state.mode);b.setAttribute('aria-pressed',String(b.dataset.mode===state.mode));});
  $('month-label').hidden=state.mode!=='season';$('season-help').hidden=state.mode!=='season';$('category-label').hidden=state.mode==='season';
 }
 if(config.presets.some(p=>'#'+p.name.toLowerCase().replaceAll(' ','-')===location.hash))history.replaceState(null,'','/explore');
 waterPlanner=FarmLensWater.mount(config.water,api);
 budgetPlanner=FarmLensBudget.mount(config.budget,api);
 vegetationPanel=FarmLensVegetation.mount(api);
 imageryPanel=FarmLensImagery.mount(api);
 companion=FarmLensCompanion.mount({onExplain:explainShortlist,onAction:(action,id)=>{
  if(action==='crop'){openCrop(id);return;}
  if(action==='evidence'){selectTab(true);$('evidence-tab').focus();return;}
  selectTab(false);const panel=$(action==='water'?'water-panel':'budget-panel');
  panel.open=true;panel.scrollIntoView({block:'start',behavior:'auto'});panel.querySelector('summary').focus();
 }});
 config.presets.forEach(point=>{const button=document.createElement('button');button.type='button';button.dataset.preset=point.name;button.innerHTML=icon('pin')+escapeHTML(point.name);button.onclick=()=>selectPoint(point,6);$('presets').append(button);});$('fire').hidden=!config.fire_configured;
 if(window.L){map=L.map('map',{zoomControl:false,minZoom:4,maxZoom:17});L.control.zoom({position:'bottomright'}).addTo(map);L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'}).addTo(map);fitNSW();map.on('click',event=>selectPoint({name:'Selected NSW point',lat:event.latlng.lat,lon:event.latlng.lng,lookupName:true}));fetch('/api/boundary').then(r=>r.json()).then(geo=>L.geoJSON(geo,{style:{color:'#3e6a45',weight:1.5,fillColor:'#7c9b60',fillOpacity:.07},interactive:false}).addTo(map)).catch(()=>{$('map-warning').hidden=false;$('map-warning').textContent='Boundary could not load. All points are still checked by the server.';});}
 else{$('map-warning').hidden=false;$('map-warning').textContent='Map library unavailable. Use a preset or address search to explore your land.';}
 updateSelection();await analyze();
 }catch(error){status(error.message,true);$('outlook').innerHTML=overviewUI.weather(null);$('climate-summary').textContent='Historical climate unavailable';$('crops').innerHTML='<div class="empty">Start the Python app with python -m farmlens.web, then reload this page.</div>';}
}
init();
