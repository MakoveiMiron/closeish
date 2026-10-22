"""Apply editorial updates to Oct 20 day from locally frozen research TSV files.
Run BEFORE build.py; it is deterministic and idempotent.
Data policy: preserve source measurements; round only at documented scoring step.
"""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import collections
import csv
import json
import unicodedata

ROOT=Path(__file__).resolve().parents[1]
DAY=ROOT/'days/day-01.json'
DATA=json.loads(DAY.read_text(encoding='utf-8'))
TIERS={1200:'PERFECT HIT',1000:'RAZOR EDGE',800:'CLOSE CALL',600:'SOLID HIT',400:'IN THE ZONE',200:'ON THE BOARD'}

def norm(text):
    return ''.join(c for c in unicodedata.normalize('NFD',text.lower()) if unicodedata.category(c)!='Mn').replace(' ','').replace('.','').replace(',','').replace('-','')

def setbands(q,cutoffs):
    q['score_bands']=[{'max_gap_inclusive':gap,'points':pts,'tier':TIERS[pts]} for pts,gap in zip([1000,800,600,400,200],cutoffs)]
    q['scoring_window']['max_scoring_distance']=cutoffs[-1]
    q['scoring_window']['units']=q['unit']

def evaluate(q,n):
    gap=n-q['limit'] if q['direction']=='above' else q['limit']-n
    if gap<0:return 0,'CROSSED LIMIT'
    if gap==0:return 1200,TIERS[1200]
    for band in q['score_bands']:
        if gap<=band['max_gap_inclusive']:return band['points'],band['tier']
    return 0,'TOO FAR'

def sync(q):
    for a in q['answers']:
        a['points'],a['tier']=evaluate(q,a['metric_value'])
    q['verified_answer_count']=len(q['answers'])
    q['recognized_category_candidate_count']=len(q.get('recognized_category_candidates',[]))
    q['catalogued_answer_count']=q['verified_answer_count']+q['recognized_category_candidate_count']
    q['alias_count']=sum(len(a.get('aliases',[])) for a in q['answers']+q.get('recognized_category_candidates',[]))
    c=collections.Counter(a['points'] for a in q['answers'])
    q['score_distribution_audit']={str(k):c[k] for k in [1200,1000,800,600,400,200,0]}
    assert all(c[p] for p in [1200,1000,800,600,400,200,0]),(q['id'],dict(c))
    assert c[1200]<=5 and c[1000]<=12,(q['id'],dict(c))
    q['content_revision']='closeish-20261020-un-members-whole-pct-v5'

def tsv(fname,columns):
    for line in (ROOT/'datasets'/fname).read_text(encoding='utf-8').splitlines():
        if not line or line.startswith('#'):continue
        parts=[x.strip() for x in line.split('|')]
        assert len(parts)==columns,line
        yield parts

# The 200 ha UNESCO question: >=150 hectares on the allowed side scores; <150 is TOO FAR.
q=DATA['q1']
setbands(q,[2,8,20,35,50]);sync(q)
assert evaluate(q,150)[0]==200
assert evaluate(q,149)[0]==0
assert evaluate(q,50)[0]==0

# Atomic mass: still uses the published RDKit rounded integer, now explicit to players.
q=DATA['q2']
q['prompt']='Name a chemical element with an atomic weight of at least 127 u. (Values are rounded to the nearest whole number.)'
setbands(q,[2,5,10,18,30]);sync(q)
assert evaluate(q,157)[0]==200 and evaluate(q,158)[0]==0

