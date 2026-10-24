import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,readdirSync} from 'node:fs';
const dayPath=new URL('../content/days/',import.meta.url);
const sources=new URL('../content/source-snapshots/',import.meta.url);
test('V23: exactly six independent question topics each redesigned day',()=>{
 const total=new Set();
 for(let day=25;day<=31;day++){
  const date=`2026-${day===31?'10':'10'}-${String(day).padStart(2,'0')}`;
  const data=JSON.parse(readFileSync(new URL(`${date}.json`,dayPath)));
  assert.equal(data.publication_status,'scheduled');
  const qs=Object.values(data.questions);
  assert.equal(qs.length,6);
  const topics=qs.map(q=>q.topic);
  assert.equal(new Set(topics).size,6,`${date}: repeated topic`);
  qs.forEach(q=>total.add(q.topic));
 }
 assert.ok(total.size>=27,`Only ${total.size} unique topics across seven days`);
});
test('V23: ten entirely new bank families have CSV snapshot matching every record',()=>{
 const files=readdirSync(sources).filter(f=>f.startsWith('v23-') && f.endsWith('.csv'));
 assert.equal(files.length,10);
 for(const name of files){
  const m=name.match(/^v23-(\d{4}-\d{2}-\d{2})-(q\d)-/);assert.ok(m,name);
  const q=JSON.parse(readFileSync(new URL(m[1]+'.json',dayPath))).questions[m[2]];
  assert.equal(q.content_revision,'v23-multidomain-complete-20261024');
  const lines=readFileSync(new URL(name,sources),'utf8').trim().split('\n');
  assert.equal(lines.length-1,q.answers.length,`${m[1]} ${m[2]}`);
  assert.equal(new Set(q.answers.map(a=>a.points)).size,7);
 }
});
