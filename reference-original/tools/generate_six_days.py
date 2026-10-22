"""Reproducible, source-record-based new CLOSEISH days. Never synthesizes entities or measurements."""
from pathlib import Path
from collections import Counter, defaultdict
import json, copy, datetime, math
from rdkit import Chem
R=Path(__file__).resolve().parents[1]
load=lambda s:json.loads((R/'datasets'/s).read_text())['records']
un=load('unesco-property-areas-2026.json'); co=load('countryinfo-snapshot-2026.json'); gap=load('gapminder-plotly-1952-2007.json'); countries=load('countryinfo-comprehensive-snapshot.json'); states=load('statsmodels-statecrime-2009.json'); firms=load('statsmodels-grunfeld-1935-1954.json')
ptable=Chem.GetPeriodicTable(); gd=defaultdict(dict)
for r in gap:gd[r['country']][r['year']]=r

# A metric definition is distinct, frozen and traceable. Many source families repeat;
# editorial warning is supplied in report instead of pretending global originality.
def entities(kind, metric, year=None, year2=None):
    out=[]
    if kind=='un':
        for r in un:
            if metric=='year':val=int(r['inscription_year']) if str(r.get('inscription_year','')).isdigit() else None
            elif metric=='area':
                try:val=float(r['area_hectares_decimal'])
                except (ValueError,TypeError):val=None
            else:continue
            out.append((str(r['id']),r['name'],val,r['url'],[]))
    elif kind=='usstate':
        for r in states:
            val=r.get(metric)
            # 2009 UCR crime reporting caveat applies to Illinois and Minnesota.
            if metric=='violent' and r['name'] in ('Illinois','Minnesota'):val=None
            out.append((r['name'],r['name'],val,f'statsmodels statecrime / {r["name"]} / {metric} / 2009 or 2010 Census',[]))
    elif kind=='firm':
        for r in firms:
            out.append((r['name'],r['name'],r.get(metric),f'Grunfeld original 11 firms, 1935–1954 / {r["name"]}',[]))
    elif kind=='heritage_country':
        # Import EVERY country/territory named by UNESCO first. Missing areas are
        # not zero; aggregate area metrics are not scoreable if any site is unmeasured.
        by=defaultdict(list)
        for r in un:
            try:area=float(r['area_hectares_decimal'])
            except (ValueError,TypeError):area=None
            if area is not None and area<=0:area=None
            for name in r.get('countries',[]):
                by[name].append(dict(area=area,cat=r.get('category',''),year=int(r['inscription_year']) if str(r.get('inscription_year','')).isdigit() else None))
        for name,items in by.items():
            areas=[x['area'] for x in items if x['area'] is not None]
            all_area_known=len(areas)==len(items)
            total=len(items)
            natural=sum(x['cat']=='Natural' for x in items)
            post2000=sum(x['year'] is not None and x['year']>=2000 for x in items)
            import statistics
            if metric=='aggregate_area':val=sum(areas) if all_area_known else None
            elif metric=='mean_area':val=sum(areas)/total if all_area_known else None
            elif metric=='max_area':val=max(areas) if all_area_known else None
            elif metric=='median_area':val=statistics.median(areas) if all_area_known else None
            elif metric=='natural_share':val=100*natural/total if all(x['cat'] in ('Natural','Cultural','Mixed') for x in items) else None
            elif metric=='modern_share':val=100*post2000/total if all(x['year'] is not None for x in items) else None
            else:continue
            out.append((name,name,val,f'UNESCO {name} / all properties, not selected by score',[]))
    elif kind=='country':
        from math import radians,sin,cos,asin,sqrt
        for r in countries:
            lat=r.get('latlng') or []
            cap=r.get('capital_latlng') or []
            area=r.get('area');pop=r.get('population');borders=r.get('borders') or []
            provinces=r.get('provinces') or []
            longok=len(cap)==2 and cap[1] is not None
            if metric=='area':val=area
            elif metric=='population':val=pop
            elif metric=='density':val=(pop/area if pop and area else None)
            elif metric=='calling_code':
                codes=[int(str(k).replace('+','')) for k in (r.get('callingCodes') or []) if str(k).replace('+','').isdigit()]
                val=min(codes) if codes else None
            elif metric=='capital_longitude':val=abs(cap[1]) if longok else None
            elif metric=='centroid_longitude':val=abs(lat[1]) if len(lat)==2 else None
            elif metric=='capital_latitude':val=abs(cap[0]) if len(cap)==2 else None
            elif metric=='centroid_latitude':val=abs(lat[0]) if len(lat)==2 else None
            elif metric=='capital_greenwich_distance':val=abs(cap[1])*111.195 if longok else None
            elif metric=='centroid_greenwich_distance':val=abs(lat[1])*111.195 if len(lat)==2 else None
            elif metric=='capital_to_centroid':
                if len(lat)!=2 or len(cap)!=2:val=None
                else:
                    x1,y1=map(radians,lat);x2,y2=map(radians,cap)
                    h=sin((x2-x1)/2)**2+cos(x1)*cos(x2)*sin((y2-y1)/2)**2
                    val=6371.0088*2*asin(min(1,sqrt(h)))
            elif metric=='lat_difference_km':val=abs(lat[0]-cap[0])*111.195 if len(lat)==2 and len(cap)==2 else None
            elif metric=='longitude_difference_km':val=abs((lat[1]-cap[1]+180)%360-180)*111.195 if len(lat)==2 and len(cap)==2 else None
            elif metric=='area_per_neighbor':val=area/len(borders) if area and borders else None
            elif metric=='population_per_neighbor':val=pop/len(borders) if pop and borders else None
            elif metric=='geojson_outline':val=r.get('source_geojson_outline_km')
            elif metric=='geojson_ns_span':val=r.get('source_geojson_ns_span_km')
            elif metric=='area_per_timezone':val=area/len(r.get('timezones') or []) if area and r.get('timezones') else None
            else:continue
            aliases=[x for x in (r.get('altSpellings') or []) if x and len(x)>=2 and x!=r['name']]
            out.append((r['ISO']['alpha3'],r['name'],val,f"countryinfo comprehensive frozen snapshot ISO {r['ISO']['alpha3']}",aliases))
    elif kind=='element':
        for z in range(1,119):
            name=ptable.GetElementName(z);symbol=ptable.GetElementSymbol(z)
            val={'number':lambda: z, 'covalent_pm':lambda: ptable.GetRcovalent(z)*100, 'vdw_pm':lambda: ptable.GetRvdw(z)*100,
                 'bohr_pm':lambda:ptable.GetRb0(z)*100,'isotope_mass':lambda:ptable.GetMostCommonIsotopeMass(z),'neutrons':lambda:ptable.GetMostCommonIsotope(z)-z}[metric]()
            if metric in ('covalent_pm','vdw_pm','bohr_pm','isotope_mass','neutrons') and val<=0:val=None
            out.append((str(z),name,val,f'RDKit periodic table Z={z}; {symbol}',[symbol]))
    elif kind=='geo':
        for r in co:
            # Frozen countryinfo snapshot, includes territories. Explicitly say country or territory.
            lat=r.get('capital_abs_latitude')
            if lat is None: val=None
            elif metric=='latitude':val=float(lat)
            elif metric=='polekm':val=(90-float(lat))*111.195
            elif metric=='lat_km':val=float(lat)*111.195
            else:continue
            out.append((r['iso3'],r['name'],val,f"countryinfo snapshot record {r['source_key']}",[]))
    elif kind=='gap':
        for name,years in gd.items():
            a=years.get(year);b=years.get(year2) if year2 else None
            if a is None or (year2 and b is None):val=None
            elif metric=='gdp':val=a['gdp_per_capita']
            elif metric=='pop':val=a['population']
            elif metric=='life':val=a['life_exp_years']
            elif metric=='gdp_gain':val=b['gdp_per_capita']-a['gdp_per_capita']
            elif metric=='pop_gain':val=b['population']-a['population']
            elif metric=='life_gain':val=b['life_exp_years']-a['life_exp_years']
            elif metric=='pop_ratio':val=(b['population']/a['population']-1)*100
            elif metric=='gdp_ratio':val=b['gdp_per_capita']/a['gdp_per_capita']*100
            else:continue
            out.append((name,name,val,f'Gapminder / {name} / {year}'+(f'–{year2}' if year2 else ''),[]))
    return out

