"""Optional offline baseline: import IANA tzdb representative populated locations with disclosed coordinate precision."""
from pathlib import Path
import json,re,math,collections
ROOT=Path(__file__).resolve().parents[1]; p=ROOT/'days/day-04.json'
data=json.loads(p.read_text('utf8'));q=data['q5']
source=Path('/usr/share/zoneinfo/zone.tab');assert source.exists()
def latlon(coord):
 m=re.fullmatch(r'([+-])(\d{4}|\d{6})([+-])(\d{5}|\d{7})',coord)
 assert m,coord
 def value(sign,digits,deg_digits):
  deg=int(digits[:deg_digits]);minu=int(digits[deg_digits:deg_digits+2]);sec=int(digits[deg_digits+2:] or 0)
  assert minu<60 and sec<60
  return (1 if sign=='+' else -1)*(deg+minu/60+sec/3600)
 return value(m[1],m[2],2),value(m[3],m[4],3)
def norm(s):return re.sub(r'[^a-z0-9]+',' ',s.casefold()).strip()
seen={norm(a['canonical']) for a in q['answers']}
R=6371.0088;lat0=math.radians(47.497912);lon0=math.radians(19.040235)
added=[]
for line in source.read_text('utf8').splitlines():
 if line.startswith('#') or not line.strip():continue
 cols=line.split('\t');cc,coord,zone=cols[:3]
 region=zone.split('/')[0]
 if region not in {'Africa','America','Asia','Europe','Australia'}:continue
 name=zone.split('/')[-1].replace('_',' ')
 # tzdb has a handful of region/country/territory labels rather than towns.
 # Those cannot be used as a settlement-level answer.
 not_places={'Antigua','Anguilla','Aruba','Barbados','Bermuda','Dominica','Costa Rica','El Salvador','Puerto Rico','St Barthelemy','Martinique','Montserrrat','Dominica','Cayman','Curacao','Vatican','Faroe','Isle of Man','Jersey','Guernsey','St Pierre','Grenada','St Lucia','St Kitts','Trinidad','Bahamas','Port au Prince'}
 if name in not_places:continue
 if name in {'Canary','Azores','Madeira','Cape Verde','Bermuda','Galapagos','Tahiti','Easter','Christmas','Cocos','Chatham','Kerguelen','Norfolk','Johnston','Wake','Kwajalein','Truk','Guam','Palau','Nauru','South Georgia','Pago Pago','Indian','Reunion'}:continue
 key=norm(f'{name}, {cc}')
 if key in seen:continue
 try:lat,lon=latlon(coord)
 except:continue
 a=math.sin((math.radians(lat)-lat0)/2)**2+math.cos(lat0)*math.cos(math.radians(lat))*math.sin((math.radians(lon)-lon0)/2)**2
 distance=round(2*R*math.asin(min(1,math.sqrt(a))))
 canonical=f'{name}, {cc}'
 aliases=[]
 if norm(name) not in seen:aliases=[{'input':name,'kind':'zone_label_city','action':'replace_with_canonical'}]
 # compare bands and direction
 if distance>q['limit']:points=0;tier='CROSSED LIMIT'
 elif distance==q['limit']:points=1200;tier='PERFECT HIT'
 else:
  diff=q['limit']-distance;band=next((b for b in q['score_bands'] if diff<=b['max_gap_inclusive']),None)
  points=band['points'] if band else 0;tier=band['tier'] if band else 'TOO FAR'
 rec={'entity_id':'tzdb-'+zone,'canonical':canonical,'aliases':aliases,'verified_status':'iana_timezone_city_coordinates','source_refs':[{'source_id':'iana-tzdb-zone-tab','locator':'https://github.com/eggert/tz/blob/main/zone.tab'}],'metric_value':distance,'points':points,'tier':tier}
 q['answers'].append(rec);seen.add(key);added.append(rec)
q['answer_scope']['dataset_count']=len(q['answers']);q['verified_answer_count']=len(q['answers']);q['catalogued_answer_count']=len(q['answers']);q['alias_count']=sum(len(a.get('aliases',[])) for a in q['answers'])
q['score_distribution_audit']={str(t):sum(x['points']==t for x in q['answers']) for t in (1200,1000,800,600,400,200,0)}
q['source_refs'].append('iana-tzdb-zone-tab')
q['answer_scope']['note']+=' IANA tzdb representative-city coordinates supplement the offline seed, but do not make it exhaustive.'
p.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),'utf8')
print('Added',len(added),'tzdb city references. Overall offline cities',len(q['answers']))
print('Example score bands',q['score_distribution_audit'])
print('Added samples',[(x['canonical'],x['metric_value'],x['points']) for x in added[:14]])
