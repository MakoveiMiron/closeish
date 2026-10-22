from pathlib import Path
import json,collections
R=Path(__file__).resolve().parents[1]
path=R/'days/day-03.json';d=json.loads(path.read_text());q=d['q4'];all_rec=json.loads((R/'datasets/unesco-property-areas-2026.json').read_text())['records'];rec=[r for r in all_rec if r['category']=='Natural']
limit=1990;edges=[1,2,5,10,22];vals=[];pending=[];counts=collections.Counter();names={1200:'PERFECT HIT',1000:'RAZOR EDGE',800:'CLOSE CALL',600:'SOLID HIT',400:'IN THE ZONE',200:'ON THE BOARD'}
for r in rec:
 try:year=int(r.get('inscription_year'))
 except (ValueError,TypeError):pending.append(r);continue
 gap=year-limit
 points=0 if gap<0 or gap>edges[-1] else 1200 if gap==0 else next([1000,800,600,400,200][i] for i,e in enumerate(edges) if gap<=e)
 counts[points]+=1
 vals.append({'entity_id':'unesco-'+r['id'],'canonical':r['name'],'aliases':[],'verified_status':'unesco_snapshot','source_refs':[{'source_id':'unesco-datahub-whc001','locator':r['url']}],'metric_value':year,'points':points,'tier':names.get(points,'CROSSED LIMIT' if gap<0 else 'TOO FAR')})
assert len(vals)+len(pending)==240 and all(counts[v]>0 for v in [1200,1000,800,600,400,200,0]), counts
q.update({'topic':'culture','bank_id':'unesco-site-inscription-year-1990','question_family':'unesco-site-first-inscription-year',
 'prompt':'Name a natural UNESCO World Heritage site first inscribed in 1990 or later. (First inscription year, not construction year.)',
 'metric':'first year of inscription on UNESCO World Heritage List','unit':'year','limit':limit,'comparison':'at_least','direction':'above',
 'score_bands':[{'max_gap_inclusive':edge,'points':p,'tier':names[p]} for edge,p in zip(edges,[1000,800,600,400,200])],
 'source':'https://data.unesco.org/explore/dataset/whc001/?flg=en-us','source_refs':['unesco-datahub-whc001'],
 'verification_status':'source_recorded_first_inscription_year','editorial_status':'RESEARCH_DRAFT_NOT_PUBLISHABLE',
 'content_revision':'2026-10-20-sixdays-research-2026-10-22-q4-year-v2',
 'metric_provenance':'UNESCO DataHub whc001 site-level first inscription year, snapshot 2026-10-17. Year values from named UNESCO records, independently reproducible.',
 'measurement':{'property':'inscription_year','edition':'unesco-datahub-whc001','numeric_rule':'year as recorded (integer)','time_dependent':False},
 'answer_scope':{'type':'finite_source_world','coverage':'complete_local_unesco_snapshot','claimed_exhaustive':True,'entity_scope':'All 240 source-listed natural World Heritage properties, whether in-range or not','dataset_count':240},
 'scoring_policy':'Integer first inscription year, above 1990 inclusive, 0 points for earlier years or more than 22 years later.',
 'scoring_window':{'max_scoring_distance':22,'units':'year','outside_window_points':0,'wrong_side_points':0,'exact_match_points':1200},
 'answers':vals,'recognized_category_candidates':[{'entity_id':'unesco-'+r['id'],'canonical':r['name'],'aliases':[],'verified_status':'measurement_unavailable','source_refs':[{'source_id':'unesco-datahub-whc001','locator':r['url']}], 'metric_value':None, 'membership_status':'recognized_entity_unverified_measurement'} for r in pending],
 'verified_answer_count':len(vals),'catalogued_answer_count':240,'recognized_category_candidate_count':len(pending),'alias_count':0,
 'excluded_answers':[{'entity_id':'unesco-'+r['id'],'canonical':r['name'],'aliases':[],'exclusion_reason':'This property is not classified as a Natural UNESCO World Heritage site.','metric_value':None,'source_refs':[{'source_id':'unesco-datahub-whc001','locator':r['url']}]} for r in all_rec if r['category']!='Natural'],
 'score_distribution_audit':{str(k):counts.get(k,0) for k in [1200,1000,800,600,400,200,0]},
 'research_status':'Year-based UNESCO identity dataset, research editorial draft; unlike site area question, measures a historical registration event.'})
path.write_text(json.dumps(d,ensure_ascii=False,separators=(',',':'))+'\n')
print('UNESCO inscription year',dict(counts))
