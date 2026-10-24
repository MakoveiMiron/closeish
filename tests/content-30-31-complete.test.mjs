import { test } from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createRequire} from 'node:module';
const require = createRequire(import.meta.url);
const Core = require('../src/core.cjs');
const expected = {
  '2026-10-30':[143, 18, 12, 59, 97, 21],
  '2026-10-31':[16, 25, 151, 107, 59, 43]
};
for(const [dayDate,sizes] of Object.entries(expected)) {
  const day=JSON.parse(readFileSync(new URL('../content/days/'+dayDate+'.json',import.meta.url)));
  test(`${dayDate}: all six complete sources, score matches and unambiguous names`,()=>{
    assert.equal(day.publication_status,'scheduled');
    assert.equal(Object.keys(day.questions).length,6);
    for(let i=1;i<=6;i++){
      const q=day.questions['q'+i], ix=Core.index(q);
      assert.equal(q.answers.length,sizes[i-1]);
      assert.equal(q.time_limit_seconds,30);
      assert.equal(q.answer_scope.claimed_exhaustive,true);
      assert.equal(q.score_bands.length,5);
      assert.equal(q.scoring_window.max_scoring_distance,q.score_bands.at(-1).max_gap_inclusive);
      for(const [key,rows] of ix)assert.equal(rows.length,1,`${dayDate}/q${i}: collision at ${key}`);
      for(const a of q.answers){
        assert.equal(Core.exact(q,a.canonical).status,'found',`${dayDate}/q${i} ${a.canonical}`);
        assert.equal(Core.score(q,a.metric_value).points,a.points,`${dayDate}/q${i} ${a.canonical}`);
        for(const alias of a.aliases||[])assert.equal(Core.exact(q,alias.input).status,'found');
      }
      assert.equal(q.answers.some(a=>a.points===0),true,`${dayDate}/q${i} must retain losing answers`);
      for(const positive of [200,400,600,800,1000,1200]) assert.equal(q.answers.some(a=>a.points===positive),true,`${dayDate}/q${i} lacks ${positive}`);
    }
  });
}
test('151 original Pokemon: female and male Nidoran are distinct, never ambiguous',()=>{
 const d=JSON.parse(readFileSync(new URL('../content/days/2026-10-31.json',import.meta.url)));
 const q=d.questions.q3;
 assert.equal(Core.exact(q,'Nidoran♀').status,'found');
 assert.equal(Core.exact(q,'Nidoran♂').status,'found');
 assert.notEqual(Core.norm('Nidoran♀'),Core.norm('Nidoran♂'));
 assert.equal(Core.exact(q,'Nidoran').status,'unknown');
});
test('all 143 three-digit primes have no small divisors',()=>{
 const d=JSON.parse(readFileSync(new URL('../content/days/2026-10-30.json',import.meta.url)));
 const q=d.questions.q1;
 const expectedPrimes=Array.from({length:900},(_,i)=>i+100).filter(n=>{
  for(let k=2;k<=Math.sqrt(n);k++)if(n%k===0)return false;
  return true;
 });
 assert.deepEqual(q.answers.map(a=>Number(a.canonical)),expectedPrimes);
 assert.ok(q.answers.some(a=>a.points===1200));
});
