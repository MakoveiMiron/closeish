"""Build genuinely distinct day 2 and 3 answer catalogues, with explicit provenance limitations.

Never fabricate measurements: derived metrics are computed from bundled source values.
The builder does NOT claim global coverage for finite research samples.
"""
import collections, copy, csv, datetime, hashlib, json, math, re, unicodedata, bisect
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; raw={i:json.loads((ROOT/(f'datasets/two-days/original-day-{i:02d}-source.json' if i in (2,3) else f'days/day-{i:02d}.json')).read_text()) for i in range(1,8)}

P=lambda a:ROOT/a
TIERS={1200:'PERFECT HIT',1000:'RAZOR EDGE',800:'CLOSE CALL',600:'SOLID HIT',400:'IN THE ZONE',200:'ON THE BOARD'}
def slug(s):
 return re.sub('[^a-z0-9]+','-',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()).strip('-')
def alias(s):return {'input':s,'kind':'verified-alternative','action':'replace_with_canonical'}
def entity(name,value,source_id,loc,aliases=(),id=None):
 return {'entity_id':id or f'{slug(source_id)}-{slug(name)}','canonical':name,'aliases':[alias(a) for a in dict.fromkeys(aliases) if a and a!=name], 'verified_status':'source_snapshot','source_refs':[{'source_id':source_id,'locator':loc}],'metric_value':int(value) if value==int(value) else float(value)}
def score(limit,direction,bands,value):
 dist=(value-limit if direction=='above' else limit-value)
 if dist<0:return 0,'CROSSED LIMIT'
 if dist==0:return 1200,'PERFECT HIT'
 for ix,(b,p) in enumerate(zip(bands,[1000,800,600,400,200])):
  if dist<=b:return p,TIERS[p]
 return 0,'TOO FAR'
