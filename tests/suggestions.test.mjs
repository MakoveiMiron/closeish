import test from 'node:test';
import assert from 'node:assert/strict';
import {createApp} from '../src/server.mjs';
import {MemorySuggestionStore,validateSuggestion} from '../src/suggestions.mjs';

async function serve(store,run,extra={}){
 const {server}=createApp({suggestionStore:store,production:false,rateLimit:0,writeRateLimit:0,apiKeys:[],...extra});
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 try{await run('http://127.0.0.1:'+server.address().port)}finally{await new Promise(resolve=>server.close(resolve))}
}
const header={'Content-Type':'application/json','Origin':'http://localhost:5173'};
const payload={question:'Name a fictional space station at most 50 m long.',direction:'below'};
const post=(base,thing=payload,headers=header)=>fetch(base+'/api/v1/suggestions',{method:'POST',headers,body:JSON.stringify(thing)});
test('anonymous public question suggestions are write-only and validated',async()=>{
 const box=new MemorySuggestionStore();
 await serve(box,async base=>{
  const first=await post(base);assert.equal(first.status,202);assert.deepEqual(await first.json(),{ok:true});
  assert.deepEqual(box.items,[payload]);
  assert.equal((await fetch(base+'/api/v1/suggestions',{headers:{Origin:'http://localhost:5173'}})).status,405);
  for(const path of ['/api/v1/suggestions/export','/api/v1/suggestions/1','/api/v1/suggestions/download','/api/v1/suggestions?limit=999']){
   const res=await fetch(base+path,{headers:{Origin:'http://localhost:5173'}});assert.ok([404,405].includes(res.status),path);
   assert.doesNotMatch(await res.text(),/fictional space station/);
  }
  for(const bad of [{question:'bad',direction:'below'}, {...payload,direction:'other'}, {...payload,extra:'admin'}, {question:8,direction:'above'}, {...payload,question:'abc\0defgh'}, [],{}]){
   assert.equal((await post(base,bad)).status,400,JSON.stringify(bad));
  }
  assert.equal(box.items.length,1);
  assert.equal((await post(base,payload,{'Content-Type':'text/plain'})).status,415);
  assert.equal((await post(base,payload,{'Content-Type':'application/json',Origin:'https://evil.invalid'})).status,403);
 });
});
test('suggestion backend only confirms successful persistence and enforces strict hourly limit',async()=>{
 const box=new MemorySuggestionStore();
 await serve(box,async base=>{
  assert.equal((await post(base)).status,202);
  assert.equal((await post(base)).status,202);
  const exceeded=await post(base);assert.equal(exceeded.status,429);assert.equal(exceeded.headers.get('Retry-After'),'3600');
 },{suggestionLimitPerHour:2});
 await serve({mode:'postgres',ready:async()=>{},create:async()=>{throw Error('DB failed')}},async base=>{
  const res=await post(base);assert.equal(res.status,503);assert.equal((await res.json()).error.code,'SUGGESTIONS_UNAVAILABLE');
 });
 await serve(null,async base=>assert.equal((await post(base)).status,503));
});
test('suggestion input trimming and validation',()=>{
 assert.deepEqual(validateSuggestion({question:'  Some question?  ',direction:'above'}),{question:'Some question?',direction:'above'});
 assert.equal(validateSuggestion({question:'x'.repeat(351),direction:'below'}),null);
});
