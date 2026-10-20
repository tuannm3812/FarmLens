const test = require('node:test');
const assert = require('node:assert/strict');
const guide = require('../web/companion.js');

function report(change={}) {
  return {result:{evidence_quality:'modelled evidence',irrigation:'rainfed',
    top_three:[{name:'Wheat',id:'wheat',total:82,strong_match:true,zero_capped:false,
      subscores:{temperature:100,rainfall:65,ph:90,fire:null},
      guidance:{checks:[{status:'not_assessed',message:'Local drainage needs checking.'}]},
      source_url:'https://ecocrop.apps.fao.org/ecocrop/srv/en/dataSheet?id=1'}],
    ...change},
    data:{soil:{data:{ph:6.3,soc_g_kg:13,clay_pct:20,sand_pct:68}},climate:{status:'cached'}}};
}

test('why uses actual first crop and distinguishes weakest factor from success',()=>{
  const answer=guide.answer('Why is this crop ranked first?',report());
  assert.match(answer.text,/Wheat.*82\/100/);
  assert.match(answer.text,/rainfall.*65\/100/i);
  assert.doesNotMatch(answer.text,/82%|guaranteed|profitable/);
});
test('zero cap and no strong match never become a positive recommendation',()=>{
  const r=report();Object.assign(r.result.top_three[0],{strong_match:false,zero_capped:true,total:20});
  r.result.top_three[0].subscores.rainfall=0;
  const answer=guide.answer('why',r);
  assert.match(answer.text,/not a strong match/i);
  assert.match(answer.text,/capped at 20/);
});
test('all preferred does not invent a weakest problem; missing fire is unassessed',()=>{
  const r=report();r.result.top_three[0].subscores={temperature:100,rainfall:100,fire:null};
  const text=guide.answer('biggest risk',r).text;
  assert.match(text,/no assessed factor/i);assert.match(text,/fire.*unassessed/i);
});
test('provisional inputs and missing shortlist remain explicit',()=>{
  assert.match(guide.answer('why',report({evidence_quality:'provisional — stale'})).text,/provisional/i);
  assert.match(guide.answer('why',report({top_three:[]})).text,/no crop candidates/i);
  assert.match(guide.answer('why',null).text,/load a land report/i);
});
test('water and budgets stay scenarios, with no automatic score or profit boost',()=>{
  const water=guide.answer('what changes with irrigation?',report());
  assert.match(water.text,/does not automatically improve/i);
  assert.equal(water.action,'water');
  const budget=guide.answer('which crop is most profitable?',report());
  assert.match(budget.text,/cannot identify/i);
  assert.equal(budget.action,'budget');
});
test('soil values use water pH and carbon percent without implying measurements',()=>{
  const answer=guide.answer('tell me about the soil',report());
  assert.match(answer.text,/6.3.*water/);
  assert.match(answer.text,/1.30%/);
  assert.match(answer.text,/modelled/);
});
test('unsupported questions get a bounded fallback and do not echo unsafe input',()=>{
  const q='<img src=x onerror=alert(1)> diagnose disease';
  const answer=guide.answer(q,report());
  assert.equal(answer.topic,'help');assert.ok(!answer.text.includes(q));
  assert.equal(guide.answer('hello',report()).topic,'help');
});
test('unsafe crop source links are discarded; valid links are attributed',()=>{
  const r=report();r.result.top_three[0].source_url='javascript:alert(1)';
  const answer=guide.answer('why',r);
  assert.ok(answer.links.every(link=>link.href.startsWith('/')||link.href.startsWith('https://')));
  assert.ok(guide.answer('why',report()).links.some(link=>link.label.includes('EcoCrop')));
});
