/* Finn is a bounded local report guide. Typed questions never leave the browser. */
(function(root) {
  'use strict';
  const factors={temperature:'temperature',rainfall:'rainfall',ph:'soil pH',
    frost:'frost proxy',fire:'fire exposure',texture:'texture fit',carbon:'carbon proxy'};
  const finite=value=>typeof value==='number'&&Number.isFinite(value);
  const score=value=>finite(value)?Math.round(value):'unassessed';
  const method={label:'Method & limits',href:'/about'};
  function topicFor(question) {
    const q=String(question||'').toLowerCase().trim();
    if(/\b(pesticide|herbicide|fungicide|dose|diagnos\w*|disease|loan|legal)\b/.test(q)) return 'help';
    if(/\b(water|irrigat\w*|rainfed|allocation)\b/.test(q)) return 'water';
    if(/\b(profit\w*|budget|return|cost|price|margin|income)\b/.test(q)) return 'budget';
    if(/\b(soil|carbon|texture|ph|clay|sand)\b/.test(q)) return 'soil';
    if(/\b(source|data|reliable|accuracy|accurate|validated|evidence)\b/.test(q)) return 'data';
    if(/\b(risk|weakest|limitation|concern|watch)\b/.test(q)) return 'risk';
    if(/\b(why|ranked|first|crop|grow|shortlist|recommend\w*|fit)\b/.test(q)) return 'why';
    return 'help';
  }
  function answer(question, report) {
    if(!report?.result) return {topic:'unavailable',title:'Let’s start with your land',
      text:'Load a land report first. I can then explain its crops, soil and planning tools.',links:[]};
    const topic=topicFor(question), result=report.result, crops=result.top_three||[];
    const crop=crops.find(c=>String(question).toLowerCase().includes(c.name.toLowerCase()))||crops[0];
    const links=[method], response={topic,title:'Let’s explore your report',text:'',links};
    if(topic==='help') {
      response.text='I answer supported questions about this report: crop fit, limitations, soil, water, budgets and sources. Try one of the questions above.';
      return response;
    }
    if(topic==='water') {
      return {...response,title:'Water is a separate planning step',action:'water',
        text:'Irrigation does not automatically improve the crop score. The water tool compares historical demand and shortfalls for wheat, barley and canola using your assumptions. It does not verify supply or prescribe today’s irrigation.'};
    }
    if(topic==='budget') {
      return {...response,title:'Explore a budget, not a profit prediction',action:'budget',
        text:'I cannot identify the most profitable crop from this land report. Enter your yield, price and costs to compare gross margins for wheat, barley and canola. The optional 2012 examples are historical, not current prices.'};
    }
    if(topic==='soil') {
      const soil=report.data?.soil?.data||{};
      const ph=finite(soil.ph)?`${soil.ph.toFixed(1)} (water)`:'unassessed';
      const carbon=finite(soil.soc_g_kg)?`${(soil.soc_g_kg/10).toFixed(2)}%`:'unassessed';
      response.title='What the soil estimates tell us';
      response.text=`pH is ${ph}; organic carbon is ${carbon}. These are modelled 0–30 cm estimates, not a farm soil test. Texture is a broad grouping; carbon does not establish crop-specific fertility.`;
      if(report.data?.soil?.stale||report.data?.soil?.status==='offline') response.text+=' Soil evidence is stale or unavailable.';
      return response;
    }
    if(topic==='data') {
      return {...response,title:'Open data, with visible limits',action:'evidence',
        text:'Climate comes from Open-Meteo, soil from Australian SLGA, and crop requirements from FAO EcoCrop with source-linked NSW checks. Scores and soil penalties are not field-calibrated. Check dates and missing evidence before using this shortlist.'};
    }
    if(!crop) return {...response,title:'No shortlist for this scenario',
      text:'There are no crop candidates in this report. Check missing soil or climate evidence, crop filters and local-guidance exclusions in Data & sources.',action:'evidence'};
    const assessed=Object.entries(crop.subscores||{}).filter(([key,value])=>key in factors&&finite(value));
    assessed.sort((a,b)=>a[1]-b[1]);
    const weakest=assessed[0], best=assessed.at(-1);
    const provisional=String(result.evidence_quality||'').includes('provisional')?'Inputs are provisional. ':'';
    const limit=!weakest?'There are too few assessed factors to explain the ranking.':
      weakest[1]===100?'There is no assessed factor below its preferred score; drainage and local soil tests still need checking.':
      `${factors[weakest[0]][0].toUpperCase()+factors[weakest[0]].slice(1)} is the weakest assessed factor at ${score(weakest[1])}/100.`;
    response.title=topic==='risk'?`What to watch for ${crop.name}`:`Why ${crop.name} appears here`;
    response.text=provisional+(topic==='risk'?limit:
      `${crop.name} scores ${score(crop.total)}/100 in this screening. `+
      (!crop.strong_match?'It is not a strong match. ':best?`${factors[best[0]][0].toUpperCase()+factors[best[0]].slice(1)} is a relative strength at ${score(best[1])}/100. `:'')+
      limit);
    if(crop.zero_capped) response.text+=' A zero factor means its total is capped at 20.';
    if(topic==='risk') {
      const unassessed=Object.keys(factors).filter(key=>!finite(crop.subscores?.[key]));
      if(unassessed.length) response.text+=' '+unassessed.map(key=>factors[key]).join(', ')+' remain unassessed.';
      const caution=crop.guidance?.checks?.find(check=>check.status!=='met')?.message;
      if(typeof caution==='string'&&caution.length<=500) response.text+=' '+caution;
    }
    try {
      const url=new URL(crop.source_url);
      if(url.protocol==='https:'&&url.hostname==='ecocrop.apps.fao.org') links.push({label:'FAO EcoCrop profile',href:url.href});
    } catch { /* A missing reference is not replaced by an invented source. */ }
    response.action='crop';response.cropId=crop.id;
    return response;
  }

  function mount({onAction,onExplain}) {
    const $=id=>document.getElementById(id);
    const dialog=$('companion-dialog'),log=$('companion-log'),input=$('companion-question');
    let report=null;
    function add(question) {
      if(!report) return;
      const result=answer(question,report);
      const entry=document.createElement('article');entry.className='guide-turn';
      const asked=document.createElement('p');asked.className='guide-question';asked.textContent=question.slice(0,240);
      const title=document.createElement('h3');title.textContent=result.title;
      const body=document.createElement('p');body.textContent=result.text;
      const refs=document.createElement('div');refs.className='guide-links';
      result.links.forEach(link=>{const a=document.createElement('a');a.textContent=link.label+' ↗';a.href=link.href;a.target='_blank';a.rel='noreferrer';refs.append(a);});
      entry.append(asked,title,body,refs);
      if(result.action) {
        const button=document.createElement('button');button.type='button';button.className='guide-action';
        button.textContent={water:'Open water planner →',budget:'Open crop budget →',evidence:'View data & sources →',crop:'View crop profile →'}[result.action];
        button.onclick=()=>{dialog.close();onAction(result.action,result.cropId);};
        entry.append(button);
      }
      log.append(entry);while(log.children.length>6)log.firstElementChild.remove();
      entry.scrollIntoView({block:'nearest',behavior:'auto'});
    }
    $('close-companion').onclick=()=>dialog.close();
    $('companion-form').onsubmit=event=>{
      event.preventDefault();const question=input.value.trim();if(!question)return;
      add(question);input.value='';input.focus({preventScroll:true});
    };
    dialog.querySelectorAll('[data-question]').forEach(button=>button.onclick=()=>add(button.dataset.question));
    $('guide-explain').onclick=()=>{dialog.close();onExplain();};
    dialog.addEventListener('click',event=>{if(event.target===dialog) {
      const box=dialog.getBoundingClientRect();
      if(event.clientX<box.left||event.clientX>box.right||event.clientY<box.top||event.clientY>box.bottom) dialog.close();
    }});
    function setContext(value) {
      report=value;log.replaceChildren();input.value='';
      input.disabled=!report;$('guide-submit').disabled=!report;
      dialog.querySelectorAll('[data-question]').forEach(b=>b.disabled=!report);
      $('guide-explain').disabled=!report?.result?.top_three?.length;
      $('guide-context').textContent=report?'Using your current report · '+(report.result.top_three?.length||0)+' crop candidates':'Load a land report to begin.';
    }
    setContext(null);
    return {setContext,open:()=>dialog.showModal()};
  }
  const api={answer,topicFor,mount};
  if(typeof module!=='undefined'&&module.exports) module.exports=api;
  else root.FarmLensCompanion=api;
})(typeof globalThis!=='undefined'?globalThis:this);
