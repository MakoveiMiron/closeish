"""Reproducible factual/scoring and editorial-blocker audit for CLOSEISH.

Usage: python tools/strict_content_audit.py
Exit status zero means *auditor ran*; the output expressly distinguishes NOT READY.
Use --fail-on-editorial to reject a release when any publishing condition fails.
"""
from pathlib import Path
from collections import Counter,defaultdict
from datetime import date,timedelta
import unicodedata,hashlib,sys,json,csv,math,re
R=Path(__file__).resolve().parents[1]
new=[json.loads((R/'days'/f'day-{d:02}.json').read_text()) for d in range(2,8)]
first=json.loads((R/'days'/'day-01.json').read_text())
rows=[];summary=[];errors=[];warnings=[];entities_all=set();ids_all=set();sources=Counter();topics=Counter();cross_source=defaultdict(set)

def norm(s):
 s=unicodedata.normalize('NFKD',s or '').casefold()
 return ''.join(c for c in s if c.isalnum())

def flag(day,rnd,kind,desc,hard=True):
 (errors if hard else warnings).append({'day':day,'round':rnd,'kind':kind,'detail':desc})

for di,bank in enumerate(new,2):
 assert list(bank)==[f'q{x}' for x in range(1,7)]
 daily_topics=[];daily_sources=[];family=[]
 for no,q in enumerate(bank.values(),1):
  z=f'day {di} q{no}';measured=q.get('answers') or [];pending=q.get('recognized_category_candidates') or [];scale=Counter(); zero=Counter();arr=[]
  ids=set();aliases=defaultdict(set); val_by_id={}
  source_id=q.get('source_refs',['unattributed'])[0]; sources[source_id]+=1;daily_sources.append(source_id)
  family.append(q.get('question_family',''))
  topics[q['topic']]+=1;daily_topics.append(q['topic'])
  for ent in measured+pending:
   id=ent.get('entity_id');canonical=ent.get('canonical','')
   if not canonical:flag(di,no,'empty_name',str(id))
   if id in ids:flag(di,no,'duplicate_id',str(id))
   ids.add(id)
   ids_all.add(id);entities_all.add(norm(canonical));cross_source[norm(canonical)].add(source_id)
   for alias in [canonical]+[a.get('input','') if isinstance(a,dict) else str(a) for a in ent.get('aliases',[])]:
    if norm(alias):aliases[norm(alias)].add(id)
  ambiguous={a:who for a,who in aliases.items() if len(who)>1}
  if ambiguous:flag(di,no,'alias_ambiguity',f'{len(ambiguous)} aliases refer to multiple IDs; examples: {list(ambiguous)[:8]}',hard=False)
  for ent in measured:
   val=ent.get('metric_value')
   if not isinstance(val,(float,int)) or isinstance(val,bool) or not math.isfinite(val):flag(di,no,'invalid_numeric',ent.get('canonical','?'));continue
   gap=val-q['limit'] if q['direction']=='above' else q['limit']-val
   if gap<0:expect=0;tier='CROSSED LIMIT'
   elif gap==0:expect=1200;tier='PERFECT HIT'
   else:
    fit=next((b for b in q['score_bands'] if gap<=b['max_gap_inclusive']),None)
    if fit:expect=fit['points'];tier=fit['tier']
    else:expect=0;tier='TOO FAR'
   if ent.get('points')!=expect or ent.get('tier')!=tier:flag(di,no,'score_mismatch',f'{ent.get("canonical")}: stored {ent.get("points")}/{ent.get("tier")} expected {expect}/{tier}')
   if q['unit']=='%' and not isinstance(val,int):flag(di,no,'noninteger_percent',ent['canonical'])
   scale[expect]+=1
   if expect==0:zero[tier]+=1
  for ent in pending:
   if ent.get('metric_value') is not None or ent.get('points') is not None:flag(di,no,'imputed_unknown',ent.get('canonical'))
  if sorted(set(b['max_gap_inclusive'] for b in q['score_bands']))!=[b['max_gap_inclusive'] for b in q['score_bands']]:flag(di,no,'overlapping_score_bands','Nonmonotonic score bands')
  if set([0,200,400,600,800,1000,1200])-set(scale):flag(di,no,'missing_score_tier',str(dict(scale)))
  if q.get('score_distribution_audit')!={str(x):scale[x] for x in [1200,1000,800,600,400,200,0]}:flag(di,no,'stale_score_summary',str(q.get('id')))
  if q['limit']<50 and q['unit']!='%':flag(di,no,'too_small_limit',str(q['limit']))
  if q['unit']=='%' and not 8<=q['limit']<=92:flag(di,no,'percent_limit_outside',str(q['limit']))
  if q['unit']=='%' and 'nearest whole percent' not in q['prompt'].lower():flag(di,no,'hidden_percentage_rounding',q['prompt'])
  if any(not ent.get('source_refs') for ent in measured):flag(di,no,'answer_without_source_ref','Some measured entities lack source locator')
  if q['editorial_status']!='RESEARCH_DRAFT_NOT_PUBLISHABLE':flag(di,no,'premature_publication','Draft question is not clearly blocked')
  n=len(measured);un=len(pending)
  if n<3000 and not q.get('answer_scope',{}).get('claimed_exhaustive'):flag(di,no,'incomplete_open_category',f'{n} measured + {un} pending; source subset NOT proven globally complete',hard=False)
  for score in [1200,1000,800,600,400,200,0]:
   # one row per real tier, plus separate 0 outcomes for downstream audit
   rows.append({'date':q['date'],'day':di,'round':no,'question':q['prompt'],'topic':q['topic'],'source_family':source_id,'question_family':q['question_family'],'score':score,'count':scale[score],'total_measured':n,'unverified':un,'source':q['source'],'catalogue_scope':q.get('answer_scope',{}).get('coverage','unknown'),'status':'RESEARCH_DRAFT_NOT_PUBLISHABLE'})
  for typ in ['TOO FAR','CROSSED LIMIT']:
   rows.append({'date':q['date'],'day':di,'round':no,'question':q['prompt'],'topic':q['topic'],'source_family':source_id,'question_family':q['question_family'],'score':'0 – '+typ,'count':zero[typ],'total_measured':n,'unverified':un,'source':q['source'],'catalogue_scope':q.get('answer_scope',{}).get('coverage','unknown'),'status':'RESEARCH_DRAFT_NOT_PUBLISHABLE'})
  summary.append({'day':di,'round':no,'topic':q['topic'],'source_family':source_id,'metric_family':q['question_family'],'question':q['prompt'],'measured':n,'unverified':un,'recognized':n+un,'tier_counts':{str(k):scale[k] for k in [1200,1000,800,600,400,200,0]},'scope':q.get('answer_scope',{}),'has_ambiguous_alias':bool(ambiguous),'is_globally_exhaustive':bool(q.get('answer_scope',{}).get('claimed_exhaustive',False))})
 if len(set(daily_topics))!=6:flag(di,'ALL','daily_topics_not_distinct',f'{len(set(daily_topics))} topics across 6 rounds: {daily_topics}')
 if len(set(daily_sources))!=6:flag(di,'ALL','daily_sources_not_distinct',f'{len(set(daily_sources))} source IDs across 6 rounds: {daily_sources}')
 if di>2:
  prev_sources={q.get('source_refs',['unattributed'])[0] for q in new[di-3].values()}
  repeat=prev_sources.intersection(daily_sources)
  if repeat:flag(di,'ALL','source_repeated_across_adjacent_days',', '.join(sorted(repeat)))

