/* Read-only, unweighted crop-factor comparison. Missing values stay missing. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.FarmLensComparison=api;})(typeof globalThis!=='undefined'?globalThis:this,()=>{
 'use strict';
 const axes=[['temperature','Temperature'],['rainfall','Rainfall'],['ph','Soil pH'],['frost','Frost'],['fire','Fire'],['texture','Texture'],['carbon','Carbon']];
 const escape=value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 function buildComparison(crops,selectedIds){
  const selected=new Set(selectedIds);
  return {axes,series:crops.filter(c=>selected.has(c.id)).map(c=>{
   const values=axes.map(([key])=>{const v=c.subscores[key];return typeof v==='number'&&Number.isFinite(v)&&v>=0&&v<=100?v:null;});
   const segments=axes.map((_,i)=>[i,(i+1)%axes.length]).filter(([a,b])=>values[a]!=null&&values[b]!=null);
   return {id:c.id,name:c.name,values,segments,complete:values.every(v=>v!=null),style:crops.indexOf(c)%3};
  })};
 }
 function renderRadar(model,width){
  const w=Math.max(280,Math.min(600,width)),h=Math.min(w,400),cx=w/2,cy=h/2,r=Math.min(w*.29,h*.34);
  const point=(i,value)=>{const a=-Math.PI/2+i*2*Math.PI/7;return [cx+Math.cos(a)*r*value/100,cy+Math.sin(a)*r*value/100];};
  const xy=p=>p.map(v=>v.toFixed(1)).join(',');
  const rings=[25,50,75,100].map(v=>`<path class="radar-grid" d="M${model.axes.map((_,i)=>xy(point(i,v))).join('L')}Z"/>`).join('');
  const spokes=model.axes.map(([key,label],i)=>{const p=point(i,100),text=point(i,122),anchor=text[0]<cx-10?'end':text[0]>cx+10?'start':'middle';return `<path class="radar-grid" d="M${cx},${cy}L${xy(p)}"/><text x="${text[0].toFixed(1)}" y="${text[1].toFixed(1)}" text-anchor="${anchor}" dominant-baseline="middle">${label}</text>`;}).join('');
  const series=model.series.map(s=>`<g class="radar-series series-${s.style}"><title>${escape(s.name)}: ${model.axes.map((a,i)=>a[1]+' '+(s.values[i]??'Unassessed')).join('; ')}</title>${s.segments.map(([a,b])=>`<path d="M${xy(point(a,s.values[a]))}L${xy(point(b,s.values[b]))}"/>`).join('')}${s.values.map((v,i)=>{if(v==null)return '';const [x,y]=point(i,v);if(s.style===1)return `<rect x="${x-3}" y="${y-3}" width="6" height="6"/>`;if(s.style===2)return `<path class="radar-dot" d="M${x},${y-4}l4,7h-8Z"/>`;return `<circle cx="${x}" cy="${y}" r="3"/>`;}).join('')}</g>`).join('');
  return `<svg viewBox="0 0 ${w} ${h}" role="img" aria-label="Crop sub-scores from zero at the centre to 100 at the outer ring. Gaps are unassessed. Exact values follow in a table."><title>Crop factor comparison</title>${rings}${spokes}<text x="${cx+5}" y="${cy-4}" class="radar-scale">0</text><text x="${cx+5}" y="${cy-r+12}" class="radar-scale">100</text>${series}</svg>`;
 }
 return {buildComparison,renderRadar};
});
