"""Reconcile the 419 originally pending day-one Q/A links from independently inspected sources.
Source notes: original frozen UNESCO snapshot; Plotly Gapminder_unfiltered.csv; UNGEGN Edinburgh;
GeoNames Cardiff; Australian Antarctic Division; Macau city-state definition.
No inferred zero values, no deletion of legitimate category members.
"""
from pathlib import Path
import json, csv, math, collections
R=Path(__file__).resolve().parents[1]
P=R/'days/day-01.json'
original=json.loads(P.read_text())
if all(q.get('content_revision')=='clean-day-2026-10-20-v2-verification' for q in original.values()):
 print('Already reconciled; no changes needed.')
 raise SystemExit(0)
assert sum(len(q['recognized_category_candidates']) for q in original.values())==419
SOURCE_UNFILTERED='https://github.com/plotly/datasets/blob/master/gapminder_unfiltered.csv'
ALIAS_TO_EXISTING={
    'Ivory Coast': "Cote d'Ivoire",
    'Democratic Republic of the Congo': 'Congo, Dem. Rep.',
    'Republic of the Congo': 'Congo, Rep.',
    'The Gambia': 'Gambia',
    'Hong Kong': 'Hong Kong, China',
    'South Korea': 'Korea, Rep.',
    'Slovakia': 'Slovak Republic',
    'Yemen': 'Yemen, Rep.',
}
CAPE={'1952': {'pop':155037,'gdpPercap':594.7341659},'2007':{'pop':423613,'gdpPercap':3205.479398}}
# Source original unfiltered: complete 1952+2007 for 137 countries;
# the following unresolved category labels have only the indicated year in the inspected file.
ONLY_1952={'Luxembourg'}
ONLY_2007=set('''Armenia|Aruba|Azerbaijan|Barbados|Belarus|Belize|Bhutan|Brunei|Cyprus|Estonia|Fiji|French Polynesia|Georgia|Grenada|Guyana|Kazakhstan|Latvia|Lithuania|Maldives|Malta|Moldova|New Caledonia|Papua New Guinea|Qatar|Russia|Samoa|Solomon Islands|Suriname|Tajikistan|The Bahamas|Tonga|Turkmenistan|Ukraine|United Arab Emirates|Uzbekistan|Vanuatu'''.split('|'))
CITIES={
 'Scotland':(55.95,'Edinburgh','https://ungegn.un.org/dashboard/cities/details?id=268'),
 'Wales':(51.48,'Cardiff','https://www.geonames.org/2653822'),
}
UNSCOREABLE={
 'Heard Island and McDonald Islands':('No inhabited capital or capital coordinate; Australian Antarctic Division confirms Australian external territory administered from Australia.','https://www.antarctica.gov.au/about-antarctica/australia-in-antarctica/the-territory-of-heard-island-and-mcdonald-islands/'),
 'Macau':('City-like special administrative region without a separate capital city. Do not treat Macau itself as a separately located capital.','https://en.wikipedia.org/wiki/Outline_of_Macau'),
}
UNESCO={r['id']:r for r in json.loads((R/'datasets/unesco-property-areas-2026.json').read_text())['records']}
TIERS={1200:'PERFECT HIT',1000:'RAZOR EDGE',800:'CLOSE CALL',600:'SOLID HIT',400:'IN THE ZONE',200:'ON THE BOARD'}
results=[]
def score(q,value):
 gap=value-q['limit'] if q['direction']=='above' else q['limit']-value
 if gap<0:return 0,'CROSSED LIMIT'
 if gap==0:return 1200,'PERFECT HIT'
 for b in q['score_bands']:
  if gap<=b['max_gap_inclusive']:return b['points'],TIERS[b['points']]
 return 0,'TOO FAR'
def append_audit(k,ent,kind,measurement='',points='',source='',note=''):
 results.append(dict(question=k,entity_id=ent['entity_id'],original_name=ent['canonical'],resolution=kind,metric_value=measurement,points=points,source_url=source,notes=note))
def append_measured(q,ent,value,refs,provenance):
 if isinstance(value,float):assert math.isfinite(value)
 rec={k:v for k,v in ent.items() if k not in ('review_status','measurement_status')}
 pts,tier=score(q,value)
 rec.update(metric_value=value,points=pts,tier=tier,verified_status='source_verified',source_refs=refs,measurement_status='source_verified',measurement_provenance=provenance)
 q['answers'].append(rec)
 return pts