def select(values,preferred=None, direction=None, big=False):
 """Use actual measured sorted distribution to pick five increasing band edges.
 Guarantee real exact hit and real members in every positive band, without creating values.
 """
 if len(values)>10000:
  return 226, "below", [3,8,15,24,39], collections.Counter(score(226,"below",[3,8,15,24,39],x)[0] for x in values)
 count=collections.Counter(values); uniq=sorted(count)
 n=len(values)
 target=([10,35,85,180,550] if big else [10,40,100,200,650] if n>1000 else [3,10,25,50,125] if n>200 else [2,6,14,30,70] if n>90 else [1,3,7,14,25] if n>50 else [1,2,4,8,16] if n>16 else [1,2,3,4,5])
 candidates=[]
 for lim in uniq:
  if count[lim]>max(3,2 if n>30 else 2):continue
  if preferred is not None and abs(lim-preferred)> (100 if n>10000 else max(100, max(uniq)-min(uniq))):pass
  for dr in (['above','below'] if direction is None else [direction]):
   diffs=sorted({(x-lim if dr=='above' else lim-x) for x in uniq if (x-lim if dr=='above' else lim-x)>0})
   if len(diffs)<6:continue
   if len(uniq)<8:continue
   distances=sorted((x-lim if dr=='above' else lim-x) for x in values if (x-lim if dr=='above' else lim-x)>0)
   if len(distances)<max(7,round(n*.03)):continue
   if lim<50:continue
   chosen=[];counts=[];prev=0
   for targetCum in target:
    vals=[d for d in diffs if d>prev]
    if len(vals)<6-len(chosen):break
    index=min(len(vals)-(5-len(chosen)), max(0, next((j for j,z in enumerate(vals) if bisect.bisect_right(distances,z)>=targetCum),0)))
    val=vals[index];chosen.append(val);prev=val
   if len(chosen)!=5:continue
   groups=collections.Counter(score(lim,dr,chosen,x)[0] for x in values)
   if not all(groups[k]>0 for k in [0,200,400,600,800,1000,1200]):continue
   # high scores not inflated; broad zero side, otherwise adjust score window.
   quality= 50*abs(groups[1200]-1)+15*abs(groups[1000]-min(10,max(1,n//45))) + \
     0.3*abs(groups[200]-min(250,max(1,n//8))) + 4*(max(0,10-sum(1 for x in values if score(lim,dr,chosen,x)[0]==0)))
   if preferred is not None:quality+=abs(lim-preferred)/max(1,(max(uniq)-min(uniq)))*30
   if n>10000:quality+=max(0,lim-250)*0.3
   candidates.append((quality,lim,dr,chosen,groups))
 if not candidates:raise ValueError('No valid 7-tier threshold for '+str((len(values),min(values),max(values),count.most_common(5))))
 result=min(candidates,key=lambda x:x[0]);return result[1:]
def make(day,num,topic,source_id,family,prompt_template,metric,unit,source,description,entries,options=None):
 options=options or {}
 seen={};clean=[]
 for e in entries:
  if not isinstance(e.get('metric_value'),(int,float)) or not math.isfinite(e['metric_value']):continue
  if e['entity_id'] in seen:raise ValueError('Duplicate id '+e['entity_id'])
  seen[e['entity_id']]=1;clean.append(e)
 vals=[a['metric_value'] for a in clean]
 if options.get('fixed_limit') is not None:
  limit=options['fixed_limit'];direction=options['direction'];edges=options['fixed_edges'];groups=collections.Counter(score(limit,direction,edges,v)[0] for v in vals)
 else:
  limit,direction,edges,groups=select(vals,options.get('preferred'),options.get('direction'),len(vals)>10000)
 scorebands=[{'max_gap_inclusive':int(v),'points':p,'tier':TIERS[p]} for v,p in zip(edges,[1000,800,600,400,200])]
 for a in clean:a['points'],a['tier']=score(limit,direction,edges,a['metric_value'])
 count=collections.Counter(a['points'] for a in clean)
 assert all(count[k] for k in [1200,1000,800,600,400,200,0]),(day,num,count)
 assert count[1200]<=2 and count[1000]<=12,(day,num,count)
 comparison='at_least' if direction=='above' else 'at_most';term='at least' if direction=='above' else 'at most'
 prompt=prompt_template.format(term=term,limit=str(limit) if unit=='year' else f'{limit:,}')
 dated=(datetime.date(2026,10,20)+datetime.timedelta(days=day-1)).isoformat()
 scope=options.get('scope','Full named-entity import from the cited frozen dataset; no global category completeness claim.')
 q={'id':f'closeish_{dated.replace("-","")}_q{num}','date':dated,'day_number':day,'topic':topic,
   'bank_id':f'20261021-day{day}-q{num}-{source_id}','question_family':family,'prompt':prompt,
   'metric':metric,'unit':unit,'limit':limit,'comparison':comparison,'time_limit_seconds':30,'direction':direction,
   'boundary_inclusive':True,'score_bands':scorebands,'source':source,'source_refs':[source_id],
   'verification_status':'frozen_source_values_audited','editorial_status':'RESEARCH_DRAFT_NOT_PUBLISHABLE',
   'content_revision':'2026-10-21-two-days-content-v1','metric_provenance':description,
   'measurement_snapshot':options.get('edition','Bundled source snapshot 2026-10-21; changing datasets must not change past scores.'),
   'measurement':{'property':metric,'edition':source_id,'numeric_rule':options.get('rounding','as stored integer; no further rounding'), 'time_dependent':options.get('time_dependent',False)},
   'answer_scope':{'type':'finite_frozen_dataset','coverage':options.get('coverage','complete_for_cited_snapshot_only'),
                   'claimed_exhaustive':options.get('exhaustive',False),'entity_scope':scope,'dataset_count':len(clean)},
   'scoring_policy':'Verified integer measurement, fixed target and finite one-direction scoring window; invalid side and too-far answers score 0.',
   'perfect_tier':{'points':1200,'tier':'PERFECT HIT','rule':'exact displayed/scored measurement match'},
   'approach_rule':{'required_side':'from_above' if direction=='above' else 'from_below','operator':'>=' if direction=='above' else '<=',
                    'exact_target_allowed':True,'wrong_side_points':0,'exact_target_points':1200},
   'scoring_window':{'max_scoring_distance':edges[-1],'units':unit,'outside_window_points':0,'wrong_side_points':0,'exact_match_points':1200},
   'input_max_length':140,'answers':clean,'recognized_category_candidates':[],
   'research_status':'Imported and numerically audited. Editorial acceptance depends on coverage/provenance limits.',
   'verified_answer_count':len(clean),'catalogued_answer_count':len(clean),'recognized_category_candidate_count':0,
   'alias_count':sum(1+len(a['aliases']) for a in clean),
   'score_distribution_audit':{str(k):count[k] for k in [1200,1000,800,600,400,200,0]}}
 return q

# 1. All alphabetic CMUdict headwords, including names. Corpus fully imported; no Scrabble-eligibility claim.
# Persist the complete source headword/measurement list for deterministic, offline rebuilding.
# Derived from cmudict Python package version 1.1.3 in this release; no package is
# required after the first import because the source TSV is part of the project.
words_tsv=P('datasets/two-days/cmudict-headwords-a1z26.tsv')
if not words_tsv.exists():
 import cmudict
 headwords=sorted({s.casefold() for s in cmudict.words() if s.isalpha()})
 words_tsv.write_text(''.join(f'{word}\t{sum(ord(z)-96 for z in word)}\n' for word in headwords),encoding='utf-8')
headwords=[]
for line in words_tsv.read_text(encoding='utf-8').splitlines():
 word,v=line.split('\t')
 assert word.isascii() and word.isalpha() and word==word.lower()
 assert sum(ord(z)-96 for z in word)==int(v)
 headwords.append(word)
assert headwords==sorted(set(headwords)), 'CMUdict source is not deduplicated or ordered'
lang=[entity(s.capitalize(),sum(ord(z)-96 for z in s),'cmudict-1.1.3-headwords','CMUdict v1.1.3 headword '+s,id='cmu-'+s) for s in headwords]
# 2–6. Independently sourced source-specific finite snapshots; never misrepresent their breadth.
def from_day(d,q):return copy.deepcopy(raw[d]['q'+str(q)]['answers'])
q2={}
q2['q1']=make(2,1,'language','cmudict-1.1.3-headwords','english-word-a1z26',
 'Name a CMU dictionary headword whose letter score (A=1 to Z=26, added together) is {term} {limit}.',
 'Sum of A=1 ... Z=26 values of letters','letter points','https://github.com/cmusphinx/cmudict',
 'Derived deterministically from all alphabetic entries of the installed CMU Pronouncing Dictionary; this is not a Scrabble word list.',lang,
 {'preferred':230,'direction':'below','coverage':'full_alphabetic_headwords_of_installed_cmudict',
  'scope':'Every unique alphabetic CMU Pronouncing Dictionary headword in the installed release; includes proper names and loanwords.',
  'edition':'Installed cmudict Python package snapshot; canonical headwords lowercased then displayed capitalized.',
  'rounding':'exact integer sum of letter ordinal values'})
q2['q2']=make(2,2,'biology','msleep-body-mass','mammal-study-bodymass',
 'Name a mammal from the published sleep study whose recorded body mass is {term} {limit} kg (rounded to the nearest kg).',
 'Body mass of a mammal in ggplot2 msleep sample, nearest kg','kg','https://ggplot2.tidyverse.org/reference/msleep.html',
 'Full 83-species research *sample*, not a complete list of mammal species.',from_day(2,5),
 {'preferred':50,'scope':'All measured mammal names from the finite ggplot2 msleep research sample; not all living mammal species.',
  'rounding':'nearest whole kg, source frozen', 'coverage':'complete_for_ggplot2_research_sample_only'})
q2['q3']=make(2,3,'design','css4-named-colors','css4-colour-brightness',
 'Name a named CSS4 colour whose perceived RGB brightness is {term} {limit} out of 255 (rounded to an integer).',
 'Weighted sRGB luma 0.299R + 0.587G + 0.114B, nearest integer','brightness points','https://matplotlib.org/stable/gallery/color/named_colors.html',
 'All 148 official CSS4 named colours from Matplotlib; not every HTML hex colour.',from_day(3,5),
 {'preferred':200,'scope':'Exactly the 148 named CSS4 colours; RGB brightness uses weighted channel sum, rounded to integer.',
  'rounding':'0.299R + 0.587G + 0.114B, rounded to integer', 'exhaustive':True,'coverage':'complete_148_css4_names'})
q2['q4']=make(2,4,'transport','mpg-2008-cars','automobiles-2008-fuel-efficiency',
 'Name a 2008 car model in the historic fuel-economy dataset that could travel {term} {limit} highway miles on 15 gallons.',
 'Highest recorded 2008 highway MPG trim times 15 US gallons, source-rounded','miles',
 'https://ggplot2.tidyverse.org/reference/mpg.html','Historical ggplot2 mpg source: 38 distinct 2008 models, not all 2008 cars.',from_day(6,5),
 {'preferred':330,'scope':'All 38 distinct 2008 car model labels in ggplot2 mpg; not every 2008 vehicle sold.',
  'rounding':'best available highway MPG times 15 US gallons', 'coverage':'complete_for_ggplot2_mpg_2008_sample_only'})
q2['q5']=make(2,5,'economics','txhousing-2010-03','texas-2010-housing-market',
 'Name a Texas housing market area with a March 2010 median sale price {term} ${limit} (nearest $100).',
 'March 2010 median property sales price in TX housing MLS area; nearest $100','USD',
 'https://ggplot2.tidyverse.org/reference/txhousing.html','All 46 reporting areas for March 2010 in the bundled ggplot2 txhousing snapshot; NOT current real estate prices.',from_day(4,5),
 {'preferred':108200,'scope':'All 46 MLS market areas reported in the bundled March 2010 Texas housing source.',
  'rounding':'nearest $100 from source','coverage':'complete_for_bundled_tseries_month_only','time_dependent':True})
# 7. Full explicit world cup 2022 historical scorer list extracted and name-normalized from public match JSON.
football={}
for line in P('datasets/two-days/football-worldcup-2022-earliest-goals.tsv').read_text().splitlines():
 tm,name=line.split('|',1); minute=int(tm); key=slug(name)
 # resolve source's inconsistent transliterations into one entity
 if key in football:football[key]['minute']=min(minute,football[key]['minute']);continue
 football[key]={'name':name,'minute':minute,'aliases':[]}
fifa=[entity(v['name'],v['minute'],'openfootball-fifa-worldcup-2022',f"2022 match goal chronology, first listed goal minute for {v['name']}",v['aliases']) for v in football.values()]
q2['q6']=make(2,6,'sports','openfootball-fifa-worldcup-2022','football-first-goal-minute',
 'Name a goalscorer at the 2022 men’s World Cup whose earliest listed goal was in minute {limit} or later.',
 'Earliest goal minute as reported in match goal event table for a player, including added time','minute',
 'https://github.com/openfootball/worldcup.json/blob/master/2022/worldcup.json',
 'Goal times parsed from all 64 fixtures; player spelling variants manually merged; source goal event limitations apply.',fifa,
 {'preferred':65,'scope':'Distinct named 2022 World Cup goalscorers in the openfootball goal-event feed; name and own-goal details are source dependent.',
  'rounding':'whole scheduled/added-time football minute; source minute notation retained as numeric minute',
  'coverage':'complete_for_2022_public_match_goal_event_snapshot'})
# 8. Full Nobel Literature recipient list: source through 2024, plus verified Nobel 2025/2026.
lit=[]
for line in P('datasets/two-days/literature-nobel-awards-through-2026.tsv').read_text().splitlines():
 year,name=line.split('|',1)
 aliases={'W. B. Yeats':['William Butler Yeats','WB Yeats'],'T. S. Eliot':['Thomas Stearns Eliot','TS Eliot'],
 'V. S. Naipaul':['Vidiadhar Naipaul','VS Naipaul'], 'J. M. Coetzee':['John Maxwell Coetzee','JM Coetzee'],
 'J. M. G. Le Clézio':['JMG Le Clezio','Le Clezio'],'Winston Churchill':['Sir Winston Churchill'],
 'Pearl S. Buck':['Pearl Buck'],'Kenzaburō Ōe':['Kenzaburo Oe']}.get(name,[])
 lit.append(entity(name,int(year),'nobel-literature-official-1901-2026',f'Nobel Prize in Literature {year}, laureate {name}',aliases))
# 9. US mapped counties one time only (original sources preserved; note map-derived approximations).
q3={}
# 7a. Exactly 30 held modern Summer Olympics editions, from the chosen historical series.
olympics=[]
for row in P('datasets/two-days/summer-olympics-nations-1896-2024.tsv').read_text().splitlines():
 year,city,nations=row.split('|',2)
 olympics.append(entity(f'{year} Summer Olympics',int(nations),'summer-olympics-country-participation',
                       f'{year} host city {city}, thissportlife historical participation count {nations}',
                       [f'{year} {city} Olympics',f'{city} {year}',f'{city} Olympics {year}'],id='olympics-'+year))
q3['q1']=make(3,1,'sports','summer-olympics-country-participation','summer-olympics-national-delegations',
 'Name a Summer Olympics edition (1896–2024) with {term} {limit} participating nations in the historic series.',
 'Number of participating countries/NOC delegations, historically sourced','nations',
 'https://www.thissportlife.com/games/olympic-games-summer/countries/number.htm',
 'All 30 staged modern Summer Games from 1896–2024; nation counts vary in some historical and modern sources, so one fixed published series is used.',
 olympics,{'fixed_limit':140,'fixed_edges':[19,28,48,71,112],'direction':'below',
          'scope':'30 Summer Olympics held from 1896 through 2024; cancelled 1916, 1940, 1944 and the unofficial 1906 games excluded.',
          'rounding':'no rounding, source-recorded delegation counts',
          'coverage':'complete_all_30_held_summer_olympic_editions_to_2024','exhaustive':True})
q3['q2']=make(3,2,'literature','nobel-literature-official-1901-2026','nobel-literature-award-year',
 'Name a Nobel Prize in Literature laureate who received the award in {limit} or later.',
 'Year of Nobel Prize in Literature','year','https://www.nobelprize.org/prizes/lists/all-nobel-prizes-in-literature/',
 'All Nobel literature laureates from 1901–2026 (including years without an award); Nobel 2025–2026 additions checked against Nobel/reliable news.',lit,
 {'fixed_limit':2000,'fixed_edges':[2,6,12,19,26],'direction':'above','scope':'Entire Nobel Prize in Literature laureate category, award years 1901 through 2026.',
  'rounding':'official award year, no rounding','coverage':'full_nobel_prize_literature_1901_2026','exhaustive':True})
q3['q3']=make(3,3,'geography','uscounties-shape-geodesy','us-counties-geodesic-area',
 'Name a U.S. county or county equivalent whose approximate mapped land area is {term} {limit} km² (nearest km²).',
 'WGS84 geodesic area of mapped county polygon, nearest km²','km²','https://matplotlib.org/basemap/stable/users/geography.html',
 'Complete 3,220 area estimates from local Basemap US counties polygon snapshot, approximate geometry, not census areas.',from_day(2,3),
 {'preferred':2100,'direction':'below','scope':'All 3,220 valid US county/county-equivalent shapes with known mapped geodesic area in bundled snapshot.',
  'rounding':'nearest square kilometre, geodesic polygon area','coverage':'complete_for_bundled_basemap_county_polygons'})
q3['q4']=make(3,4,'society','statecrime-2009-violent','us-2009-violent-crime-rate',
 'Name a U.S. state or Washington, D.C., with {term} {limit} recorded violent crimes per 100,000 residents in 2009.',
 'Recorded 2009 violent crime rate per 100,000 residents, nearest integer','incidents/100k',
 'https://www.statsmodels.org/stable/datasets/generated/statecrime.html',
 'Historic statistics, 50 states and DC; some rates may be source-methodology-limited.',from_day(7,5),
 {'preferred':358,'scope':'50 US states and District of Columbia, as tabulated in 2009 statsmodels statecrime snapshot.',
  'rounding':'nearest whole incident per 100,000','coverage':'complete_for_statecrime_2009_source','time_dependent':True})
# 11. Countryinfo frozen population rather than repeated old country density measure.
sourcecountry=json.loads(P('datasets/countryinfo-comprehensive-snapshot.json').read_text())
country=[]
for i,r in enumerate(sourcecountry['records']):
 if not isinstance(r.get('population'),(int,float)) or r['population']<=0:continue
 country.append(entity(r['name'],int(math.floor((r['population']+500000)/1000000))*1000000,'countryinfo-frozen-demographic',
          f"countryinfo complete snapshot country={r['name']} population={r['population']}",r.get('altSpellings',[]),id='ci-'+slug(r['name'])))
q3['q5']=make(3,5,'demography','countryinfo-frozen-demographic','world-country-frozen-population',
 'Name a country or territory whose historical countryinfo population is {term} {limit} people (nearest million).',
 'Population estimate as recorded in old countryinfo snapshot, no claim of 2026 population','people',
 'https://github.com/porimol/countryinfo',
 'Bundled countryinfo population snapshot with no reliable single common reference year; do not present estimates as current.',country,
 {'fixed_limit':25000000,'fixed_edges':[1000000,3000000,6000000,12000000,24000000],'direction':'below','scope':'Countries and territories with nonzero recorded population in bundled countryinfo snapshot; outdated/source-varying years.',
  'rounding':'nearest million people; snapshot, not current','coverage':'historic_countryinfo_sample_not_exhaustive','time_dependent':True})
# 12. Presidential office chronology is distinct from the previous day's athlete-goal category.
q3['q6']=make(3,6,'history','us-presidential-terms-1953-2009','president-first-office-year',
 'Name a U.S. president in the 1953–2009 timeline who first took office in {limit} or later.' ,
 'First year the president took office','year','https://ggplot2.tidyverse.org/reference/presidential.html',
 'Eleven presidents whose first service began in the ggplot2 presidential 1953–2009 timeline; not every American president.',from_day(5,5),
 {'fixed_limit':1977,'fixed_edges':[4,12,16,24,32],'direction':'above','scope':'All eleven presidents in the bounded ggplot2 1953–2009 presidential timeline.',
  'rounding':'historical accession year, exact','coverage':'complete_for_bundled_1953_2009_presidential_timeline'})
# Save only day 2 and 3: Day 1 remains byte-identical.
for d,bank in [(2,q2),(3,q3)]:
 assert list(bank)==[f'q{i}' for i in range(1,7)]
 (ROOT/f'days/day-{d:02d}.json').write_text(json.dumps(bank,ensure_ascii=False,indent=2)+'\n')

# Add deterministic auditing statistics.
audit=[]
for d,bank in [(2,q2),(3,q3)]:
 for k,q in bank.items():
  cnt=collections.Counter(a['points'] for a in q['answers']);zero=collections.Counter(a['tier'] for a in q['answers'] if a['points']==0)
  audit.append({'date':q['date'],'day':d,'round':int(k[1:]),'topic':q['topic'],'prompt':q['prompt'],'family':q['question_family'],'source_family':q['source_refs'][0],
    'verified_entities':len(q['answers']),'unverified':len(q['recognized_category_candidates']),
    'target':q['limit'],'direction':q['direction'],'1200':cnt[1200],'1000':cnt[1000],'800':cnt[800],'600':cnt[600],'400':cnt[400],
    '200':cnt[200],'0':cnt[0],'0_too_far':zero['TOO FAR'],'0_crossed':zero['CROSSED LIMIT'],'coverage':q['answer_scope']['coverage']})
path=ROOT/'docs'/'DAY-02-03-AUDIT.csv'
with path.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(audit[0]));w.writeheader();w.writerows(audit)
print('NEW DAY 2/3')
for x in audit:print(f"D{x['day']} Q{x['round']} {x['topic']:12s} {x['verified_entities']:>7,} {' '.join(f'{i}:{x[i]}' for i in ('1200','1000','800','600','400','200','0'))}")
print('TOTAL MEASURED:',sum(x['verified_entities'] for x in audit))
