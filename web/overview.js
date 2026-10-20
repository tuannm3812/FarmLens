/* Dated point context and observed forecast values; never changes crop scores. */
(function(root){
 'use strict';
 const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const finite=v=>typeof v==='number'&&Number.isFinite(v);
 const num=(v,d=0)=>finite(v)?v.toLocaleString('en-AU',{maximumFractionDigits:d,minimumFractionDigits:d}):'—';
 const months=['January','February','March','April','May','June','July','August','September','October','November','December'];
 const sourceLabel=s=>!s?'Loading':s.status==='offline'?'Unavailable':s.stale?'Saved · stale':s.status==='cached'?'Cached':'Live';
 const glyphs={land:'<path d="m3 8 9-5 9 5-9 5-9-5Zm0 5 9 5 9-5M3 18l9 5 9-5"/>',sun:'<circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1 1m12 12 1 1M5 19l1-1M18 6l1-1"/>',cloud:'<path d="M6 18a5 5 0 0 1-1-10 7 7 0 0 1 13-1 5.5 5.5 0 0 1 0 11H6Z"/>',rain:'<path d="M5 14a4 4 0 0 1 0-8 6 6 0 0 1 11-1 4.5 4.5 0 0 1 2 9M7 17l-1 3m6-3-1 3m6-3-1 3"/>',snow:'<path d="M12 2v20M3 7l18 10M3 17 21 7M8 4l4 3 4-3M8 20l4-3 4 3"/>',storm:'<path d="M5 14a4 4 0 0 1 0-8 6 6 0 0 1 11-1 4.5 4.5 0 0 1 2 9M12 12l-3 6h5l-3 5"/>',fog:'<path d="M5 8a4 4 0 0 1 7-4 4 4 0 0 1 6 4M3 12h18M5 16h14M3 20h18"/>',temp:'<path d="M9 14V5a3 3 0 0 1 6 0v9a5 5 0 1 1-6 0ZM12 8v10"/>'};
 const icon=(type,label)=>`<svg viewBox="0 0 24 24" ${label?`role="img" aria-label="${esc(label)}"`:'aria-hidden="true"'}>${glyphs[type]||glyphs.temp}</svg>`;
 function conditions(code){
  if(code===0)return ['sun','Clear sky'];
  if([1,2,3].includes(code))return ['cloud',code===3?'Overcast':'Mainly clear / partly cloudy'];
  if([45,48].includes(code))return ['fog','Fog'];
  if([51,53,55,56,57,61,63,65,66,67,80,81,82].includes(code))return ['rain','Rain / drizzle'];
  if([71,73,75,77,85,86].includes(code))return ['snow','Snow'];
  if([95,96,99].includes(code))return ['storm','Thunderstorm'];
  return ['temp','Conditions unavailable'];
 }
 const landAssets={111:'cultivated',112:'natural',124:'aquatic',215:'built',216:'bare',220:'water'};
 const landIcon=slug=>`<svg class="land-icon" viewBox="0 0 24 24" aria-hidden="true"><use href="/assets/icons/land.svg#${slug}"/></svg>`;
 function land(soil,cover){
  const s=soil?.data||{},c=cover?.data||{};
  const available=['live','cached'].includes(cover?.status)&&Number.isInteger(c.class_code)&&landAssets[c.class_code]&&typeof c.label==='string'&&c.label.trim();
  const asset=available?landAssets[c.class_code]:'unknown';
  const texture=finite(s.clay_pct)&&finite(s.sand_pct)&&s.clay_pct>=0&&s.sand_pct>=0&&s.clay_pct+s.sand_pct<=100?(s.clay_pct>=35?'Clay-rich':s.sand_pct>=65?'Sandy':'Medium'):'Unassessed';
  const title=available?c.label:cover?.status==='loading'||!cover?'Checking land cover…':'Land cover unavailable';
  const coverNote=available?`${c.year} · ${c.resolution_m} m pixel`:'No estimate substituted';
  const caution=available&&[215,220].includes(c.class_code)?'<p class="cover-caution">This pixel maps '+(c.class_code===215?'built surfaces':'water')+'. Check an agricultural point nearby.</p>':'';
  return `<section class="overview-card land-card" aria-labelledby="land-heading">
   <div class="overview-heading"><h2 id="land-heading">Land snapshot</h2><span class="eyebrow">AT YOUR PIN</span></div>
   <div class="cover-row cover-compact"><div class="cover-copy"><h3 class="cover-title">${landIcon(asset)}${esc(title)}</h3><p>${esc(coverNote)}${available?' · DEA · '+esc(sourceLabel(cover)):''}</p></div>
   </div>${caution}
   <dl class="soil-strip"><div><dt>${landIcon('texture')}Soil texture</dt><dd>${texture}</dd></div><div><dt>${landIcon('ph')}pH · water</dt><dd>${num(s.ph,1)}</dd></div><div><dt>${landIcon('carbon')}Organic carbon</dt><dd>${finite(s.soc_g_kg)?num(s.soc_g_kg/10,2)+'%':'—'}</dd></div></dl>
   <details class="overview-note"><summary>Modelled soil · 0–30 cm · ${esc(sourceLabel(soil))}</summary><p><b>Soil:</b> SLGA ~90 m estimates. Texture is a broad grouping; test drainage and fertility locally. Water pH differs from calcium-chloride pH.</p><p><b>Land cover:</b> annual DEA classification, not a farm boundary, current condition or cultivation permission. No effect on crop scores.</p>${cover?.warning?`<p>${esc(cover.warning)}</p>`:''}<a href="https://knowledge.dea.ga.gov.au/data/product/dea-land-cover-landsat/" target="_blank" rel="noreferrer">DEA Land Cover source ↗</a><p><a href="https://maps.dea.ga.gov.au/" target="_blank" rel="noreferrer">Explore DEA satellite maps ↗</a></p></details>
  </section>`;
 }
 function validDays(f){
  const d=f.days;
  return Array.isArray(d)&&d.length===7&&d[0].date===f.start_date&&d[6].date===f.end_date&&d.every((day,i)=>/^\d{4}-\d{2}-\d{2}$/.test(day.date)&&Number.isFinite(Date.parse(day.date))&&(!i||Date.parse(day.date)-Date.parse(d[i-1].date)===86400000)&&finite(day.rainfall_mm)&&day.rainfall_mm>=0&&finite(day.min_temperature_c)&&finite(day.max_temperature_c)&&day.min_temperature_c<=day.max_temperature_c);
 }
 function dateRange(start,end){
  if(!start||!end||!Number.isFinite(Date.parse(start))||!Number.isFinite(Date.parse(end)))return '';
  const a=new Date(start+'T12:00:00Z'),b=new Date(end+'T12:00:00Z');
  const fmt={day:'numeric',month:'short',timeZone:'UTC'};
  return a.getUTCMonth()===b.getUTCMonth()&&a.getUTCFullYear()===b.getUTCFullYear()?`${a.getUTCDate()}–${b.toLocaleDateString('en-AU',{...fmt,year:'numeric'})}`:`${a.toLocaleDateString('en-AU',{...fmt,year:'numeric'})} – ${b.toLocaleDateString('en-AU',{...fmt,year:'numeric'})}`;
 }
 function weather(source){
  const f=source?.data||{},missing=!source||source.status==='offline'||!finite(f.rainfall_mm)||!finite(f.min_temperature_c)||!finite(f.max_temperature_c);
  if(missing)return '<section class="overview-card weather-card"><div class="overview-heading"><h2>Seven-day weather</h2></div><p class="overview-empty">Outlook unavailable. Refresh or choose a cached preset.</p><p class="overview-caption">Crop scores use historical climate.</p></section>';
  const stale=source.stale,cold=f.min_temperature_c<0,hot=f.max_temperature_c>=35;
  const flag=stale?'Refresh before use':cold&&hot?'Frost & heat flags':cold?'Sub-zero forecast':hot?'35°C+ forecast':'No temperature flag';
  const strip=validDays(f)?`<div class="forecast-strip">${f.days.map(day=>{const [type,label]=conditions(day.weather_code),date=new Date(day.date+'T12:00:00Z');return `<div class="forecast-day"><time datetime="${esc(day.date)}" title="${esc(day.date)}">${date.toLocaleDateString('en-AU',{weekday:'short',timeZone:'UTC'})}<small>${date.getUTCDate()}</small></time>${icon(type,label)}<b>${num(day.max_temperature_c)}°</b><span>${num(day.min_temperature_c)}°</span><small class="daily-rain">${num(day.rainfall_mm,1)}<span> mm</span></small></div>`;}).join('')}</div>`:'<p class="overview-empty">Daily detail unavailable.</p>';
  return `<section class="overview-card weather-card${stale?' is-stale':''}" aria-labelledby="weather-heading"><div class="overview-heading"><h2 id="weather-heading">${stale?'Saved outlook':'Seven-day weather'}</h2><span class="data-tag">${esc(sourceLabel(source))}</span></div><div class="weather-summary"><span>${esc(dateRange(f.start_date,f.end_date))}</span><b>${num(f.rainfall_mm)} mm <small>total rain</small></b></div>${strip}<div class="weather-foot"><span class="weather-flag${!stale&&(cold||hot)?' flagged':''}">${esc(flag)}</span><details class="overview-note"><summary>About this forecast</summary><p>${esc(f.start_date)} to ${esc(f.end_date)} · Open-Meteo. ${stale?'Out of date; current temperature flags unassessed.':'Flags: below 0°C or at least 35°C. Risk depends on crop stage and local conditions.'} Thermometer = conditions unavailable. Crop rankings use historical climate.</p>${source.warning?`<p>${esc(source.warning)}</p>`:''}</details></div></section>`;
 }
 function climate(source){
  const c=source?.data||{},m=c.monthly;
  if(source?.status==='offline'||!Array.isArray(m)||m.length!==12||!m.every((v,i)=>v.month===i+1&&finite(v.rainfall_mm)&&v.rainfall_mm>=0&&finite(v.temperature_c)&&Math.abs(v.temperature_c)<=90))return '<div class="overview-empty">Monthly climate unavailable. No seasonal curve is estimated.</div>';
  const width=600,start=36,step=47,base=105,top=25;
  const rainMax=Math.max(10,Math.ceil(Math.max(...m.map(v=>v.rainfall_mm))/10)*10);
  const tempMin=Math.floor(Math.min(0,...m.map(v=>v.temperature_c))/5)*5,tempMax=Math.max(tempMin+5,Math.ceil(Math.max(...m.map(v=>v.temperature_c))/5)*5);
  const y=v=>base-(v-tempMin)/(tempMax-tempMin)*(base-top);
  const labels=m.map((v,i)=>`<text x="${start+i*step}" y="125" text-anchor="middle">${months[i].slice(0,3)}</text>`).join('');
  const rain=m.map((v,i)=>`<rect x="${start+i*step-11}" y="${base-v.rainfall_mm/rainMax*(base-top)}" width="22" height="${v.rainfall_mm/rainMax*(base-top)}" rx="3"/>`).join('');
  const line=m.map((v,i)=>`${start+i*step},${y(v.temperature_c)}`).join(' ');
  const axes=`<path class="chart-axis" d="M20 ${base}H580M20 ${top}H580"/>`;
  return `<div class="seasonal-content"><p class="overview-caption">${esc(c.period)} · Open-Meteo ERA5 · ${esc(sourceLabel(source))} · historical monthly means</p><figure class="seasonal-chart"><figcaption><b>Rainfall</b><span>mm / month</span></figcaption><svg viewBox="0 0 ${width} 137" role="img" aria-label="Historical mean monthly rainfall; values in the table below"><text x="20" y="16">${rainMax} mm</text>${axes}<g class="rain-bars">${rain}</g><text x="5" y="108">0</text>${labels}</svg></figure><figure class="seasonal-chart"><figcaption><b>Temperature</b><span>Mean °C</span></figcaption><svg viewBox="0 0 ${width} 137" role="img" aria-label="Historical mean monthly temperature; values in the table below"><text x="20" y="16">${tempMax}°C</text>${axes}<polyline class="temp-line" points="${line}"/>${m.map((v,i)=>`<circle class="temp-dot" cx="${start+i*step}" cy="${y(v.temperature_c)}" r="3"/>`).join('')}<text x="2" y="118">${tempMin}°</text>${labels}</svg></figure><details class="overview-note"><summary>View monthly values</summary><table><caption>${esc(c.period)} historical averages; not a forecast.</caption><thead><tr><th scope="col">Month</th><th scope="col">Rainfall mm</th><th scope="col">Mean °C</th></tr></thead><tbody>${m.map((v,i)=>`<tr><th scope="row">${months[i]}</th><td>${num(v.rainfall_mm,1)}</td><td>${num(v.temperature_c,1)}</td></tr>`).join('')}</tbody></table></details></div>`;
 }
 function createCoverLoader(api,onUpdate){
  let version=0,key=null,controller=null;
  function cancel(){version++;controller?.abort();key=null;}
  function select(point,{refresh=false}={}){
   const next=JSON.stringify([point.lat,point.lon,!!point.cache_only]);
   if(next===key&&!refresh)return;
   cancel();key=next;const current=version;controller=new AbortController();
   onUpdate({status:'loading',data:{}});
   api('/api/land-cover',{lat:point.lat,lon:point.lon,cache_only:!!point.cache_only,refresh},controller.signal).then(result=>{if(current===version)onUpdate(result);}).catch(()=>{if(current===version)onUpdate({status:'offline',data:{},warning:'Land cover could not be loaded.'});});
  }
  return {select,cancel};
 }
 const api={land,weather,climate,createCoverLoader};
 if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.FarmLensOverview=api;
})(typeof globalThis!=='undefined'?globalThis:this);
