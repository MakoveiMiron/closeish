from pathlib import Path
import re,json
ROOT=Path(__file__).resolve().parents[1]
s=Path('/mnt/data/CLOSEISH-V12-bovitett-jatekok-vizesesek-nilus.html').read_text('utf8')
m=re.search(r'<script id="pack-data" type="application/json">(.*?)</script>',s,re.S)
assert m,'No V12 real compiled data'
remote=json.loads(m.group(1))['5']
p=ROOT/'days/day-05.json';data=json.loads(p.read_text('utf8'))
for key in ('q1','q2'):
 old=data[key];new=remote[key]
 assert len(new['answers'])>len(old['answers']),(key,len(new['answers']),len(old['answers']))
 assert new['id']==old['id'] and new['limit']==old['limit'] and new['score_bands']==old['score_bands']
 data[key]=new
 print(key,'restored records',len(old['answers']),'->',len(new['answers']))
p.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),'utf8')
