#!/usr/bin/env python3
"""CLOSEISH 1–3. nap: valós forrásimport, újrapontozás és HTML-build.

Usage from CLOSEISH folder (with internet):
  python tools/finalize_first_three.py --download
Or offline with previously fetched official sources:
  python tools/finalize_first_three.py --source-dir datasets/external-original

Never declares a day content-complete without the source data actually being
loaded and an explicit, reproducible audit. A failed download is a hard error.
"""
import argparse,csv,hashlib,json,os,subprocess,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def check(label, expression):
    if not expression: raise RuntimeError(label)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--download',action='store_true',help='download Reep, MDD and PanTHERIA using this computer Internet connection')
    p.add_argument('--source-dir',type=Path,default=ROOT/'datasets'/'external-original')
    p.add_argument('--min-players',type=int,default=10000)
    p.add_argument('--min-measured-mammals',type=int,default=2000)
    p.add_argument('--output-dir',type=Path,default=ROOT/'release')
    args=p.parse_args()
    target=args.source_dir.resolve(); target.mkdir(parents=True,exist_ok=True)
    day1=(ROOT/'days/day-01.json').read_bytes();day4plus=[(ROOT/'days'/f'day-{i:02}.json').read_bytes() for i in range(4,8)]
    if args.download:
        subprocess.run([sys.executable,str(ROOT/'tools/download_public_sources.py'),'--out',str(target)],check=True,cwd=ROOT)
    people=target/'Reep_v0_2026.25_people.csv'
    names=target/'Reep_v0_2026.25_aliases.csv'
    mdd=target/'MDD_v2.5_species.csv'
    pantheria=target/'PanTHERIA_1-0_WR05_Aug2008.txt'
    missing=[str(f) for f in (people,names,mdd,pantheria) if not f.exists() or f.stat().st_size<100]
    check('Required primary data missing. Cannot claim final dataset: '+', '.join(missing),not missing)
    subprocess.run([sys.executable,str(ROOT/'tools/import_full_universes.py'),'--people',str(people),'--names',str(names),'--mdd',str(mdd),'--pantheria',str(pantheria),'--min-players',str(args.min_players),'--min-measured-mammals',str(args.min_measured_mammals),'--strict'],check=True,cwd=ROOT)
    imp=json.loads((ROOT/'DATA-IMPORT-AUDIT.json').read_text('utf8'))
    check('Required name/measurement import thresholds were not met',imp.get('data_thresholds_passed'))
    check('Original first day changed during import!',day1==(ROOT/'days/day-01.json').read_bytes())
    check('Days 4–7 changed!',day4plus==[(ROOT/'days'/f'day-{i:02}.json').read_bytes() for i in range(4,8)])
    subprocess.run([sys.executable,str(ROOT/'tools/audit_first_three.py')],check=True,cwd=ROOT)
    subprocess.run([sys.executable,str(ROOT/'tools/build.py')],check=True,cwd=ROOT)
    args.output_dir.mkdir(parents=True,exist_ok=True)
    import shutil
    shutil.copy2(ROOT/'CLOSEISH-standalone.html',args.output_dir/'CLOSEISH-elso-3-nap.html')
    shutil.copy2(ROOT/'FIRST-THREE-AUDIT.csv',args.output_dir/'CLOSEISH-pontozasi-audit.csv')
    shutil.copy2(ROOT/'DATA-IMPORT-AUDIT.json',args.output_dir/'FORRAS-IMPORT-AUDIT.json')
    sha=lambda v:hashlib.sha256(v).hexdigest()
    manifest={'import_completed':True,'first_day_unchanged_sha256':sha(day1),'source_counts':imp,'day_4_to_7_unchanged':True,'notes':('Forrásadat-import és technikai audit kész. A teljes világ összes autómodelljének és minden emlősfaj mérési adatának lefedettsége továbbra sem következik az importból. A sikeres futás nem automatikus szerkesztői publikálási jóváhagyás.')}
    (args.output_dir/'ATADAS-ALLAPOT.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
    print('SOURCE IMPORT AND SCORING AUDIT PASS. Release artifacts:',args.output_dir)
if __name__=='__main__':
    try:main()
    except Exception as exc:print('VALIDATION FAILED:',exc,file=sys.stderr);sys.exit(2)
