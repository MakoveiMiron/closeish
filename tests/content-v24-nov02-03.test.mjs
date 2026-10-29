import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,readdirSync} from 'node:fs';
import Core from '../src/core.cjs';
import {loadContent,scoreAnswer} from '../src/content.mjs';

const basedir=new URL('../content/',import.meta.url);
const snapshots=new URL('./source-snapshots/',basedir);
const content=loadContent();
const dates=['2026-11-02','2026-11-03'];
function csvParse(input){
 const rows=[];let row=[],cell='',quoted=false;
 for(let i=0;i<input.length;i++){
  const c=input[i];
  if(c==='"'){if(quoted&&input[i+1]==='"'){cell+='"';i++;}else quoted=!quoted;}
  else if(c===','&&!quoted){row.push(cell);cell='';}
  else if(c==='\n'&&!quoted){row.push(cell.replace(/\r$/,''));rows.push(row);row=[];cell='';}
  else cell+=c;
 }
 if(cell||row.length){row.push(cell);rows.push(row)}
 return rows;
}

test('V24: two complete new days, 12 distinct topics, all source CSVs and all 7 tiers',()=>{
 assert.equal(content.size,14);
 assert.equal(Core.END,'2026-11-05');
 assert.equal(Core.dateForDay(11),dates[0]);
 assert.equal(Core.dateForDay(12),dates[1]);
 const topics=new Set(),families=new Set();
 const oldFamilies=new Set();
 for(const [date,{day}]of content){
  if(!dates.includes(date))for(const q of Object.values(day.questions))oldFamilies.add(q.question_family);
 }
 for(const [i,date]of dates.entries()){
  const entry=content.get(date);assert.ok(entry,`missing ${date}`);
  const d=entry.day;assert.equal(d.day_number,11+i);assert.equal(d.publication_status,'scheduled');
  assert.deepEqual(Object.keys(d.questions),['q1','q2','q3','q4','q5','q6']);
  for(const [key,q]of Object.entries(d.questions)){
   assert.equal(q.date,date);assert.equal(q.day_number,11+i);
   assert.ok(q.prompt.length<170,`${date}/${key}: verbose question`);
   assert.match(q.prompt,/^Name (an? |one of )/i);
   assert.match(q.prompt,/\bat (least|most)\b|\b(ranked\b.*\bor better)/i);
   assert.ok(!/\.csv|database|API|dataset|spreadsheet/i.test(q.prompt));
   assert.ok(!topics.has(q.topic),`${date}/${key}: topic reused`);topics.add(q.topic);
   assert.ok(!families.has(q.question_family),`${date}/${key}: family reused`);families.add(q.question_family);
   assert.ok(!oldFamilies.has(q.question_family),`${date}/${key}: 14-day bank repetition`);
   assert.equal(q.answers.length,q.answer_scope.dataset_count);
   assert.ok(q.answer_scope.claimed_exhaustive);
   assert.ok(q.answers.length>=12&&q.answers.length<=400);
   assert.ok(Array.isArray(q.measurement.source_urls)&&q.measurement.source_urls.length);
   assert.deepEqual([...new Set(q.answers.map(a=>a.points))].sort((a,b)=>a-b),[0,200,400,600,800,1000,1200]);
   const sourcefile=`v24-${date}-${key}-${q.question_family}.csv`;
   const parsed=csvParse(readFileSync(new URL(sourcefile,snapshots),'utf8'));
   assert.deepEqual(parsed[0],['entity_id','canonical','metric_value','points','tier','unit','source_url','source_row']);
   assert.equal(parsed.length,q.answers.length+1,`${date}/${key}: incomplete CSV`);
   const keys=new Set();
   for(const [ix,a]of q.answers.entries()){
    const [id,canonical,val,pts,tier,unit,url,row]=parsed[ix+1];
    assert.equal(id,a.entity_id);assert.equal(canonical,a.canonical);
    assert.equal(Number(val),a.metric_value);assert.equal(Number(pts),a.points);
    assert.equal(tier,a.tier);assert.equal(unit,q.unit);assert.equal(url,q.source);
    assert.equal(Number(row),ix+1);
    assert.equal(Core.score(q,a.metric_value).points,a.points);
    for(const answer of [a.canonical,...a.aliases.map(x=>x.input)]){
     const norm=Core.norm(answer);
     assert.ok(norm);
     assert.ok(!keys.has(norm)||keys.has(norm)&&Core.exact(q,answer).match?.ent.entity_id===a.entity_id,`${date}/${key}: alias collision ${answer}`);
     keys.add(norm);
     const resolved=Core.exact(q,answer);
     assert.equal(resolved.status,'found',`${date}/${key}: unresolvable alias ${answer}`);
     assert.equal(resolved.match.ent.entity_id,a.entity_id,`${date}/${key}: collision ${answer}`);
    }
    const scored=scoreAnswer(entry.questions[Number(key.slice(1))-1],a.canonical);
    assert.equal(scored.points,a.points);
    assert.equal(scored.metric_value,a.metric_value);
   }
  }
 }
 assert.equal(topics.size,12);
 assert.equal(families.size,12);
 assert.equal(readdirSync(snapshots).filter(f=>/^v24-2026-11-0[23]-q\d-.+\.csv$/.test(f)).length,12);
});

test('V24: special source anchors and non-colliding language notation',()=>{
 const tour=content.get(dates[0]).day.questions.q2;
 assert.equal(tour.answers.find(a=>a.canonical==='Stage 19').metric_value,93.1);
 assert.equal(tour.answers.length,21);
 const tiobe=content.get(dates[1]).day.questions.q3;
 assert.equal(tiobe.unit,'percentage points');
 assert.equal(tiobe.answers.length,20);
 assert.equal(Core.exact(tiobe,'C').match.ent.canonical,'C');
 assert.equal(Core.exact(tiobe,'C++').match.ent.canonical,'C++');
 assert.equal(Core.exact(tiobe,'C#').match.ent.canonical,'C#');
 const human=content.get(dates[1]).day.questions.q4;
 assert.equal(human.answers.length,24);
});
