"""Increase real answer coverage using locally installed GIS source data and UNESCO snapshot.
No made-up entities: each answer carries a file-backed identity and a reproducible metric.
"""
from pathlib import Path
import json,math,statistics,csv,re,collections,copy,hashlib
import shapefile,pycountry
from pyproj import Geod
from shapely.geometry import shape as toshape
R=Path(__file__).resolve().parents[1]; geom=Geod(ellps='WGS84')
import importlib
S=str(Path(list(importlib.import_module('mpl_toolkits.basemap_data').__path__)[0])/'UScounties')
reader=shapefile.Reader(S,encoding='latin1')
print('Reading',len(reader),'real counties and county equivalents')
rows=[]
for shp_rec in reader.iterShapeRecords():
 r=shp_rec.record.as_dict(); poly=toshape(shp_rec.shape.__geo_interface__)
 if poly.is_empty:continue
 minlon,minlat,maxlon,maxlat=poly.bounds
 if maxlon-minlon>180:
  # A date-line-spanning Alaska county cannot be measured safely using this simple bbox.
  # Keep its identity in each catalog as an unscored, unresolved measurement.
  state=pycountry.subdivisions.get(code='US-'+r['STATE']);state_name=state.name if state else r['STATE']
  name=r['NAME']+' Census Area, '+state_name
  rows.append({'fips':r['FIPS'],'canonical':name,'state_code':r['STATE'],'name':r['NAME'],'aliases':[r['NAME']+' Census Area, '+r['STATE']],'measurements':{k:None for k in ['area','equator','width','perimeter','height','dc_distance']}})
  continue
 center_lon,center_lat=(minlon+maxlon)/2,(minlat+maxlat)/2
 state=pycountry.subdivisions.get(code='US-'+r['STATE'])
 state_name=state.name if state else r['STATE']
 suffix=r['LSAD']
 # Some source codes have machine abbreviations. Keep the original code FIPS as identity.
 county_label=r['NAME']+' '+({'County':'County','Parish':'Parish','Borough':'Borough','City':'City','Muno':'Municipio','Muny':'Municipality','Cty&Bor':'City and Borough','CA':'Census Area'}.get(suffix,suffix) if suffix!='0' else '')
 county_label=county_label.strip()
 if county_label.endswith(' County County'):county_label=county_label.removesuffix(' County')
 full=county_label+', '+state_name
 alias_names=[county_label+', '+r['STATE']]
 if r['NAME']!=county_label:alias_names.extend([r['NAME']+', '+state_name, r['NAME']+', '+r['STATE']])
 # geodetic polygon area and perimeter computed from simplified shape; use abs for orientation.
 try:
  area_m2,perimeter_m=geom.geometry_area_perimeter(poly)
  area_km2=abs(area_m2)/1e6
 except Exception:
  continue
 width_km=(maxlon-minlon)*111.195*math.cos(math.radians(center_lat))
 height_km=(maxlat-minlat)*111.195
 # Great-circle county-bound-box center to Washington, DC (38.9072 N, -77.0369 E).
 az1,az2,capital_distance_m=geom.inv(center_lon,center_lat,-77.0369,38.9072)
 values={
 'area': area_km2,
 'equator':abs(center_lat)*111.195,
 'width':width_km,
 'perimeter':perimeter_m/1000,
 'height':height_km,
 'dc_distance':capital_distance_m/1000,
 }
 if any(not math.isfinite(v) or v<0 for v in values.values()):continue
 rows.append({'fips':r['FIPS'],'canonical':full,'state_code':r['STATE'],'name':r['NAME'],'aliases':sorted(set(a for a in alias_names if a!=full)),'measurements':values})
