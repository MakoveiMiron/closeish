from pathlib import Path
import json,csv,collections,datetime
R=Path(__file__).resolve().parents[1]
questions=[];rows=[];total=0;pending=0;names=set();src=collections.Counter();cats=collections.Counter()
for day in range(1,8):
 d=json.loads((R/'days'/f'day-{day:02d}.json').read_text())
 for qid,q in d.items():
  if day>1:
   total+=len(q['answers']); pending+=len(q['recognized_category_candidates']);names.update(a['canonical'] for a in q['answers']);src[q['source']]+=1;cats[q['topic']]+=1
  counts=collections.Counter(a['points'] for a in q['answers'])
  rows.append([day,qid,q['date'],q['topic'],q['question_family'],q['prompt'],q['limit'],q['unit'],q['direction'],len(q['answers']),len(q['recognized_category_candidates']),len(q.get('excluded_answers',[])), *[counts[k] for k in [1200,1000,800,600,400,200,0]],q['editorial_status'],q['source']])
  if day>1:questions.append(q)
with (R/'QUESTION-AUDIT-EXPANDED.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['day','round','date','topic','family','question','target','unit','direction','measured_answers','unverified_measurements','ineligible_recognized','points_1200','points_1000','points_800','points_600','points_400','points_200','points_0','editorial_status','source']);w.writerows(rows)
assert total==25692, total
assert len(questions)==36
print('measured new',total,'unverified new',pending,'unique names',len(names),'topics',cats)
# Revised rulebook: quantitative denominator, UI, frozen local data and true status.
g=R/'docs/KERDESGENERALASI-SZABALYZAT-FRISSITETT.txt'
s=g.read_text()
new='''

## 17. Újabb tanulságok – tényleges válaszmennyiség és interakció (2026. október 20.)

- A **kérdés–válasz rekordok összegét** és a **különböző entitások számát** mindig külön kell jelenteni. Például 6×3000 megye nem 18 000 különböző megye. A napi és a hatnapos audit mindkét értéket közölje.
- A valóban nagy nyitott forrásokat teljesen kell importálni; a kifejezetten zárt, név szerint definiált halmazokat (pl. 118 kémiai elem, 437 adott forrásban szereplő középnyugati megye) nem kell 1000-ig mesterségesen duzzasztani. Az 1000-es minimum nyitott válaszkategóriákra vonatkozik, nem egy véges lista bővítésének előírása.
- Ha egy GIS-adatkészlet helynévvel azonosított alakzatokat tartalmaz, a **tényleges polygon / bounding-box alapján számított geodetikus érték** pontozható mint *közelítés*, de a kérdésben, a mérés metaadataiban és a forrásjelölésben ezt világosan közölni kell. Megyei körvonal hossza, térképi terület és közigazgatási nyilvántartás nem azonos fogalom.
- A forrásból hiányzó, a dátumvonalon átnyúló vagy nem mérhető entitás megmarad felismerhető rekordként, **nem kap költött számértéket**, és nem számítható be a pontozható válaszok közé.
- A több napban újrahasznált entitáskategória és adatszármazási család **nem tekinthető automatikusan különálló ötletnek**, még akkor sem, ha a numerikus metrika más. Hosszabb távon prioritás legyen további független források és újfajta mérési kapcsolatok importálása.
- Az automatikus válaszfelismerésben a játékos által írt szöveg **nem módosulhat az engedélye nélkül**. A legvalószínűbb megnevezés halvány, utána írt kiegészítésként jelenjen meg a beviteli mezőn belül; az első Enter csak a javasolt entitást erősítse meg, a **második Enter** véglegesítse a választ. Nem lehet lenyíló névlistával szükségtelenül leszűkíteni a nyitott választást. Többértelmű nevet tovább kell pontosítani.
- A végső válaszkatalógus **ALL** nézete mindig pontszám szerint csökkenően soroljon (1200, 1000, 800, 600, 400, 200, 0); az azonos pontú válaszok másodlagos rendezése lehet célértéktől való távolság és név.
- A kutatási előnézetben az összes, helyben hozzáadott archív nap szabadon választható dátumtól függetlenül. Ez **nem lehet az éles napi verseny biztonsági beállítása**: egy offline, teljes válaszbankot tartalmazó HTML-ben a jövőbeli kérdések és válaszok eleve kiolvashatók. Éles kiadásnál napi adatkiadás szükséges.
- Minden szerkesztői kiválasztásnak forráshűnek kell lennie: ha az egyetlen használható adatforrás elavult, becsült vagy részben másodlagosan dokumentált, a kérdés kutatási státusza marad **RESEARCH_DRAFT_NOT_PUBLISHABLE**. A teszt átfutása önmagában nem igazol publikálhatóságot.
'''
if '## 17. Újabb tanulságok' not in s:s+=new
g.write_text(s)
report=f'''# CLOSEISH – hét napos kibővített kutatási előnézet (2026-10-20)

## Valós mennyiségek

- Hat új nap, összesen **36 új kérdés** (2026-10-21–26). A korábbi első nap változatlan.
- Az új hat nap együtt **{total:,} pontozható kérdés–válasz rekord**, **{len(names):,} különböző megjelenített válasznév** és **{pending:,} felismert, de mérésre váró rekord**. A kérdés–válasz rekord nem egyedi entitás!
- Az első nappal együtt a teljes hét napban **{total+1942:,}** pontozható kérdés–válasz rekord található.
- Az adatbázis egyetlen rekordját sem töltöttük fel kitalált mértékegységgel vagy tippelt névvel.

## Új adatforrások és korlátaik

**Amerikai megyei térképi állomány (Basemap UScounties):** 3221 névvel és 5 jegyű FIPS-azonosítóval szereplő megye, közülük 3220 közelítő geodéziai mérés. A dátumvonalat keresztező Aleutians West Census Area azonosítható, de nem pontozható. A mérés az archivált térkép poligonjaiból (WGS84 geodézia és közelítő bounding-box) származik; nem hivatalos mai terület- vagy közigazgatási statisztika. **Hat külön kérdés** használja, tehát továbbra is forráskoncentráció van.

**2000-es Census-alapú középnyugati megyék (ggplot2/plotnine `midwest.csv`):** 437 névvel és PID-vel azonosított rekord Illinois, Indiana, Michigan, Ohio és Wisconsin államokból. A hat kérdés a népesség, felnőttek száma, oktatás és szegénységi mutatók különböző értékeit méri. A forrás maga jelzi, hogy egyes változók leírása feltételezésen alapul; ezért nem hitelesített aktuális hivatalos népszámlálásként jelennek meg. A százalékos értékeket egészre kerekítve pontozzuk.

**UNESCO DataHub `whc001`:** a 240 *Natural* besorolású világörökségi helyszín első felvételi éve, a más típusú helyszínek külön felismert, nem jogosult válaszok. Ez valóban más metrika, mint az első napi hektár-alapú feladat. A helyszín besorolását az adatforrás szerinti pillanatképből használjuk.

**Megmaradt korábbi források:** RDKit elemek, Gapminder 1952–2007, régebbi országpillanatkép és UNESCO országonként aggregált mutatók. Ezek jelenleg továbbra is szűk, tematikailag ismétlődő kategóriák, ezért a hat nap **nem tekinthető végleges szerkesztői tartalomnak**. Nem állítjuk, hogy a 36 kérdés 36 teljesen független ötlet.

## Felületi módosítások

- Névfelismerés: gépelés közbeni **inputon belüli** halk kiegészítés és instrukció, legördülő nélkül. Első Enter megerősít, a második Enter küldi be; a küldés előtt a játékos tovább módosíthatja a szöveget.
- `ALL` válaszkatalógus: 1200-tól 0-ig csökkenő, a pontkategóriákat követő rendezés; a teljes nulla pontos kategória látható.
- Archívum: a teljes hét nap azonnal megnyitható, az időzítés nem kerülhető meg a logós visszalépéssel, az aktív kör abszolút határideje megmarad.
- Az összesítő háromoszlopos struktúrája, a százalékos statisztikai mutató és a simított eloszlási görbe változatlan. A játékoseloszlás továbbra is **demo**, nem valós többjátékosos adat.

## Technikai ellenőrzések és publikálhatóság

A `QUESTION-AUDIT-EXPANDED.csv` mind a 42 kérdésre tartalmazza a teljes 1200/1000/800/600/400/200/0 bontást, a még ellenőrizetlen és kizárt nevek számát is. A hét nap pontozási és adatintegritási ellenőrzése, valamint a két Enteres működés, a 3220 soros ALL rendezése és a két nézetméret böngészős tesztje teljesült. Egy hosszú, ötnézetes regressziós futtatás időkorlátba ütközött: az nem tekinthető sikeres teljes tesztnek.

**Státusz: RESEARCH_DRAFT_NOT_PUBLISHABLE.** A legnagyobb továbbra is fennálló hiány a témaköri forráskoncentráció, a régi demográfiai pillanatképek és a tényleges független külső adatexportok további ellenőrzése. Egy többezer rekordos katalógus nem önmagában minőségi kérdés; a kreatív szerkesztői kritériumokat külön kell alkalmazni.

## Források

- UNESCO: https://data.unesco.org/explore/dataset/whc001/?flg=en-us
- ggplot2 Midwest (és a változóleírások bizonytalansága): https://ggplot2.tidyverse.org/reference/midwest.html
- Basemap adatterjesztés: https://matplotlib.org/basemap/stable/users/geography.html
- Egyéb korábbi források: `docs/SOURCE-NOTICES.md`
'''
(R/'docs/EXPANSION-2026-10-20-REPORT.md').write_text(report)
readme=R/'README-HU.md';base=readme.read_text();base=base.replace('Az önálló HTML-fájl a **CLOSEISH-standalone.html**; böngészőben közvetlenül megnyitható. A játék október 20-ra szól, előzetes kipróbáláshoz a fájl URL-jében `?preview=1` használható (vagy megnyitható a helyi webszerveren ezzel a paraméterrel). Nincs szükség alkalmazásszerverre.', 'Az önálló HTML-fájl a **CLOSEISH-standalone.html**; böngészőben közvetlenül megnyitható. Hét nap (2026. október 20–26.), archívumból mind a hét nap dátumkorlát nélkül játszható. Nincs szükség alkalmazásszerverre.')
base+='''\n\n## 2026-10-20: bővített forrásalapú kutatási kiadás\n\nAz új hat nap 25 692 pontozható kérdés–válasz rekordot tartalmaz. A korábbi 5254-es számot az új szám felülírja; a rekordok **nem mind különböző entitások**. Részletes, családonkénti statisztika és forráskorlátok: `docs/EXPANSION-2026-10-20-REPORT.md`; a CSV `QUESTION-AUDIT-EXPANDED.csv`.\n\nA kezdéskor a kiválasztott dátum nem korlátoz: minden archív nap játszható. A beviteli mezőbe a javasolt entitás vége halványan kerül, és két Enter szükséges a kiválasztáshoz és beküldéshez. Minden ALL válaszkatalógus legfelül 1200 pontot, legalul 0 pontot mutat.\n\nTovábbi lehetséges publikálási akadályok maradtak: több új kérdés azonos megyei térképi adatbázison alapul, egyes adatok becsültek vagy elavultak, és a teljes böngészős regresszióteszt nem fejeződött be. A kérdésbankokat ezért csak kutatási státuszúnak tekintjük.\n'''
readme.write_text(base)
print('Release report and guidelines updated: new answers',total,'unique names',len(names),'pending',pending)
