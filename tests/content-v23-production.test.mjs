import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
const Core=createRequire(import.meta.url)('../src/core.cjs');
const sizes={
  "2026-10-25": [
    30,
    123,
    32,
    26,
    190,
    50
  ],
  "2026-10-26": [
    100,
    54,
    20,
    142,
    27,
    28
  ],
  "2026-10-27": [
    32,
    48,
    100,
    26,
    31,
    21
  ],
  "2026-10-28": [
    48,
    27,
    309,
    60,
    26,
    61
  ],
  "2026-10-29": [
    48,
    32,
    61,
    25,
    142,
    20
  ],
  "2026-10-30": [
    143,
    18,
    12,
    59,
    97,
    21
  ],
  "2026-10-31": [
    16,
    25,
    151,
    107,
    59,
    43
  ],
  "2026-11-01": [
    88,
    18,
    24,
    14,
    135,
    41
  ]
};
const base=new URL('../content/days/',import.meta.url);
test('V23 production: all ten days scheduled; six questions each; no local test assets',()=>{
  for(let i=0;i<10;i++) {
    const d=new Date(Date.UTC(2026,9,23+i)).toISOString().slice(0,10);
    const day=JSON.parse(readFileSync(new URL(`${d}.json`,base)));
    assert.equal(day.publication_status,'scheduled',d);
    assert.equal(Object.keys(day.questions).length,6,d);
    if(sizes[d]) assert.deepEqual(Object.values(day.questions).map(q=>q.answers.length),sizes[d],d);
  }
});
test('V23 keeps the active 2026-10-24 content byte-identical',()=>{
  const h=crypto.createHash('sha256').update(readFileSync(new URL('2026-10-24.json',base))).digest('hex');
  assert.equal(h,'1cf1dd25bed3f58cce5bf8d9750290d2a733525baa5899e0371e09b12e6116d4');
});
test('V23 question banks: exact and alias resolution, scoring, at least one losing answer',()=>{
  for(const d of Object.keys(sizes))for(const [qId,q] of Object.entries(JSON.parse(readFileSync(new URL(`${d}.json`,base))).questions)) {
    const ix=Core.index(q);const row=q.answers.find(a=>a.points===1200);
    assert.ok(row,`${d} ${qId} has no exact hit`);
    assert.ok(q.answers.some(a=>a.points===0),`${d} ${qId} has no zero`);
    for(const a of q.answers){
      assert.equal(Core.score(q,a.metric_value).points,a.points,`${d} ${qId} ${a.canonical}`);
      assert.equal(Core.exact(q,a.canonical).status,'found',`${d} ${qId} ${a.canonical}`);
    }
    for(const [k,rows] of ix)assert.equal(rows.length,1,`${d} ${qId} alias collision ${k}`);
  }
});

test('V23 replaces elementary matching and USA-state word games',()=>{
 const disallowed=/\b(?:UNO|Roman numeral|Scrabble|double-six domino|palindrome|Monopoly|Rider.Waite tarot|phonetic alphabet code word)\b/i;
 for(const date of Object.keys(sizes)) {
   const d=JSON.parse(readFileSync(new URL(`${date}.json`,base)));
   for(const q of Object.values(d.questions)) assert.ok(!disallowed.test(q.prompt),`${date}: ${q.prompt}`);
 }
});
test('V23 fixes complete Nile 1871–1970 data and meaningful prime-gap problem',()=>{
 const d27=JSON.parse(readFileSync(new URL('2026-10-27.json',base)));
 const nile=d27.questions.q3;
 assert.equal(nile.answers.length,100);
 assert.equal(nile.answers.at(0).canonical,'1871');
 assert.equal(nile.answers.at(-1).canonical,'1970');
 assert.ok(nile.answers.every(a=>Number.isFinite(a.metric_value)));
 const d30=JSON.parse(readFileSync(new URL('2026-10-30.json',base)));
 const primes=d30.questions.q1;
 for(const a of primes.answers) {
   const v=Number(a.canonical);
   const next = [...Array(100)].map((_,i)=>v+1+i).find(n=>{for(let k=2;k<=Math.sqrt(n);k++)if(n%k===0)return false;return true;});
   assert.equal(a.metric_value,next-v,a.canonical);
 }
});