S=[]
def add(kind,metric,prompt,unit,year=None,year2=None,round_to=1,topic=None):
    S.append(dict(kind=kind,metric=metric,prompt=prompt,unit=unit,year=year,year2=year2,round_to=round_to,topic=topic or {'un':'culture','heritage_country':'culture','element':'science','geo':'geography','gap':'economics','country':'geography','usstate':'society','firm':'economics'}[kind]))
# 36 numerical tasks, source-defined categories, distributed six per day.
# Where the Gapminder set contains a territory (e.g. Hong Kong or Réunion),
# the visible question explicitly allows territories; it does NOT call them sovereign countries.
# This is still a DRAFT: source concentration and uncommon composites require editorial review.
add('gap','pop','Name a country whose population in 1982 was at least {limit} people. (Rounded to the nearest million people.)','people',year=1982,round_to=1000000,topic='history')
add('gap','life','Name a country whose life expectancy in 2007 was at least {limit} years. (Rounded to the nearest whole year.)','years',year=2007,topic='biology')
add('gap','gdp','Name a country with 1972 GDP per person of at most US${limit}. (Rounded to the nearest US$100.)','$',year=1972,round_to=100,topic='economics')
add('gap','gdp_gain','Name a country whose inflation-adjusted GDP per person increased by at most US${limit} between 1952 and 2007. (Rounded to the nearest US$100.)','$',year=1952,year2=2007,round_to=100,topic='economics')
add('gap','pop_ratio','Name a country whose population grew by at least {limit}% between 1952 and 2007. (Percentages are rounded to the nearest whole percent.)','%',year=1952,year2=2007,topic='history')
add('gap','pop_gain','Name a country whose population rose by at least {limit} people between 1952 and 2007. (Rounded to the nearest million people.)','people',year=1952,year2=2007,round_to=1000000,topic='geography')
for metric,desc,unit,mode in [
 ('number','atomic number','', 'at least'),('covalent_pm','covalent radius','pm','at most'),
 ('vdw_pm','van der Waals radius','pm','at least'),('bohr_pm','Rb0 atomic radius parameter','pm','at most'),
 ('isotope_mass','mass of its most common isotope','u','at least'),('neutrons','neutron count in its most abundant isotope','neutrons','at most')]:
    add('element',metric,f'Name a chemical element with {desc} {mode} {{limit}}{(" "+unit) if unit else ""}. (Values rounded to the nearest whole unit.)',unit,topic='science')
