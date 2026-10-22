import test from 'node:test';
import assert from 'node:assert/strict';
import {randomUUID} from 'node:crypto';
import {createApp} from '../src/server.mjs';
import {createLazyContent} from '../src/content.mjs';
import {MemoryStatsStore} from '../src/statistics.mjs';
const date='2026-10-22';
const days=createLazyContent();
async function scenario(callback){
 const store=new MemoryStatsStore(),app=createApp({days,store,previewDate:date,rateLimit:0,writeRateLimit:0,
  signingSecret:'s'.repeat(64),playerSecret:'p'.repeat(64)});
 await new Promise(done=>app.server.listen(0,'127.0.0.1',done));
 const base='http://127.0.0.1:'+app.server.address().port;
 const post=async (path,body)=>{const r=await fetch(base+path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});return {status:r.status,data:await r.json()}};
 try{await callback({base,post})}finally{await app.close()}
}
test('lazy load does not deserialize all historical banks at startup',()=>{
 assert.equal(days.size,7);assert.deepEqual([...days.keys()].slice(0,2),['2026-10-22','2026-10-23']);
 assert.equal(days.get('2026-10-22').questions.length,6);
});
test('progress is authoritative: persists each server-scored answer and forbids replay',async()=>scenario(async({base,post})=>{
 const boot=await (await fetch(base+'/api/v1/today')).json();
 const playerId=randomUUID(),runId=randomUUID();
 const progressUrl=()=>base+'/api/v1/progress?'+new URLSearchParams({playerId});
 const first=await (await fetch(progressUrl())).json();assert.equal(first.progress,null);
 const start={playerId,runId,date,revision:boot.revision,activeRound:0,activeDeadline:Date.now()+30000};
 let res=await post('/api/v1/progress/start',start);assert.equal(res.status,200);assert.equal(res.data.progress.activeRound,0);
 const receipts=[];
 const skipped={date,revision:boot.revision,playerId,runId,raw:'',kind:'skipped'};
 for(let i=0;i<6;i++){
  if(i){res=await post('/api/v1/progress/start',{...start,activeRound:i,activeDeadline:Date.now()+30000});assert.equal(res.status,200)}
  const question=boot.questions['q'+(i+1)];
  res=await post(`/api/v1/questions/${question.id}/answer`,skipped);
  assert.equal(res.status,200);assert.equal(res.data.result.points,0);receipts.push(res.data.result.receipt);
  assert.equal(res.data.progress.responses.length,i+1);
  if(i===1){
   const replay=await post(`/api/v1/questions/${boot.questions.q1.id}/answer`,{...skipped,kind:'answer',raw:'fake'});
   assert.equal(replay.status,200);assert.deepEqual(replay.data.result,res.data.progress.responses[0]);
  }
 }
 let state=await (await fetch(progressUrl())).json();assert.equal(state.progress.completed,true);assert.equal(state.progress.responses.length,6);
 assert.deepEqual(state.days.map(x=>x.answers),[6]);
 res=await post('/api/v1/progress/start',{...start,runId:randomUUID()});assert.equal(res.status,409);
 res=await post('/api/v1/results',{date,revision:boot.revision,playerId,runId,receipts});assert.equal(res.status,200);
 state=await (await fetch(progressUrl())).json();assert.equal(state.counted,true);
 const another=await (await fetch(base+'/api/v1/progress?'+new URLSearchParams({playerId,month:'2026-09'}))).json();assert.deepEqual(another.days,[]);
}));
test('out-of-order answers cannot insert later rounds; forged progress cannot alter completed answers',async()=>scenario(async({base,post})=>{
 const boot=await (await fetch(base+'/api/v1/today')).json(),playerId=randomUUID(),runId=randomUUID();
 let result=await post('/api/v1/questions/'+boot.questions.q4.id+'/answer',{date,revision:boot.revision,playerId,runId,kind:'skipped',raw:''});
 assert.equal(result.status,409);
 result=await post('/api/v1/progress/start',{playerId,runId,date,revision:boot.revision,activeRound:6,activeDeadline:Date.now()+30000});assert.equal(result.status,400);
 result=await post('/api/v1/progress/import',{date,revision:boot.revision,playerId,runId,responses:[{receipt:'forged',points:7200}]});assert.equal(result.status,400);
 const state=await (await fetch(base+'/api/v1/progress?playerId='+playerId)).json();assert.equal(state.progress?.responses.length||0,0);
}));
