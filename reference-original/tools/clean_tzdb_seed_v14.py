from pathlib import Path
import json
P=Path(__file__).resolve().parents[1]/'days/day-04.json'
d=json.loads(P.read_text('utf8'));q=d['q5']
# IANA uses some country/island/region labels for civil-time zones. These are not
# town identities, so never score them as if they were populated places.
non_settlements={'Andorra, AD','Lord Howe, AU','Lindeman, AU','Bahrain, BH','Brunei, BN','Noronha, BR','Bahia, BR','Danmarkshavn, GL','Thule, GL','Guadeloupe, GP','Guyana, GY','Jamaica, JM','Montserrat, MS','Malta, MT','Bahia Banderas, MX','Qatar, QA','Sakhalin, RU','Kamchatka, RU','St Vincent, VC','Tortola, VG','St Thomas, VI'}
renames={'Belize, BZ':'Belize City, BZ','Guatemala, GT':'Guatemala City, GT','Kuwait, KW':'Kuwait City, KW','Panama, PA':'Panama City, PA'}
removed=[]
for ent in list(q['answers']):
 if not ent['entity_id'].startswith('tzdb-'):continue
 if ent['canonical'] in non_settlements:
  q['answers'].remove(ent);removed.append(ent['canonical']);continue
 if ent['canonical'] in renames:
  ent['canonical']=renames[ent['canonical']]
  ent['aliases']=[]
q['answer_scope']['dataset_count']=len(q['answers']);q['verified_answer_count']=len(q['answers']);q['catalogued_answer_count']=len(q['answers']);q['alias_count']=sum(len(a.get('aliases',[])) for a in q['answers'])
q['score_distribution_audit']={str(t):sum(x['points']==t for x in q['answers']) for t in (1200,1000,800,600,400,200,0)}
P.write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')),'utf8')
print('Removed',len(removed),'non-place tzdb region names:',removed)
print('Offline city/settlement seed',len(q['answers']),q['score_distribution_audit'])
