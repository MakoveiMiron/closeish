import json,os,hashlib,collections,math,unicodedata,datetime,statistics
from pathlib import Path
import numpy as np
from plotnine import data as p9
import plotnine,pycountry,rdkit,statsmodels,plotly
from statsmodels import datasets as smdatasets
from rdkit import Chem
import plotly.express as px
from matplotlib.colors import CSS4_COLORS,to_rgb,rgb_to_hsv
import matplotlib
ROOT=Path(__file__).resolve().parent.parent
SRCS={
 'msleep':('https://ggplot2.tidyverse.org/reference/msleep.html',f'plotnine {plotnine.__version__} bundled ggplot2 msleep 83 species'),
 'subdiv':('https://github.com/pycountry/pycountry',f'pycountry {pycountry.__version__} frozen ISO3166-1 and ISO3166-2 records'),
 'elnino':('https://www.statsmodels.org/stable/datasets/generated/elnino.html',f'statsmodels {statsmodels.__version__} bundled NOAA ERSST.V3B 1950-2010 61-year series'),
 'mtcars':('https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/mtcars.html',f'plotnine {plotnine.__version__} 32-row Motor Trend sample from Henderson & Velleman 1981'),
 'midwest':('https://ggplot2.tidyverse.org/reference/midwest.html',f'plotnine {plotnine.__version__} 437 county 2000 US Census subset'),
 'css4':('https://matplotlib.org/stable/gallery/color/named_colors.html',f'matplotlib {matplotlib.__version__} CSS4_COLORS 148 frozen named colors'),
 'gap':('https://www.gapminder.org/data/',f'plotly {plotly.__version__} Gapminder 2007 snapshot 142 countries'),
 'borders':('https://github.com/porimol/countryinfo', 'countryinfo Python bundled countryinfo.json frozen country records; snapshot not independently recertified'),
 'meat':('https://plotnine.org/reference/meat.html',f'plotnine {plotnine.__version__} bundled USDA ERS monthly meat 1944-2023'),
 'element':('https://www.rdkit.org/docs/source/rdkit.Chem.rdchem.html',f'RDKit {rdkit.__version__} installed periodic table elements Z=1-118'),
 'huron':('https://search.r-project.org/R/refmans/datasets/html/LakeHuron.html',f'plotnine {plotnine.__version__} R LakeHuron 1875-1972 98 annual readings'),
 'macro':('https://www.statsmodels.org/stable/datasets/generated/macrodata.html',f'statsmodels {statsmodels.__version__} FRED quarterly vintage through 2009Q3'),
 'statecrime':('https://www.statsmodels.org/stable/datasets/generated/statecrime.html',f'statsmodels {statsmodels.__version__} 2009 US statecrime snapshot 50 states plus DC'),
 'copper':('https://www.statsmodels.org/stable/datasets/generated/copper.html',f'statsmodels {statsmodels.__version__} Gill copper market 1951-1975'),
 'mpg':('https://ggplot2.tidyverse.org/reference/mpg.html',f'plotnine {plotnine.__version__} 234 EPA trims for 1999 and 2008'),
 'interest':('https://www.statsmodels.org/stable/datasets/generated/interest_inflation.html',f'statsmodels {statsmodels.__version__} German 1972Q2-1998Q4 long-term rates'),
 'density':('https://github.com/porimol/countryinfo','countryinfo bundled frozen population/area country records; historical year not independently synchronized'),
 'co2':('https://www.statsmodels.org/stable/datasets/generated/co2.html',f'statsmodels {statsmodels.__version__} Mauna Loa weekly CO2 Mar 1958-Dec 2001')
}
AUDIT=[];generated={};bank_ids=[]
def ans(name,val,eid,ref,aliases=None,metadata=None):
 assert isinstance(val,(int,float)) and math.isfinite(float(val)), (name,val)
 d={'entity_id':eid,'canonical':str(name),'aliases':[{'input':str(s),'kind':'documented_name_or_code','action':'replace_with_canonical'} for s in (aliases or []) if str(s).casefold()!=str(name).casefold()], 'verified_status':'frozen_source_record', 'source_refs':[{'source_id':ref,'locator':eid}], 'metric_value':val}
 if metadata:d['source_evidence']=metadata
 return d

