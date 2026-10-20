/* Pin labels only: never changes the selected coordinates or land assessment. */
(function(root){
 'use strict';
 function createResolver(api,onUpdate,delayMs=450){
  let version=0,timer=null,controller=null;
  function cancel(){version++;clearTimeout(timer);controller?.abort();}
  function select(point,cacheOnly){
   cancel();const current=version;controller=new AbortController();const signal=controller.signal;
   onUpdate({status:'loading',name:null,note:'Finding the nearby locality…'});
   timer=setTimeout(async()=>{
    try{
     const result=await api('/api/reverse',{lat:point.lat,lon:point.lon,cache_only:cacheOnly},signal);
     if(current!==version)return;
     const name=result.data?.name;
     if(typeof name==='string'&&name.trim()){
      const scope=result.data.kind==='area'?'Nearby area':'Nearby locality';
      const saved=result.stale?' · saved name may be outdated':result.status==='cached'?' · cached':'';
      onUpdate({status:'resolved',name,note:`${scope} · OpenStreetMap${saved}. Pin coordinates unchanged.`});
     }else onUpdate({status:'unavailable',name:null,note:'Place name unavailable · using your selected coordinates.'});
    }catch(error){
     if(current===version)onUpdate({status:'unavailable',name:null,note:'Place name unavailable · using your selected coordinates.'});
    }
   },delayMs);
  }
  return {select,cancel};
 }
 const api={createResolver};
 if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.FarmLensLocation=api;
})(typeof globalThis!=='undefined'?globalThis:this);
