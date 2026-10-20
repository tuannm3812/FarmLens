const test = require('node:test');
const assert = require('node:assert/strict');
const imagery = require('../web/imagery.js');

test('bounded image is centred on actual point and uses fixed NSW source', () => {
  const url = new URL(imagery.imageURL({lat:-32.2569,lon:148.6011}));
  assert.equal(url.hostname, 'maps.six.nsw.gov.au');
  assert.equal(url.searchParams.get('size'), '600,360');
  const [left,bottom,right,top] = url.searchParams.get('bbox').split(',').map(Number);
  const x = 6378137*148.6011*Math.PI/180;
  assert.ok(Math.abs((left+right)/2-x)<1);
  assert.equal(right-left,1200);
  assert.equal(top-bottom,720);
  assert.throws(()=>imagery.imageURL({lat:NaN,lon:148}));
});

test('imagery accepts Lord Howe Island within the NSW boundary', () => {
  const url = new URL(imagery.imageURL({lat:-31.5553,lon:159.082}));
  const [left,,right] = url.searchParams.get('bbox').split(',').map(Number);
  assert.ok(left < 17709330 && right > 17709330);
  assert.equal(url.hostname,'maps.six.nsw.gov.au');
});

test('unavailable imagery cannot throw out of the optional report view', () => {
  const vm = require('node:vm');
  const fs = require('node:fs');
  const host = {querySelector:()=>null,replaceChildren(){this.textContent='';}};
  const nodes = {
    'land-imagery':host,
    'imagery-dialog':{open:false,addEventListener(){}},
    'close-imagery':{},
    'imagery-large':{removeAttribute(){}},
    'imagery-date-detail':{},
  };
  const scope = {module:{exports:{}},document:{getElementById:id=>nodes[id]},clearTimeout};
  vm.runInNewContext(fs.readFileSync(require.resolve('../web/imagery.js'),'utf8'),scope);
  const view = scope.module.exports.mount(()=>{throw new Error('No request for invalid point');});
  assert.doesNotThrow(()=>view.setContext({lat:NaN,lon:148}));
  assert.match(host.textContent,/unavailable/i);
  view.setContext(null);
  assert.equal(host.textContent,'');
});

test('dates describe survey blocks and stay unknown when metadata is absent', () => {
  assert.match(imagery.dateLabel({data:{blocks:[]}}),/date unavailable/i);
  assert.match(imagery.dateLabel({data:{blocks:[{survey_date:'2009-04-03'}]}}),/2009/);
  assert.match(imagery.dateLabel({data:{blocks:[{survey_date:'2009-04-03'},{survey_date:'2021-02-01'}]}}),/multiple/i);
});

test('new context clears old metadata and ignores late completion', async () => {
  const pending=[], updates=[];
  const loader=imagery.createLoader((path,point)=>new Promise(resolve=>pending.push({point,resolve})), value=>updates.push(value));
  loader.select({lat:-32,lon:148});
  loader.select({lat:-31,lon:149});
  pending[0].resolve({data:{blocks:[{name:'old'}]}});
  await Promise.resolve();
  assert.equal(updates.at(-1).status,'loading');
  pending[1].resolve({data:{blocks:[{name:'new'}]}});
  await Promise.resolve();
  assert.equal(updates.at(-1).data.blocks[0].name,'new');
  loader.select(null);
  assert.equal(updates.at(-1),null);
});


test('mounted imagery forwards explicit refresh once and keeps cached browsing offline', async () => {
  const vm = require('node:vm');
  const fs = require('node:fs');
  const elements = new Map();
  const host = {
    querySelector(selector) {
      if (!elements.has(selector)) elements.set(selector, {removeAttribute(){}});
      return elements.get(selector);
    },
    replaceChildren(){elements.clear();},
  };
  const nodes = {
    'land-imagery':host,
    'imagery-dialog':{open:false,addEventListener(){}},
    'close-imagery':{},
    'imagery-large':{removeAttribute(){}},
    'imagery-date-detail':{},
  };
  const scope = {
    module:{exports:{}},document:{getElementById:id=>nodes[id]},
    URLSearchParams,AbortController,setTimeout,clearTimeout,
  };
  vm.runInNewContext(fs.readFileSync(require.resolve('../web/imagery.js'),'utf8'),scope);
  const requests = [];
  const view = scope.module.exports.mount(async (path,point,signal) => {
    requests.push({path,point,signal});
    return {status:'cached',data:{blocks:[{survey_date:'2009-04-03'}]}};
  });
  const point = {lat:-32.2569,lon:148.6011,cache_only:true};
  try {
    view.setContext({...point,refresh:true});
    assert.equal(requests[0].path,'/api/imagery');
    assert.equal(requests[0].point.refresh,true);
    assert.equal(requests[0].point.cache_only,true);
    assert.equal(requests[0].point.lat,point.lat);
    assert.equal(requests[0].point.lon,point.lon);
    await Promise.resolve();
    assert.match(host.querySelector('[data-imagery-date]').textContent,/2009/);

    view.setContext(point);
    assert.equal(requests.length,2);
    assert.equal(requests[0].signal.aborted,true);
    assert.equal(requests[1].point.refresh,false);
    assert.equal(requests[1].point.cache_only,true);
  } finally {
    view.setContext(null);
  }
});
