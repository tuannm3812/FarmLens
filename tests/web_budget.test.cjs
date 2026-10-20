const {test}=require('node:test');
const assert=require('node:assert/strict');
const b=require('../web/budget.js');
const row={crop_id:'wheat',name:'Wheat',status:'available',margin_aud_ha:-20,revenue_aud_ha:500,cost_aud_ha:520,break_even_price_aud_t:null,break_even_yield_t_ha:null,sensitivity:{low:-200,base:-20,high:150}};
test('budget renders losses, undefined break-even and unknown rows without invented zero',()=>{
 const html=b.render({rows:[row,{crop_id:'barley',name:'Barley',status:'incomplete',reason:'Enter assumptions'}]},false);
 assert.match(html,/-\$20/); assert.match(html,/Not reachable/);assert.match(html,/No positive yield/);
 assert.match(html,/Enter assumptions/);assert.doesNotMatch(html,/NaN|Infinity/);
});
test('archived budget provenance stays visible with results and names are escaped',()=>{
 const html=b.render({rows:[{...row,name:'<img src=x>'}]},true);
 assert.match(html,/2012/);assert.match(html,/&lt;img/);assert.doesNotMatch(html,/<img/);
});
test('zero-margin-at-any-yield budget is not labelled unreachable',()=>{
 const html=b.render({rows:[{...row,margin_aud_ha:0,revenue_aud_ha:60,cost_aud_ha:60,
  break_even_yield_any:true,break_even_price_aud_t:20,sensitivity:{low:-9.6,base:0,high:14.4}}]},false);
 assert.match(html,/Any yield \(zero margin\)/);
 assert.doesNotMatch(html,/Not reachable/);
});
test('pending land selection immediately clears old assumptions, labels and results',()=>{
 const inputs=['yield_t_ha','price_aud_t','variable_aud_ha','selling_aud_t','irrigation_aud_ha'].map(field=>({value:'',dataset:{crop:'wheat',field}}));
 const nodes={};global.document={getElementById(id){return nodes[id]??=( {textContent:'',innerHTML:'',disabled:false,addEventListener(){},querySelectorAll(){return inputs;},replaceChildren(){this.innerHTML='';}});}};
 try{
  const planner=b.mount({profiles:{wheat:{name:'Wheat',example:{yield_t_ha:1.5,price_aud_t:275,variable_aud_ha:293.91,selling_aud_t:0,irrigation_aud_ha:0}}}},()=>{});
  planner.setContext({lat:-32.2569,lon:148.6011,name:'Dubbo',irrigation:'rainfed'});
  nodes['budget-example'].onclick();nodes['budget-results'].innerHTML='old result';
  planner.setContext(null);
  assert.ok(inputs.every(i=>i.value===''));
  assert.doesNotMatch(nodes['budget-location'].textContent,/Dubbo/);
  assert.equal(nodes['budget-results'].innerHTML,'');assert.equal(nodes['budget-calculate'].disabled,true);
 }finally{delete global.document;}
});
