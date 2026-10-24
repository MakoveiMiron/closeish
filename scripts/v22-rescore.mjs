import fs from 'node:fs';
import path from 'node:path';
import Core from '../src/core.cjs';
const directory=new URL('../content/days/',import.meta.url);
for(const name of fs.readdirSync(directory).filter(n=>n.endsWith('.json')&&n>'2026-10-24.json')) {
 const filename=new URL(name,directory),day=JSON.parse(fs.readFileSync(filename,'utf8'));
 for(const q of Object.values(day.questions)) {
  if(q.content_revision?.startsWith('v22-')) {
   q.score_bands.forEach(b=>b.max_gap_inclusive=Math.round((b.max_gap_inclusive+Number.EPSILON)*10000)/10000);
   q.scoring_window.max_scoring_distance=q.score_bands.at(-1).max_gap_inclusive;
  }
  q.answers.forEach(a=>{const res=Core.score(q,a.metric_value);a.points=res.points;a.tier=res.tier;});
 }
 fs.writeFileSync(filename,JSON.stringify(day,null,2)+'\n');
}