def make_question(day,qn,topic,family,prompt,metric,unit,comparison,records,source_name,measurement,eligibility,notes='',candidates=None,exclusions=None,rounding='',preferred_limit=None):
 assert len(records)>0
 names={}
 for a in records:
  x=a['canonical'].casefold()
  if x in names:raise ValueError(('duplicate',family,x));names[x]=a
  assert a['source_refs']
 nums=sorted(set(float(a['metric_value']) for a in records))
 direction='above' if comparison=='at_least' else 'below'
 def choose_limit(limit):
  diffs=sorted({round((v-limit if direction=='above' else limit-v),10) for v in nums if (v-limit if direction=='above' else limit-v)>1e-8})
  crossed=sum((v<limit if direction=='above' else v>limit) for v in nums)
  return diffs,crossed
 if preferred_limit is None:
  order=[0.50,0.45,0.55,0.35,0.65,0.30,0.70,0.40,0.60,0.20,0.80,0.15,0.85,0.10,0.90,0.05,0.95]
  options=[]
  for qr in order:
   limit=nums[min(len(nums)-1,int((len(nums)-1)*qr))]
   diffs,crossed=choose_limit(limit)
   if len(diffs)>=7 and crossed>=1:
    options.append((len(diffs),limit,diffs,qr))
  if not options:raise ValueError(('insufficient distinct levels',family,len(nums),nums))
  # Prefer central cutoff for balanced number of answers, even when tail variation is smaller
  preferred_limit=options[0][1]
 if family=='lake_huron_annual_level_change_cm': preferred_limit=0
 limit=preferred_limit
 gaps,crossed=choose_limit(limit)
 if len(gaps)<7:raise ValueError(('not enough positive score ranges',family,len(gaps),limit))
 # Choose five strictly rising positive gap thresholds, reserve at least one TOO FAR
 gap_index=[max(0,min(len(gaps)-2,round((len(gaps)-1)*f)-1)) for f in [0.12,0.26,0.42,0.60,0.78]]
 for i in range(1,len(gap_index)):
  if gap_index[i]<=gap_index[i-1]:gap_index[i]=gap_index[i-1]+1
 if gap_index[-1]>=len(gaps)-1:
  gap_index=list(range(0,5))
 bounds=[gaps[i] for i in gap_index]
 # Floating values can make a gap computed by another runtime a hair wider, so add small precision tolerance in threshold
 # For fixed-decimal metrics, thresholds use +1e-7 to avoid source binary precision edge mismatches.
 if any(float(v)!=int(float(v)) for v in nums):bounds=[round(x+1e-7,8) for x in bounds]
 scores=[1000,800,600,400,200]
 tiers=['RAZOR EDGE','CLOSE CALL','SOLID HIT','IN THE ZONE','ON THE BOARD']
 sb=[{'max_gap_inclusive':int(v) if int(v)==v else v,'points':score,'tier':tier} for v,score,tier in zip(bounds,scores,tiers)]
 score_count=collections.Counter()
 for a in records:
  v=a['metric_value'];gap=limit-v if direction=='below' else v-limit
  if gap< -1e-8:points,tier=0,'CROSSED LIMIT'
  elif abs(gap)<1e-8:points,tier=1200,'PERFECT HIT'
  else:
   points,tier=0,'TOO FAR'
   for b in sb:
    if gap<=b['max_gap_inclusive']+1e-12:
     points,tier=b['points'],b['tier'];break
  a.update(points=points,tier=tier)
  score_count[points]+=1
 poscounts={p:sum(a['points']==p for a in records) for p in [1200,1000,800,600,400,200]}
 if any(not c for c in poscounts.values()):raise ValueError(('missing score tier',family,poscounts,limit,bounds))
 source,edition=SRCS[source_name]
 qid=f'closeish_202610{day:02d}_{qn}'
 ret={
 'id':qid,'date':f'2026-10-{day:02d}','day_number':day-22,
 'topic':topic,'bank_id':f'202610{day:02d}-{family}', 'question_family':family,
 'prompt':prompt.replace('{LIMIT}',f'{limit:g}'),'metric':metric,'unit':unit,
 'limit':int(limit) if float(limit).is_integer() else limit,'comparison':comparison,
 'time_limit_seconds':30,'direction':direction,'boundary_inclusive':True,
 'score_bands':sb,'source':source,'source_refs':[source_name],
 'verification_status':'frozen_package_source_reproducible_external_fact_checks_not_exhaustive',
 'editorial_status':'draft_requires_source_editorial_signoff',
 'content_revision':f'2026-10-{day:02d}-frozen-series-v1',
 'metric_provenance':measurement,'measurement_snapshot':edition,
 'measurement':{'edition':edition,'property':metric,'numeric_rule':rounding or measurement,'time_dependent':True if 'year' in metric.casefold() or 'annual' in metric.casefold() else False},
 'answer_scope':{'type':'finite_frozen_dataset','coverage':'complete_for_stated_frozen_source_only', 'claimed_exhaustive':False,
    'entity_scope':eligibility,'dataset_count':len(records),'note':'Entire available eligible source universe used; this is not a new independent source-by-source verification. '+notes},
 'scoring_policy':'metric-only; ambiguous names must not silently resolve; wrong side or too far=0',
 'perfect_tier':{'points':1200,'tier':'PERFECT HIT','rule':'exact displayed rounded metric'},
 'approach_rule':{'required_side':'from_above' if direction=='above' else 'from_below','operator':'>=' if direction=='above' else '<=', 'exact_target_allowed':True,'wrong_side_points':0,'exact_target_points':1200},
 'scoring_window':{'max_scoring_distance':sb[-1]['max_gap_inclusive'],'units':unit,'outside_window_points':0,'wrong_side_points':0,'exact_match_points':1200},
 'input_max_length':140,
 'answers':records
 }
 if candidates:ret['recognized_category_candidates']=candidates
 if exclusions:ret['excluded_answers']=exclusions
 AUDIT.append({'date':ret['date'],'q':qn,'topic':topic,'n':len(records),'limits':ret['limit'],'dir':direction, 'source':source_name,'score_bands':bounds, 'counts':{str(p):poscounts.get(p,0) for p in [1200,1000,800,600,400,200]},'zero_count':score_count[0], 'candidates':len(candidates or []), 'note':notes})
 bank_ids.append(family)
 return ret

