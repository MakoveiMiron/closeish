import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import Core from './core.cjs';

export const contentDir = new URL('../content/days/', import.meta.url);
const publicFields = ['id','date','day_number','topic','prompt','metric','unit','limit','direction',
  'time_limit_seconds','score_bands','scoring_window','input_max_length','source','content_revision',
  'allow_unverified_year_zero'];
export function validateDay(day, filename, ids = new Set()) {
  const fail = message => { throw new Error(`${filename}: ${message}`); };
  if(day.schema_version !== 1 || !/^\d{4}-\d{2}-\d{2}$/.test(day.date)) fail('Invalid schema/date');
  try { Core.dayNumber(day.date); } catch { fail('Invalid calendar date'); }
  if(filename !== `${day.date}.json`) fail('Filename must match date');
  if(!Number.isInteger(day.day_number) || day.day_number < 1 || typeof day.revision !== 'string' || !day.revision.trim()) fail('Invalid number/revision');
  if(!['scheduled','draft'].includes(day.publication_status)) fail('Use scheduled or draft');
  if(Object.keys(day.questions || {}).join(',') !== 'q1,q2,q3,q4,q5,q6') fail('Exactly q1…q6 required, in order');
  for(const q of Object.values(day.questions)) {
    if(typeof q.id !== 'string' || !q.id || ids.has(q.id)) fail(`Duplicate/missing ID ${q.id}`);
    ids.add(q.id);
    if(q.date !== day.date || q.day_number !== day.day_number) fail(`${q.id}: day mismatch`);
    if(typeof q.prompt !== 'string' || !q.prompt.trim() || !['above','below'].includes(q.direction)) fail(`${q.id}: prompt/direction`);
    if(!Number.isFinite(q.limit) || !Number.isFinite(q.scoring_window?.max_scoring_distance)) fail(`${q.id}: limit/window`);
    if(!Number.isInteger(q.time_limit_seconds) || q.time_limit_seconds < 1 || q.time_limit_seconds > 300) fail(`${q.id}: timer`);
    if(!Array.isArray(q.answers) || !q.answers.length) fail(`${q.id}: empty answer bank`);
    Core.score(q, q.limit); // Also validates all five bands.
    if(q.scoring_window.max_scoring_distance !== q.score_bands.at(-1).max_gap_inclusive) fail(`${q.id}: window differs from bands`);
    const entities = new Set();
    for(const a of [...q.answers, ...(q.recognized_category_candidates || []), ...(q.excluded_answers || [])]) {
      if(typeof a.canonical !== 'string' || !a.canonical.trim()) fail(`${q.id}: empty canonical`);
      if(!Array.isArray(a.aliases || []) || (a.aliases || []).some(x=>typeof x.input !== 'string')) fail(`${q.id}: invalid aliases`);
    }
    for(const a of q.answers) {
      const identity = a.entity_id || a.canonical;
      if(entities.has(identity)) fail(`${q.id}: duplicate entity ${identity}`);
      entities.add(identity);
      if(!Number.isFinite(a.metric_value)) fail(`${q.id}: scored answer needs a finite value`);
      if(Core.score(q,a.metric_value).points !== a.points) fail(`${q.id}: stored score mismatch for ${a.canonical}`);
    }
  }
  return day;
}
function lowerBound(keys, key) {
  let lo=0, hi=keys.length;
  while(lo<hi) { const mid=(lo+hi)>>>1; if(keys[mid]<key) lo=mid+1; else hi=mid; }
  return lo;
}
function compileQuestion(q) {
  const index=Core.index(q), keys=[...index.keys()].sort();
  const excluded=new Map();
  for(const a of q.excluded_answers || []) for(const name of [a.canonical,...(a.aliases||[]).map(x=>x.input)]) {
    const key=Core.norm(name), rows=excluded.get(key)||[]; rows.push(a); excluded.set(key,rows);
  }
  const sorted=[...q.answers].sort((a,b)=>b.points-a.points || Math.abs(a.metric_value-q.limit)-Math.abs(b.metric_value-q.limit) || a.canonical.localeCompare(b.canonical,'en'));
  const pools=new Map([['all',sorted],['other',q.recognized_category_candidates||[]]]);
  for(const points of [0,200,400,600,800,1000,1200]) pools.set(String(points),sorted.filter(a=>a.points===points));
  if(q.allow_unverified_year_zero) for(const key of ['all','0']) pools.set(key,[...pools.get(key),...(q.recognized_category_candidates||[])]);
  const searchTexts=new WeakMap();
  for(const a of [...sorted,...(q.recognized_category_candidates||[])]) searchTexts.set(a,[a.canonical,...(a.aliases||[]).map(x=>x.input)].map(Core.norm).join('\n'));
  return {q,index,keys,excluded,pools,searchTexts,searchCache:new Map()};
}
export function loadContent(directory=contentDir, onlyDate=null) {
  const days=new Map(), ids=new Set(), numbers=new Set();
  for(const file of fs.readdirSync(directory).filter(x=>x.endsWith('.json')&&(!onlyDate||x===onlyDate+'.json')).sort()) {
    const raw=fs.readFileSync(new URL(file, directory));
    const day=validateDay(JSON.parse(raw),file,ids);
    if(numbers.has(day.day_number)) throw new Error(`Duplicate day number ${day.day_number}`);
    numbers.add(day.day_number);
    const revision=crypto.createHash('sha256').update(raw).digest('hex').slice(0,24);
    const questions=Object.values(day.questions).map(compileQuestion);
    const publicQuestions=Object.fromEntries(questions.map(({q},i)=>['q'+(i+1),{
      ...Object.fromEntries(publicFields.filter(k=>q[k]!==undefined).map(k=>[k,q[k]])),
      answer_count:q.answers.length, candidate_count:(q.recognized_category_candidates||[]).length
    }]));
    const legacyKey=Core.progressKey({[day.day_number]:day.questions},day.day_number);
    days.set(day.date,{day,revision,questions,publicQuestions,legacyKey});
  }
  if(!days.size) throw new Error('No day files found');
  return days;
}
export function hints(compiled, raw) {
  const key=Core.norm(raw); if(!key) return [];
  const present=compiled.index.get(key);
  const expose=(row,match,dist=0)=>({ent:{canonical:row.ent.canonical},isAlias:row.isAlias,match,dist});
  if(present) return present.length===1 ? [expose(present[0],'exact')] : []; // Never silently resolve ambiguity.
  if(key.length<4) return [];
  const found=new Map();
  let inspected=0;
  for(let i=lowerBound(compiled.keys,key);i<compiled.keys.length && inspected<300;i++,inspected++) {
    const alias=compiled.keys[i]; if(!alias.startsWith(key)) break;
    const gap=alias.length-key.length;
    if(gap>Math.max(5,Math.round(alias.length*.35))) continue;
    for(const row of compiled.index.get(alias)) {
      const existing=found.get(row.ent.canonical);
      if(!existing || gap<existing.dist) found.set(row.ent.canonical,expose(row,'prefix',gap));
    }
  }
  return [...found.values()].sort((a,b)=>a.dist-b.dist || a.ent.canonical.localeCompare(b.ent.canonical,'en')).slice(0,4);
}
export function scoreAnswer(compiled, raw, automatic=false) {
  const base={raw,canonical:null,points:0,tier:'NO SCORE',kind:'unlisted',metric_value:null,autoLocked:automatic};
  const key=Core.norm(raw), rows=compiled.index.get(key)||[];
  if(rows.length!==1) {
    const outside=compiled.excluded.get(key)||[];
    if(!rows.length && outside.length===1) return {...base,canonical:outside[0].canonical,tier:'INELIGIBLE',kind:'invalid',reason:outside[0].exclusion_reason};
    return {...base,...(rows.length>1?{reason:'The name is ambiguous. Use the full catalogue name.'}:{})};
  }
  const {ent:a,isAlias}=rows[0];
  if(a.exclusion_reason) return {...base,canonical:a.canonical,tier:'INELIGIBLE',kind:'invalid',reason:a.exclusion_reason};
  if(!Number.isFinite(a.metric_value)) return {...base,canonical:a.canonical,tier:'NO VERIFIED DATA',kind:'unverified'};
  return {...base,canonical:a.canonical,metric_value:a.metric_value,...Core.score(compiled.q,a.metric_value),aliasUsed:isAlias};
}
export function catalogue(compiled,{query='',filter='all',offset=0,limit=120}={}) {
  const needle=Core.norm(query), cacheKey=filter+'|'+needle;
  let matches=compiled.searchCache.get(cacheKey);
  if(!matches) {
    const pool=compiled.pools.get(filter);
    if(!pool) throw new Error('Invalid catalogue filter');
    matches=needle?pool.filter(a=>compiled.searchTexts.get(a).includes(needle)):pool;
    // Bounded cache: at most 16 result arrays per question; bank itself is immutable.
    if(compiled.searchCache.size>=16) compiled.searchCache.delete(compiled.searchCache.keys().next().value);
    compiled.searchCache.set(cacheKey,matches);
  }
  return {total:matches.length,offset,limit,entries:matches.slice(offset,offset+limit).map(a=>({canonical:a.canonical,metric_value:a.metric_value??null,points:a.points??0,membership_status:a.membership_status}))};
}

