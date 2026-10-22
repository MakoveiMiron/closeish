#!/usr/bin/env python3
"""Identity-first source importer. Never invents measurements or scoring values.

Usage:
  python tools/import_full_universes.py --people PATH/people.csv \
    --mdd PATH/MDD_v2.5.csv --pantheria PATH/PanTHERIA_1-0_WR05_Aug2008.txt

Source references:
  Reep v0 2026.25 (CC0) https://github.com/withqwerty/reep/tree/main/data
  Mammal Diversity Database v2.5 https://www.mammaldiversity.org/releases/
  PanTHERIA Jones et al. 2009 https://esapubs.org/archive/ecol/E090/184/
"""
import argparse,csv,json,collections,hashlib,unicodedata,math,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def norm(s):
    return re.sub(r'[^a-z0-9]+',' ',unicodedata.normalize('NFKD',str(s or '')).encode('ascii','ignore').decode().lower()).strip()
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
def read_csv(path,sep=','):
    with path.open('r',encoding='utf-8-sig',newline='') as f:
        yield from csv.DictReader(f,delimiter=sep)
def pick(row,*keys):
    for k in keys:
        if row.get(k):return str(row[k]).strip()
    return ''
def alias(s,canon):
    return {'input':s,'kind':'verified_registry_alias','action':'replace_with_canonical'} if s and norm(s)!=norm(canon) else None

def reep_candidates(path,known,aliases_file=None):
    aliases_by_qid=collections.defaultdict(set)
    if aliases_file and aliases_file.exists():
        for r in read_csv(aliases_file):
            qid=pick(r,'key_wikidata'); alias_name=pick(r,'alias')
            if qid and alias_name:aliases_by_qid[qid].add(alias_name)
    names={}; all_rows=0; player_rows=0
    for row in read_csv(path):
        all_rows+=1
        if row.get('type','').lower()!='player':continue
        player_rows+=1
        eid=pick(row,'reep_id');name=pick(row,'name');full=pick(row,'full_name');dob=pick(row,'date_of_birth')
        if not (eid and name):continue
        if eid in names:continue
        names[eid]={'entity_id':'reep-'+eid,'canonical':name,'original_name':name,'dob':dob,'full_name':full,'qid':pick(row,'key_wikidata')}
    names={k:v for k,v in names.items() if norm(v['original_name']) not in known}
    collisions=collections.Counter(norm(v['canonical']) for v in names.values())
    used=set(known);out=[]
    for v in names.values():
        n=v['canonical'];dob=v['dob'];full=v['full_name'];nkey=norm(n)
        if collisions[nkey]>1:
            suffix=dob or v['entity_id'].split('-')[-1]
            v['canonical']=f'{n} ({suffix})'
        if norm(v['canonical']) in used:
            v['canonical']+=f" [{v['entity_id'][-7:]}]"
        used.add(norm(v['canonical']))
        aliases=[a for a in [alias(n,v['canonical']),alias(full,v['canonical']),*(alias(k,v['canonical']) for k in sorted(aliases_by_qid.get(v['qid'],set())))] if a]
        out.append({'entity_id':v['entity_id'],'canonical':v['canonical'],
                    'aliases':aliases,'membership_status':'recognized_entity_unverified_measurement',
                    'measurement_status':'not_proven_to_have_scored_2022_wc_goal',
                    'source_refs':[{'source_id':'reep-v0-2026.25','locator':v['entity_id']}],
                    'metric_value':None})
    return out, {'raw_person_rows':all_rows,'raw_player_rows':player_rows,'recognized_extra_players':len(out),
                 'duplicate_names_disambiguated':sum(n for n in collisions.values() if n>1),
                 'known_extra_aliases':sum(len(x['aliases']) for x in out)}

def pantheria_mass(path):
    observations={}; total=0;measured=0
    for row in read_csv(path,'\t'):
        total+=1
        name=pick(row,'MSW05_Binomial','MSW05_Binomial_name','scientificNameStd')
        v=pick(row,'5-1_AdultBodyMass_g','AdultBodyMass_g')
        if not name: continue
        try:mass=float(v)
        except (ValueError,TypeError):continue
        if mass<=0 or not math.isfinite(mass) or mass==-999:continue
        measured+=1
        observations.setdefault(norm(name),(name,mass/1000.0))
    return observations,{'pantheria_rows':total,'pantheria_measured_rows':measured,'pantheria_distinct_measured_species':len(observations)}

