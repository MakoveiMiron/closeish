"""Expand 2008 car question from 38 ggplot2 brands to 436 names in a frozen
US fuel economy source. This is a year-limited source, NOT the world car market.

Input: manually cross-transcribed model→max highway MPG from upstream CSV
https://github.com/maithilid12/Fuel_Economy_Data_Analysis/blob/master/Data/all_alpha_08.csv
The source table has 2404 rows (gasoline, diesel, multi-fuel, CNG and N/A).
For each Model label this frozen derivative takes the highest available
integer highway MPG for gasoline/diesel, or gasoline side of ethanol/gas split.
Rows without a relevant numerical metric remain pending, never 0 MPG.
"""
import json,pathlib,hashlib,re,unicodedata,collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
base=ROOT/'datasets/two-days/epa-2008-highway-best-by-model-verified.tsv'
path=ROOT/'days/day-02.json';day=json.loads(path.read_text());q=day['q4']
model_rows=[]
for line in base.read_text().splitlines():
    brand,models=line.split('|',1)
    for item in models.split(';'):
        model,mpg_raw=item.rsplit(':',1)
        model_rows.append((brand+' '+model,None if mpg_raw=='?' else int(mpg_raw)))
assert len(model_rows)==436 and sum(v is not None for _,v in model_rows)==411
assert len({name.casefold() for name,_ in model_rows})==436
points={1200:'PERFECT HIT',1000:'RAZOR EDGE',800:'CLOSE CALL',600:'SOLID HIT',400:'IN THE ZONE',200:'ON THE BOARD'}
def score(value):
    gap=value-q['limit'] if q['direction']=='above' else q['limit']-value
    if gap<0:return 0,'CROSSED LIMIT'
    if gap==0:return 1200,'PERFECT HIT'
    for b in q['score_bands']:
        if gap<=b['max_gap_inclusive']:
            v=b['points'];return v,points[v]
    return 0,'TOO FAR'
def slug(text):return re.sub(r'[^a-z0-9]+','-',unicodedata.normalize('NFKD',text).encode('ascii','ignore').decode().lower()).strip('-')
# Generic brand names ("3", "300" etc.) cannot be auto-expanded from a bare suffix.
suffixes=collections.Counter(n.partition(' ')[2].casefold() for n,_ in model_rows)
answers=[];candidates=[]
for name,mpg in model_rows:
    brand,_,model=name.partition(' ')
    if name.startswith('ASTON MARTIN ') or name.startswith('LAND ROVER ') or name.startswith('MERCEDES-BENZ ') or name.startswith('ROLLS-ROYCE '):
        brand,model=name.rsplit(' ',1) if False else (None,None)
        for label in ('ASTON MARTIN','LAND ROVER','MERCEDES-BENZ','ROLLS-ROYCE'):
            if name.startswith(label+' '):brand=label;model=name[len(label)+1:];break
    display=(brand if brand in {'BMW','GMC','MINI','KIA','GMC'} else brand.title())+' '+model
    short=model.strip()
    aliases=[]
    if suffixes[short.casefold()]==1 and len(short)>=4 and not short.isdecimal():
        aliases=[{'input':short,'kind':'model_only_unique','action':'replace_with_canonical'}]
    cid='epa2008-'+slug(name)
    common={'entity_id':cid,'canonical':display,'aliases':aliases,'verified_status':'source_snapshot',
            'source_refs':[{'source_id':'all-alpha-2008-epa-based','locator':f'Model={name}, best documented highway MPG='+('N/A' if mpg is None else str(mpg))}]}
    if mpg is None:
        common.update(membership_status='recognized_entity_unverified_measurement',
                      measurement_status='not_reported_in_source',
                      measurement_note='No matching numerical 2008 highway MPG in frozen source. Do not treat as MPG=0.')
        candidates.append(common)
    else:
        value=15*mpg;scorevalue,tier=score(value)
        common.update(metric_value=value,metric_source_value=mpg,points=scorevalue,tier=tier)
        answers.append(common)
q['answers']=sorted(answers,key=lambda x:x['canonical'].casefold())
q['recognized_category_candidates']=sorted(candidates,key=lambda x:x['canonical'].casefold())
q['recognized_candidate_count']=len(candidates)
q['verified_answer_count']=len(answers)
q['catalogued_answer_count']=len(answers)+len(candidates)
q['alias_count']=sum(1+len(x['aliases']) for x in [*answers,*candidates])
q['score_distribution_audit']={str(k):sum(a['points']==k for a in answers) for k in (1200,1000,800,600,400,200,0)}
q['source']='https://github.com/maithilid12/Fuel_Economy_Data_Analysis/blob/master/Data/all_alpha_08.csv'
q['source_refs']=['all-alpha-2008-epa-based']
q['measurement_snapshot']='Frozen 2008 all_alpha_08.csv derivative (2404 source variant/area rows). Model level max numeric highway MPG from gasoline/diesel or gasoline side of FFV, multiplied by 15 US gallons. Not global model list.'
q['metric_provenance']='2008 historical EPA-related fuel economy compilation: highest numeric highway MPG among listed trims for each Model label, multiplied by 15 US gal. Included 436 models: 411 with numeric highway efficiency, 25 known models without comparable numerical MPG. Cars outside this table remain unverified; source varies by trim/fuel and does not cover worldwide model universe.'
q['answer_scope']={'type':'open_world','coverage':'research_partial_2008_us_source','claimed_exhaustive':False,'entity_scope':'Any 2008 car model with a verifiable highway MPG appropriate to 15 US gallons of fuel; currently only this US 2008 data extract has been verified. Unlisted models may be eligible.',
                   'dataset_count':436,'source_data_row_count':2404}
q['measurement']['edition']='all-alpha-2008-model-highway-max-2026-10-21'
q['content_revision']='2026-10-21-rebuild-2008-epa-broad-v1'
assert all(q['score_distribution_audit'][str(p)]>0 for p in (1200,1000,800,600,400,200,0)),q['score_distribution_audit']
path.write_text(json.dumps(day,ensure_ascii=False,indent=2)+'\n')
print('Cars expanded:',len(answers),'measured',len(candidates),'measurement pending','score counts',q['score_distribution_audit'])