// Production loads only the active day's large answer bank; future/historic
// JSONs are never compiled just to boot the service. Deployment validation
// still checks ALL daily packages (npm run validate).
export function createLazyContent(directory=contentDir,{cacheSize=2}={}) {
  const names=fs.readdirSync(directory).filter(x=>/^\d{4}-\d{2}-\d{2}\.json$/.test(x)).sort();
  const metadata=new Map();
  for(const file of names){
    const fd=fs.openSync(new URL(file,directory),'r');let head='';
    try{const buf=Buffer.alloc(1024);const n=fs.readSync(fd,buf,0,buf.length,0);head=buf.toString('utf8',0,n)}finally{fs.closeSync(fd)}
    const status=head.match(/"publication_status"\s*:\s*"(scheduled|draft)"/);
    if(!status)throw new Error(file+': publication status missing from JSON header');
    metadata.set(file.slice(0,10),{day:{publication_status:status[1]}});
  }
  const cache=new Map();
  return {get size(){return metadata.size},
    keys(){return metadata.keys()},
    has(date){return metadata.has(date)},
    [Symbol.iterator](){return metadata[Symbol.iterator]()},
    get(date){
      if(!metadata.has(date))return undefined;
      if(metadata.get(date).day.publication_status==='draft')return metadata.get(date);
      if(cache.has(date))return cache.get(date);
      const value=loadContent(directory,date).get(date);
      cache.set(date,value);
      if(cache.size>cacheSize)cache.delete(cache.keys().next().value);
      return value;
    }};
}
