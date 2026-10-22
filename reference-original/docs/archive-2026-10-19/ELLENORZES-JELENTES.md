# CLOSEISH – A 419 nyitott válasz ellenőrzése

**Kiadás:** 2026-10-19, a 2026-10-20-i első nap adataihoz.  
**Állapot:** részleges adatkiegészítés, teljesen tételes audit. **Nem állítható, hogy mind a 419 mérési érték igazolható.**

## Mérleg

| Státusz | Eredeti kérdés–entitás kapcsolatok |
|---|---:|
| Meglévő mért entitás aliasaként azonosítva | 24 |
| Új, ellenőrzött mérési adattal pontozhatóvá tett | 5 |
| Nem alkalmazható (nincs külön földrajzi főváros) | 2 |
| UNESCO-forrásból hiányzó / nulla, ezért **nem igazolt** hektáradat | 103 |
| Gapminder 1952/2007 összehasonlítható adatpár nem áll rendelkezésre | 285 |
| **Összes eredeti kapcsolat** | **419** |

**Összesen 29 rendezett kapcsolat** (24 alias + 5 mért). A 2 földrajzilag nem értelmezhető esetet kivéve **388 megválaszolatlan mérés** maradt. A korábbi 419 nem 419 különböző entitás volt: ugyanaz a 104 ország/terület három kérdésben is szerepelt.

## Részletek

**Q1 – UNESCO (103):** Az eredeti DataHub-pillanatképben 18 `null` és 85 `0`-ként tárolt területadat hiányzik. A `0` itt hiányos publikált területadatot jelent, nem ellenőrzött nulla hektárt. Mind a 103 világörökségi hely azonosítható maradt, de nincs megbízható, ehhez a pontosan definiált bejegyzett területhez társítható új mérésük.

**Q3 – főváros (4):** Edinburgh szélességi foka 55,95° (Skócia), Cardiffé ~51,48° (Wales). A játék egységes 100 km-es kerekítésével **6200 km** és **5700 km**. Mindkettő megadott kérdésnél 0 pont, mert kívül vannak a pontszerzési ablakon, de valós, felismert válaszok. Heard és McDonald-szigeteknek nincs külön fővárosuk; Makaó városjellegű különleges közigazgatási terület, szintén nincs külön főváros-entitása. Ezek továbbra is szerepelnek a felismert, de nem pontozható kategóriában.

**Q4–Q6 – történeti országadatok (312 eredeti kapcsolat):** Nyolc név minden kérdésben már meglévő, ellenőrzött rekord másik megnevezése: *Ivory Coast, Democratic Republic of the Congo, Republic of the Congo, The Gambia, Hong Kong, South Korea, Slovakia, Yemen*. Ez **24** alias-kapcsolat. A **Cape Verde / Zöld-foki Köztársaság** 1952-es és 2007-es megfigyelése megtalálható a Gapminder eredeti, szűrés nélküli adatállományában: Q4 **37%** (0 pont), Q5 **2600 nemzetközi $** (400 pont), Q6 **300 000 lakos** (0 pont). Ez **3** új mért rekord. A többi **285** kapcsolatban nem áll rendelkezésre ugyanezen mérési sorozat mindkét éve, ezért azok nem kaptak kitalált értéket.

## Pontosság és korlátok

Az 1952-es és 2007-es GDP/fő méréseknél nem szabad más bázisévű, eltérő PPP-módszertanú modern GDP-sorozatot az eredeti Gapminder-értékekkel keverni. Egy hiányzó ország- vagy világörökség-adat nem igazolja sem a nullát, sem a rossz irányú 0 pontot. A hiányos entitások az adatbázisban maradtak a további kutatáshoz.

## Források

- [UNESCO World Heritage List – area_hectares](https://data.unesco.org/explore/dataset/whc001/?flg=en-us)
- [Plotly / Gapminder – unfiltered historical CSV](https://github.com/plotly/datasets/blob/master/gapminder_unfiltered.csv)
- [UNGEGN – Edinburgh 55.95°](https://ungegn.un.org/dashboard/cities/details?id=268)
- [GeoNames – Cardiff 51.48°](https://www.geonames.org/2653822)
- [Australian Antarctic Division – Heard Island territory](https://www.antarctica.gov.au/about-antarctica/australia-in-antarctica/the-territory-of-heard-island-and-mcdonald-islands/)
- [Macao as city-like SAR (capital not separately applicable)](https://en.wikipedia.org/wiki/Outline_of_Macau)

## Fájlok

- `ELLENORZES-419.csv`: **419 sor**, minden eredeti nyitott kapcsolat státusza, forrása, pontszáma (ha hiteles), és indoklása.
- `QUESTION-AUDIT.csv`: frissített Q1–Q6 ponteloszlás.
- `days/day-01.json`: a játék ténylegesen frissített adatbankja.
- `tools/reconcile_pending.py`: az adatösszevezetés dokumentált, egyszer lefuttatandó forráskódja.
