"""Synchronize legacy audit tables with currently active day bank JSON."""
from pathlib import Path
import json,csv
R=Path(__file__).resolve().parents[1]
items=[]
for d in range(1,8):
 b=json.loads((R/'days'/f'day-{d:02}.json').read_text())
 for rn,q in enumerate(b.values(),1):
  audit=q['score_distribution_audit']; items.append({'day':d,'round':f'q{rn}','date':q['date'],'topic':q['topic'],'family':q['question_family'],'question':q['prompt'],'target':q['limit'],'unit':q['unit'],'direction':q['direction'],'measured_answers':len(q['answers']),'unverified_measurements':len(q['recognized_category_candidates']),'ineligible_recognized':len(q.get('recognized_ineligible_candidates',[])),'points_1200':audit.get('1200',0),'points_1000':audit.get('1000',0),'points_800':audit.get('800',0),'points_600':audit.get('600',0),'points_400':audit.get('400',0),'points_200':audit.get('200',0),'points_0':audit.get('0',0),'editorial_status':q.get('editorial_status','existing_day'),'source':q['source']})
with (R/'QUESTION-AUDIT-EXPANDED.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=list(items[0]));w.writeheader();w.writerows(items)
print('Synced 42 rows in QUESTION-AUDIT-EXPANDED.csv')