assert len(rows)>3000,len(rows)
print('Computed shapes',len(rows))
source=R/'datasets'/'basemap-uscountries-shapefile-derived.json'
source.write_text(json.dumps({'source':'mpl_toolkits.basemap_data/UScounties.shp local version','measurement_method':'WGS84 geodesic area/perimeter and shape bounding-box proxy; approximate geography, not official census survey measurements','source_records':len(rows),'records':rows},ensure_ascii=False,separators=(',',':')))
unesco=json.loads((R/'datasets/unesco-property-areas-2026.json').read_text())['records']
metrics={
 'area':('approximate geodesic area of its mapped US county polygon', 'km²','below',1, 'Name a U.S. county or county equivalent whose mapped area is at most {limit} km². (Approximate shape-based value, rounded to the nearest km².)'),
 'equator':('geographic distance between its bounding-box centre and the equator', 'km','above',1, 'Name a U.S. county or county equivalent whose mapped centre is at least {limit} km north of the equator. (Approximate bounding-box centre; nearest km.)'),
 'width':('east–west width of its geographic bounding box','km','above',1,'Name a U.S. county or county equivalent whose mapped east–west span is at least {limit} km. (Approximate bounding-box width; nearest km.)'),
 'perimeter':('geodesic perimeter of its mapped county polygon','km','below',1,'Name a U.S. county or county equivalent whose mapped perimeter is at most {limit} km. (Approximate polygon boundary; nearest km.)'),
 'height':('north–south height of its geographic bounding box','km','above',1,'Name a U.S. county or county equivalent whose mapped north–south span is at least {limit} km. (Approximate bounding-box height; nearest km.)'),
 'dc_distance':('distance from its bounding-box centre to Washington, DC','km','above',1,'Name a U.S. county or county equivalent whose mapped centre is at least {limit} km from Washington, DC. (Approximate bounding-box centre; nearest km.)')
}
# Six questions, one per new day, each originally country-only geography Q3.
score_names={1200:'PERFECT HIT',1000:'RAZOR EDGE',800:'CLOSE CALL',600:'SOLID HIT',400:'IN THE ZONE',200:'ON THE BOARD'}

def build_question(q,all_entities,measure_key,desc,unit,direction,step,prompt,source_url,source_id,source_desc):
 observed=[]; pending=[]
 for ent in all_entities:
  val=ent['values'].get(measure_key)
  if val is None or not math.isfinite(val):pending.append(ent);continue
  v=int(math.floor(float(val)/step+0.5))*step
  observed.append((ent,v))
 freq=collections.Counter(v for _,v in observed)
 good_unique=sorted(set(freq)); assert len(good_unique)>=10
 candidates=[]
 for target in good_unique:
  if (unit=='%' and not 8<=target<=92) or (unit!='%' and target<50):continue
  if freq[target]>4:continue
  positive=[(v-target if direction=='above' else target-v) for _,v in observed if (v-target if direction=='above' else target-v)>0]
  max_dist=max(10*step,target*(0.75 if unit=='%' else 0.30))
  eligible=sorted(g for g in positive if g<=max_dist)
  distinct=sorted(set(eligible))
  if len(distinct)<5 or len(eligible)<(12 if unit=='%' else 40):continue
  edges=[distinct[0],distinct[1]]
  for pct in (.10,.33,.85):
   boundary=eligible[min(len(eligible)-1,int((len(eligible)-1)*pct))]
   boundary=next((g for g in distinct if g>edges[-1] and g>=boundary),None)
   if boundary is None:break
   edges.append(boundary)
  if len(edges)!=5:continue
  if len(set(edges))!=5:continue
  counts=[];previous=0
  for e in edges:counts.append(sum(previous<g<=e for g in eligible));previous=e
  if not all(counts):continue
  perfect=freq[target]
  total_earning=sum(g<=edges[-1] for g in positive)
  # Prefer a genuinely unusual perfect hit, a rich 200 tier, and natural target.
  rank=(perfect,abs(total_earning-len(observed)*.18),abs(target-statistics.median(good_unique)))
  candidates.append((rank,target,edges,counts))
 if not candidates:raise ValueError(f'No acceptable seven-tier geometry split for {measure_key}')
 candidates.sort(key=lambda t:t[0]);_,limit,edges,counts=candidates[0]
 bands=[{'max_gap_inclusive':int(edge),'points':points,'tier':score_names[points]} for edge,points in zip(edges,[1000,800,600,400,200])]
 from collections import Counter
 scores=collections.Counter()
 answers=[]
 for ent,v in observed:
  gap=v-limit if direction=='above' else limit-v
  points=0 if gap<0 or gap>edges[-1] else 1200 if gap==0 else next(b['points'] for b in bands if gap<=b['max_gap_inclusive'])
  tier=score_names.get(points,'TOO FAR' if gap>edges[-1] else 'CROSSED LIMIT')
  scores[points]+=1
  answers.append({'entity_id':ent['id'],'canonical':ent['canonical'],'aliases':[{'input':alt,'kind':'source_alias','action':'replace_with_canonical'} for alt in ent.get('aliases',[])],
                  'verified_status':'source_derived_approximate','source_refs':[{'source_id':source_id,'locator':ent['locator']}], 'metric_value':int(v),'points':points,'tier':tier})
 assert sorted(scores)==[0,200,400,600,800,1000,1200],(measure_key, scores)
 # Whole-percent metrics use the rounded integer for both scoring and visibility.
 q.update({'topic':'geography' if 'county' in source_id else 'culture','bank_id':f'{source_id}-{measure_key}-{limit}', 'question_family':f'{source_id}-{measure_key}',
  'metric':desc,'unit':unit,'prompt':prompt.replace('{limit}',f'{limit:,}'),'limit':int(limit),'direction':direction,'comparison':'at_least' if direction=='above' else 'at_most',
  'score_bands':bands,'source':source_url,'source_refs':[source_id],
  'verification_status':'locally_computed_from_named_snapshot','editorial_status':'RESEARCH_DRAFT_NOT_PUBLISHABLE',
  'content_revision':q['content_revision'] if q['content_revision'].endswith('-expanded-v2') else q['content_revision']+'-expanded-v2',
  'metric_provenance':source_desc+'; score uses rounded measure and a finite window; named records source-linked.',
  'measurement_snapshot':'CLOSEISH local documented data snapshot',
  'measurement':{'property':measure_key,'edition':source_id,'numeric_rule':f'nearest {step} {unit}','time_dependent':False},
  'answer_scope':{'type':'finite_source_world','coverage':'source_snapshot','claimed_exhaustive':True,'entity_scope':f'All {len(observed)+len(pending)} source records (measured and pending separately)','dataset_count':len(observed)+len(pending)},
  'scoring_policy':'Bounded signed distance on rounded measures. Wrong side and too far earn zero. Approximate geometry disclosed.',
  'scoring_window':{'max_scoring_distance':int(edges[-1]),'units':unit,'outside_window_points':0,'wrong_side_points':0,'exact_match_points':1200},
  'answers':answers,'recognized_category_candidates':[{'entity_id':ent['id'],'canonical':ent['canonical'],'aliases':[{'input':x,'kind':'source_alias','action':'replace_with_canonical'} for x in ent.get('aliases',[])],
  'verified_status':'measurement_unavailable','source_refs':[{'source_id':source_id,'locator':ent['locator']}], 'metric_value':None,'membership_status':'recognized_entity_unverified_measurement'} for ent in pending],
  'verified_answer_count':len(answers),'catalogued_answer_count':len(observed)+len(pending),'recognized_category_candidate_count':len(pending),
  'alias_count':sum(len(a['aliases']) for a in answers),
  'score_distribution_audit':{str(k):scores.get(k,0) for k in [1200,1000,800,600,400,200,0]},
  'research_status':'Named source-derived measurements, research draft; verify source limitations before publication.'})
 if unit=='%':
  q['scoring_rounding']={'method':'nearest_whole_percent','scored_precision':'1 percentage point','display_precision':'integer'}
 return {'limit':limit,'measured':len(answers),'pending':len(pending),'distribution':dict(scores),'family':q['question_family']}

