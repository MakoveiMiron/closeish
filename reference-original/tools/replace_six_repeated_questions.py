"""Replace six consecutive Midwest-county questions with six independent,
source-backed entity families. This is an editorial research improvement, NOT a
claim that all 36 questions meet the user's publication requirements.

Run from any directory: python tools/replace_six_repeated_questions.py
Only updates day-02..day-07 q5; no changes to day-01 or the UI.
"""
from pathlib import Path
from collections import Counter
from datetime import date
from math import floor
import copy,csv,json,re,statistics
ROOT=Path(__file__).resolve().parents[1]
PLOT=Path(__import__('plotnine').__file__).parent/'data'
TIERS=[(1000,'RAZOR EDGE'),(800,'CLOSE CALL'),(600,'SOLID HIT'),(400,'IN THE ZONE'),(200,'ON THE BOARD')]

def read_csv(name):
    with (PLOT/name).open(newline='',encoding='utf8') as fp:return list(csv.DictReader(fp))

def make_record(id,canonical,metric,locator,aliases=()):
    return {'entity_id':str(id),'canonical':canonical,'metric_value':metric,'aliases':[str(x) for x in aliases if x and x!=canonical], 'source_locator':str(locator)}

def animals():
    out=[]
    for r in read_csv('msleep.csv'):
        try:val=float(r['bodywt'])
        except (ValueError,TypeError):continue
        if val>0:
            out.append(make_record('msleep-'+r['name'].lower().replace(' ','-'),r['name'],val,f'ggplot2/msleep.csv mammal name={r["name"]}',[r['genus']+' ('+r['name']+')']))
    return out

def css_colors():
    from matplotlib.colors import CSS4_COLORS, to_rgb
    out=[]
    for name,hexval in CSS4_COLORS.items():
        r,g,b=[round(x*255) for x in to_rgb(hexval)]
        brightness=(299*r+587*g+114*b)/1000
        formatted=re.sub(r'([a-z])([A-Z])',r'\1 \2',name).title()
        out.append(make_record('css-'+name,formatted,brightness,'CSS4 named color: '+name+' '+hexval,[name]))
    return out

def housing():
    out=[]
    for r in read_csv('txhousing.csv'):
        if r['year']=='2010' and r['month']=='3':
            try:val=float(r['median'])
            except (ValueError,TypeError):continue
            if val>0:out.append(make_record('txhousing-'+r['city'].lower().replace(' ','-'),r['city'],val,f'ggplot2/txhousing.csv / {r["city"]} / 2010-03'))
    return out

def presidents():
    out=[]
    for r in read_csv('presidential.csv'):
        # One row per US presidency (1953-2017), source scope visibly stated in prompt.
        val=int(r['start'][:4]); name=r['name']
        names={'Eisenhower':'Dwight D. Eisenhower','Kennedy':'John F. Kennedy','Johson':'Lyndon B. Johnson','Nixon':'Richard Nixon','Ford':'Gerald Ford','Carter':'Jimmy Carter','Reagan':'Ronald Reagan','Clinton':'Bill Clinton','Obama':'Barack Obama'}
        canonical=('George H. W. Bush' if val==1989 else 'George W. Bush') if name=='Bush' else names[name]
        out.append(make_record('presidential-'+str(val)+'-'+name.lower(),canonical,val,f'ggplot2/presidential.csv / {name} / {r["start"]}', [name] if name not in ('Bush','Johson') else []))
    return out

def vehicles():
    # mpg.csv: several trims per make/model/year. For "could travel" we use the
    # highest highway MPG among documented configurations (not an invented average).
    best={}
    for r in read_csv('mpg.csv'):
        if r['year']!='2008':continue
        try:val=int(r['hwy'])
        except (ValueError,TypeError):continue
        key=(r['manufacturer'],r['model'])
        if key not in best or val>best[key][0]:best[key]=(val,r)
    out=[]
    for (make,model),(mpg,r) in best.items():
        name=f'{make.title()} {model}'
        out.append(make_record('mpg2008-'+make+'-'+model,name,mpg*15,f'ggplot2/mpg.csv / {make} {model} / 2008 / max highway MPG={mpg}',[make+' '+model]))
    return out

def state_violent():
    import statsmodels.api as sm
    data=sm.datasets.statecrime.load_pandas().data
    return [make_record('statecrime2009-'+str(name).lower().replace(' ','-'),str(name),float(r['violent']),f'statsmodels statecrime (2009) / {name} / violent', [str(name)+' state']) for name,r in data.iterrows()]