def question(day,i,topic,family,prompt,metric,unit,comparison,records,source,measurement,scope,notes='',candidates=None,rounding=''):
 return make_question(day,'q'+str(i),topic,family,prompt,metric,unit,comparison,records,source,measurement,scope,notes,candidates,rounding=rounding)

def isoaliases(c):
 return [x for x in [getattr(c,'official_name',None),getattr(c,'common_name',None),c.alpha_2,c.alpha_3] if x]

days={29:[],30:[],31:[]}
# 2026-10-29 day 7: biology (independent trait from previously sampled mammal mass)
recs=[]
for i,row in p9.msleep.reset_index(drop=True).iterrows():
 if math.isfinite(row['sleep_total']):recs.append(ans(row['name'],int(math.floor(float(row['sleep_total'])+0.5)),f'msleep-{i+1:03d}','msleep',metadata={'row':i+1,'sleep_total_hours_unrounded':float(row['sleep_total'])}))
days[29].append(question(29,1,'biology','mammal_daily_sleep_duration','Name a mammal in the published 83-species sleep dataset that sleeps at most {LIMIT} hours per day on average (rounded to the nearest whole hour).','Typical total daily sleep','hours','at_most',recs,'msleep','ggplot2 msleep: sleep_total, hours; nearest whole hour before scoring','All 83 mammals in the frozen msleep source, including wrong-side/too-far species','Observational means are not universal species-level constants.'))
# ISO 3166-2 subdivisions entries by country
subcounts=collections.Counter(s.country_code for s in pycountry.subdivisions)
recs=[]
for c in pycountry.countries:
 value=int(subcounts.get(c.alpha_2,0))
 recs.append(ans(c.name,value,f'iso3166-1-{c.alpha_2}','subdiv',aliases=isoaliases(c),metadata={'iso_alpha_2':c.alpha_2,'iso_alpha_3':c.alpha_3,'subdivisions_listed':value}))
