import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,readdirSync} from 'node:fs';
import Core from '../src/core.cjs';
import {loadContent,scoreAnswer} from '../src/content.mjs';

const content=loadContent();
const days=['2026-11-04','2026-11-05'];
const tierSet=[0,200,400,600,800,1000,1200];
const base=new URL('../content/source-snapshots/',import.meta.url);
function parseCSV(s){
 const rows=[]; let row=[],cell='',quotes=false;
 for(let i=0;i<s.length;i++){
  const c=s[i];
  if(c==='"'){if(quotes&&s[i+1]==='"'){cell+='"';i++;}else quotes=!quotes;}
  else if(c===','&&!quotes){row.push(cell);cell='';}
  else if(c==='\n'&&!quotes){row.push(cell.replace(/\r$/,''));rows.push(row);row=[];cell='';}
  else cell+=c;
 }
 if(row.length||cell){row.push(cell);rows.push(row)}
 return rows;
}

test('V25: 14 days, future schedule gate and original 12 days untouched by day numbering',()=>{
 assert.equal(content.size,14);
 assert.equal(Core.START,'2026-10-23');assert.equal(Core.END,'2026-11-05');
 for(let d=1;d<=14;d++){
  const date=Core.dateForDay(d);
  assert.equal(content.get(date)?.day.day_number,d,`${date} order`);
 }
 assert.equal(Core.dateForDay(13),days[0]);assert.equal(Core.dateForDay(14),days[1]);
});

test('V25: full 12 answer banks, independently enumerated CSV rows and production backend scoring',()=>{
 const previousFamilies=new Set(); const previousTopics=new Set();
 for(const [date,{day}] of content){if(days.includes(date))continue;
  for(const q of Object.values(day.questions)){
   previousFamilies.add(q.question_family);previousTopics.add(q.topic);
  }
 }
 const newTopics=new Set(), newFamilies=new Set(); let total=0;
 for(const [di,date] of days.entries()){
  const entry=content.get(date);assert.ok(entry,`missing ${date}`);
  const day=entry.day; assert.equal(day.day_number,13+di);assert.equal(day.publication_status,'scheduled');
  assert.deepEqual(Object.keys(day.questions),['q1','q2','q3','q4','q5','q6']);
  for(const [key,q] of Object.entries(day.questions)){
   assert.equal(q.date,date);assert.equal(q.day_number,13+di);
   assert.ok(q.prompt.length<170);assert.match(q.prompt,/^Name /i);
   assert.match(q.prompt,/at least|at most/i);
   assert.doesNotMatch(q.prompt,/\.csv|database|dataset|spreadsheet|\bAPI\b/i);
   assert.ok(!previousFamilies.has(q.question_family),`${date}/${key} repeated bank`);
   assert.ok(!previousTopics.has(q.topic),`${date}/${key} repeated macro topic`);
   assert.ok(!newFamilies.has(q.question_family),`${date}/${key} repeated new family`);
   assert.ok(!newTopics.has(q.topic),`${date}/${key} repeated new topic`);
   newFamilies.add(q.question_family);newTopics.add(q.topic);
   assert.ok(q.answers.length>=12&&q.answers.length<=400);
   assert.equal(q.answers.length,q.answer_scope.dataset_count);
   assert.equal(q.answer_scope.claimed_exhaustive,true);
   assert.ok(q.measurement.source_urls.length>0);
   assert.equal(q.time_limit_seconds,30);
   assert.deepEqual([...new Set(q.answers.map(a=>a.points))].sort((a,b)=>a-b),tierSet);
   const filename=`v25-${date}-${key}-${q.question_family}.csv`;
   const csv=parseCSV(readFileSync(new URL(filename,base),'utf8'));
   assert.deepEqual(csv[0],['entity_id','canonical','metric_value','points','tier','unit','source_url','source_row']);
   assert.equal(csv.length,q.answers.length+1,`${date}/${key} incomplete CSV`);
   const normalized=new Map();
   for(let i=0;i<q.answers.length;i++){
    const a=q.answers[i], row=csv[i+1];
    assert.equal(row[0],a.entity_id);assert.equal(row[1],a.canonical);
    assert.equal(Number(row[2]),a.metric_value);assert.equal(Number(row[3]),a.points);
    assert.equal(row[4],a.tier);assert.equal(row[5],q.unit);
    assert.equal(row[6],q.source);assert.equal(Number(row[7]),i+1);
    const calculated=Core.score(q,a.metric_value);
    assert.deepEqual({points:calculated.points,tier:calculated.tier},{points:a.points,tier:a.tier},`${date}/${key} numeric score`);
    for(const phrase of [a.canonical,...a.aliases.map(x=>x.input)]){
     const id=Core.norm(phrase);assert.ok(id,`${date}/${key}: empty normalized name`);
     assert.ok(!normalized.has(id)||normalized.get(id)===a.entity_id,`${date}/${key} COLLISION ${phrase} with ${normalized.get(id)}`);
     normalized.set(id,a.entity_id);
     const found=Core.exact(q,phrase);
     assert.equal(found.status,'found',`${date}/${key}: ${phrase}`);
     assert.equal(found.match.ent.entity_id,a.entity_id);
     const actual=scoreAnswer(entry.questions[Number(key.slice(1))-1],phrase);
     assert.equal(actual.points,a.points,`${date}/${key}: ${phrase} production points`);
     assert.equal(actual.metric_value,a.metric_value);
    }
   }
   assert.equal(Core.score(q,q.limit).points,1200);
   assert.equal(Core.score(q,q.direction==='above'?q.limit-1:q.limit+1).points,0);
   total+=q.answers.length;
  }
 }
 assert.equal(newTopics.size,12);assert.equal(newFamilies.size,12);
 assert.equal(readdirSync(base).filter(n=>/^v25-2026-11-0[45]-q[1-6]-.+\.csv$/.test(n)).length,12);
 assert.ok(total>300);console.log(`V25 verified: ${total} source rows across 12 complete banks`);
});

test('V25: bounded historical source anchors',()=>{
 const n4=content.get(days[0]).day.questions;
 const n5=content.get(days[1]).day.questions;
 assert.equal(n4.q1.answers.length,26);
 assert.equal(n4.q2.answers.length,37);
 assert.equal(n4.q3.answers.length,30);
 assert.equal(n4.q4.answers.length,25);
 assert.equal(n4.q5.answers.length,32);
 assert.equal(n4.q6.answers.length,30);
 assert.equal(n5.q1.answers.length,24);
 assert.equal(n5.q2.answers.length,29);
 assert.equal(n5.q3.answers.length,64);
 assert.equal(n5.q4.answers.length,30);
 assert.equal(n5.q5.answers.length,30);
 assert.equal(n5.q6.answers.length,20);
 assert.equal(Core.exact(n5.q3,'Grigori Perelman').status,'found');
 assert.equal(Core.exact(n5.q4,'Fomalhaut').status,'found');
 assert.equal(Core.exact(n5.q5,'Honshu').match.ent.metric_value,228000);
 assert.equal(Core.exact(n5.q2,'Hungary').match.ent.metric_value,15);
});