SPEC=[
  dict(day=2,topic='wildlife',type='mammal',dataset='msleep-body-mass',src='https://ggplot2.tidyverse.org/reference/msleep.html',records=animals, step=1, unit='kg',direction='above',min_threshold=50, prompt='Name a mammal weighing at least {limit} kg in the published mammal sleep dataset. (Body masses are rounded to the nearest kilogram before scoring.)', metric='Recorded mammal body mass in kilograms',rounding='nearest whole kilogram', caveat='The source is a finite research sample of mammals, NOT a comprehensive catalogue of mammal species.'),
  dict(day=3,topic='design',type='named-color',dataset='css4-named-colors',src='https://matplotlib.org/stable/gallery/color/named_colors.html',records=css_colors,step=1,unit='brightness',direction='below',min_threshold=50,prompt='Name a CSS4 colour with a brightness of at most {limit} out of 255. (Brightness is rounded to a whole number, using 0.299R + 0.587G + 0.114B.)',metric='Standard weighted sRGB brightness (0 = black; 255 = white)',rounding='nearest brightness unit',caveat='Exactly the 148 named CSS4 colours shipped with Matplotlib; independent aliases do not create more colours.'),
  dict(day=4,topic='housing',type='texas-city',dataset='txhousing-2010-03',src='https://ggplot2.tidyverse.org/reference/txhousing.html',records=housing,step=100,unit='USD',direction='above',min_threshold=50,prompt='Name a Texas housing-market area whose median home sale price in March 2010 was at least ${limit}. (Prices are rounded to the nearest $100.)',metric='March 2010 median price of recorded home sales per city',rounding='nearest $100',caveat='Only the 46 Texas MLS market areas in the source sample; includes counties and metropolitan areas, not just cities.'),
  dict(day=5,topic='history',type='president',dataset='us-presidential-terms-1953-2009',src='https://ggplot2.tidyverse.org/reference/presidential.html',records=presidents,step=1,unit='year',direction='below',min_threshold=50,prompt='Name a US president who first took office in {limit} or earlier, among presidents who took office from 1953 to 2009.',metric='First year serving as US president, within 1953–2009 historical list',rounding='exact calendar year',caveat='Finite list of the 11 presidencies documented in this 1953–2009 snapshot; does not cover every US president.'),
  dict(day=6,topic='transport',type='car-model',dataset='mpg-2008-cars',src='https://ggplot2.tidyverse.org/reference/mpg.html',records=vehicles,step=15,unit='miles',direction='above',min_threshold=50,prompt='Name a 2008 car model that could travel at least {limit} highway miles on 15 US gallons of fuel. (Calculated from its best listed highway MPG trim.)',metric='Highway range for 15 US gallons using the source model’s most efficient listed configuration',rounding='exact multiples of 15 miles (integer source MPG)',caveat='Only the 2008 makes and models in ggplot2 mpg; each model takes the most efficient recorded configuration.'),
  dict(day=7,topic='public-safety',type='us-state',dataset='statecrime-2009-violent',src='https://www.statsmodels.org/stable/datasets/generated/statecrime.html',records=state_violent,step=1,unit='per 100k',direction='below',min_threshold=50,prompt='Name a US state or Washington, DC with at most {limit} violent crimes per 100,000 residents in 2009. (Rates rounded to the nearest whole incident.)',metric='2009 recorded violent crime incidence per 100,000 population',rounding='nearest whole rate unit',caveat='The source is a 2009 historical snapshot for the 50 states and Washington, DC, not today’s statistics.'),
]

def rounded(val,step):return int(floor(val/step+0.5))*step

def build(spec):
    raw=spec['records']();step=spec['step']; direction=spec['direction']
    # Deduplicate canonical IDs, even when an upstream sample has repeated rows.
    indexed={}
    for a in raw:
        if a['entity_id'] in indexed:raise AssertionError('Nonunique source identity '+a['entity_id'])
        indexed[a['entity_id']]=a
    values=[(r,rounded(r['metric_value'],step)) for r in raw]
    dist_count=Counter(v for _,v in values)
    total=len(values)
    possibilities=[]
    for limit,f in sorted(dist_count.items()):
        if limit<spec['min_threshold'] or f>4:continue
        positive=sorted((v-limit if direction=='above' else limit-v) for r,v in values if (v-limit if direction=='above' else limit-v)>0)
        uniqued=sorted(set(positive))
        if len(uniqued)<5:continue
        # Search distinct positive bands; cap the point window before the extreme tail.
        for fraction in [0.35,0.55,0.75,0.9,1.0]:
            inside=positive[:max(5,int(len(positive)*fraction))]
            if len(set(inside))<5:continue
            # Aim at several good rare positions without splitting tied measurements.
            edges=[]
            for p in [0.04,0.12,0.28,0.52,0.96]:
                e=inside[min(len(inside)-1,int((len(inside)-1)*p))]
                if e not in edges:edges.append(e)
            if len(edges)<5:
                for gap in sorted(set(inside)):
                    if gap not in edges:edges.append(gap)
                    if len(edges)>=5:break
            edges=sorted(edges)
            if len(edges)!=5:continue
            tiercounts=[sum((edges[i-1] if i else 0)<g<=edge for g in positive) for i,edge in enumerate(edges)]
            if not all(tiercounts):continue
            paid=sum(g<=edges[-1] for g in positive)
            # Prefer rare exact scores, meaningful positive answers, and a natural usable window.
            target=(1 if f<=2 else 2, abs(paid-max(7,int(total*.40))),abs(sum(tiercounts)-total*.4),edges[-1],limit)
            possibilities.append((target,limit,edges,tiercounts))
    if not possibilities:raise ValueError('Unable to construct all seven true score tiers: '+spec['dataset']+' / sample='+str(total)+' / distinct='+str(len(dist_count)))
    possibilities.sort(key=lambda v:v[0]);_,limit,edges,tiercounts=possibilities[0]
    tiers=[];answers=[];counter=Counter()
    for e,(pts,label) in zip(edges,TIERS):tiers.append({'max_gap_inclusive':int(e),'points':pts,'tier':label})
    for ent,v in values:
        gap=v-limit if direction=='above' else limit-v
        if gap<0:pts=0;tier='CROSSED LIMIT'
        elif gap==0:pts=1200;tier='PERFECT HIT'
        elif gap>edges[-1]:pts=0;tier='TOO FAR'
        else:pts,tier=next((pts,label) for e,(pts,label) in zip(edges,TIERS) if gap<=e)
        counter[pts]+=1
        answers.append({'entity_id':ent['entity_id'],'canonical':ent['canonical'], 'aliases':[{'input':x,'kind':'source_alias','action':'replace_with_canonical'} for x in ent['aliases']], 'verified_status':'source_snapshot', 'source_refs':[{'source_id':spec['dataset'],'locator':ent['source_locator']}], 'metric_value':v, 'points':pts,'tier':tier})
    assert set(counter)=={0,200,400,600,800,1000,1200},(spec['dataset'],counter)
    return raw,answers,limit,tiers,counter

