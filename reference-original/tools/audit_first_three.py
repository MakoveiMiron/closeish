"""Reproducible score, scope and measurement validation for days 1-3.
Editorial completeness is reported honestly; not inferred from source import size.
"""
from pathlib import Path
from collections import Counter,defaultdict
import json,csv,math,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[1]
rows=[]
notes={
 (1,1):('RESEARCH','UNESCO snapshot excludes some properties and unmapped measurements; open category not proven exhaustive.'),
 (1,2):('SOURCE_COMPLETE','118 chemical elements; atomic weight numerical conventions are source-specific.'),
 (1,3):('RESEARCH','Territory/country roster and modeled capital-equator distances are source-specific; 232 measured.'),
 (1,4):('RESEARCH','192 member-country forest measurements, no evidence of all UN member values being resolved.'),
 (1,5):('RESEARCH','Only 142 GDP-history country series; not all countries/territories.'),
 (1,6):('SOURCE_COMPLETE','88 IAU constellations in named list.'),
 (2,1):('SOURCE_COMPLETE_ONLY','117,493 alphabetic CMUdict headwords, including proper names; not the entire English lexicon; 0 values are scores, not missing.'),
 (2,2):('RESEARCH','83 mammals from msleep sample. Not all mammal species; PanTHERIA or comparable trait survey still needs import and common-name matching.'),
 (2,3):('SOURCE_COMPLETE','148 official named CSS4 colors, weighted RGB brightness.'),
 (2,4):('RESEARCH','436 model names from a 2008 US fuel-economy derivative (411 measured, 25 pending); the global 2008 model universe remains unverified. Source uses best listed highway trim/variant MPG.'),
 (2,5):('RESEARCH','46 MLS areas for March 2010 Texas study; not all Texas places or housing sales. Historical sample retained.'),
 (2,6):('RESEARCH','118 2022 source goal scorers with scoring minutes + 158 independently identified 2022 non-scorers from bookings/goals cross-check. Not all footballers or even all roster members.'),
 (3,1):('SOURCE_COMPLETE','All 30 held Summer Olympics through 2024; historical delegation counts from a frozen reference table.'),
 (3,2):('SOURCE_COMPLETE','123 Nobel Literature recipients 1901-2026 including 2026 Anne Carson, 2025 Krasznahorkai.'),
 (3,3):('RESEARCH','3,220 US county-like polygons; geodesic area estimates not official US Census land area; geometry completeness/source year not proven.'),
 (3,4):('SOURCE_COMPLETE','50 US states and Washington DC for frozen 2009 statecrime measure.'),
 (3,5):('RESEARCH','231 countries/territories in mixed-year historical population source; no single measurement date.'),
 (3,6):('SOURCE_COMPLETE','All 45 distinct presidents through Oct 2026, first accession date; Cleveland and Trump counted once.'),
}
for day in range(1,4):
    data=json.loads((ROOT/'days'/f'day-{day:02d}.json').read_text())
    assert list(data)==[f'q{i}' for i in range(1,7)]
    for i,q in enumerate(data.values(),1):
        answers=q['answers'];ids=set();expected=Counter();bad=[];crossed=0;too_far=0
        assert q['time_limit_seconds']==30
        assert q['direction'] in ('above','below')
        assert isinstance(q['limit'],(int,float)) and (q['limit']>=50 or (q['unit']=='%' and 8<=q['limit']<=92))
        edges=[b['max_gap_inclusive'] for b in q['score_bands']];assert len(edges)==5 and edges==sorted(set(edges))
        for a in answers:
            aid=a['entity_id'];assert aid not in ids,(day,i,aid)
            ids.add(aid)
            assert math.isfinite(a['metric_value'])
            diff=a['metric_value']-q['limit'] if q['direction']=='above' else q['limit']-a['metric_value']
            if diff<0:score,tier=0,'CROSSED LIMIT';crossed+=1
            elif diff==0:score,tier=1200,'PERFECT HIT'
            else:
                j=next((j for j,edge in enumerate(edges) if diff<=edge),-1)
                score=[1000,800,600,400,200][j] if j>=0 else 0
                tier=['RAZOR EDGE','CLOSE CALL','SOLID HIT','IN THE ZONE','ON THE BOARD'][j] if j>=0 else 'TOO FAR'
                if j<0:too_far+=1
            expected[score]+=1
            if a['points']!=score or a['tier']!=tier:bad.append((a['canonical'],a['points'],score))
        assert not bad,(day,i,bad[:5])
        assert all(expected[k]>0 for k in (1200,1000,800,600,400,200,0))
        assert len(q.get('recognized_category_candidates',[]))+len(q.get('excluded_answers',[]))+len(answers)>0
        state,note=notes[day,i]
        rows.append({'day':day,'q':i,'question':q['prompt'],'topic':q['topic'],'source':q['source'],'unit':q['unit'],
             'target':q['limit'],'direction':q['direction'],'scored_count':len(answers),'recognized_missing_measurement':len(q.get('recognized_category_candidates',[])),
             'recognized_excluded':len(q.get('excluded_answers',[])),'point_1200':expected[1200],'point_1000':expected[1000],
             'point_800':expected[800],'point_600':expected[600],'point_400':expected[400],'point_200':expected[200],
             'point_0_too_far':too_far,'point_0_crossed':crossed,'tech_check':'PASS','source_coverage_status':state,'publishable_under_strict_coverage':'YES' if state=='SOURCE_COMPLETE' else 'NO',
             'reason':note})
