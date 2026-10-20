/* Point-scale satellite context, separate from suitability and crop yield. */
(function(root){
 'use strict';
 const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const factors=[['green_pct','Green vegetation','green'],['dry_pct','Dry vegetation','dry'],['bare_pct','Bare ground','bare']];
 const valid=s=>s?.status==='available'&&/^\d{4}-\d{2}-\d{2}$/.test(s.date)&&factors.every(([k])=>typeof s[k]==='number'&&Number.isFinite(s[k])&&s[k]>=0&&s[k]<=100);
 const fmt=v=>Number.isFinite(v)?v.toLocaleString('en-AU',{maximumFractionDigits:1}):'—';
 function render(source){
  if(source?.status==='loading')return '<p class="insight-empty" role="status">Checking dated satellite samples and cloud flags…</p>';
  const samples=source?.data?.samples||[],usable=samples.filter(valid),last=usable.at(-1);
  const warning=source?.warning?`<p class="insight-caption">${esc(source.warning)}</p>`:'';
  if(!last)return `<p class="insight-empty">No usable vegetation samples. Try refreshing data or a cached preset.</p>${warning}<p class="insight-caption">No regional estimate substituted.</p>`;
  const bars=factors.map(([k,label,tone])=>`<div class="cover-measure"><span><i class="cover-dot ${tone}"></i>${label}</span><div class="cover-track" aria-hidden="true"><i class="${tone}" style="width:${last[k]}%"></i></div><b>${fmt(last[k])}%</b></div>`).join('');
  const width=560,left=30,right=530,top=18,bottom=116;
  const firstDate=Date.parse(samples[0].date),duration=Math.max(1,Date.parse(samples.at(-1).date)-firstDate);
  const x=s=>left+(Date.parse(s.date)-firstDate)/duration*(right-left),y=n=>bottom-n/100*(bottom-top);
  const lines=factors.map(([k,,tone],series)=>{
   let segments=[],current=[];
   samples.forEach(s=>{if(valid(s))current.push(s);else{if(current.length)segments.push(current);current=[];}});if(current.length)segments.push(current);
   return `<g class="trend-${tone}">${segments.filter(segment=>segment.length>1).map(segment=>`<polyline points="${segment.map(s=>`${x(s)},${y(s[k])}`).join(' ')}" ${series?`stroke-dasharray="${series===1?'5 4':'2 3'}"`:''}/>`).join('')}${usable.map(s=>`<circle cx="${x(s)}" cy="${y(s[k])}" r="3"/>`).join('')}</g>`;
  }).join('');
  const trend=samples.length>1?`<figure class="cover-trend"><figcaption>Sampled observations <span>0–100% cover</span></figcaption><svg viewBox="0 0 ${width} 145" role="img" aria-label="Green, dry and bare cover through time. Gaps are unassessed; exact values in the table."><text x="2" y="22">100</text><text x="12" y="119">0</text><path class="cover-axis" d="M30 18H530M30 116H530"/>${lines}<text x="30" y="140">${esc(samples[0].date)}</text><text x="530" y="140" text-anchor="end">${esc(samples.at(-1).date)}</text></svg></figure>`:'';
  const rows=samples.map(s=>`<tr><th scope="row">${esc(s.date)}</th>${factors.map(([k])=>`<td>${valid(s)?fmt(s[k])+'%':'—'}</td>`).join('')}<td>${valid(s)?'Clear / dry':'Gap · '+esc(s.reason||'Invalid observation')}</td></tr>`).join('');
  return `<div class="vegetation-meta"><span>Latest usable sample · <b>${esc(last.date)}</b></span><span class="data-tag">${source.stale?'Saved · stale':source.status==='offline'?'Partial':source.status==='cached'?'Cached':'Live'} · 30 m pixel</span></div>${bars}${trend}<p class="insight-caption">${usable.length} of ${samples.length} sampled dates usable. Vegetation includes tree canopy; this is not a soil-health or crop-yield score.</p><details class="insight-details"><summary>Values, quality & sources</summary><p>Up to 12 monthly samples: the last available scene in each month. Cloud, shadow, water and missing quality flags leave gaps; clearer scenes earlier in the month may exist. Lines connect usable neighbouring samples only.</p><p>Separate cover estimates are not normalised to 100%. Dry vegetation includes branches and litter; bare ground includes rock. Observation dates use DEA local solar days. Pixel estimates do not describe an entire farm.</p><p>Latest sample unmixing error: ${fmt(last.unmixing_error)}. Cloud/water flags filter observations; other model uncertainty remains. Catalogue checked through ${esc(source.data.as_of)}.</p><div class="insight-table-wrap"><table><caption>Observed cover percentages</caption><thead><tr><th>Date</th><th>Green</th><th>Dry</th><th>Bare</th><th>Quality</th></tr></thead><tbody>${rows}</tbody></table></div><p><a href="https://knowledge.dea.ga.gov.au/data/product/dea-fractional-cover-landsat/" target="_blank" rel="noreferrer">DEA Fractional Cover · CC BY 4.0 ↗</a> · <a href="https://knowledge.dea.ga.gov.au/notebooks/DEA_products/DEA_Fractional_Cover/" target="_blank" rel="noreferrer">Quality-mask method ↗</a></p>${warning}</details>`;
 }
 function createLoader(api,onUpdate){
  let version=0,key=null,controller=null,timer=null;
  function cancel(){version++;controller?.abort();clearTimeout(timer);key=null;}
  function select(point,{refresh=false}={}){
   const next=JSON.stringify([point.lat,point.lon,!!point.cache_only]);if(next===key&&!refresh)return;
   cancel();key=next;const current=version;controller=new AbortController();onUpdate({status:'loading'});
   timer=setTimeout(()=>{if(current===version){cancel();onUpdate({status:'offline',data:{samples:[]},warning:'Satellite request timed out. Try cached data or refresh.'});}},70000);
   api('/api/vegetation',{lat:point.lat,lon:point.lon,cache_only:!!point.cache_only,refresh},controller.signal)
    .then(r=>{if(current===version){clearTimeout(timer);onUpdate(r);}})
    .catch(()=>{if(current===version){clearTimeout(timer);key=null;onUpdate({status:'offline',data:{samples:[]},warning:'Vegetation data could not be loaded.'});}});
  }
  return {select,cancel};
 }
 function mount(api){
  const panel=document.getElementById('vegetation-panel'),output=document.getElementById('vegetation-results');let context=null;
  const loader=createLoader(api,r=>{output.innerHTML=render(r);});
  const load=(refresh=false)=>{if(context&&panel.open)loader.select(context,{refresh});};
  panel.addEventListener('toggle',()=>load());
  document.getElementById('vegetation-refresh').onclick=()=>load(true);
  return {setContext(next){context=next;if(!next){loader.cancel();output.innerHTML='<p class="insight-empty">Select a valid NSW point to view vegetation cover.</p>';return;}load();}};
 }
 const api={render,createLoader,mount};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.FarmLensVegetation=api;
})(typeof globalThis!=='undefined'?globalThis:this);