days[29].append(question(29,2,'international-standards','iso3166_2_subdivision_entry_count','Name a country or territory with at least {LIMIT} ISO 3166-2 subdivision entries in the frozen pycountry catalogue.','Number of ISO 3166-2 subdivision codes','subdivision codes','at_least',recs,'subdiv','count of matching country_code in bundled ISO 3166-2 entries','All ISO 3166-1 entries in pycountry 24.6.1, including countries with 0 catalogue entries','Catalogue entry count, not actual total administrative divisions at a current date.'))
# Pacific monthly temperature count >23C
eln= smdatasets.elnino.load_pandas().data
recs=[]
for _,r in eln.iterrows():
 year=int(r.YEAR);cols=[c for c in eln.columns if c!='YEAR']
 vals=[float(r[c]) for c in cols]
 if not all(math.isfinite(v) for v in vals):raise ValueError('missing elnino monthly series')
 count=sum(v>23.0 for v in vals)
 recs.append(ans(str(year),count,f'elnino-year-{year}','elnino',metadata={'year':year,'monthly_values_celsius':dict(zip(cols,vals))}))
days[29].append(question(29,3,'oceanography','nino12_warm_months_over_23c','Name a year from 1950–2010 with at least {LIMIT} months warmer than 23 °C in the NOAA Niño 1+2 sea-surface-temperature dataset.','Count of months with recorded average SST > 23 °C','months','at_least',recs,'elnino','NOAA monthly SST > 23°C, strict comparison; count all 12','61 complete NOAA Niño 1+2 years, 1950–2010','Versioned NOAA historical ERSST.V3B extract; snapshot not live.'))
# classic vehicles power conversion using hp mechanical
recs=[]
for i,r in p9.mtcars.reset_index(drop=True).iterrows():
 kilowatts=int(math.floor(float(r.hp)*0.7456998715822702+0.5))
 recs.append(ans(r['name'],kilowatts,f'mtcars-1974-{i+1:02d}','mtcars',metadata={'gross_horsepower_original':int(r.hp),'kw_conversion':0.7456998715822702}))
days[29].append(question(29,4,'automotive-history','motor_trend_1974_gross_engine_power_kw','Name a car in the 1973–74 Motor Trend test dataset whose gross engine power is at least {LIMIT} kW (converted from mechanical horsepower, nearest kW).','Converted gross engine power','kW','at_least',recs,'mtcars','mechanical hp * 0.7456998715822702 kW/hp, round half up to whole kW','All 32 named cars in the Motor Trend 1974 test sample','1970s gross horsepower ratings, not modern net-power test figures.'))
# 437 US counties original 2000 pop
recs=[]
for i,r in p9.midwest.reset_index(drop=True).iterrows():
 n=int(r.poptotal);rounded=int(math.floor(n/1000+0.5)*1000)
 recs.append(ans(f"{str(r['county']).title()} County, {r.state}",rounded,f'midwest-{str(r.state)}-{int(r.PID)}','midwest',aliases=[f"{str(r['county']).title()} County, { {'IL':'Illinois','IN':'Indiana','MI':'Michigan','OH':'Ohio','WI':'Wisconsin'}.get(r.state,r.state)}"],metadata={'2000_census_population_original':n,'county_pid':int(r.PID)}))
