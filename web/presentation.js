/* Pure presentation helpers shared by the shortlist and crop drawer. */
(function(root){
 'use strict';
 const escape=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const cropIcons={wheat:'grain',barley:'barley',canola:'flower',oats:'oats',chickpea:'pod',lentil:'pod',sorghum:'sorghum',cotton:'cotton',rice:'rice',lucerne:'forage',grapes:'grapes',olives:'olive',citrus:'citrus',macadamia:'nut',improved_pasture:'grass'};
 const cropUses={wheat:'Grain',barley:'Grain',canola:'Oilseed',oats:'Grain',chickpea:'Pulse',lentil:'Pulse',sorghum:'Grain',cotton:'Fibre',rice:'Grain',lucerne:'Forage',grapes:'Fruit',olives:'Fruit / oil',citrus:'Fruit',macadamia:'Nut',improved_pasture:'Pasture'};
 const finite=value=>typeof value==='number'&&Number.isFinite(value);
 function cropIcon(id){return `<svg viewBox="0 0 24 24" aria-hidden="true"><use href="/assets/icons/crops.svg#${cropIcons[id]||'grass'}"/></svg>`;}
 function tags(crop){
  const life=crop.category==='annual'?'Annual':crop.category==='perennial'||['lucerne','improved_pasture'].includes(crop.id)?'Perennial':null;
  return `<span class="crop-tags">${[life,cropUses[crop.id]].filter(Boolean).map(t=>`<span class="crop-tag">${escape(t)}</span>`).join('')}</span>`;
 }
 function scoreState(crop){
  if(!finite(crop.total))return {tone:'unknown',label:'Unassessed'};
  if(crop.zero_capped)return {tone:'limiting',label:'Limit reached'};
  return crop.strong_match?{tone:'strong',label:'Stronger screen'}:{tone:'mixed',label:'Weak screen'};
 }
 function factorState(value,key){
  if(!finite(value))return {tone:'unknown',label:'Not assessed'};
  if(key==='carbon')return {tone:'experimental',label:'Experimental'};
  if(value===0)return {tone:'limiting',label:'At proxy limit'};
  if(value===100)return {tone:'strong',label:'Full points'};
  return {tone:'mixed',label:'Partial fit'};
 }
 function weatherState(source){
  const data=source?.data||{};
  if(source?.status==='offline'||!finite(data.min_temperature_c)||!finite(data.max_temperature_c))return {tone:'unknown',label:'Unavailable',detail:'No current forecast to assess.'};
  if(source.stale)return {tone:'unknown',label:'Outlook out of date',detail:'Refresh before using these forecast values.'};
  const cold=data.min_temperature_c<0,hot=data.max_temperature_c>=35;
  return {tone:cold||hot?'mixed':'neutral',label:cold&&hot?'Frost & heat flags':cold?'Sub-zero forecast':hot?'35°C+ forecast':'No temperature flag',detail:'Flags use forecast minima below 0°C or maxima at least 35°C. Crop stage and local conditions still matter.'};
 }
 function link(url,label){return typeof url==='string'&&/^https:\/\//.test(url)?`<a href="${escape(url)}" target="_blank" rel="noreferrer">${escape(label)}</a>`:escape(label);}
 function photoMarkup(crop,asset){
  const valid=asset&&asset.src===`/assets/crops/${crop.id}.jpg`&&/^[a-z_]+$/.test(crop.id);
  const fallback=`<div class="photo-fallback" ${valid?'hidden':''}>${cropIcon(crop.id)}<span>Example photo unavailable</span></div>`;
  if(!valid)return `<figure class="crop-photo"><div class="crop-photo-frame">${fallback}</div></figure>`;
  return `<figure class="crop-photo"><div class="crop-photo-frame">${fallback}<img src="${escape(asset.src)}" alt="${escape(asset.alt)}" loading="lazy" decoding="async" width="${Number(asset.width)||960}" height="${Number(asset.height)||640}" data-crop-photo="${escape(crop.id)}"></div><figcaption><span>Example crop · not this location</span><details class="photo-credit"><summary>Photo credit & licence</summary><p>${link(asset.source_url,asset.title)}<br>${escape(asset.creator)}${asset.attribution?` · ${escape(asset.attribution)}`:''}<br>${link(asset.license_url,asset.license)} · via Wikimedia Commons<br>Thumbnail displayed in a cropped frame.</p></details></figcaption></figure>`;
 }
 const api={cropIcon,tags,scoreState,factorState,weatherState,photoMarkup};
 if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.FarmLensPresentation=api;
})(typeof globalThis!=='undefined'?globalThis:this);
