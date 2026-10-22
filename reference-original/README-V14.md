# CLOSEISH V14 — 4. nap, 5. kérdés: városok fair pontozása

## Azonosított hiba
A V13 forrás ZIP mindössze 971 várost tartalmazott a 4. nap 5. kérdéséhez, miközben a kérdés a világ összes városára és kisvárosára nyitott volt. Minden listán kívüli válasz automatikusan 0 pontot kapott, függetlenül attól, hogy valódi település és a pozitív pontsávba esik-e. A feladat nem kezelhető teljesen igazságosan egy 971 elemű, zárt listával.

## Javítás
- 1270 beépített, mért távolságú városi/települési név szerepel az önálló HTML-ben: az eredeti 971 és további 299 IANA tzdb referenciatelepülés.
- Beírt, a helyi listában nem szereplő település esetén a játékmotor **beküldéskor** Open-Meteo geokódolást kér, nem véletlenszerű értéket állít elő. A feloldott koordinátákból haversine nagy kör szerinti távolságot számol a Budapest (47.497912 N, 19.040235 E) koordinátához képest.
- Távolság megjelenítése kerekített kilométer; a már definiált 1200 / 1000 / 800 / 600 / 400 / 200 / 0 pontsávok változatlanok.
- A beírás pillanatában a 30 másodperces óra lezárul; a hálózati késleltetés nem számít levonásnak.
- Az online megerősített város bekerül a megnyitott válaszkatalógusba, és legfeljebb 500 megoldott találat helyileg (localStorage) gyorsítótárazódik. Ezt követően a korábban ellenőrzött város internet nélkül is pontozható ugyanabban a böngészőben, ha a böngésző tárolója elérhető.
- Az azonos nevű, eltérő földrajzi helyű városoknál ország-/régiópontosítás szükséges, ha nincs egyértelmű találat (pl. `City, Country`). A játék nem pontoz önkényesen egy másik várost.
- Ismeretlen szabad szöveg továbbra is beküldhető 0 pontért; nem jelenik meg előzetes figyelmeztetés vagy automatikus helyettesítés.

## Pontozás értelmezése
A 4792 km-es célpont közelítése **alulról** történik; a pozitív tartomány 1098–4792 km, szigorúan a pontsávok szerint. Egy valódi osztrák település (például Hallstatt) jóval 1098 km-en belül van: a távolság számítása után jogszerűen 0 pontot ér, nem azért mert nem szerepelt az adatbankban. Kutaisi (Georgia) az integrációs tesztben 1943 km és 400 pont.

## Tényleges lefedettség, korlát
**Nem teljes offline világváros-adatbázis.** A világ minden településének teljes és következetes geokódolása nincs beépítve, és az online Open-Meteo API működése/hálózati elérhetősége ettől a HTML-től független. Első alkalommal offline, nem katalogizált települést nem lehet hitelesen pontozni, ezért a V13 szabad válaszos szabály szerint 0 pont lesz. A böngészős integrációt determinisztikus API-válasz szimulációjával ellenőriztem; az élő távoli API ebből a futtatókörnyezetből nem volt elérhető. A ZIP nem állítja, hogy minden várost offline felismer.

## V13-ból visszacsúszott adatbankok helyreállítása
A V12 játszható HTML 670 videojáték-rekordot és 126 vízesést tartalmazott, de a V13 projektje/HTML-je csak 349 és 79 rekordot. A V14 nap-05 q1/q2 adatbankjai a V12 valódi beépített rekordjaiból helyreálltak. Ezek továbbra sem globálisan teljes listák.

## Eredet és attribúció
- GeoNames (CC BY 4.0): https://www.geonames.org/about.html
- Open-Meteo földrajzi névfeloldás: https://open-meteo.com/en/docs/geocoding-api
- IANA tzdb referenciahely-koordináták: https://github.com/eggert/tz/blob/main/zone.tab
- Eredeti Faker földrajzi minta: https://github.com/joke2k/faker/blob/master/faker/providers/geo/en_US/__init__.py

## Ellenőrzések
- `node tests/test_city_geo_v14.cjs` — helyes haversine számítás, ország-illesztés, azonos nevek elkülönítése, nincs kitalált érték.
- `python tests/test_v14_city_geocoding_browser.py` — Chromium, Open-Meteo válasz szimulálva: hiányzó Kutaisi (1943 km, 400 p) és Hallstatt (0 p, de valós, feloldott és helyesen túl távoli település), katalógusba építés, hibamentes JS.
- `node tests/test_core.cjs`, `python tests/test_distance_and_new_topics.py`, `python tools/audit_first_three.py` — sikeres.
- Nap 1, 2, 3, 6, 7 kérdésadat-fájlok a V13-hoz képest bájtra pontosan változatlanok.

**További tartalmi figyelmeztetés:** A projekt többi nyitott válaszkörű kérdése is tartalmazhat elégtelen méretű katalógust; a 42 kérdés áttekintő státusza a mellékelt CSV-ben található. A V14 csak a koordináta-alapú kérdés feloldását és a V12 rekordvisszaállítást oldotta meg, nem minden hiányos adatbankot.
