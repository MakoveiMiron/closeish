import test from 'node:test';
import assert from 'node:assert/strict';
import {createApp} from '../src/server.mjs';
import {createLazyContent} from '../src/content.mjs';
import {MemoryProgressStore} from '../src/progress.mjs';
import {MemoryStatsStore} from '../src/statistics.mjs';

test('published historical dates remain playable exactly once and count in their ORIGINAL daily statistics',async()=>{
 const store=new MemoryStatsStore(),progressStore=new MemoryProgressStore();
 const {server}=createApp({days:createLazyContent(),store,progressStore,previewDate:'2026-10-25',rateLimit:0,writeRateLimit:0,apiKeys:[],
  signingSecret:'a'.repeat(64),playerSecret:'b'.repeat(64)});
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 const base='http://127.0.0.1:'+server.address().port;
 const A='00000000-0000-4000-8000-000000000001',B='00000000-0000-4000-8000-000000000002';
 const runA='11111111-1111-4111-8111-111111111111',runB='22222222-2222-4222-8222-222222222222';
 const get=async path=>{const res=await fetch(base+path);return {status:res.status,data:await res.json()}};
 const post=async(path,obj)=>{const res=await fetch(base+path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(obj)});return {status:res.status,data:await res.json()}};
 try{
  const current=await get('/api/v1/today');assert.equal(current.data.date,'2026-10-25');
  const older=await get('/api/v1/days/2026-10-23');assert.equal(older.status,200);assert.equal(older.data.date,'2026-10-23');
  assert.equal(Object.keys(older.data.questions).length,6);
  assert.equal(older.data.questions.q1.answers,undefined,'Never expose answer bank');
  for(const invalid of ['2026-10-26','2026-10-35','2025-01-01'])assert.equal((await get('/api/v1/days/'+invalid)).status,404,invalid);
  assert.equal((await get('/api/v1/today?date=2026-10-23')).status,400);
  const date='2026-10-23',revision=older.data.revision;
  let r=await get('/api/v1/progress?playerId='+A+'&day='+date);assert.equal(r.status,200);assert.equal(r.data.progress,null);
  const requests=[];
  for(const [playerId,runId] of [[A,runA],[B,runB]]){
   const first=await post('/api/v1/progress/start',{date,revision,playerId,runId,activeRound:0,activeDeadline:Date.now()+30000});assert.equal(first.status,200);
   for(let n=1;n<=6;n++){
    const q=older.data.questions['q'+n];
    const item=await post('/api/v1/questions/'+q.id+'/answer',{date,revision,playerId,runId,kind:'skipped',raw:''});
    assert.equal(item.status,200,'past-round '+n+' '+JSON.stringify(item.data));
    assert.equal(item.data.progress.responses.length,n);
    if(n===6)assert.equal(item.data.counted,true,'Past completion should be counted immediately');
    requests.push(item);
   }
  }
  const finalA=await get('/api/v1/progress?playerId='+A+'&day='+date);assert.equal(finalA.data.progress.completed,true);
  assert.equal(finalA.data.counted,true);assert.equal(finalA.data.officialScore,0);
  assert.equal(finalA.data.days.find(x=>x.date===date)?.completed,true);
  let stats=await post('/api/v1/statistics',{playerId:A,date,revision});assert.equal(stats.status,200);assert.equal(stats.data.statistics.total,2);
  assert.equal(stats.data.statistics.histogram.find(x=>x.score===0).count,2);
  assert.equal((await post('/api/v1/questions/'+older.data.questions.q1.id+'/answer',{date,revision,playerId:A,runId:runB,kind:'skipped',raw:''})).status,409);
  assert.equal((await post('/api/v1/progress/start',{date,revision,playerId:A,runId:runB,activeRound:0,activeDeadline:Date.now()+30000})).status,409);
  assert.equal((await post('/api/v1/questions/'+older.data.questions.q1.id+'/answer',{date:'2026-10-26',revision,playerId:A,runId:runA,kind:'skipped'})).status,404);
  assert.equal((await get('/api/v1/today')).data.date,'2026-10-25');
  // Results for the October 24 challenge must remain unaffected by late October 22 completions.
  const untouched=await post('/api/v1/statistics',{playerId:A,date:'2026-10-25',revision:current.data.revision});
  assert.equal(untouched.data.statistics.total,0);
 }finally{await new Promise(resolve=>server.close(resolve))}
});


test('calendar/progress reads use day metadata without compiling the 52 MB historical answer bank',async()=>{
 const days=createLazyContent(),original=days.get;let compiled=0;
 days.get=(d)=>{compiled++;return original(d)};
 const {server}=createApp({days,progressStore:new MemoryProgressStore(),store:new MemoryStatsStore(),
  previewDate:'2026-10-25',rateLimit:0,writeRateLimit:0,apiKeys:[]});
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 const base='http://127.0.0.1:'+server.address().port,player='00000000-0000-4000-8000-000000000001';
 try {
  let res=await fetch(base+'/api/v1/progress?playerId='+player+'&day=2026-10-24');
  assert.equal(res.status,200);assert.equal(compiled,0,'Progress must not load answer banks');
  assert.equal((await res.json()).date,'2026-10-24');
  res=await fetch(base+'/api/v1/progress?playerId='+player);
  assert.equal(res.status,200);assert.equal(compiled,0,'Default progress must not load answer banks either');
  res=await fetch(base+'/api/v1/days/2026-10-23');
  assert.equal(res.status,200);assert.equal(compiled,1,'Dated question retrieval should compile that day');
 }finally{await new Promise(resolve=>server.close(resolve))}
});
