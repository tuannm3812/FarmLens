/* Real NSW imagery, isolated from scoring and the report's async lifecycle. */
(function(root) {
  'use strict';
  const source = 'https://maps.six.nsw.gov.au/arcgis/rest/services/public/NSW_Imagery/MapServer';

  function imageURL(point) {
    if (!point || !Number.isFinite(point.lat) || !Number.isFinite(point.lon) ||
        point.lat < -38 || point.lat > -28 || point.lon < 140 || point.lon > 160) {
      throw new Error('Choose a NSW point');
    }
    const radius = 6378137;
    const x = radius * point.lon * Math.PI / 180;
    const y = radius * Math.log(Math.tan(Math.PI / 4 + point.lat * Math.PI / 360));
    const params = new URLSearchParams({
      f: 'image', bbox: [x-600,y-360,x+600,y+360].join(','),
      bboxSR: '3857', imageSR: '3857', size: '600,360',
      format: 'jpg', transparent: 'false',
    });
    return source + '/export?' + params;
  }

  function dateLabel(metadata) {
    const blocks = metadata?.data?.blocks || [];
    const dates = [...new Set(blocks.map(b=>b.survey_date).filter(Boolean))];
    if (!dates.length || blocks.some(b=>!b.survey_date)) return 'Survey date unavailable';
    if (dates.length > 1) return 'Multiple survey dates';
    const parsed = new Date(dates[0]+'T00:00:00Z');
    return Number.isNaN(parsed.getTime()) ? 'Survey date unavailable' :
      'Survey: '+parsed.toLocaleDateString('en-AU',{day:'numeric',month:'short',year:'numeric',timeZone:'UTC'});
  }

  function createLoader(api, update) {
    let version = 0, controller;
    function select(point) {
      const current = ++version;
      controller?.abort();
      update(point ? {status:'loading',data:{blocks:[]}} : null);
      if (!point) return;
      controller = new AbortController();
      api('/api/imagery', point, controller.signal)
        .then(data=>{if(current===version) update(data);})
        .catch(()=>{if(current===version) update({status:'offline',data:{blocks:[]}});});
    }
    return {select};
  }

  function mount(api) {
    const host = document.getElementById('land-imagery');
    const dialog = document.getElementById('imagery-dialog');
    let version=0, timer=null, metadata=null;
    const loader = createLoader(api, value=>{
      metadata=value;
      const caption=host.querySelector('[data-imagery-date]');
      if(caption) caption.textContent=value?.status==='loading'?'Checking survey date…':dateLabel(value);
      const expanded=document.getElementById('imagery-date-detail');
      if(expanded) expanded.textContent=dateLabel(value)+(value?.stale?' · saved metadata is stale':'')+
        '. Block date at the pin; surrounding imagery may differ.';
    });
    document.getElementById('close-imagery').onclick=()=>dialog.close();
    dialog.addEventListener('click', event=>{if(event.target===dialog) {
      const box=dialog.getBoundingClientRect();
      if(event.clientX<box.left||event.clientX>box.right||event.clientY<box.top||event.clientY>box.bottom) dialog.close();
    }});
    function setContext(point) {
      const current=++version;
      clearTimeout(timer);
      if(dialog.open) dialog.close();
      document.getElementById('imagery-large').removeAttribute('src');
      loader.select(null);
      host.replaceChildren();
      if(!point) return;
      let url;
      try {
        // Server boundary validation includes NSW islands such as Lord Howe.
        url=imageURL(point);
      } catch {
        host.textContent='Imagery unavailable for this point.';
        return;
      }
      host.innerHTML='<figure class="land-image"><button type="button" class="imagery-open" disabled aria-label="Enlarge aerial and satellite imagery at your pin"><img alt="NSW aerial and satellite imagery centred on the selected pin" hidden><span class="imagery-state" role="status">Loading land imagery…</span><span class="imagery-pin" aria-hidden="true"></span><span class="imagery-expand" hidden>View land ↗</span></button><figcaption><span data-imagery-date>Checking survey date…</span><a href="'+source+'" target="_blank" rel="noreferrer">© NSW Spatial Services ↗</a></figcaption></figure>';
      const img=host.querySelector('img'),button=host.querySelector('button');
      const message=host.querySelector('.imagery-state');
      let attempts=0;
      function load() {
        const attempt=++attempts;
        function fail() {
          if(current!==version||attempt!==attempts) return;
          clearTimeout(timer);
          img.onload=null;img.onerror=null;
          img.removeAttribute('src');
          if(attempt<2) {load();return;}
          img.hidden=true;
          message.hidden=false;
          message.textContent='Imagery unavailable';
          button.disabled=true;
          host.querySelector('.imagery-pin').hidden=true;
        }
        img.onload=()=>{
          if(current!==version||attempt!==attempts) return;
          clearTimeout(timer);
          img.hidden=false;message.hidden=true;button.disabled=false;
          host.querySelector('.imagery-expand').hidden=false;
        };
        img.onerror=fail;
        timer=setTimeout(fail,10000);
        img.src=url+(attempt>1?'&retry=1':'');
      }
      button.onclick=()=>{
        document.getElementById('imagery-large').src=img.src;
        document.getElementById('imagery-date-detail').textContent=dateLabel(metadata)+
          (metadata?.stale?' · saved metadata is stale':'')+
          '. Block date at the pin; surrounding imagery may differ.';
        dialog.showModal();
      };
      loader.select({lat:point.lat,lon:point.lon,cache_only:!!point.cache_only,refresh:!!point.refresh});
      load();
    }
    return {setContext};
  }
  const api={imageURL,dateLabel,createLoader,mount};
  if(typeof module!=='undefined'&&module.exports) module.exports=api;
  else root.FarmLensImagery=api;
})(typeof globalThis!=='undefined'?globalThis:this);