# Q4: 2023 forestry, measured against 2023 World Bank/FAO WDI source.
q=DATA['q4']
q['topic']='environment'
q['bank_id']='worldbank_forest_area_land_share_2023'
q['question_family']='forest_cover_country_2023'
q['prompt']='Name a UN member state with at least 31% forest cover in 2023. (Percentages are rounded to the nearest whole percent before scoring.)'
q['metric']='2023 forest area as a share of land area; rounded to nearest whole percent for scoring'
q['unit']='%'
q['limit']=31 # whole-percentage scoring: the smallest integer strictly greater than 30
q['comparison']='at_least';q['direction']='above';q['boundary_inclusive']=True
q['source']='https://data.worldbank.org/indicator/AG.LND.FRST.ZS'
q['source_refs']=['world-bank-wdi-AG.LND.FRST.ZS-2023','FAOSTAT-2023']
q['verification_status']='transcribed_source_snapshot_recheck_recommended'
q['editorial_status']='research_preview'
q['metric_provenance']='World Bank WDI indicator AG.LND.FRST.ZS (FAOSTAT), 2023, hand-transcribed to 1 decimal; scoring uses conventional half-up rounding to whole percent. Eligible entries are UN member states, not World Bank economies or territories.'
q['measurement_snapshot']='Source year 2023; copied from World Bank 2023 list on 2026-10-19.'
q['measurement']={'snapshot_date':'2023-12-31','property':q['bank_id'],'edition':'WDI-AG.LND.FRST.ZS-2023-transcribed','numeric_rule':'2023 forest area % of land area, World Bank display values at 0.1 precision; round half-up to integer BEFORE comparison and scoring. 31 is the lowest eligible rounded value.','time_dependent':True}
q['source_dataset']='world-bank-wdi-forest-2023-transcribed'
q['research_status']='un_member_states_source_transcription_one_unmeasured_country'
q['scoring_rounding']={'method':'nearest_whole_percent','tie_break':'half_up','applied_before_limit_comparison':True}
q['eligible_entity_rule']='UN member states (193); external territories and nonmember entities are ineligible'
q['entity_scope_reference']='https://www.un.org/en/about-us/member-states'
setbands(q,[1,2,4,7,12])
# Preserve aliases from the previous complete-enough Q3 world identity bank.
q3entities=DATA['q3']['answers']+DATA['q3'].get('recognized_category_candidates',[])
byname={}
for ent in q3entities:
    byname.setdefault(norm(ent['canonical']),ent)
    for a in ent.get('aliases',[]):
        key=norm(a['input'])
        if key and (key not in byname or byname[key] is ent):byname[key]=ent
# Keep naming collisions ambiguous in the canonical catalogue; never bind one alias to two entities.
renames={
 'Bahamas, The':'The Bahamas','Congo, Dem. Rep.':'Democratic Republic of the Congo',
 'Congo, Rep.':'Republic of the Congo',"Cote d'Ivoire":'Côte d’Ivoire',
 'Egypt, Arab Rep.':'Egypt','Gambia, The':'The Gambia','Iran, Islamic Rep.':'Iran',
 'Korea, Dem. People\'s Rep.':'North Korea','Korea, Rep.':'South Korea',
 'Kyrgyz Republic':'Kyrgyzstan','Lao PDR':'Laos','Naoero':'Nauru',
 'Russian Federation':'Russia','Slovak Republic':'Slovakia',
 'Somalia, Fed. Rep.':'Somalia','Turkiye':'Türkiye','Venezuela, RB':'Venezuela',
 'Viet Nam':'Vietnam','Yemen, Rep.':'Yemen',
 'Micronesia, Fed. Sts.':'Federated States of Micronesia',
 'Puerto Rico (US)':'Puerto Rico','Virgin Islands (U.S.)':'U.S. Virgin Islands',
 'West Bank and Gaza':'Palestine',
}
new=[]
used_ids=set()
measured_names=set()
for original,raw in tsv('worldbank-forest-share-2023-transcribed.tsv',2):
    canonical=renames.get(original,original)
    match=byname.get(norm(canonical)) or byname.get(norm(original))
    if match and match['entity_id'] not in used_ids:
        eid=match['entity_id'].replace('country-capital-','forest-wb-')
        aliases=[a.copy() for a in match.get('aliases',[])]
        if match['canonical']!=canonical:
            aliases.append({'input':match['canonical'],'kind':'recognized_name_or_code','action':'replace_with_canonical'})
    else:
        eid='forest-wb-'+norm(canonical)
        aliases=[]
    if original!=canonical:aliases.append({'input':original,'kind':'recognized_name_or_code','action':'replace_with_canonical'})
    if original=="Cote d'Ivoire":aliases.append({'input':'Ivory Coast','kind':'common_name','action':'replace_with_canonical'})
    # De-duplicate aliases, including canonical spelling.
    unique=[];seen={norm(canonical)}
    for a in aliases:
        key=norm(a['input']);
        if key and key not in seen:
            unique.append(a);seen.add(key)
    pct=Decimal(raw)
    points_value=int(pct.quantize(Decimal('1'),rounding=ROUND_HALF_UP))
    new.append({'entity_id':eid,'canonical':canonical,'aliases':unique,'verified_status':'source_2023_transcribed','source_refs':[{'source_id':'world-bank-wdi-forest-2023','locator':f'AG.LND.FRST.ZS / {original} / 2023 / {raw} %'}], 'source_value_2023_pct':float(pct),'metric_value':points_value})
    used_ids.add(eid)
    measured_names.add(norm(canonical))
