import test from 'node:test';
import assert from 'node:assert/strict';
import {createApp} from '../src/server.mjs';
import {createLazyContent} from '../src/content.mjs';
import {MemoryStatsStore} from '../src/statistics.mjs';
import {MemoryProgressStore} from '../src/progress.mjs';
import {dateInZone} from '../src/server.mjs';

const app = createApp({days:createLazyContent(),clock:()=>new Date('2026-10-23T09:00:00Z'),
  store:new MemoryStatsStore(),progressStore:new MemoryProgressStore(),rateLimit:0,writeRateLimit:0,
  signingSecret:'x'.repeat(64),playerSecret:'y'.repeat(64)});

test('23 October is first playable, day #001, archive starts that date and day 22 is blocked throughout',async()=>{
 await new Promise(ok=>app.server.listen(0,'127.0.0.1',ok));
 const base='http://127.0.0.1:'+app.server.address().port;
 try{
   const boot=await (await fetch(base+'/api/v1/today')).json();
   assert.equal(boot.date,'2026-10-23'); assert.equal(boot.day_number,1);
   assert.equal(boot.start_date,'2026-10-23');assert.deepEqual(boot.published_dates,['2026-10-23']);
   assert.equal((await fetch(base+'/api/v1/days/2026-10-22')).status,404);
   assert.equal((await fetch(base+'/api/v1/days/2026-10-24')).status,404);
   const json={playerId:'00000000-0000-4000-8000-000000000001',date:'2026-10-22',revision:boot.revision};
   for(const path of ['/api/v1/progress/start','/api/v1/progress/import','/api/v1/statistics','/api/v1/results']){
     const r=await fetch(base+path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(json)});
     assert.ok(r.status>=400, path); 
   }
   const old=await fetch(base+'/api/v1/progress?playerId='+json.playerId+'&day=2026-10-22');assert.equal(old.status,404);
 } finally {await app.close()}
});

test('all published prompts use consistent metric physical units; converted range preserves original scoring',()=>{
 const days=createLazyContent();
 for(const day of days){
   const pack=days.get(day[0]);
   for(const {q} of pack.questions){
     assert.ok(!/\b(miles?|feet|inches?|gallons?|pounds?|fahrenheit|mph)\b/i.test(q.prompt), q.id);
     assert.ok(!['miles','feet','inches','gallons','pounds','lb','US gallons'].includes(q.unit),q.id);
   }
 }
 const q=days.get('2026-10-24').questions[3].q;
 assert.equal(q.unit,'km');assert.equal(q.limit,579.36);
 const examples=new Map([['Acura RL',1200],['Audi A4 Avant',1000],['Acura TL',600],['Aston Martin DB9',0]]);
 for(const [name,points] of examples){
   const entry=q.answers.find(x=>x.canonical===name);assert.equal(entry.points,points);
 }
});

test('migration 004 hashes agree with the exact shifted daily JSON files',async()=>{
 const fs=await import('node:fs');const crypto=await import('node:crypto');
 const script=fs.readFileSync(new URL('../migrations/004_shift_launch_to_oct23.sql',import.meta.url),'utf8');
 for(let n=23;n<=29;n++){
   const old='2026-10-'+String(n-1),next='2026-10-'+String(n);
   const raw=fs.readFileSync(new URL(`../content/days/${next}.json`,import.meta.url));
   const hash=crypto.createHash('sha256').update(raw).digest('hex').slice(0,24);
   assert.match(script,new RegExp(`WHEN date '${old}' THEN old_revision := '[a-f0-9]{24}'; new_revision := '${hash}'`));
 }
});