def main():
    out=[]
    # First compute ALL 6 replacements: if any source fails, leave the project unchanged.
    for spec in SPEC:
        raw,answers,limit,tiers,counter=build(spec)
        out.append((spec,raw,answers,limit,tiers,counter))
        print('Candidate:',spec['day'],spec['dataset'],'rows',len(answers),'limit',limit,'score counts',dict(counter))
    for spec,raw,answers,limit,tiers,counter in out:
        p=ROOT/'days'/f'day-{spec["day"]:02}.json';bank=json.loads(p.read_text());q=bank['q5'];step=spec['step']
        q.update({
          'topic':spec['topic'], 'bank_id':f'{spec["dataset"]}-limit-{limit}', 'question_family':spec['type']+'-'+spec['dataset'],
          'prompt':spec['prompt'].replace('{limit}',f'{limit:,}'), 'metric':spec['metric'], 'unit':spec['unit'], 'limit':limit,
          'direction':spec['direction'],'comparison':'at_least' if spec['direction']=='above' else 'at_most',
          'source':spec['src'],'source_refs':[spec['dataset']],'score_bands':tiers,'verification_status':'source_snapshot_derived',
          'editorial_status':'RESEARCH_DRAFT_NOT_PUBLISHABLE','content_revision':'2026-10-21-creative-rebalance-v1',
          'metric_provenance':spec['caveat']+' Measurement provenance: '+spec['metric'],
          'measurement_snapshot':'Frozen bundled dataset exported 2026-10-21',
          'measurement':{'property':spec['metric'],'edition':spec['dataset'],'numeric_rule':spec['rounding'],'time_dependent':spec['day'] in (4,5,6,7)},
          'answer_scope':{'type':'finite_source_world','coverage':'complete_for_bundled_snapshot_not_global_category','claimed_exhaustive':False,'entity_scope':spec['caveat'],'dataset_count':len(answers)},
          'scoring_policy':'Rounded signed distance from a fixed target within a finite scoring window. Wrong-side and too-far answers score zero.',
          'scoring_window':{'max_scoring_distance':tiers[-1]['max_gap_inclusive'],'units':spec['unit'],'outside_window_points':0,'wrong_side_points':0,'exact_match_points':1200},
          'answers':answers,'recognized_category_candidates':[],'verified_answer_count':len(answers),'catalogued_answer_count':len(answers),
          'recognized_category_candidate_count':0,'alias_count':sum(len(x['aliases']) for x in answers),
          'score_distribution_audit':{str(k):counter[k] for k in [1200,1000,800,600,400,200,0]},
          'research_status':'INCOMPLETE_RESEARCH: six new source families added, but six-day full diversity and exhaustive-source targets still NOT met.',
        })
        if spec['unit']=='%':q['scoring_rounding']={'method':'nearest_whole_percent','scored_precision':'1 percentage point','display_precision':'integer'}
        else:q.pop('scoring_rounding',None)
        p.write_text(json.dumps(bank,ensure_ascii=False,separators=(',',':'))+'\n')
        snapshot={'dataset_id':spec['dataset'],'source_url':spec['src'],'source_file_description':spec['caveat'],'metric':spec['metric'],'rounding_step':step, 'entities':raw}
        (ROOT/'datasets'/f'{spec["dataset"]}-frozen.json').write_text(json.dumps(snapshot,ensure_ascii=False,separators=(',',':')))
    print('Updated six days, 6 independently sourced question categories. First day unchanged.')
if __name__=='__main__':main()
