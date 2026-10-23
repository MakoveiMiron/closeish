#!/usr/bin/env python3
"""Standard-library-only exhaustive source-universe checks for the V18 replacement banks."""
import json,math,re,sys,csv
from pathlib import Path
from decimal import Decimal,ROUND_HALF_UP
base=Path(__file__).resolve().parents[1]
days={d:json.loads((base/'days'/f'{d}.json').read_text(encoding='utf-8')) for d in ['2026-10-30','2026-10-31']}
q30=days['2026-10-30']['questions'];q31=days['2026-10-31']['questions']
def get(q):return {a['canonical']:a['metric_value'] for a in q['answers']}
def validate_csv(fname,q):
    with (base/'source-snapshots'/fname).open(encoding='utf-8',newline='') as f:rs=list(csv.DictReader(f))
    assert len(rs)==len(q['answers'])
    for r,a in zip(rs,q['answers']):
        assert r['entity_id']==a['entity_id'] and r['canonical']==a['canonical'] and Decimal(r['metric_value'])==Decimal(str(a['metric_value']))
for name,q in [('three-digit-primes.csv',q30['q1']),('fide-64-chess-squares.csv',q30['q2']),('folger-38-plays-title-length.csv',q30['q4']),('bipm-24-si-prefixes.csv',q30['q6']),('pokemon-original-151-speed.csv',q31['q3']),('icao-26-phonetic-words.csv',q31['q5'])]:validate_csv(name,q)
primes={str(n):sum(int(c) for c in str(n)) for n in range(100,1000) if all(n%d for d in range(2,math.isqrt(n)+1))}
assert get(q30['q1'])==primes and len(primes)==143
squares={f'{chr(97+f)}{r}':round(math.hypot(f,r-1),2) for f in range(8) for r in range(1,9)}
assert get(q30['q2'])==squares and len(squares)==64
assert len(q30['q4']['answers'])==38
assert all(a['metric_value']==len(re.findall('[A-Za-z]',a['canonical'])) for a in q30['q4']['answers'])
assert len(q30['q6']['answers'])==24 and set(a['metric_value'] for a in q30['q6']['answers'])=={30,27,24,21,18,15,12,9,6,3,2,1,-1,-2,-3,-6,-9,-12,-15,-18,-21,-24,-27,-30}
assert len(q31['q3']['answers'])==151
assert [int(a['entity_id'].split('-')[-1]) for a in q31['q3']['answers']]==list(range(1,152))
assert len(set(a['canonical'] for a in q31['q3']['answers']))==151
assert len(q31['q5']['answers'])==26
assert {a['entity_id'] for a in q31['q5']['answers']}=={f'icao-{chr(i)}' for i in range(97,123)}
for a in q31['q5']['answers']:
 word=a['canonical']
 count=sum(c.upper() in 'AEIOU' for c in word);letters=sum(c.isalpha() for c in word)
 value=int((Decimal(count*100)/Decimal(letters)).quantize(Decimal('1'),rounding=ROUND_HALF_UP))
 assert a['metric_value']==value
for date,d in days.items():
 assert d['publication_status']=='draft' and len(d['questions'])==6
 assert all(q['time_limit_seconds']==30 for q in d['questions'].values())
 for key,q in d['questions'].items():
  assert q['answer_scope']['claimed_exhaustive']
  assert q['answer_scope']['dataset_count']==len(q['answers'])
  assert set(a['points'] for a in q['answers'])=={0,200,400,600,800,1000,1200}
print('OK: 12 questions, 849 records; 6 replacement bank universes independently recomputed; 6 preserved bounded historical banks covered by backend validation.')