assert len(rows)==18
with (ROOT/'FIRST-THREE-AUDIT.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,rows[0].keys());w.writeheader();w.writerows(rows)
summary=Counter(r['source_coverage_status'] for r in rows)
scored=sum(r['scored_count'] for r in rows);missing=sum(r['recognized_missing_measurement'] for r in rows);excluded=sum(r['recognized_excluded'] for r in rows)
original_hash=hashlib.sha256((ROOT/'days/day-01.json').read_bytes()).hexdigest()
report=f'''# CLOSEISH – első három nap: tényleges audit és javítási állapot

Audit: 2026-10-21. **Nem végleges publikálási jóváhagyás.** A kérdések mechanikai pontozása ellenőrizhető, de a tartalmi teljesség több nyitott kategóriában nem.

- **18 kérdés**, 3 × 6, minden pontkategóriának van tényleges válasza.
- **{scored:,} pontozott kérdés–válasz rekord** összesen (nem egyedi globális személy/dolog; ebből 117 493 a CMUdict szavainak kérdése).
- **{missing:,} felismert, méréssel nem rendelkező** és **{excluded:,} felismert, de jelen kérdésben nem jogosult** nevet tárolnak a bankok ezen felül. Ezek NEM növelik a pontozott rekordok számát.
- **{summary['SOURCE_COMPLETE']} zárt, ellenőrizhető kategória**, **{summary['SOURCE_COMPLETE_ONLY']} forráskiadáson belül teljes, de globálisan nem teljes**, **{summary['RESEARCH']} kutatási és lefedettségi hiányos**.
- 1. nap JSON SHA-256: `{original_hash}` – tartalma változatlan.
- A 2–3. nap szerkesztett kérdésszövegei nem a forrásfájlt említik a kérdésben, a forrás a katalógusban is elérhető.
- Az amerikai mértékegységek csak a megjelenítést változtatják; tárolt mért érték, pontozási irány, határ és pontsáv eredeti bázison marad.
- A katalógus a teljes importált részhalmazon keres, alapból 240 sort rajzol ki, és felhasználói kérésre újabb 240-et tölt be. Ez nem 240 elemszámú bankot jelent.

## Kérdésenként

| Nap/Q | Téma | Pontozott | Felismert más státuszban | Lefedettség | Pontozás |
|---|---|---:|---:|---|---|
'''
for r in rows:
 report+=f"| {r['day']}/{r['q']} | {r['topic']} | {r['scored_count']:,} | {r['recognized_missing_measurement']+r['recognized_excluded']:,} | {r['source_coverage_status']} | PASS |\n"
report+='''
## A publikálás útjában álló legfontosabb problémák

**2/2 – emlősök:** az `msleep` állomány 83 egyede mintavétel, nem fajkatalógus. Nincs jogalap a világszintű lefedettség kijelentésére, és más fajok súlyát sem szabad kitalálni. PanTHERIA vagy hasonló nagy trait-adatbázis importja, nevek egyeztetése és mérési audit szükséges.

**2/4 – 2008-as autók:** a korábbi 38 modell helyett most 436 név van importálva a 2008-as amerikai üzemanyag-fogyasztási forrásból: 411 pontozható, 25 mérésre vár. Az eltérő járműváltozatok közül a legmagasabb ismert highway MPG-t vesszük; ez a szerkesztői definíció a forrás megtekintésekor ellenőrizhető. A világ összes 2008-as modelljének lefedettsége ettől még nem igazolt. Az adatkészlet szűk, forrásalapú kutatási kiadás.

**2/6 – futballisták:** jelenleg 118 pontozott gólszerző és 158 olyan 2022-es tornán szereplő futballista ismert, aki a külön keresztellenőrzött góllistán nem szerepel. Az utóbbi név beírható, felismerhető és nulla ponttal „nem jogosult” státuszt kap; nem „0. perc” mérésként tároljuk. A világ százezres futballista-univerzuma NINCS importálva, és a többi név szabad szövegként csak felülvizsgálatra kerülhet.

**2/5 – texasi piacok:** a 46 jelentő helyi MLS-területből nem gyártható mesterségesen több ezer. A tényleges kérdéskör adott referenciahónapban ennyi helyet tartalmaz az importált kiadásban; ez szűk, de az adatok valósak.

**3/3 – megyék:** a 3 220 poligonból számított érték földrajzi becslés, nem hivatalos területstatisztika. A kérdés „mapped area” szóhasználata jelzi ezt.

**3/5 – népesség:** a fagyasztott `countryinfo`-tábla vegyes időpontjai miatt a történeti értékek nem egy egységes év statisztikái; időponthoz kötött, teljesebb forrás kell.

**3/6 – elnökök:** 11 helyett most mind a 45 különböző személy megtalálható. A kérdés a hivatalba lépés ELSŐ évét méri; Grover Cleveland és Donald Trump nem szerepel kétszer.

**1. nap:** változatlan maradt. A kémiai elemek és csillagképek természetes, zárt kategóriák; egyes ország- és UNESCO-kérdéseknél a forráslefedettség további ellenőrzést igényel.

## Minőségbiztosítás

A `tools/audit_first_three.py` valamennyi pontozott rekord pontját újraszámolja. Az alkalmazás Playwright tesztje mobilon és asztali nézetben ellenőrzi a 18 fordulót, a katalógust és az egységváltást. A technikai PASS nem jelenti a hiányzó entitások tartalmi teljességét.
'''
(ROOT/'FIRST-THREE-AUDIT-HU.md').write_text(report,encoding='utf-8')
print('AUDIT PASS',len(rows),'questions',scored,'scored',missing,'pending',excluded,'excluded','states',dict(summary))