cnt=[{'id':'us-county-'+r['fips'],'canonical':r['canonical'],'aliases':r['aliases'],'values':r['measurements'],'locator':f'Basemap UScounties.shp / FIPS {r["fips"]}'} for r in rows]
summary=[]
for day,metric in enumerate(metrics,2):
 args=metrics[metric]; p=R/'days'/f'day-{day:02d}.json'; data=json.loads(p.read_text());q=data['q3']
 result=build_question(q,cnt,metric,*args,source_url='https://matplotlib.org/basemap/stable/users/geography.html',source_id='basemap-county-shapes',source_desc='U.S. county boundaries distributed with Basemap; approximate WGS84 geodesy. NOT authoritative measured area/length')
 p.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
 print(f'Day {day}, Q3 county {metric} -> {result}');summary.append({'day':day,'q':'q3',**result})
# Replace two of the small UNESCO-by-country rollups by source-complete UNESCO *individual sites*.
# Different questions: site inscribed-area vs year (inscription is not area).
un_rows=[]
for v in unesco:
 canonical=v['name'];sid=v['id'];site={'id':'unesco-'+sid,'canonical':canonical,'aliases':[], 'locator':v['url'],'values':{}}
 if v.get('measurement_status')=='numeric_positive':
  try:site['values']['area']=float(v['area_hectares_decimal'])
  except (ValueError,TypeError):pass
 try:site['values']['inscription_year']=int(v['inscription_year'])
 except (ValueError,TypeError):pass
 un_rows.append(site)
for day,metric,detail,prompt,direction in [
 (3,'area','inscribed property area','Name a UNESCO World Heritage site whose inscribed area is at least {limit} hectares. (Areas rounded to the nearest whole hectare; buffer zones excluded.)','above'),
 (6,'inscription_year','year of inscription onto the UNESCO World Heritage List','Name a UNESCO World Heritage site inscribed no later than {limit}. (Inscription year, not initial construction year.)','below')]:
 p=R/'days'/f'day-{day:02d}.json';data=json.loads(p.read_text()); q=data['q4'];
 # UNESCO year has many ties even for rare years. Keep actual records and mark the editorial requirement unmet if necessary.
 try: result=build_question(q,un_rows,metric,detail,'hectares' if metric=='area' else 'year', direction, 1,prompt,
         source_url='https://data.unesco.org/explore/dataset/whc001/?flg=en-us',source_id='unesco-world-heritage-sites',
         source_desc='UNESCO DataHub whc001 snapshot 2026-10-17, individual source site records, inscription year or inscribed property area')
 except ValueError as e:
  print('SKIPPING',day,metric,str(e));continue
 q['topic']='culture';p.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
 print(f'Day {day} Q4 UNESCO {metric} -> {result}'); summary.append({'day':day,'q':'q4',**result})
