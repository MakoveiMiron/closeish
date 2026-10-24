import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import Core from '../src/core.cjs';
import {loadContent, scoreAnswer} from '../src/content.mjs';
const d=JSON.parse(fs.readFileSync(new URL('../content/days/2026-11-01.json',import.meta.url)));
const numbers=[88,18,24,14,135,41];
const stored=loadContent(new URL('../content/days/',import.meta.url),'2026-11-01');
const selected=stored.get('2026-11-01');

test('full scheduled 2026-11-01: 6 distinct questions, 320 complete sourced answers',()=>{
 assert.equal(d.publication_status,'scheduled');assert.equal(d.date,'2026-11-01');assert.equal(d.day_number,10);
 assert.deepEqual(Object.keys(d.questions),['q1','q2','q3','q4','q5','q6']);
 assert.equal(new Set(Object.values(d.questions).map(q=>q.topic)).size,6);
 for(let i=0;i<6;i++){
   const q=d.questions['q'+(i+1)];assert.equal(q.answers.length,numbers[i]);
   assert.equal(q.answer_scope.claimed_exhaustive,true);assert.equal(q.answer_scope.known_unmeasured_count,0);
   assert.ok(/\bat (?:most|least)\b|\bin 2005 or earlier\b/i.test(q.prompt));assert.ok(!/frozen|dataset|source|statsmodels|sample|library/i.test(q.prompt));
   assert.equal(q.time_limit_seconds,30);
   assert.deepEqual(new Set(q.answers.map(a=>a.points)),new Set([0,200,400,600,800,1000,1200]));
   assert.equal(q.scoring_window.max_scoring_distance,q.score_bands[4].max_gap_inclusive);
   assert.deepEqual(q.answers.filter(a=>a.points===1200).map(a=>a.metric_value).every(x=>x===q.limit),true);
 }
});

test('no alias collisions; all canonical answers and aliases resolve to original entity and stored points',()=>{
 for(let i=0;i<6;i++){
   const q=d.questions['q'+(i+1)],compiled=selected.questions[i],seen=new Map();
   for(const answer of q.answers){
     assert.equal(Core.score(q,answer.metric_value).points,answer.points);
     for(const text of [answer.canonical,...answer.aliases.map(a=>a.input)]){
       const norm=Core.norm(text);
       assert.ok(norm);
       assert.ok(!seen.has(norm)||seen.get(norm)===answer.entity_id,`alias collision ${q.id} ${text}`);
       seen.set(norm,answer.entity_id);
       const resolved=scoreAnswer(compiled,text);
       assert.equal(resolved.canonical,answer.canonical,`Alias incorrectly resolved: ${q.id} ${text}`);
       assert.equal(resolved.points,answer.points);
     }
   }
 }
});

test('music sharps, flats and day 10 resolved correctly without clobbering neighboring notes',()=>{
 assert.equal(Core.dateForDay(10),'2026-11-01');
 assert.equal(Core.dateForDay(11),'2026-11-02');
 const q=selected.questions[0];
 assert.equal(scoreAnswer(q,'D#4').canonical,'D#4');
 assert.equal(scoreAnswer(q,'D♯4').canonical,'D#4');
 assert.equal(scoreAnswer(q,'Eb4').canonical,'D#4');
 assert.equal(scoreAnswer(q,'E♭4').canonical,'D#4');
 assert.equal(scoreAnswer(q,'D4').canonical,'D4');
 assert.equal(scoreAnswer(q,'A#4').canonical,'A#4');
 assert.equal(scoreAnswer(q,'Bb4').canonical,'A#4');
 assert.equal(scoreAnswer(q,'A4').canonical,'A4');
});

test('historical fact anchors reflect selected source vintage',()=>{
 let names=Object.fromEntries(d.questions.q2.answers.map(a=>[a.canonical,a.metric_value]));
 assert.equal(names.Milton,287);assert.equal(names.Ernesto,157);
 names=Object.fromEntries(d.questions.q3.answers.map(a=>[a.canonical,a.metric_value]));
 assert.equal(names['Las Vegas Strip Circuit'],6201);assert.equal(names['Lusail International Circuit'],5419);
 assert.equal(names['Red Bull Ring'],4326);assert.equal(names['Marina Bay Street Circuit'],4927);
 names=Object.fromEntries(d.questions.q5.answers.map(a=>[a.canonical,a.metric_value]));
 assert.equal(names['STS-51L'],0);assert.equal(names['STS-135'],12);
 names=Object.fromEntries(d.questions.q6.answers.map(a=>[a.canonical,a.metric_value]));
 assert.equal(names['The Colour of Magic'],1983);assert.equal(names['Thud!'],2005);assert.equal(names["The Shepherd's Crown"],2015);
});
