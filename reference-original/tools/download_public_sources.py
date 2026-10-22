#!/usr/bin/env python3
"""One-shot source acquisition for a locally bundled, internet-independent CLOSEISH HTML.
Run this on a networked machine. Every downloaded source is saved alongside its hash.
External sources are not presumed available in the build environment.
"""
from pathlib import Path
import urllib.request,json,hashlib,zipfile,sys,re,argparse
ROOT=Path(__file__).resolve().parents[1]
FILES={
 'Reep_v0_2026.25_people.csv':('https://raw.githubusercontent.com/withqwerty/reep/main/data/people.csv','CC0; frozen release 2026.25 (2026-06-21)'),
 'Reep_v0_2026.25_aliases.csv':('https://raw.githubusercontent.com/withqwerty/reep/main/data/names.csv','CC0; frozen Reep name aliases 2026.25'),
 'MDD_v2.5.zip':('https://raw.githubusercontent.com/mammaldiversity/mammaldiversity.github.io/master/assets/data/MDD.zip','Official ASM Mammal Diversity Database v2.5 (2026-07-28)'),
 'PanTHERIA_1-0_WR05_Aug2008.txt':('https://raw.githubusercontent.com/pedroj/Megafauna/master/datasets/PanTHERIA_1-0_WR05_Aug2008.txt','PanTHERIA: Jones et al. 2009; original trait release')}

def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  while x:=f.read(1024*1024):h.update(x)
 return h.hexdigest()

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--out',type=Path,default=ROOT/'datasets'/'external-original')
 parser.add_argument('--overwrite',action='store_true')
 args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=True)
 records={};failed=[]
 for name,(url,license) in FILES.items():
  target=args.out/name
  try:
   if not target.exists() or args.overwrite:
    req=urllib.request.Request(url,headers={'User-Agent':'CLOSEISH-data-quality-audit/1.0'})
    with urllib.request.urlopen(req,timeout=90) as r,target.open('wb') as o:
     while block:=r.read(1024*1024):o.write(block)
   records[name]={'source':url,'source_notice':license,'bytes':target.stat().st_size,'sha256':sha(target)}
  except Exception as ex:failed.append(f'{name}: {ex}')
 # Official MDD zip contains an MDD taxonomic CSV and extra metadata; do not
 # accidentally extract its synonyms file and count it as accepted species.
 source=args.out/'MDD_v2.5.zip'
 if source.exists():
  try:
   with zipfile.ZipFile(source) as z:
    csvs=[n for n in z.namelist() if re.search(r'(?i)MDD_v2[._-]5.*\.csv$',n) and 'syn' not in n.lower()]
    if not csvs:csvs=[n for n in z.namelist() if n.lower().endswith('.csv') and 'mdd' in n.lower() and 'syn' not in n.lower()]
    if not csvs:raise RuntimeError('No unambiguous taxonomy species CSV in official MDD.zip; inspect archive before importing')
    selected=sorted(csvs,key=len)[0]
    target=args.out/'MDD_v2.5_species.csv'
    with z.open(selected) as inp,target.open('wb') as out:
     while data:=inp.read(1024*1024):out.write(data)
    records[target.name]={'extracted_from':'MDD_v2.5.zip','member':selected,'sha256':sha(target),'bytes':target.stat().st_size}
  except Exception as ex:failed.append(f'MDD extraction: {ex}')
 (args.out/'SOURCE-MANIFEST.json').write_text(json.dumps({'files':records,'errors':failed},indent=2,ensure_ascii=False),encoding='utf-8')
 for k,v in records.items():print(k,format(v['bytes'],','),'bytes SHA-256',v['sha256'][:12])
 if failed:
  for e in failed:print('FAILED:',e,file=sys.stderr)
  sys.exit(2)
 print('Downloaded and hashed. Next: run tools/import_full_universes.py --people ... --mdd ... --pantheria ...')
if __name__=='__main__':main()