def mdd_mammals(path,mass):
    out=[];checked=set();total=0
    for row in read_csv(path):
        total+=1
        sci=pick(row,'sciName','scientificName','scientific_name','MSW05_Binomial')
        if not sci:continue
        key=norm(sci)
        if key in checked:continue
        checked.add(key)
        common=pick(row,'mainCommonName','commonName','common_name')
        display=common if common and common not in {'NA','N/A','-'} else sci
        if display.lower()=='none':display=sci
        id=pick(row,'id','MDD_ID','taxonID') or f'mdd-{len(checked)}'
        ent={'entity_id':'mdd-'+id,'canonical':display,'aliases':[],
             'source_refs':[{'source_id':'mdd-taxonomy','locator':sci}],
             'taxon_name':sci}
        if norm(display)!=key:ent['aliases'].append({'input':sci,'kind':'scientific_name','action':'replace_with_canonical'})
        if key in mass:
            kg=mass[key][1]
            ent.update({'raw_mass_kg':kg,'metric_value':math.floor(kg+0.5),'verified_status':'pantheria_source_measurement'})
        else:
            ent.update({'metric_value':None,'membership_status':'recognized_entity_unverified_measurement'})
        out.append(ent)
    # a given common name can refer to more than one species. Disambiguate only these.
    counts=collections.Counter(norm(x['canonical']) for x in out)
    for x in out:
        if counts[norm(x['canonical'])]>1:
            x['aliases'].append({'input':x['canonical'],'kind':'ambiguous_common_name','action':'require_disambiguation'})
            x['canonical']=f"{x['canonical']} ({x['taxon_name']})"
    return out,{'mdd_source_rows':total,'mdd_unique_species':len(out),
                'mdd_species_with_pantheria_mass':sum(isinstance(x['metric_value'],int) for x in out),
                'mdd_missing_mass':sum(x['metric_value'] is None for x in out)}

def score(q,value):
    gap=(value-q['limit']) if q['direction']=='above' else (q['limit']-value)
    if gap<0:return (0,'CROSSED LIMIT')
    if gap==0:return (1200,'PERFECT HIT')
    for b in q['score_bands']:
        if gap<=b['max_gap_inclusive']:return (b['points'],b['tier'])
    return (0,'TOO FAR')

def tune_mammal_bands(q,measured,report):
    """Pick reproducible, naturally populated score boundaries from real data.

    Preserve the existing target when possible. Different taxonomic joins can
    change the observed distribution: the seven tiers must remain backed by
    measured real species and include a finite far-zero window.
    """
    original=int(q['limit'])
    values=[x['metric_value'] for x in measured]
    choices=sorted(set(v for v in values if 50<=v<=500),key=lambda n:(abs(n-original),n))
    for target in choices:
        # Integer-valued values are already rounded as specified in question.
        positive=sorted(set(target-v for v in values if v<target))
        # At least five nonzero bands, plus an actual zero-point TOO FAR value.
        if len(positive)<6 or not any(v>target for v in values):continue
        max_window=min(positive[-2],int(target*.90))
        viable=[g for g in positive if g<=max_window]
        if len(viable)<5 or not any(g>max_window for g in positive):continue
        # Spread boundaries over the empirical distribution rather than a
        # universal arbitrary percent-of-target formula.
        percentiles=(.06,.16,.32,.55,.90)
        selected=[]
        for pct in percentiles:
            idx=min(len(viable)-1,max(len(selected),int(pct*(len(viable)-1))))
            selected.append(viable[idx])
        if len(set(selected))!=5 or not all(selected[i]<selected[i+1] for i in range(4)):continue
        original_bands=q['score_bands']
        newbands=[]
        for band,edge in zip(original_bands,selected):newbands.append({**band,'max_gap_inclusive':edge})
        old_target,old_bands=q['limit'],q['score_bands']
        q['limit'],q['score_bands']=target,newbands
        ct=collections.Counter(score(q,v)[0] for v in values)
        if all(ct[v]>0 for v in (1200,1000,800,600,400,200,0)):
            report['mammal_original_target']=original
            report['mammal_tuned_target']=target
            report['mammal_empirical_bands']=selected
            return True
        q['limit'],q['score_bands']=old_target,old_bands
    return False