days[29].append(question(29,5,'local-demography','midwest_sample_2000_county_population','Name a county in the frozen 437-county Midwest dataset whose 2000 population was at most {LIMIT} people (nearest 1,000 people).','Year-2000 county population in the named sample','people','at_most',recs,'midwest','2000 US census poptotal, nearest 1000 persons before scoring','The 437 counties in the ggplot2/plotnine midwest sample, not all US counties','Some historic county totals may differ from later census revisions.'))
# CSS4 saturation, alternative to previous brightness
recs=[]
for name,hexc in sorted(CSS4_COLORS.items()):
 rgb=to_rgb(hexc);sat=float(rgb_to_hsv(rgb)[1]);val=int(math.floor(sat*100+0.5))
 recs.append(ans(name,val,f'css4-{name}','css4',metadata={'hex':hexc.upper(),'hsv_saturation_unrounded_pct':sat*100}))
days[29].append(question(29,6,'digital-design','css4_named_colour_hsv_saturation','Name a CSS4 named colour with an HSV saturation of at least {LIMIT}% (computed from its sRGB hex code, nearest whole percent).','HSV saturation of CSS4 sRGB color','%','at_least',recs,'css4','Convert sRGB to HSV; saturation=(max-min)/max, 0 if max=0; round 100*S nearest integer','All 148 CSS4 named color keywords including gray/grey distinct standardized keywords','Identical color values may have multiple independent standard CSS keywords.'))
# Day 8 life expectancy in frozen 2007 Gapminder
recs=[]
gap=px.data.gapminder().query('year == 2007')
for _,r in gap.iterrows():
 age=int(math.floor(float(r.lifeExp)+0.5))
 recs.append(ans(r.country,age,f'gapminder-2007-{r.iso_alpha}','gap',metadata={'source_iso3':r.iso_alpha,'life_expectancy_raw':float(r.lifeExp)}))
days[30].append(question(30,1,'public-health','gapminder_2007_life_expectancy','Name a country in the frozen Gapminder dataset with life expectancy at birth of at least {LIMIT} years in 2007 (nearest whole year).','Life expectancy at birth in 2007','years','at_least',recs,'gap','Gapminder 2007 lifeExp, nearest whole year before scoring','All 142 source-covered countries with 2007 Gapminder lifeExp','Historic source series; not every current UN member.'))
# countryinfo border code count, note catalogue distinction
from countryinfo import CountryInfo
ci=CountryInfo().all()
recs=[]
for key,v in ci.items():
 borderlist=v.get('borders')
 iso=v.get('ISO') or {}
 if not isinstance(borderlist,list) or not iso.get('alpha3'):
  continue
 name=v.get('name') or key.title()
 eid=iso['alpha3']
 recs.append(ans(name,len(borderlist),f'countryinfo-borders-{eid}','borders',metadata={'alpha3':eid,'source_border_codes':borderlist}))
days[30].append(question(30,2,'political-geography','countryinfo_recorded_border_code_count','Name a country or territory with at most {LIMIT} bordering-area codes listed in the frozen CountryInfo borders dataset.','Number of ISO-like border codes listed in the archived CountryInfo record','border codes','at_most',recs,'borders','len(borders), count actual source list entries; blank list=0 entries recorded, not evidence of no real borders','All bundled CountryInfo objects with an ISO alpha3 and a borders list','Some records reflect historic/disputed border definitions; this is a source-list count, not an independently verified current border count.'))
# yearly US pork production converts million pounds to thousand metric tonnes
meat=p9.meat.copy();meat['year']=meat.date.dt.year
recs=[];cands=[]
for year,r in meat.groupby('year'):
 if len(r)!=12 or r.pork.isna().any():
  cands.append({'canonical':str(year),'metric_value':None,'reason':'Incomplete or missing monthly pork data'})
  continue
 original_mill_lbs=float(r.pork.sum());thousand_metric_t=round(original_mill_lbs*0.45359237)
 recs.append(ans(str(year),int(thousand_metric_t),f'us-pork-yr-{year}','meat',metadata={'sum_million_us_pounds_original':original_mill_lbs,'source_months':12,'tonnes_per_million_lb':453.59237}))