# Fixed category: 193 UN member states, not the broader World Bank set of economies.
# Source: https://www.un.org/en/about-us/member-states ; territories source:
# https://www.un.org/dppa/decolonization/en/nsgt
# All 193 member states occur in the transcribed measured names except Grenada,
# which must remain pending because its 2023 source value is not verified here.
NON_UN_MEMBERS_IN_TRANSCRIPTION={
    'American Samoa','Aruba','Bermuda','British Virgin Islands','Cayman Islands',
    'Curacao','Faroe Islands','French Polynesia','Gibraltar','Greenland','Guam',
    'Isle of Man','New Caledonia','Northern Mariana Islands','Puerto Rico',
    'Sint Maarten (Dutch part)','St. Martin (French part)',
    'Turks and Caicos Islands','U.S. Virgin Islands','Palestine',
}
assert len(NON_UN_MEMBERS_IN_TRANSCRIPTION)==20
by_legal_name={e['canonical']:e for e in new}
assert all(n in by_legal_name for n in NON_UN_MEMBERS_IN_TRANSCRIPTION)
excluded=[]
for n in NON_UN_MEMBERS_IN_TRANSCRIPTION:
    e=by_legal_name[n]
    # Maintain source provenance but never allow a scored metric for an ineligible entity.
    e['metric_value']=None
    e['points']=0
    e['tier']='INELIGIBLE'
    e['exclusion_reason']='Not a UN member state; outside the eligible Q4 answer category.'
    e['membership_status']='excluded_non_un_member'
    excluded.append(e)
q['answers']=[e for e in new if e['canonical'] not in NON_UN_MEMBERS_IN_TRANSCRIPTION]
assert len(q['answers'])==192, len(q['answers'])
# Recognize unscorable place names separately, without granting unverified points.
# Prevent duplicate or competing entries for the same measured member state.
ALIAS_OF_MEASURED={
    'Saint Kitts and Nevis':'St. Kitts and Nevis',
    'Saint Lucia':'St. Lucia',
    'Saint Vincent and the Grenadines':'St. Vincent and the Grenadines',
}
for alias, canonical in ALIAS_OF_MEASURED.items():
    entry=next(a for a in q['answers'] if a['canonical']==canonical)
    if norm(alias) not in {norm(x['input']) for x in entry['aliases']}:
        entry['aliases'].append({'input':alias,'kind':'common_name','action':'replace_with_canonical'})
accepted_names={norm(e['canonical']) for e in q['answers']}
accepted_names.update(norm(a['input']) for e in q['answers'] for a in e['aliases'])
excluded_names={norm(e['canonical']) for e in excluded}
excluded_names.update(norm(a['input']) for e in excluded for a in e['aliases'])
for ent in q3entities:
    n=norm(ent['canonical'])
    if n in accepted_names or n in excluded_names:
        continue
    if n==norm('Grenada'):
        continue
    excluded.append({
        'entity_id':'forest-ineligible-'+n,
        'canonical':ent['canonical'],
        'aliases':ent.get('aliases',[]),
        'source_refs':[],
        'metric_value':None,'points':0,'tier':'INELIGIBLE',
        'membership_status':'excluded_non_un_member',
        'exclusion_reason':'Not a UN member state; outside the eligible Q4 answer category.'
    })
    excluded_names.add(n)
# The one recognized UN member without a verified 2023 value is explicitly pending.
grenada=next((e for e in q3entities if norm(e['canonical'])==norm('Grenada')),None)
assert grenada
q['recognized_category_candidates']=[{
    'entity_id':'forest-wb-grenada','canonical':'Grenada',
    'aliases':grenada.get('aliases',[]),'verified_status':'unverified',
    'source_refs':[],'metric_value':None,'review_status':'2023_forest_percent_not_catalogued',
    'measurement_status':'unverified','verification_note':
      'Grenada is a UN member, but no 2023 forest value has been verified in the frozen transcription.'
}]
q['excluded_answers']=sorted(excluded,key=lambda e:e['canonical'])
assert sum(x['canonical']=='Western Sahara' for x in q['excluded_answers'])==1
assert not any(x['canonical']=='Western Sahara' for x in q['answers']+q['recognized_category_candidates'])
q['answer_scope']={
 'type':'closed_membership_partial_measurement','coverage':'193_UN_members',
 'claimed_exhaustive':False,
 'entity_scope':'UN member states only (193); all are recognized, but one has no verified 2023 forest measurement',
 'dataset_count':193,'note':'Only UN member states are eligible. The World Bank 2023 numbers are source data rounded half-up to whole percentages BEFORE checking the 31% target; excluded territories are recognized only to explain ineligibility.'
}
q['excluded_entity_count']=len(q['excluded_answers'])
sync(q)