def merge_mammals(q,mdd,report):
    scored=[x for x in mdd if x['metric_value'] is not None]
    if not tune_mammal_bands(q,scored,report):
        report['mammal_publication_ready']=False
        report['mammal_scored_records']=len(scored)
        report['mammal_tiers_missing']='Could not find naturally occupied seven-tier distribution with finite zero window'
        return
    cts=collections.Counter(score(q,x['metric_value'])[0] for x in scored)
    report['mammal_tiers_missing']=[];report['mammal_publication_ready']=True
    for x in scored:
        x['points'],x['tier']=score(q,x['metric_value'])
    q['answers']=scored
    q['recognized_category_candidates']=[x for x in mdd if x['metric_value'] is None]
    q['excluded_answers']=[]
    q['metric']='Mean adult body mass of the named mammal species, nearest kg (PanTHERIA 2009)'
    q['prompt']=f"Name a mammal species with an average adult body mass of at most {q['limit']} kg. (Masses are rounded to the nearest whole kilogram before scoring.)"
    q['source']='https://esapubs.org/archive/ecol/E090/184/'
    q['answer_scope']={'type':'species_registry_and_measurement_crosswalk',
        'entity_scope':'MDD mammal species taxonomy joined to PanTHERIA 2009 body mass; not a complete census of all extinct mammals.',
        'claimed_exhaustive':False,'dataset_count':len(mdd),
        'measured_count':len(scored),'unmeasured_count':len(mdd)-len(scored)}
    q['source_refs']=[{'source_id':'mdd-taxonomy','locator':'Mammal Diversity Database taxonomy'},{'source_id':'pantheria-2009','locator':'PanTHERIA AdultBodyMass_g'}]
    q['measurement']={'property':'PanTHERIA adult body mass','numeric_rule':'nearest whole kg','edition':'PanTHERIA 2009'}
    q['measurement_snapshot']='PanTHERIA 2009 × MDD source release'
    q['metric_provenance']='Mammal Diversity Database taxonomic names; PanTHERIA adult body mass in grams, converted to kg before nearest-kg rounding. No measured value is assumed for an unmatched species.'
    q['verification_status']='verified_trait_source_but_taxonomic_join_requires_audit'
    q['editorial_status']='RESEARCH_PENDING_FULL_AUDIT'
    q['verified_answer_count']=len(scored)
    q['catalogued_answer_count']=len(scored)
    q['recognized_category_candidate_count']=len(q['recognized_category_candidates'])
    q['content_revision']='mdd-pantheria-identity-first-v5'
    report['mammal_distributions']={str(k):v for k,v in sorted(cts.items())}
    report['mammal_scored_records']=len(scored)

def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--people',type=Path,help='Reep v0 data/people.csv (2026.25, 444707 people incl. coaches)')
    a.add_argument('--names',type=Path,help='Reep v0 data/names.csv (optional name aliases)')
    a.add_argument('--mdd',type=Path,help='MDD official taxonomy CSV, preferably v2.5')
    a.add_argument('--pantheria',type=Path,help='PanTHERIA_1-0_WR05_Aug2008.txt')
    a.add_argument('--output',type=Path,default=ROOT)
    a.add_argument('--min-players',type=int,default=10000)
    a.add_argument('--min-measured-mammals',type=int,default=2000)
    a.add_argument('--strict',action='store_true',help='fail if required sources or coverage are missing')
    z=a.parse_args()
    if not z.people and not z.mdd: a.error('Provide --people and/or both --mdd and --pantheria')
    if bool(z.mdd)!=bool(z.pantheria):a.error('--mdd and --pantheria must be supplied together')
    for k in ('people','names','mdd','pantheria'):
        p=getattr(z,k)
        if p and not p.is_file():a.error(f'{p} not found')
    report={'tool':'CLOSEISH identity-first importer v4','source_files':{},'publication_ready':False}
    src=ROOT/'days';out=z.output/'days';out.mkdir(parents=True,exist_ok=True)
    for day in (1,2,3):
        if day!=2:
            if (src/f'day-{day:02}.json').resolve()!=(out/f'day-{day:02}.json').resolve():
                (out/f'day-{day:02}.json').write_bytes((src/f'day-{day:02}.json').read_bytes())
            continue
        j=json.loads((src/'day-02.json').read_text(encoding='utf8'))
        if z.people:
            # The 2022 FIFA goal-minute question is event-locked. A general
            # player registry (Reep) never establishes 2022 goal scorer status.
            # It may be used in a separate research process, but MUST NOT be
            # appended as the question's recognized/eligible candidate pool.
            report['football']={'excluded_general_registry_import':True,
               'reason':'2022 goal-minute question admits verified 2022 World Cup goalscorers only',
               'verified_goal_scorers':len(j['q6']['answers']),
               'ineligible_non_scorers':len(j['q6'].get('excluded_answers',[]))}
            report['source_files']['reep']={'path':str(z.people),'sha256':sha(z.people),'used_for_question_eligibility':False}
            j['q6']['recognized_category_candidates']=[]
            j['q6']['recognized_category_candidate_count']=0
            j['q6']['recognized_outside_goal_scorer_count']=len(j['q6'].get('excluded_answers',[]))
        if z.mdd:
            masses,info=pantheria_mass(z.pantheria)
            mammals,summary=mdd_mammals(z.mdd,masses)
            merge_mammals(j['q2'],mammals,report)
            report['mammals']={**info,**summary,'passes_minimum_measured':report['mammal_scored_records']>=z.min_measured_mammals}
            report['source_files']['mdd']={'path':str(z.mdd),'sha256':sha(z.mdd)}
            report['source_files']['pantheria']={'path':str(z.pantheria),'sha256':sha(z.pantheria)}
        (out/'day-02.json').write_text(json.dumps(j,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
    ok=bool(report.get('mammals',{}).get('passes_minimum_measured') and report.get('mammal_publication_ready'))
    report['publication_ready']=False # first day and car models require independent audits; never imply full 3-day readiness
    report['data_thresholds_passed']=ok
    (z.output/'DATA-IMPORT-AUDIT.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('source_files','mammal_distributions')},ensure_ascii=False,indent=2))
    if z.strict and not ok:sys.exit(2)
if __name__=='__main__':main()
