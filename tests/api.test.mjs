import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createApp,dateInZone} from '../src/server.mjs';
import {loadContent,hints,scoreAnswer,validateDay} from '../src/content.mjs';
const days=loadContent();
async function serve(options,run) {
  const {server}=createApp({days,rateLimit:0,writeRateLimit:0,apiKeys:[],previewDate:'2026-10-23',...options});
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  try{await run('http://127.0.0.1:'+server.address().port)}finally{await new Promise(resolve=>server.close(resolve))}
}
test('all 60 questions: every stored numeric score validates and each scoring tier survives server resolution',()=>{
  for(const {questions} of days.values()) for(const c of questions) {
    for(const points of [0,200,400,600,800,1000,1200]) {
      const sample=c.q.answers.find(a=>a.points===points && c.index.get(a.canonical.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase())?.length===1)
        ||c.q.answers.find(a=>a.points===points);
      if(!sample)continue;
      const result=scoreAnswer(c,sample.canonical);
      if(result.reason?.includes('ambiguous'))continue;
      assert.equal(result.points,sample.points,`${c.q.id}: ${sample.canonical}`);
    }
  }
});
test('daily public payload has exactly today’s six prompts; no bank or future access',async()=>serve({},async base=>{
  const r=await fetch(base+'/api/v1/today');assert.equal(r.status,200);
  const raw=await r.text(),data=JSON.parse(raw);assert.equal(data.date,'2026-10-23');
  assert.equal(Object.keys(data.questions).length,6);assert.ok(raw.length<12000);
  for(const q of Object.values(data.questions)) {assert.equal(q.date,data.date);assert.equal(q.answers,undefined);assert.equal(q.recognized_category_candidates,undefined)}
  assert.ok(data.published_dates.every(d=>d<=data.date));
  assert.equal((await fetch(base+'/api/v1/today?date=2026-10-24')).status,400);
  assert.equal((await fetch(base+'/backend/content/days/2026-10-24.json')).status,404);
  assert.equal((await fetch(base+'/api/v1/questions/closeish_20261023_q5/hints')).status,404);
  const cached=await fetch(base+'/api/v1/today',{headers:{'If-None-Match':r.headers.get('etag')}});assert.equal(cached.status,304);
}));
test('answer aliases, forged client points, stale revisions, bounded catalogue and hint privacy',async()=>serve({},async base=>{
  const today=await (await fetch(base+'/api/v1/today')).json(),q=days.get(today.date).questions[0],answer=q.q.answers[0];
  const args={date:today.date,revision:today.revision};const path=base+'/api/v1/questions/'+q.q.id;
  const post=body=>fetch(path+'/answer',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  const r=await post({...args,raw:answer.canonical,points:999999});assert.equal(r.status,200);assert.equal((await r.json()).result.points,answer.points);
  assert.equal((await post({...args,revision:'forged',raw:answer.canonical})).status,409);
  assert.equal((await post({...args,raw:'x'.repeat(500)})).status,400);
  const suggestions=await (await fetch(path+'/hints?'+new URLSearchParams({...args,q:answer.canonical}))).json();
  assert.equal(suggestions.candidates.length,1);assert.deepEqual(Object.keys(suggestions.candidates[0].ent),['canonical']);
  const book=await (await fetch(path+'/catalogue?'+new URLSearchParams({...args,limit:2}))).json();assert.equal(book.entries.length,2);
  assert.equal((await fetch(path+'/catalogue?'+new URLSearchParams({...args,limit:1000}))).status,400);
  assert.equal((await post(null)).status,400);
  assert.equal((await post({...args,raw:'x'.repeat(5000)})).status,413);
  assert.equal((await fetch(base+'/api/v1/today',{headers:{Origin:'https://untrusted.example'}})).status,403);
}));
test('Budapest midnight, DST, no stale date clamp and production preview rejection',async()=>{
  assert.equal(dateInZone(new Date('2026-10-22T21:59:59Z')),'2026-10-22');
  assert.equal(dateInZone(new Date('2026-10-22T22:00:00Z')),'2026-10-23');
  assert.equal(dateInZone(new Date('2026-10-25T22:59:59Z')),'2026-10-25');
  assert.equal(dateInZone(new Date('2026-10-25T23:00:00Z')),'2026-10-26');
  assert.throws(()=>createApp({days,production:true,previewDate:'2026-10-22'}),/forbidden/);
  let now=new Date('2026-10-22T21:59:59Z');
  await serve({previewDate:'',clock:()=>now},async base=>{
    const first=await fetch(base+'/api/v1/today'),etag=first.headers.get('etag');
    now=new Date('2026-10-22T22:00:00Z');
    const next=await fetch(base+'/api/v1/today',{headers:{'If-None-Match':etag}});assert.equal(next.status,200);assert.equal((await next.json()).date,'2026-10-23');
    now=new Date('2026-10-30T12:00:00Z');const scheduled=await (await fetch(base+'/api/v1/today')).json();assert.equal(scheduled.available,true);assert.equal(scheduled.date,'2026-10-30');
    now=new Date('2026-11-02T12:00:00Z');const absent=await (await fetch(base+'/api/v1/today')).json();assert.equal(absent.available,false);assert.deepEqual(absent.questions,{});
  });
});
test('large dictionary preserved and updated Scrabble bank uses the full 26-letter universe',()=>{
  const word=days.get('2026-10-24').questions[0];assert.equal(word.q.answers.length,188798);
  assert.ok(hints(word,'inter').length<=4);
  const scrabble=days.get('2026-10-26').questions[4];assert.equal(scrabble.q.answers.length,26);
  assert.equal(scoreAnswer(scrabble,'letter B').points,1000);
  assert.equal(scoreAnswer(scrabble,'not a letter').metric_value,null);
  assert.ok(!fs.readFileSync(new URL('../src/content.mjs',import.meta.url),'utf8').includes('geocoding-api'));
});
test('rate limit bounds requests; draft sets are never published',async()=>{
  await serve({rateLimit:2},async base=>{for(let i=0;i<2;i++)assert.equal((await fetch(base+'/api/v1/today')).status,200);assert.equal((await fetch(base+'/api/v1/today')).status,429)});
  const copy=new Map(days),current=copy.get('2026-10-23');copy.set('2026-10-23',{...current,day:{...current.day,publication_status:'draft'}});
  await serve({days:copy},async base=>{assert.equal((await (await fetch(base+'/api/v1/today')).json()).available,false)});
});
test('write limit is stricter than read limit and only counts answer/result POSTs',async()=>serve({writeRateLimit:2},async base=>{
  const today=await (await fetch(base+'/api/v1/today')).json(),id=today.questions.q1.id;
  const post=()=>fetch(base+`/api/v1/questions/${id}/answer`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({date:today.date,revision:today.revision,raw:'',kind:'skipped'})});
  assert.equal((await post()).status,200);assert.equal((await post()).status,200);
  const third=await post();assert.equal(third.status,429);assert.equal(third.headers.get('retry-after'),'60');
  for(let i=0;i<5;i++)assert.equal((await fetch(base+'/api/v1/today')).status,200);
}));
test('optional API key: required on /api/* when configured, health endpoints stay open, CORS allows the header',async()=>{
  const key='k'.repeat(32),other='o'.repeat(32);
  await serve({apiKeys:[key,other]},async base=>{
    assert.equal((await fetch(base+'/api/v1/today')).status,401);
    assert.equal((await fetch(base+'/api/v1/today',{headers:{'X-API-Key':'wrong'}})).status,401);
    assert.equal((await fetch(base+'/api/v1/today',{headers:{'X-API-Key':key}})).status,200);
    assert.equal((await fetch(base+'/api/v1/today',{headers:{'X-API-Key':other}})).status,200);
    assert.equal((await fetch(base+'/healthz')).status,200);
    const pre=await fetch(base+'/api/v1/results',{method:'OPTIONS',headers:{Origin:'http://localhost:5173','Access-Control-Request-Headers':'content-type,x-api-key'}});
    assert.equal(pre.status,204);assert.match(pre.headers.get('access-control-allow-headers'),/X-API-Key/);
  });
  await serve({},async base=>assert.equal((await fetch(base+'/api/v1/today')).status,200));
  assert.throws(()=>createApp({days,apiKeys:['short']}),/at least 24/);
});
test('content validation rejects inconsistent scores, filenames and duplicate identities',()=>{
  const day=JSON.parse(fs.readFileSync(new URL('../content/days/2026-10-23.json',import.meta.url)));
  assert.throws(()=>validateDay(day,'wrong.json'),/Filename/);
  day.questions.q1.answers[0].points=999;assert.throws(()=>validateDay(day,'2026-10-23.json'),/score mismatch/);
});