if len(sources)!=36:flag('ALL','ALL','source_concentration',f'36 questions from {len(sources)} source-family identifiers, most repeated: {sources.most_common(9)}')
if len(set(f['metric_family'] for f in summary))!=36:flag('ALL','ALL','metric_families_repeated','Metric family not unique')
# Different labels for metrics from the same category DO NOT prove source independence.
if max(sources.values())>2:flag('ALL','ALL','source_family_overrepresented',f'{sources.most_common(8)}')

out=R/'QUESTION-AUDIT-36-DETAILED.csv'
with out.open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
result={'date':'2026-10-21','publication_approved':False,'total_questions':36,'unique_topics':len(topics),'unique_source_families':len(sources),
        'total_scored_records':sum(x['measured'] for x in summary),'total_recognized_unverified':sum(x['unverified'] for x in summary),
        'unique_canonical_names':len(entities_all),'unique_source_entity_ids':len(ids_all),
        'cross_source_name_collisions':sum(len(v)>1 for v in cross_source.values()),
        'source_question_counts':dict(sources),'topic_question_counts':dict(topics),
        'blocking_failures':errors,'warnings':warnings,'questions':summary}
(R/'docs'/'STRICT-AUDIT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
header=['# CLOSEISH – szigorú tartalmi és lefedettségi audit','',
        '**ÁLLAPOT: NEM PUBLIKÁLHATÓ – kutatási részkiadás (2026-10-21).**','',
        'Ez a jelentés a szerkesztett új 36 kérdés teljes pontozási adatát ellenőrzi, de az ismert források teljes világbeli lefedettségét önmagában nem tudja igazolni.','',
        '## Összesítő','',
        f'- Új kérdések: **36**; felismert számos rekord: **{result["total_scored_records"]:,}**; mérési adatra vár: **{result["total_recognized_unverified"]:,}**.',
        f'- Forrásonként különböző kanonikus nevek a teljes időszakban: **{result["unique_canonical_names"]:,}**. Ez nem feltétlenül egyenlő a valóban különböző biológiai/történeti entitások számával.',
        f'- Kérdésben használt forráscsalád-azonosítók: **{len(sources)}**; hard blokk: **{len(errors)}**; figyelmeztetés: **{len(warnings)}**.',
        '', '## Napokra bontott adatsorok','', '| Nap/Q | Téma | Felismert | Mért | Hiányzó | Adatforrás |', '|---|---|---:|---:|---:|---|']
for q in summary:
 header.append(f'| {q["day"]}/Q{q["round"]} | {q["topic"]} | {q["recognized"]:,} | {q["measured"]:,} | {q["unverified"]:,} | {q["source_family"]} |')
header.extend(['', '## Publikálást akadályozó hibák', ''])
for issue in errors:header.append(f'- **{issue["kind"]}** ({issue["day"]}/Q{issue["round"]}): {issue["detail"]}')
header.extend(['', '## Nyitott minőségi figyelmeztetések',''])
for issue in warnings[:80]:header.append(f'- **{issue["kind"]}** ({issue["day"]}/Q{issue["round"]}): {issue["detail"]}')
if len(warnings)>80:header.append(f'- (További {len(warnings)-80} figyelmeztetés a JSON-állományban.)')
header.extend(['','## Új helyi források és korlátjaik','',
 '- Az állatok a ggplot2 `msleep` 83 rekordos történeti mintájából származnak, nem az állatfajok teljes jegyzékéből.',
 '- A CSS4 színnevek a Matplotlib 148 elemű, CSS4-kompatibilis listájából kerültek be.',
 '- A texasi ingatlanárak a `txhousing` 2010. márciusi MLS-városi mintáján alapulnak.',
 '- A korábbi elnökök csak 1953–2009 hivatalba lépett személyeinek helyi, 11 elemű mintájából származnak.',
 '- A járművek csak az `mpg` 2008. évi, 38 darabos népszerűmodell-mintájából származnak.',
 '- A `statecrime` 2009. évi adatai 50 államot és DC-t fednek le. Illinois és Minnesota erőszakos bűnözési rátáinál a forrás külön UCR-módszertani hiányt jelez.',
 '- Más új kérdések továbbra is a korábbi Gapminder, elemtáblázat, megyei térképi és UNESCO-adatbankokon osztoznak.',
 '', '## Nem teljesült követelmények','',
 'A 36 kérdés még nem alkot 36 egymástól független, kreatív tudásfeladatot. A teljes globális forráslefedettség nincs meg, és több nap szomszédos forrásokat ismétel. Nem állítható, hogy minden jogosult válasz szerepel. A böngészőtesztek a működést, nem a világszintű teljességet bizonyítják.',
 '', 'A `QUESTION-AUDIT-36-DETAILED.csv` mind a 36 kérdés mind a hét pontkategóriáját és a két nulla pontos okot rögzíti.',''])
(R/'docs'/'COVERAGE-REPORT-2026-10-21.md').write_text('\n'.join(header),encoding='utf8')
print('AUDIT:',len(summary),'question banks;',result['total_scored_records'],'measured;',result['total_recognized_unverified'],'unverified;',len(sources),'source families;',len(errors),'blocking failures;',len(warnings),'warnings')
print('Not publishable:',not result['publication_approved'])
if '--fail-on-editorial' in sys.argv and errors:sys.exit(2)