(R/'datasets'/'EXPANSION-AUDIT.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
print('TOTAL new:',sum(x['measured'] for x in summary),'metrics',len(summary))

# Additional source: 2000 US Census-derived 437-county midwest sample shipped with plotnine.
# Regional population, education and poverty questions provide non-geometric diversity;
# five-state scope is explicit, so nobody is misled into expecting all US counties.
import pandas as pd
md=pd.read_csv(str(Path(importlib.import_module('plotnine').__file__).parent/'data'/'midwest.csv'))
state_map={x:pycountry.subdivisions.get(code='US-'+x).name for x in md.state.unique()}
midwest=[]
for _,r in md.iterrows():
 canonical=r['county'].title()+' County, '+state_map[r['state']]
 vals={k:float(r[k]) for k in ['poptotal','popadults','percollege','perchsd','percchildbelowpovert','percelderlypoverty'] if pd.notna(r[k])}
 midwest.append({'id':'midwest-census-'+str(int(r['PID'])),'canonical':canonical,'aliases':[r['county'].title()+' County, '+r['state']], 'locator':f'plotnine midwest.csv / PID {int(r["PID"])}', 'values':vals})
assert len(midwest)==437
(R/'datasets'/'midwest-2000-snapshot.json').write_text(json.dumps({'source':'ggplot2 / plotnine midwest dataset; descriptive variables extrapolated from metadata','year':2000,'limitations':'The upstream docs call variable explanations partly speculative; not official 2026 census measurements','records':midwest},ensure_ascii=False,separators=(',',':')))
midwest_metrics={
 2:('poptotal','population recorded for an eligible Midwestern county in 2000','people','above',100,'Name a county in Illinois, Indiana, Michigan, Ohio or Wisconsin with at least {limit} residents in the 2000 Census-based dataset. (Rounded to the nearest 100 people.)'),
 3:('percollege','share of county residents recorded as college educated in 2000','%','below',1,'Name a county in Illinois, Indiana, Michigan, Ohio or Wisconsin with at most {limit}% college-educated residents in the 2000 dataset. (Rounded to the nearest whole percent.)'),
 4:('percchildbelowpovert','share of children below poverty threshold in 2000','%','above',1,'Name a county in Illinois, Indiana, Michigan, Ohio or Wisconsin with at least {limit}% of children below the poverty line in the 2000 dataset. (Rounded to the nearest whole percent.)'),
 5:('popadults','number of adults in the 2000 dataset','people','below',100,'Name a county in Illinois, Indiana, Michigan, Ohio or Wisconsin with at most {limit} adults in the 2000 dataset. (Rounded to the nearest 100 people.)'),
 6:('perchsd','share of residents recorded as high-school graduates in 2000','%','above',1,'Name a county in Illinois, Indiana, Michigan, Ohio or Wisconsin with at least {limit}% high-school graduates in the 2000 dataset. (Rounded to the nearest whole percent.)'),
 7:('percelderlypoverty','share of elderly below poverty threshold in 2000','%','below',1,'Name a county in Illinois, Indiana, Michigan, Ohio or Wisconsin with at most {limit}% elderly residents below the poverty line in the 2000 dataset. (Rounded to the nearest whole percent.)')}
for day,args in midwest_metrics.items():
 metric,desc,unit,direction,step,prompt=args
 p=R/'days'/f'day-{day:02d}.json';data=json.loads(p.read_text());q=data['q5']
 try:
  result=build_question(q,midwest,metric,desc,unit,direction,step,prompt,
   source_url='https://ggplot2.tidyverse.org/reference/midwest.html',source_id='midwest-census-2000',
   source_desc='Published ggplot2/plotnine 2000-era Midwest county sample. Variable descriptions partly speculative according to publisher; not current official measurements')
 except ValueError as e:
  print('SKIPPING Midwest',day,metric,str(e));continue
 q['topic']='education' if metric in ['percollege','perchsd'] else 'society'
 p.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
 print(f'Day {day} Q5 Midwest {metric} -> {result}');summary.append({'day':day,'q':'q5',**result})
(R/'datasets'/'EXPANSION-AUDIT.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