days[30].append(question(30,3,'food-industry','us_pork_annual_production_tonnes','Name a year from 1944–2023 when recorded U.S. pork production reached at least {LIMIT} thousand metric tonnes (annual total, rounded to the nearest 1,000 tonnes).','Sum of the 12 published USDA monthly pork-production figures','thousand metric tonnes','at_least',recs,'meat','USDA meat monthly pork million lbs; sum*0.45359237 thousand metric tonnes, rounded to integer','All full-data calendar years in plotnine meat series 1944–2023','Frozen USDA historical statistical series, not guaranteed same as live revised USDA release.',cands))
# elements atomic numbers
periodic=Chem.GetPeriodicTable();recs=[]
for z in range(1,119):
 name=periodic.GetElementName(z);sym=periodic.GetElementSymbol(z)
 recs.append(ans(name,z,f'rdkit-element-{z:03d}','element',aliases=[sym],metadata={'symbol':sym,'atomic_number':z}))
days[30].append(question(30,4,'chemistry','periodic_table_atomic_number','Name a chemical element with atomic number at most {LIMIT} (number of protons).','Atomic number / proton count','protons','at_most',recs,'element','Element RDKit PeriodicTable GetAtomicNumber/GetElementName/GetElementSymbol; exact integers','All 118 chemical elements recorded in the frozen RDKit table','Atomic number is distinct from the atomic-weight question on the opening day.'))
# Lake Huron annual change in cm, 1876-1972
huron=p9.huron.sort_values('year').reset_index(drop=True);recs=[];cands=[{'canonical':'1875','metric_value':None,'reason':'No prior-year 1874 record in frozen series'}]
for i in range(1,len(huron)):
 now=huron.iloc[i];prev=huron.iloc[i-1];assert int(now.year)==int(prev.year)+1
 delta_ft=float(now.level)-float(prev.level)
 delta_cm=int(math.floor(delta_ft*30.48+0.5)) # nearest whole cm including negative
 recs.append(ans(str(int(now.year)),delta_cm,f'LakeHuron-change-{int(now.year)}','huron',metadata={'current_feet':float(now.level),'previous_feet':float(prev.level),'delta_foot':round(delta_ft,5),'cm_per_foot':30.48}))
days[30].append(question(30,5,'lake-science','lake_huron_annual_level_change_cm','Name a year from 1876–1972 when Lake Huron’s annual water level changed by at least {LIMIT} cm compared with the previous year (nearest cm; a negative change is a fall).','Change in LakeHuron annual recorded level versus preceding year','cm','at_least',recs,'huron','(level_ft(year)-level_ft(previous year))*30.48 cm/ft, nearest cm','Every year 1876–1972 with paired annual observations','Original source foot units converted exactly; 1875 excluded from scoring because previous year is unavailable.',cands))
# USA real consumption 1959-2008 annual average 4 quarters, 2009 partial candidate
macro=smdatasets.macrodata.load_pandas().data; recs=[];cands=[]
for year,r in macro.groupby('year'):
 year=int(year)
 if len(r)!=4 or r.realcons.isna().any():
  cands.append({'canonical':str(year),'metric_value':None,'reason':f'{len(r)} quarterly observations, not a complete annual year'})
  continue
 ave=float(r.realcons.mean());round_bil=int(math.floor(ave/100+0.5)*100)
 recs.append(ans(str(year),round_bil,f'fred-realcons-annual-{year}','macro',metadata={'four_quarter_values_billion_2005usd':[float(v) for v in r.realcons], 'mean_raw':ave}))
days[30].append(question(30,6,'economic-history','us_annual_real_personal_consumption','Name a year from 1959–2008 when average quarterly U.S. real personal consumption reached at most {LIMIT} billion chained-2005 U.S. dollars (nearest $100 billion).','Mean of quarterly FRED realcons annualized-rate levels for four quarters','billion chained-2005 USD','at_most',recs,'macro','FRED macrodata quarterly realcons (billion 2005 US$ SAAR), four-quarter arithmetic mean, nearest 100 billion','All 50 complete years 1959–2008 in source','2009 is partial through Q3 and is withheld instead of imputing Q4.',cands))
# Day 9
crime=smdatasets.statecrime.load_pandas().data
recs=[]
for st,r in crime.iterrows():
 val=float(r.poverty);val=int(math.floor(val+0.5))
 recs.append(ans(st,val,f'statecrime-poverty-2009-{st.lower().replace(" ","-")}','statecrime',metadata={'original_2009_poverty_rate_pct':float(r.poverty)}))