for k,q in original.items():
 remain=[]
 for ent in q['recognized_category_candidates']:
  n=ent['canonical']
  if k=='q1':
   prop=UNESCO[ent['entity_id'][len('unesco-'):]]
   v=prop.get('area_hectares_decimal')
   typ='UNESCO_RECORD_NO_AREA' if v is None else 'UNESCO_RECORD_ZERO_NOT_VERIFIED_AREA'
   ent['review_status']='official_area_missing_or_zero_unresolved'
   ent['verification_note']='UNESCO bulk field is null or zero; no positive inscribed-property area has been independently established. Not equivalent to 0 hectares.'
   append_audit(k,ent,typ,'','',prop['url'],ent['verification_note'])
   remain.append(ent)
  elif k=='q3':
   if n in CITIES:
    lat,city,url=CITIES[n]
    value=int(math.floor(abs(lat)*111.195/100+0.5)*100)
    pts=append_measured(q,ent,value,[{'source_id':'manual-capital-city-check-2026','locator':url}],f'{city}; latitude={lat} degrees; abs(latitude)*111.195 km, rounded to nearest 100 km')
    append_audit(k,ent,'MEASURED_FROM_VERIFIED_CAPITAL',value,pts,url,'Latitude source is named and auditable; no synthetic coordinate.')
   else:
    why,url=UNSCOREABLE[n]
    ent['review_status']='not_applicable_no_separate_capital'
    ent['measurement_status']='not_applicable'
    ent['verification_note']=why
    append_audit(k,ent,'NOT_APPLICABLE_NO_CAPITAL','','',url,why)
    remain.append(ent)
  else:
   if n in ALIAS_TO_EXISTING:
    target=next(a for a in q['answers'] if a['canonical']==ALIAS_TO_EXISTING[n])
    if not any(a.get('input')==n for a in target['aliases']):
     target['aliases'].append({'input':n,'kind':'geographical_common_name','action':'replace_with_canonical'})
    append_audit(k,ent,'ALIAS_OF_ALREADY_MEASURED',target['metric_value'],target['points'],target['source_refs'][0]['locator'],f'Reconciled with {target["canonical"]}; not a separate country or measurement.')
   elif n=='Cape Verde':
    p0,p1=CAPE['1952'],CAPE['2007']
    if k=='q4':val=int(math.floor(p0['pop']/p1['pop']*100+0.5))
    elif k=='q5':val=int(math.floor((p1['gdpPercap']-p0['gdpPercap'])/100+0.5)*100)
    else:val=int(math.floor((p1['pop']-p0['pop'])/100000+0.5)*100000)
    pts=append_measured(q,ent,val,[{'source_id':'gapminder-plotly-unfiltered-1952-2007','locator':SOURCE_UNFILTERED+'; Cape Verde 1952 and 2007'}],f'1952 pop={p0["pop"]}, 2007 pop={p1["pop"]}; 1952 gdpPercap={p0["gdpPercap"]}, 2007 gdpPercap={p1["gdpPercap"]}')
    append_audit(k,ent,'MEASURED_WITH_SAME_GAPMINDER_SERIES',val,pts,SOURCE_UNFILTERED,'1952 and 2007 values verified in unfiltered original Gapminder data.')
   else:
    if n in ONLY_1952:qualifier='1952 exists; 2007 absent'
    elif n in ONLY_2007:qualifier='2007 exists; 1952 absent'
    else:qualifier='No complete 1952/2007 pair found under checked labels in this Gapminder extract'
    ent['review_status']='gapminder_historical_pair_unavailable'
    ent['measurement_status']='unverified'
    ent['verification_note']=qualifier+'; do not infer 0 or mix incompatible GDP per capita series.'
    append_audit(k,ent,'HISTORICAL_PAIR_UNAVAILABLE','','',SOURCE_UNFILTERED,ent['verification_note'])
    remain.append(ent)
 q['recognized_category_candidates']=remain
 q['verified_answer_count']=len(q['answers'])
 q['recognized_category_candidate_count']=len(remain)
 q['catalogued_answer_count']=len(q['answers'])+len(remain)
 q['alias_count']=sum(len(a.get('aliases',[])) for a in q['answers']+remain)
 q['score_distribution_audit']={str(p):sum(a['points']==p for a in q['answers']) for p in [1200,1000,800,600,400,200,0]}
 q['content_revision']='clean-day-2026-10-20-v2-verification'
 q['verification_status']='verified_source_snapshot_with_remaining_gaps'
 q['research_status']='partially_reconciled_source_gaps_reported'
 q['editorial_status']='research_preview'
 if k in ('q4','q5','q6'):
  q['source_refs'] += ['gapminder-plotly-unfiltered-1952-2007']
  q['answer_scope']['note']+=' Pending 1952/2007 country and territory data reviewed against unfiltered Gapminder; 1952 missing for many.'
 if k=='q3':q['source_refs']+=['ungegn-edinburgh-2026','geonames-cardiff-2026']
assert len(results)==419
assert len({(r['question'],r['entity_id']) for r in results})==419
R.joinpath('days/day-01.json').write_text(json.dumps(original,ensure_ascii=False,indent=2)+'\n')
S=R/'datasets/gapminder-unfiltered-1952-2007-added.json'
S.write_text(json.dumps({'source_url':SOURCE_UNFILTERED,'selection':'Original unfiltered Gapminder country historical records with both requested years previously omitted from frozen filtered day dataset. Entity aliases were reconciled against existing canonical answers.','Cape Verde':CAPE},ensure_ascii=False,indent=2)+'\n')
A=R/'ELLENORZES-419.csv'
with A.open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(results)
# Up-to-date question audit
with (R/'QUESTION-AUDIT.csv').open('w',newline='',encoding='utf-8') as f:
 keys=['round','question','topic','limit','metric','recognized_entities','measured_entities','unverified_measurements','1200','1000','800','600','400','200','0','status']
 w=csv.DictWriter(f,fieldnames=keys);w.writeheader()
 for i,(k,q) in enumerate(original.items(),1):
  w.writerow(dict(round=i,question=q['prompt'],topic=q['topic'],limit=q['limit'],metric=q['metric'],recognized_entities=q['catalogued_answer_count'],measured_entities=q['verified_answer_count'],unverified_measurements=q['recognized_category_candidate_count'],**q['score_distribution_audit'],status='source_recheck_pending_for_some'))
summary=collections.Counter(r['resolution'] for r in results)
print('419 original candidate links:',summary)
print('pending',sum(len(q['recognized_category_candidates']) for q in original.values()))
print('measured',sum(len(q['answers']) for q in original.values()))
for k,q in original.items():print(k,len(q['answers']),len(q['recognized_category_candidates']),q['score_distribution_audit'])
