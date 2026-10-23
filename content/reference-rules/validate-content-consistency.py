#!/usr/bin/env python3
"""CLOSEISH offline structural/semantic checks; no claim of external source verification.
Usage: python content/reference-rules/validate-content-consistency.py
Optional: pip install jsonschema for formal day.schema.json validation.
"""
from pathlib import Path
from datetime import date
import collections,glob,json,math,sys,unicodedata,re
from decimal import Decimal
ROOT=Path(__file__).resolve().parent.parent
DAYS=ROOT/'days'
errors=[]; warnings=[]; counts=collections.Counter(); ids=set(); qindex=[]
score_points=(1000,800,600,400,200)
tier_names=('RAZOR EDGE','CLOSE CALL','SOLID HIT','IN THE ZONE','ON THE BOARD')
def norm(t):return unicodedata.normalize('NFKC',t).strip().casefold()
def folded(t):return ''.join(c for c in unicodedata.normalize('NFKD',t) if not unicodedata.combining(c)).casefold().strip()
def err(where, why):errors.append(f'{where}: {why}')
def score(q,val):
 gap=(Decimal(str(q['limit']))-Decimal(str(val))) if q['direction']=='below' else (Decimal(str(val))-Decimal(str(q['limit'])))
 if gap<0:return (0,'CROSSED LIMIT')
 if gap==0:return (1200,'PERFECT HIT')
 for band in q['score_bands']:
  if gap<=Decimal(str(band['max_gap_inclusive'])):return (band['points'],band['tier'])
 return (0,'TOO FAR')
try:
 from jsonschema import Draft202012Validator,FormatChecker
 schema=json.loads((ROOT/'day.schema.json').read_text('utf-8'))
 checker=Draft202012Validator(schema,format_checker=FormatChecker())
 schema_checked=True
except ImportError:
 checker=None; schema_checked=False
 warnings.append('jsonschema nincs telepítve: a formai JSON Schema ellenőrzés kimaradt (a belső ellenőrzések futnak).')
for p in sorted(DAYS.glob('*.json')):
 day=p.stem
 try:d=json.loads(p.read_text('utf-8'))
 except Exception as e:err(day,'JSON parsing: '+str(e));continue
 counts['days']+=1
 if p.stem!=d['date']:err(day,'filename mismatch')
 if d['day_number']!=(date.fromisoformat(day)-date(2026,10,23)).days+1:err(day,'day_number mismatch')
 if d['publication_status'] not in ('scheduled','draft'):err(day,'publication_status')
 if checker:
  for e in checker.iter_errors(d):err(day,'schema '+str(list(e.path))+': '+e.message)
 if set(d['questions'])!={f'q{i}' for i in range(1,7)}:err(day,'not exactly 6 questions')
 for qn,q in d['questions'].items():
  where=f'{day}/{qn}';counts['questions']+=1
  if q['id'] in ids:err(where,'duplicate question id '+q['id'])
  ids.add(q['id'])
  if q['date']!=day or q['day_number']!=d['day_number']:err(where,'date/day_number inconsistent')
  if q['time_limit_seconds']!=30:err(where,'not 30 seconds')
  is_below=q['direction']=='below'
  if q['comparison']!=('at_most' if is_below else 'at_least'):err(where,'comparison/direction mismatch')
  if q['approach_rule']['required_side']!=('from_below' if is_below else 'from_above'):err(where,'required_side/direction mismatch')
  if q['approach_rule']['operator']!=('<=' if is_below else '>='):err(where,'operator/direction mismatch')
  if len(q['score_bands'])!=5:err(where,'incorrect score band length')
  prev=-math.inf
  for i,b in enumerate(q['score_bands']):
   if b['points']!=score_points[i] or b['tier']!=tier_names[i]:err(where,'invalid score tier '+str(i))
   if b['max_gap_inclusive']<=prev:err(where,'non-increasing score band')
   prev=b['max_gap_inclusive']
  if q['scoring_window']['max_scoring_distance']!=prev:err(where,'incorrect scoring window max distance')
  if q['scoring_window']['units']!=q['unit']:err(where,'unit/scoring_window mismatch')
  names=collections.defaultdict(set)
  names_fold=collections.defaultdict(set)
  eids=set()
  for i,a in enumerate(q['answers']):
   counts['answers']+=1
   if a['entity_id'] in eids:err(where,'duplicate answer entity_id: '+a['entity_id'])
   eids.add(a['entity_id'])
   v=a.get('metric_value')
   if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):err(where,f'answer[{i}] nonnumeric metric');continue
   if (a['points'],a['tier'])!=score(q,v):err(where,f'answer[{i}] points/tier wrong for value {v}')
   for name in [a['canonical']]+[al['input'] for al in a.get('aliases',[])]:
    if name.strip():
     names[norm(name)].add(a['entity_id'])
     names_fold[folded(name)].add(a['entity_id'])
  for name,entities in names.items():
   if len(entities)>1:err(where,f'AMBIGUOUS NAME {name}: '+','.join(sorted(entities)))
  for name,entities in names_fold.items():
   if len(entities)>1:err(where,f'AMBIGUOUS DIACRITIC-FOLDED NAME {name}: '+','.join(sorted(entities)))
  for c in q.get('recognized_category_candidates',[]):
   if c.get('metric_value') is not None:err(where,'recognized candidate metric_value non-null')
  qindex.append({'date':day,'id':q['id'],'topic':q['topic'],'prompt':q['prompt'],'direction':q['direction'],'limit':q['limit'],'unit':q['unit'],'answers':len(q['answers']),'content_revision':q.get('content_revision','')})
index=json.loads((ROOT/'question-index.json').read_text('utf-8'))
if index!=qindex:err('question-index.json','index differs from day files (including order/fields/revisions)')
print('CLOSEISH offline validator')
print('days',counts['days'],'questions',counts['questions'],'answers',counts['answers'],'schema_checked',schema_checked)
for w in warnings:print('WARNING:',w)
for e in errors[:100]:print('ERROR:',e)
print('TOTAL ERRORS',len(errors))
sys.exit(1 if errors else 0)