# Q6: A different entity category, celestial astronomy, complete 88-constellation IAU set.
q=DATA['q6']
q['topic']='astronomy'
q['bank_id']='iau_constellation_area_sqdeg'
q['question_family']='iau_constellation_sky_area'
q['prompt']='Name an official constellation covering at most 500 square degrees of the sky. (Areas are rounded to the nearest whole square degree.)'
q['metric']='Area of an IAU constellation on the celestial sphere, in square degrees (rounded to nearest whole number)'
q['unit']='square degrees'
q['limit']=500
q['comparison']='at_most';q['direction']='below';q['boundary_inclusive']=True
q['source']='https://www.astropixels.com/constellations/constellationslist.html'
q['source_refs']=['IAU-88-constellations','astropixels-constellation-areas']
q['verification_status']='cross_referenced_constellation_area_source'
q['editorial_status']='research_preview'
q['metric_provenance']='IAU official set of 88 constellations; area rounded to whole square degrees as tabulated by AstroPixels (Fred Espenak).'
q['measurement_snapshot']='Astronomical boundaries fixed; source page last updated September 2014.'
q['measurement']={'snapshot_date':'2026-10-19','property':q['bank_id'],'edition':'IAU-Delporte-constellation-boundaries-tabulated','numeric_rule':'Constellation solid angle in sq. degrees; source already whole-degree rounded','time_dependent':False}
q['source_dataset']='astropixels-iau-88-constellation-areas'
q['research_status']='complete_finite_iau_88_constellations'
setbands(q,[4,10,25,55,125])
constellations=[]
for name,abbr,raw in tsv('constellations-area-rounded-1sqdeg.tsv',3):
    aliases=[{'input':abbr,'kind':'recognized_name_or_code','action':'replace_with_canonical'}]
    if name=='Boötes':aliases.append({'input':'Bootes','kind':'alternate_spelling','action':'replace_with_canonical'})
    if name=='Crux':aliases.append({'input':'Southern Cross','kind':'common_name','action':'replace_with_canonical'})
    if name=='Ursa Major':aliases.append({'input':'Great Bear','kind':'common_name','action':'replace_with_canonical'})
    if name=='Ursa Minor':aliases.append({'input':'Little Bear','kind':'common_name','action':'replace_with_canonical'})
    if name=='Piscis Austrinus':aliases.append({'input':'Pisces Austrinus','kind':'alternate_spelling','action':'replace_with_canonical'})
    constellations.append({'entity_id':'iau-constellation-'+abbr.lower(),'canonical':name,'aliases':aliases,'verified_status':'published_constellation_area','source_refs':[{'source_id':'astropixels-constellation-areas','locator':f'{name} ({abbr}); {raw} square degrees'}],'metric_value':int(raw)})
q['answers']=constellations
q['recognized_category_candidates']=[]
q['answer_scope']={'type':'closed_world','coverage':'complete_source_set','claimed_exhaustive':True,'entity_scope':'All 88 officially recognized IAU constellations','dataset_count':len(constellations),'note':'88 official constellations; complete catalog for selected source edition. Constellation areas are 2-dimensional angular areas, not physical land areas.'}
sync(q)
assert len(constellations)==88

for k in ['q3','q5']:
    # A content revision ensures saved attempts from an older daily bank cannot be silently reused.
    DATA[k]['content_revision']='closeish-20261020-rounding-visible-v4'

DAY.write_text(json.dumps(DATA,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with (ROOT/'QUESTION-AUDIT.csv').open('w',encoding='utf-8',newline='') as out:
    w=csv.writer(out);w.writerow(['round','question','topic','limit','metric','recognized_entities','measured_entities','unverified_measurements',1200,1000,800,600,400,200,0,'status'])
    for i,q in enumerate(DATA.values(),1):
        w.writerow([i,q['prompt'],q['topic'],q['limit'],q['metric'],q['catalogued_answer_count'],q['verified_answer_count'],q['recognized_category_candidate_count'],*(q['score_distribution_audit'][str(n)] for n in [1200,1000,800,600,400,200,0]),q['verification_status']])
print('Revised banks:')
for n,q in DATA.items():
    print(n,q['prompt'],q['verified_answer_count'],q['recognized_category_candidate_count'],q['score_distribution_audit'])
