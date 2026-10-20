const {test}=require('node:test');
const assert=require('node:assert/strict');
const p=require('../web/presentation.js');

test('zero-capped scores never get a strong colour, and missing scores remain unknown',()=>{
 assert.equal(p.scoreState({total:20,zero_capped:true,strong_match:true}).tone,'limiting');
 assert.equal(p.scoreState({total:null,strong_match:true}).tone,'unknown');
 assert.equal(p.scoreState({total:98,strong_match:true}).tone,'strong');
 assert.equal(p.scoreState({total:59,strong_match:false}).tone,'mixed');
});

test('stale and offline outlooks never announce current temperature flags',()=>{
 assert.equal(p.weatherState({status:'cached',stale:true,data:{min_temperature_c:-3,max_temperature_c:40}}).tone,'unknown');
 assert.equal(p.weatherState({status:'offline',data:{}}).label,'Unavailable');
 assert.match(p.weatherState({status:'live',data:{min_temperature_c:-1,max_temperature_c:36}}).label,/Frost.*heat/i);
 assert.match(p.weatherState({status:'cached',stale:false,data:{min_temperature_c:0,max_temperature_c:34}}).label,/No temperature flag/);
});

test('photo markup permits only bundled crop paths, escapes metadata and retains licences',()=>{
 const crop={id:'canola',name:'Canola'};
 const asset={src:'/assets/crops/canola.jpg',alt:'Flowering <crop>',creator:'A & B',title:'Photo.jpg',source_url:'https://commons.wikimedia.org/wiki/File:Photo.jpg',license:'CC BY-SA 4.0',license_url:'https://creativecommons.org/licenses/by-sa/4.0/',width:960,height:640};
 const out=p.photoMarkup(crop,asset);
 assert.match(out,/Example crop/);assert.match(out,/CC BY-SA 4.0/);assert.match(out,/A &amp; B/);
 assert.match(out,/Flowering &lt;crop&gt;/);assert.match(out,/loading="lazy"/);
 assert.doesNotMatch(p.photoMarkup(crop,{...asset,src:'https://tracker.example/a.jpg'}),/<img/);
 assert.doesNotMatch(p.photoMarkup(crop,{...asset,source_url:'javascript:alert(1)'}),/href="javascript/);
 assert.match(p.photoMarkup(crop,null),/Example photo unavailable/);
});