days[31].append(question(31,1,'social-history','us_state_poverty_rate_2009','Name a U.S. state or Washington, D.C., where at least {LIMIT}% of people were below the poverty line in the frozen 2009 state data (nearest whole percent).','Percent below the poverty line in 2009 statecrime dataset','%','at_least',recs,'statecrime','statecrime poverty percentage, round nearest whole % for scoring','All 50 U.S. states and Washington D.C. in 2009 statsmodels snapshot','Different from 2009 violent-crime question; source vintage should be documented.'))
# World annual copper in thousand metric tonnes
copper=smdatasets.copper.load_pandas().data
recs=[]
for i,r in copper.reset_index(drop=True).iterrows():
 yr=1951+i;v=int(math.floor(float(r.WORLDCONSUMPTION)/100+0.5)*100)
 recs.append(ans(str(yr),v,f'copper-global-{yr}','copper',metadata={'source_consumption_thousand_tonnes':float(r.WORLDCONSUMPTION),'time_code':float(r.TIME)}))
days[31].append(question(31,2,'industrial-history','world_copper_consumption_1951_1975','Name a year from 1951–1975 when world copper consumption was at most {LIMIT} thousand metric tonnes (nearest 100,000 tonnes).','Annual world copper consumption','thousand metric tonnes','at_most',recs,'copper','source WORLDCONSUMPTION in 1000 metric tonnes; round nearest 100 such units','All 25 years of the original Gill world copper market dataset','Source rights retained by original author, as described in statsmodels documentation.'))
# EPA mpg group maximum displacement by make/model/year
mpg=p9.mpg.copy();recs=[]
for (maker,model,yr),r in mpg.groupby(['manufacturer','model','year'],sort=True):
 maxlitres=float(r.displ.max());cc=int(round(maxlitres*1000));eid=f'epa-mpg-{maker.replace(" ","-")}-{model.replace(" ","-")}-{int(yr)}'
 name=f'{maker.title()} {model.title()} ({int(yr)})'
 recs.append(ans(name,cc,eid,'mpg',metadata={'source_trims':len(r),'source_max_engine_displacement_litres':maxlitres}))
days[31].append(question(31,3,'car-engineering','epa_1999_2008_max_engine_displacement','Name a manufacturer–model–year combination in the frozen U.S. EPA 1999/2008 car sample whose largest listed engine is at least {LIMIT} cm³.','Largest engine displacement listed among trims for each manufacturer-model-year combination','cm³','at_least',recs,'mpg','max(displ litres) by manufacturer/model/year, multiply by 1000 cm³/L, exactly','All distinct manufacturer–model–year keys represented by 234 EPA sample trim rows','Only sampled models/trims in mpg; not a complete 1999/2008 U.S. vehicle market.'))
# German quarterly rate nominal in basis points
intdf=smdatasets.interest_inflation.load_pandas().data
recs=[]
for _,r in intdf.iterrows():
 year=int(r.year);quarter=int(r.quarter);bp=int(math.floor(float(r.R)*10000+0.5));key=f'{year}-Q{quarter}'
 recs.append(ans(key,bp,f'german-rate-{key}','interest',metadata={'original_decimal_interest_rate':float(r.R),'conversion':'decimal rate * 10,000 = basis points'}))