for metric,desc,unit,comp,topic in [
 ('area','land area','km²','at least','geography'),('population','population in the frozen source snapshot','people','at most','geography'),
 ('density','population density in the source snapshot','people/km²','at least','geography'),
 ('calling_code','international telephone country calling code','', 'at most','technology'),
 ('capital_longitude','absolute longitude of its capital','degrees','at least','geography'),
 ('centroid_longitude','absolute longitude of its mapped country centre','degrees','at most','geography'),
 ('capital_latitude','latitude of its capital away from the equator','degrees','at least','geography'),
 ('centroid_latitude','latitude of its mapped country centre away from the equator','degrees','at least','geography'),
 ('capital_greenwich_distance','east-west equatorial arc distance of its capital longitude from Greenwich','km','at least','geography'),
 ('centroid_greenwich_distance','equatorial arc distance of its country-centre longitude from Greenwich','km','at most','geography'),
 ('capital_to_centroid','great-circle distance between its capital and country centre','km','at least','geography'),
 ('lat_difference_km','north-south separation of its capital from its mapped centre','km','at most','geography'),
 ('longitude_difference_km','east-west equatorial arc separation of its capital from the country centre','km','at least','geography'),
 ('area_per_neighbor','land area per land-bordering neighbor','km²','at most','geography'),
 ('population_per_neighbor','inhabitants per land-bordering neighbor','people','at least','geography'),
 ('geojson_outline','total mapped polygon-boundary length in a simplified geographic dataset','km','at most','geography'),
 ('geojson_ns_span','north–south span of its simplified mapped territory','km','at least','geography'),
 ('area_per_timezone','land area per listed time zone','km²','at most','geography')]:
    add('country',metric,f'Name a country or territory whose {desc} is {comp} {{limit}}{" "+unit if unit else ""}. (Values rounded to the nearest {{rounding_note}}.)',unit,round_to=(100000 if unit=='people' else 100 if unit=='km²' else 10 if unit=='km' else 1),topic=topic)
