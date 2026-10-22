import test from 'node:test';
import assert from 'node:assert/strict';
import {randomUUID} from 'node:crypto';
import {createReceipts} from '../src/receipts.mjs';
import {calculateStats,MemoryStatsStore,createStatistics} from '../src/statistics.mjs';
import {createApp} from '../src/server.mjs';
import {loadContent} from '../src/content.mjs';
const secret='s'.repeat(64),playerSecret='p'.repeat(64),date='2026-10-22',revision='a'.repeat(24);
const signer=createReceipts({secret,playerSecret});
function completeArgs(scores=[0,200,400,600,800,1200]){
 const playerId=randomUUID(),runId=randomUUID();
 return {date,revision,playerId,runId,receipts:scores.map((points,i)=>signer.issue({playerId,runId,date,revision,questionId:'q'+(i+1),points}))};
}
test('receipts reject forged scores, foreign players, mixed runs, duplicates and expired signatures',()=>{
 const input=completeArgs();assert.equal(signer.completion({...input,score:7200}).score,3200);
 const forged=[...input.receipts];forged[0]=Buffer.from(JSON.stringify({...JSON.parse(Buffer.from(forged[0].split('.')[0],'base64url')),s:1200})).toString('base64url')+'.'+forged[0].split('.')[1];
 assert.throws(()=>signer.completion({...input,receipts:forged}),/signature/);
 assert.throws(()=>signer.completion({...input,playerId:randomUUID()}),/same player/);
 assert.throws(()=>signer.completion({...input,runId:randomUUID()}),/same player/);
 assert.throws(()=>signer.completion({...input,receipts:Array(6).fill(input.receipts[0])}),/Repeated/);
 assert.throws(()=>signer.completion({...input,receipts:input.receipts.slice(1)}),/six/);
 const future=createReceipts({secret,playerSecret,clock:()=>new Date(Date.now()+73*3600000)});
 assert.throws(()=>future.completion(input),/expired/);
 assert.equal(signer.playerHash(input.playerId),signer.playerHash(input.playerId.toUpperCase()));
});
test('exact histogram: self excluded, ties not beaten, zero/one users have no percentile',()=>{
 assert.equal(calculateStats([]).mean,null);
 assert.equal(calculateStats([{score:200,count:1}],{score:200}).comparison.betterThanPercent,null);
 const result=calculateStats([{score:0,count:1},{score:200,count:2},{score:7200,count:1}],{score:200});
 assert.equal(result.histogram.length,37);assert.equal(result.total,4);assert.equal(result.mean,1900);
 assert.deepEqual(result.comparison,{score:200,others:3,lower:1,equal:1,higher:1,betterThanPercent:100/3});
 assert.equal(result.median,200);assert.equal(result.q25,0);assert.equal(result.q75,200);
});
test('first completion wins across retries and replays; content revisions are separate cohorts',async()=>{
 const store=new MemoryStatsStore(),stats=createStatistics(store,{cacheMs:0});
 const first=signer.completion(completeArgs());
 await Promise.all(Array.from({length:20},()=>stats.record(first)));
 const replay={...first,runId:randomUUID(),score:7200};let result=await stats.record(replay);
 assert.equal(result.total,1);assert.equal(result.official.score,3200);
 await stats.record({...first,playerHash:'b'.repeat(64),score:0});
 result=await stats.get(date,revision,first.playerHash);assert.equal(result.total,2);assert.equal(result.comparison.betterThanPercent,100);
 result=await stats.get(date,'c'.repeat(24),first.playerHash);assert.equal(result.total,0);assert.equal(result.comparison,null);assert.equal(result.official.score,3200);
});
test('HTTP statistics contract: six server scores, repeat deduplication, error/readiness behavior',async()=>{
 const days=loadContent(),store=new MemoryStatsStore();
 const app=createApp({days,store,signingSecret:secret,playerSecret,previewDate:date,rateLimit:0});
 await new Promise(resolve=>app.server.listen(0,'127.0.0.1',resolve));
 const base='http://127.0.0.1:'+app.server.address().port;
 const post=async(path,body)=>{const r=await fetch(base+path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});return {status:r.status,body:await r.json()}};
 try{
  const boot=await (await fetch(base+'/api/v1/today')).json(),playerId=randomUUID(),runId=randomUUID(),receipts=[];
  assert.equal(boot.statistics,'memory');
  for(const q of Object.values(boot.questions)){
   const reply=await post('/api/v1/questions/'+q.id+'/answer',{date,revision:boot.revision,playerId,runId,raw:'',kind:'skipped',points:1200});
   assert.equal(reply.status,200);assert.equal(reply.body.result.points,0);receipts.push(reply.body.result.receipt);
  }
  const payload={date,revision:boot.revision,playerId,runId,receipts,score:7200};
  let reply=await post('/api/v1/results',payload);assert.equal(reply.status,200);assert.equal(reply.body.statistics.official.score,0);assert.equal(reply.body.statistics.total,1);
  const retries=await Promise.all(Array.from({length:10},()=>post('/api/v1/results',payload)));assert.ok(retries.every(r=>r.body.statistics.total===1));
  reply=await post('/api/v1/statistics',{date,revision:boot.revision,playerId});assert.equal(reply.body.statistics.comparison.betterThanPercent,null);
  assert.equal((await post('/api/v1/results',{...payload,playerId:randomUUID()})).status,400);
  assert.equal((await post('/api/v1/statistics',{date:'2026-10-23',revision:boot.revision,playerId})).status,400);
  assert.equal((await fetch(base+'/readyz')).status,200);
  store.ready=async()=>{throw new Error('offline')};assert.equal((await fetch(base+'/readyz')).status,503);assert.equal((await fetch(base+'/healthz')).status,200);
  store.record=async()=>{throw Object.assign(new Error('offline'),{code:'TEST_OFFLINE'})};assert.equal((await post('/api/v1/results',payload)).status,503);
 }finally{await app.close()}
 assert.throws(()=>createApp({days,production:true,previewDate:''}),/PostgreSQL/);
});