days[31].append(question(31,4,'financial-history','german_1972_1998_long_term_interest_basis_points','Name a YYYY-Q# quarter from 1972-Q2 through 1998-Q4 when Germany’s nominal long-term interest rate reached at least {LIMIT} basis points (100 basis points = 1%).','German quarter-end nominal long-term interest rate','basis points','at_least',recs,'interest','statsmodels R decimal nominal rate * 10000 to basis points, rounded to integer','All 107 consecutive quarters 1972Q2–1998Q4','West Germany for early observations and unified Germany in later quarters.'))
# CountryInfo source-defined population density: both numerator and land area required, never invent missing values
recs=[];cands=[]
for key,v in ci.items():
 population=v.get('population');area=v.get('area');iso=v.get('ISO') or {};name=v.get('name') or key.title()
 if not iso.get('alpha3'):continue
 if not isinstance(population,(int,float)) or not isinstance(area,(int,float)) or area<=0 or population<0 or not math.isfinite(area):
  cands.append({'canonical':name,'metric_value':None,'reason':'Missing/non-comparable population or positive land-area number in CountryInfo snapshot'})
  continue
 density=int(math.floor(population/area+0.5))
 recs.append(ans(name,density,f'countryinfo-density-{iso["alpha3"]}','density',metadata={'population_original':population,'area_original_km2':area,'formula':'pop / area (km²) rounded to people/km²'}))
days[31].append(question(31,5,'population-geography','countryinfo_historical_population_density','Name a country or territory whose frozen CountryInfo population density was at least {LIMIT} people/km² (population divided by land area, nearest whole person/km²).','Historical CountryInfo population divided by the same record’s area','people/km²','at_least',recs,'density','population count divided by source area in square kilometres, round nearest integer','All ISO3-tagged CountryInfo records with both a valid population and positive area','The historical countryinfo records do not share a reliably documented census year; result is explicitly a catalogue-specific snapshot, not a 2026 density ranking.',cands))
# annual Mauna Loa available weekly means for full 1959-2001, 1958 partial withheld
co2=smdatasets.co2.load_pandas().data
recs=[];cands=[{'canonical':'1958','metric_value':None,'reason':'Partial year: record begins in March 1958; no full calendar-year mean'}]
for yr,r in co2.groupby(co2.index.year):
 if yr<=1958:continue
 good=r.co2.dropna()
 if not len(good):cands.append({'canonical':str(yr),'metric_value':None,'reason':'No measured weekly data'});continue
 avg=float(good.mean()); val=int(math.floor(avg+0.5))
 recs.append(ans(str(yr),val,f'mauna-loa-co2-{yr}','co2',metadata={'valid_weekly_measurements':int(len(good)),'missing_weeks':int(r.co2.isna().sum()),'unrounded_annual_average_ppm':avg}))
days[31].append(question(31,6,'atmospheric-science','mauna_loa_annual_co2_ppm_1959_2001','Name a year from 1959–2001 when the frozen Mauna Loa annual mean CO₂ concentration was at least {LIMIT} ppm (mean of available weekly readings, nearest whole ppm).','Arithmetic annual average of available weekly Mauna Loa atmospheric CO2 records','ppm','at_least',recs,'co2','Mean of nonmissing weekly CO2 values for each complete calendar year; nearest whole ppm','Full years 1959–2001 in frozen statsmodels weekly dataset','1958 only partial and listed as unscored candidate; some other years have missing weeks that are not imputed.',cands))

# Write days (draft)
for day,questions in days.items():
 assert len(questions)==6
 ds=f'2026-10-{day:02d}'
 d={'schema_version':1,'date':ds,'day_number':day-22,'revision':f'202610{day:02d}-frozen-source-draft-v1','publication_status':'draft',
    'editorial_note':'New six-question source-bounded research DRAFT. Numeric scores/eligibility checked against frozen offline package datasets; not independently recertified against every original upstream item. Manual source/license/editorial audit required before scheduling.',
    'questions':{f'q{i}':q for i,q in enumerate(questions,1)}}
 outf=ROOT/'days'/f'{ds}.json'
 with open(outf,'w',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
 print('WROTE',outf,os.path.getsize(outf),'answers',sum(len(q['answers']) for q in questions))

(ROOT/'reference-rules'/'NEW-DAYS-MACHINE-AUDIT.json').write_text(json.dumps(AUDIT,ensure_ascii=False,indent=2),encoding='utf-8')
print('SUMMARY',len(AUDIT),'questions',sum(x['n'] for x in AUDIT),'answers')
for a in AUDIT:print(a['date'],a['q'],a['topic'],a['n'],'lim',a['limits'],'bands',a['score_bands'],'points',a['counts'],'0',a['zero_count'])