for metric,description,unit,comp in [
 ('aggregate_area','total inscribed UNESCO World Heritage site area','hectares','at least'),
 ('mean_area','average area of its inscribed UNESCO sites','hectares','at most'),
 ('max_area','area of its largest UNESCO World Heritage site','hectares','at least'),
 ('median_area','median inscribed area of its UNESCO World Heritage sites','hectares','at most'),
 ('natural_share','share of its listed UNESCO sites classified as natural','%','at least'),
 ('modern_share','share of its listed UNESCO sites inscribed since 2000','%','at most')]:
    add('heritage_country',metric,f'Name a country or territory named in the UNESCO World Heritage dataset whose {description} is {comp} {{limit}}{(" "+unit) if unit != "%" else "%"}. (Values rounded to the nearest whole {"percent" if unit=="%" else "unit"}.)',unit,topic='culture')
assert len(S)==36,len(S)
# Interleave six families across each day. Each day has one question each from:
# Gapminder, chemistry, country metrics (3), UNESCO aggregates.
G=S[:6];E=S[6:12];C=S[12:30];H=S[30:]
for spec in G:
    spec['prompt']=spec['prompt'].replace('Name a country ', 'Name a country or territory listed by Gapminder ')
# Replace selected geographically clustered ideas with different source families.
C[1]=dict(kind='usstate',metric='violent',prompt='Name a US state or Washington, DC with a 2009 violent-crime incident rate of at most {limit} per 100,000 residents. (Rates are rounded to the nearest whole incident.)',unit='per 100k',year=None,year2=None,round_to=1,topic='society')
C[4]=dict(kind='usstate',metric='urban',prompt='Name a US state or Washington, DC with at least {limit}% of residents living in a US Census urbanized area in 2010. (Percentages are rounded to the nearest whole percent.)',unit='%',year=None,year2=None,round_to=1,topic='society')
C[7]=dict(kind='usstate',metric='hs_grad',prompt='Name a US state or Washington, DC where at most {limit}% of residents had graduated from high school in 2009. (Percentages are rounded to the nearest whole percent.)',unit='%',year=None,year2=None,round_to=1,topic='education')
C[10]=dict(kind='usstate',metric='single',prompt='Name a US state or Washington, DC where at least {limit}% of family households had a householder with no spouse present in 2009. (Percentages are rounded to the nearest whole percent.)',unit='%',year=None,year2=None,round_to=1,topic='society')
C[13]=dict(kind='usstate',metric='white',prompt='Name a US state or Washington, DC where at most {limit}% of residents reported their race as white alone in the 2009 American Community Survey. (Percentages are rounded to the nearest whole percent.)',unit='%',year=None,year2=None,round_to=1,topic='society')
C[16]=dict(kind='usstate',metric='poverty',prompt='Name a US state or Washington, DC with a poverty rate of at least {limit}% in 2009. (Percentages are rounded to the nearest whole percent.)',unit='%',year=None,year2=None,round_to=1,topic='society')
S=[question for d in range(6) for question in (G[d],E[d],C[3*d],H[d],C[3*d+1],C[3*d+2])]
TEMPLATE=json.loads((R/'days/day-01.json').read_text())['q1']
points=[1000,800,600,400,200]
names={1200:'PERFECT HIT',1000:'RAZOR EDGE',800:'CLOSE CALL',600:'SOLID HIT',400:'IN THE ZONE',200:'ON THE BOARD',0:'TOO FAR'}
SOURCE={'un':'https://data.unesco.org/explore/dataset/whc001/?flg=en-us','geo':'https://github.com/porimol/countryinfo','country':'https://github.com/porimol/countryinfo','heritage_country':'https://data.unesco.org/explore/dataset/whc001/?flg=en-us','usstate':'https://www.statsmodels.org/stable/datasets/generated/statecrime.html','firm':'https://www.statsmodels.org/stable/datasets/generated/grunfeld.html', 'element':'https://www.rdkit.org/docs/source/rdkit.Chem.rdchem.html','gap':'https://www.gapminder.org/data/'}
AUDIT=[]
def make(spec,day,qi):
    raw=entities(spec['kind'],spec['metric'],spec['year'],spec['year2'])
    step=spec['round_to']
    v=[(ident,name,math.floor(float(val)/step+0.5)*step if val is not None and math.isfinite(float(val)) else None,locator,aliases)
       for ident,name,val,locator,aliases in raw]
    valid=sorted(set(int(a[2]) for a in v if a[2] is not None))
    direction='above' if 'at least' in spec['prompt'] else 'below'
    # Choose genuine observed target with at least one answer in each of five distinct neighborhoods.
    candidates=[]
    for t in valid:
        if t< (8 if spec['unit']=='%' else 50) or (spec['unit']=='%' and t>92):continue
        signed=[(x[2]-t if direction=='above' else t-x[2]) for x in v if x[2] is not None]
        good=sorted(g for g in signed if g>0)
        min_size=(5 if len(v)<40 else 14)
        if len(good)<min_size:continue
        # Every published score window must be finite and reasonably close to the target.
        # Small percentage targets have a 6 percentage-point minimum to support 7 tiers.
        max_dist=max(5*step, 6 if spec['unit']=='%' else 0, round(abs(t)*(.55 if spec['unit']=='%' else .4)))
        eligible=sorted(g for g in good if g<=max_dist)
        gaps=sorted(set(eligible))
        if len(gaps)<5:continue
        # 1000 and 800 reward the two nearest observed distances; lower tiers
        # progressively cover more answers, without ever expanding beyond max_dist.
        edges=[gaps[0],gaps[1]]
        for quantile in (.2,.5, .85):
            goal=eligible[min(len(eligible)-1,int(len(eligible)*quantile))]
            edge=next((g for g in gaps if g>edges[-1] and g>=goal),None)
            if edge is None:edge=next((g for g in gaps if g>edges[-1]),None)
            if edge is None:break
            edges.append(edge)
        if len(edges)!=5:continue
        cuts=edges
        outside=sum(x<0 or x>cuts[-1] for x in signed)
        if outside<(3 if len(v)<40 else 20):continue
        high=sum(x==0 for x in signed)
        if high>5:continue
        near=sum(0<x<=cuts[0] for x in signed)
        if near>12:continue
        c200=sum(cuts[3]<x<=cuts[4] for x in signed)
        # Prefer alternatives naturally producing a broad final scoring tier.
        candidates.append((high, -min(c200,15), abs(len(eligible)-len(v)*.20),t,cuts))
    if not candidates:
        # Explicitly fail rather than make up arbitrary scores or silently drop entities.
        raise ValueError(f'No fully scored 7 tiers for {spec}: data points {len(valid)}')
    candidates.sort(key=lambda x:(x[0],x[1],x[2],abs(x[3]-(200 if spec['unit']!='%' else 50))))
    _,_,_,target,cuts=candidates[0]
    band=[dict(max_gap_inclusive=int(edge),points=p,tier=names[p]) for p,edge in zip(points,cuts)]
    # If a zero occurs in an omitted category, retain it in the correct entity scope.
    out=copy.deepcopy(TEMPLATE)
    date=(datetime.date(2026,10,20)+datetime.timedelta(days=day-1)).isoformat()
    out.update(id=f"closeish_{date.replace('-','')}_q{qi}",date=date,day_number=day,
      topic=spec['topic'],bank_id=f"{spec['kind']}-{spec['metric']}-{spec['year'] or 'all'}-{spec['year2'] or 'end'}-{day}",question_family=f"{spec['kind']}-{spec['metric']}",
      prompt=spec['prompt'].replace('{limit}',f'{int(target):,}').replace('{rounding_note}',('100,000 people' if step==100000 else '100 square kilometres' if step==100 else '10 kilometres' if step==10 else 'whole unit')), metric=f"{spec['kind']} {spec['metric']} {spec['year']} {spec['year2']}",unit=spec['unit'],limit=int(target),
      comparison='at_least' if direction=='above' else 'at_most',direction=direction,score_bands=band,time_limit_seconds=30,
      source=SOURCE[spec['kind']],source_refs=[spec['kind']+'-frozen-snapshot'],
      verification_status='computed_from_frozen_local_snapshot',editorial_status='RESEARCH_DRAFT_NOT_PUBLISHABLE',
      content_revision=f"2026-10-20-sixdays-research-v1-{day}-{qi}",metric_provenance=f"Source snapshot {spec['kind']} metric {spec['metric']} ({spec['year']}, {spec['year2']}). Original source values converted to {step} increment; no unseen values imputed.",
      measurement_snapshot='Frozen local October 2026 source data',measurement=dict(snapshot_date='2026-10-20',property=spec['metric'],edition=spec['kind'],numeric_rule=f'round to nearest {step}',time_dependent=True),
      answer_scope=dict(type='finite_source_world',coverage='frozen_source_snapshot',claimed_exhaustive=False,entity_scope='All entities in the frozen source snapshot; broader completeness not guaranteed',dataset_count=len(raw)),
      scoring_window=dict(max_scoring_distance=int(cuts[-1]),units=spec['unit'],outside_window_points=0,wrong_side_points=0,exact_match_points=1200),
      approach_rule=dict(required_side=f'from_{direction}',operator='>=' if direction=='above' else '<=',exact_target_allowed=True,wrong_side_points=0,exact_target_points=1200))
    if spec['unit']=='%':
        out['scoring_rounding']={'method':'nearest_whole_percent','precision':1}
    out['answers']=[];out['recognized_category_candidates']=[]
    for ident,name,value,locator,aliases in v:
        base=dict(entity_id=f"{spec['kind']}-{ident}-{''.join(ch.lower() if ch.isalnum() else '-' for ch in name)}",canonical=name,aliases=[dict(input=a,kind='symbol',action='replace_with_canonical') for a in aliases if a.lower()!=name.lower()],
                  verified_status='source_snapshot',source_refs=[dict(source_id=spec['kind']+'-frozen-snapshot',locator=locator)])
        if value is None:
            base.update(metric_value=None,membership_status='recognized_entity_unverified_measurement')
            out['recognized_category_candidates'].append(base)
        else:
            delta=value-target if direction=='above' else target-value
            points_obtained=0 if delta<0 or delta>cuts[-1] else 1200 if delta==0 else next(p for p,b in zip(points,cuts) if delta<=b)
            base.update(metric_value=value,points=points_obtained,tier=('CROSSED LIMIT' if delta<0 else 'TOO FAR' if points_obtained==0 else names[points_obtained]))
            out['answers'].append(base)
    c=Counter(a['points'] for a in out['answers'])
    assert all(c[k] for k in [0,200,400,600,800,1000,1200]),(spec,c)
    out['verified_answer_count']=len(out['answers']);out['catalogued_answer_count']=len(out['answers'])+len(out['recognized_category_candidates']);out['recognized_category_candidate_count']=len(out['recognized_category_candidates']);out['alias_count']=sum(len(a['aliases']) for a in out['answers']);out['score_distribution_audit']={str(k):c[k] for k in [1200,1000,800,600,400,200,0]}
    out['research_status']='SOURCE-DERIVED RESEARCH DRAFT; significant topic/source repetition across six days; not editorially cleared'
    out['scoring_policy']='Round source values consistently, wrong side and farther-than-window score zero, missing measurement unscored'
    out['perfect_tier']={'points':1200,'tier':'PERFECT HIT','rule':'exact rounded target match'}
    if 'source_dataset' in out:out.pop('source_dataset')
    AUDIT.append(dict(day=day,q=qi,prompt=out['prompt'],source=spec['kind'],family=out['question_family'],measured=len(out['answers']),pending=len(out['recognized_category_candidates']),score_distribution=dict(c)))
    return out

for day in range(2,8):
    questions={f'q{i}':make(S[(day-2)*6+(i-1)],day,i) for i in range(1,7)}
    (R/'days'/f'day-{day:02d}.json').write_text(json.dumps(questions,ensure_ascii=False,indent=2)+'\n')
(R/'docs'/'SIX-DAY-RESEARCH-AUDIT.json').write_text(json.dumps(AUDIT,ensure_ascii=False,indent=2)+'\n')
print('Generated',len(AUDIT),'research drafts',sum(q['measured'] for q in AUDIT),'scored entity rows across all questions')
for a in AUDIT:print(f"day{a['day']} q{a['q']} {a['family']} {a['measured']} measured; {a['prompt'][:85]}")
