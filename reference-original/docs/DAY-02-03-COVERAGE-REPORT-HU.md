# CLOSEISH – 2. és 3. nap: részletes tartalmi és forráslefedettségi audit

**Kiadás:** 2026. október 21. | **Kérdések:** 12 új kérdés (2. nap: 2026-10-21; 3. nap: 2026-10-22). 1. nap byte-identikus a bázishoz. A 4–7. nap a korábbi kutatási bank, tehát még NEM újratervezett.

**Státusz:** A két nap tesztelhető, teljes hatfordulós játékmenete működik, és minden importált entitásra újraszámolt pontszám ellenőrzött. Ugyanakkor a szigorú, világszinten lehető legteljesebb válaszkatalógusra és a legalább 3000 entitásra vonatkozó követelményt több nyitott kategória nem teljesíti. **A 12 kérdés ezért szerkesztői szempontból NEM publikálható véglegesként.**

## Kérdésenkénti tartalom és tényleges rekordok

| Nap / Q | Témakör | Ellenőrzött pontozási rekord | Forráscsalád | Státusz |
|---|---|---:|---|---|
| 2 / Q1 | language | 117,493 | `cmudict-1.1.3-headwords` | Forrásra korlátozott |
| 2 / Q2 | biology | 83 | `msleep-body-mass` | Forrásra korlátozott |
| 2 / Q3 | design | 148 | `css4-named-colors` | Zárt / teljes forráslista |
| 2 / Q4 | transport | 38 | `mpg-2008-cars` | Forrásra korlátozott |
| 2 / Q5 | economics | 46 | `txhousing-2010-03` | Forrásra korlátozott |
| 2 / Q6 | sports | 118 | `openfootball-fifa-worldcup-2022` | Forrásra korlátozott |
| 3 / Q1 | sports | 30 | `summer-olympics-country-participation` | Zárt / teljes forráslista |
| 3 / Q2 | literature | 123 | `nobel-literature-official-1901-2026` | Zárt / teljes forráslista |
| 3 / Q3 | geography | 3,220 | `uscounties-shape-geodesy` | Forrásra korlátozott |
| 3 / Q4 | society | 51 | `statecrime-2009-violent` | Forrásra korlátozott |
| 3 / Q5 | demography | 231 | `countryinfo-frozen-demographic` | Forrásra korlátozott |
| 3 / Q6 | history | 11 | `us-presidential-terms-1953-2009` | Forrásra korlátozott |

## Kérdésenkénti korlátok és forrásjegyzék

### 2. nap, Q1: Name a CMU dictionary headword whose letter score (A=1 to Z=26, added together) is at most 226.

- **Forrás:** https://github.com/cmusphinx/cmudict
- **Rekord:** 117,493; **mért érték nélkül elkülönített név:** 0; **közelítési irány:** below; **cél:** 226 letter points.
- **Katalógus definíciója:** Every unique alphabetic CMU Pronouncing Dictionary headword in the installed release; includes proper names and loanwords.
- **Mérés és kerekítés:** exact integer sum of letter ordinal values
- **Korlát:** Az összes, a csomaghoz mellékelt CMUdict 1.1.3-as verziójának 117 493 különböző, kizárólag betűs címszava. Az angol nyelv valamennyi szava NEM garantált; tulajdonnevek is vannak.
- **Értékelés:** Forrásállományon belül teljes; a nyelvre globálisan nem.

### 2. nap, Q2: Name a mammal from the published sleep study whose recorded body mass is at most 56 kg (rounded to the nearest kg).

- **Forrás:** https://ggplot2.tidyverse.org/reference/msleep.html
- **Rekord:** 83; **mért érték nélkül elkülönített név:** 0; **közelítési irány:** below; **cél:** 56 kg.
- **Katalógus definíciója:** All measured mammal names from the finite ggplot2 msleep research sample; not all living mammal species.
- **Mérés és kerekítés:** nearest whole kg, source frozen
- **Korlát:** Az msleep 83 elemű publikált kutatási MINTÁJA. Sok ezer további emlősfaj nem tartozik a forrásba. A kg-érték kerekítve jelenik meg.
- **Értékelés:** Korlátozott minta; nem teljes emlőskatalógus.

### 2. nap, Q3: Name a named CSS4 colour whose perceived RGB brightness is at least 201 out of 255 (rounded to an integer).

- **Forrás:** https://matplotlib.org/stable/gallery/color/named_colors.html
- **Rekord:** 148; **mért érték nélkül elkülönített név:** 0; **közelítési irány:** above; **cél:** 201 brightness points.
- **Katalógus definíciója:** Exactly the 148 named CSS4 colours; RGB brightness uses weighted channel sum, rounded to integer.
- **Mérés és kerekítés:** 0.299R + 0.587G + 0.114B, rounded to integer
- **Korlát:** A 148 hivatalos CSS4 színnév a Matplotlib listájából; a fényesség a deklarált RGB-képletből számolt.
- **Értékelés:** Zárt, teljes CSS4 névkészlet az adott kiadásban.

### 2. nap, Q4: Name a 2008 car model in the historic fuel-economy dataset that could travel at least 360 highway miles on 15 gallons.

- **Forrás:** https://ggplot2.tidyverse.org/reference/mpg.html
- **Rekord:** 38; **mért érték nélkül elkülönített név:** 0; **közelítési irány:** above; **cél:** 360 miles.
- **Katalógus definíciója:** All 38 distinct 2008 car model labels in ggplot2 mpg; not every 2008 vehicle sold.
- **Mérés és kerekítés:** best available highway MPG times 15 US gallons
- **Korlát:** 38 egyedileg megnevezett 2008-as autómodell a ggplot2 mpg 2008-as felméréséből. NEM az összes 2008-as autó. A 15 gallonra számított autópálya-hatótáv származtatott érték.
- **Értékelés:** Korlátozott kutatási minta.

### 2. nap, Q5: Name a Texas housing market area with a March 2010 median sale price at most $108,200 (nearest $100).

- **Forrás:** https://ggplot2.tidyverse.org/reference/txhousing.html
- **Rekord:** 46; **mért érték nélkül elkülönített név:** 0; **közelítési irány:** below; **cél:** 108,200 USD.
- **Katalógus definíciója:** All 46 MLS market areas reported in the bundled March 2010 Texas housing source.
- **Mérés és kerekítés:** nearest $100 from source
- **Korlát:** 46 helyi texasi MLS-piac a txhousing 2010 márciusi forrásában. Nem Texas minden települése / eladásai.
- **Értékelés:** Korlátozott földrajzi és időbeli adatsor.

### 2. nap, Q6: Name a goalscorer at the 2022 men’s World Cup whose earliest listed goal was in minute 60 or later.

- **Forrás:** https://github.com/openfootball/worldcup.json/blob/master/2022/worldcup.json
- **Rekord:** 118; **mért érték nélkül elkülönített név:** 0; **közelítési irány:** above; **cél:** 60 minute.
- **Katalógus definíciója:** Distinct named 2022 World Cup goalscorers in the openfootball goal-event feed; name and own-goal details are source dependent.
- **Mérés és kerekítés:** whole scheduled/added-time football minute; source minute notation retained as numeric minute
- **Korlát:** Az openfootball 2022-es férfi VB mérkőzésesemény-állományából feldolgozott 118 név, első feljegyzett gólperc szerint. Névvariánsok kézi egységesítése; nem független FIFA-rekordaudit.
- **Értékelés:** Forrásra korlátozott; hivatalos, teljes körű ellenőrzés még szükséges.

### 3. nap, Q1: Name a Summer Olympics edition (1896–2024) with at most 140 participating nations in the historic series.

- **Forrás:** https://www.thissportlife.com/games/olympic-games-summer/countries/number.htm
- **Rekord:** 30; **mért érték nélkül elkülönített név:** 0; **közelítési irány:** below; **cél:** 140 nations.
- **Katalógus definíciója:** 30 Summer Olympics held from 1896 through 2024; cancelled 1916, 1940, 1944 and the unofficial 1906 games excluded.
- **Mérés és kerekítés:** no rounding, source-recorded delegation counts
- **Korlát:** 1896 és 2024 közötti 30 megtartott modern nyári olimpia a rögzített thissportlife történeti táblázatával. Egyes ország-/delegációszámok forrásonként eltérnek, pl. a korai olimpiák.
- **Értékelés:** A 30 nyári olimpiai kiadás teljes listája, egy választott számsor szerint.

### 3. nap, Q2: Name a Nobel Prize in Literature laureate who received the award in 2000 or later.

- **Forrás:** https://www.nobelprize.org/prizes/lists/all-nobel-prizes-in-literature/
- **Rekord:** 123; **mért érték nélkül elkülönített név:** 0; **közelítési irány:** above; **cél:** 2,000 year.
- **Katalógus definíciója:** Entire Nobel Prize in Literature laureate category, award years 1901 through 2026.
- **Mérés és kerekítés:** official award year, no rounding
- **Korlát:** Az irodalmi Nobel-díj összes ismert díjazottja 1901–2026 (123 név), 2025 Krasznahorkai és 2026 Anne Carson. Díj nélküli évek nem entitások.
- **Értékelés:** Teljes, történetileg zárt Nobel-díjas-kategória az említett határnapig.

### 3. nap, Q3: Name a U.S. county or county equivalent whose approximate mapped land area is at most 2,074 km² (nearest km²).

- **Forrás:** https://matplotlib.org/basemap/stable/users/geography.html
- **Rekord:** 3,220; **mért érték nélkül elkülönített név:** 0; **közelítési irány:** below; **cél:** 2,074 km².
- **Katalógus definíciója:** All 3,220 valid US county/county-equivalent shapes with known mapped geodesic area in bundled snapshot.
- **Mérés és kerekítés:** nearest square kilometre, geodesic polygon area
- **Korlát:** 3220 telepített amerikai megye-/megyei jogállású földrajzi poligon, WGS84-geodéziai becsült területtel. Nem hivatalos US Census-földterület-érték.
- **Értékelés:** Teljes helyi poligon-snapshot; nem hivatalos területmérés.

### 3. nap, Q4: Name a U.S. state or Washington, D.C., with at least 358 recorded violent crimes per 100,000 residents in 2009.

- **Forrás:** https://www.statsmodels.org/stable/datasets/generated/statecrime.html
- **Rekord:** 51; **mért érték nélkül elkülönített név:** 0; **közelítési irány:** above; **cél:** 358 incidents/100k.
- **Katalógus definíciója:** 50 US states and District of Columbia, as tabulated in 2009 statsmodels statecrime snapshot.
- **Mérés és kerekítés:** nearest whole incident per 100,000
- **Korlát:** A statsmodels 2009-es statecrime történeti adatsora: 50 állam és Washington DC. Az adatok módszertana eltérhet a rendőrségi statisztikák között.
- **Értékelés:** Teljes 51 elemű zárt közigazgatási egység a forrásban.

### 3. nap, Q5: Name a country or territory whose historical countryinfo population is at most 25,000,000 people (nearest million).

- **Forrás:** https://github.com/porimol/countryinfo
- **Rekord:** 231; **mért érték nélkül elkülönített név:** 0; **közelítési irány:** below; **cél:** 25,000,000 people.
- **Katalógus definíciója:** Countries and territories with nonzero recorded population in bundled countryinfo snapshot; outdated/source-varying years.
- **Mérés és kerekítés:** nearest million people; snapshot, not current
- **Korlát:** 231 ország/terület a régi countryinfo-állományból. Nem egységes referenciaévű népességadat, és biztosan NEM 2026-os népesség.
- **Értékelés:** Történeti forrás-minta; hiteles, egységes időpontú statisztika kell.

### 3. nap, Q6: Name a U.S. president in the 1953–2009 timeline who first took office in 1977 or later.

- **Forrás:** https://ggplot2.tidyverse.org/reference/presidential.html
- **Rekord:** 11; **mért érték nélkül elkülönített név:** 0; **közelítési irány:** above; **cél:** 1,977 year.
- **Katalógus definíciója:** All eleven presidents in the bounded ggplot2 1953–2009 presidential timeline.
- **Mérés és kerekítés:** historical accession year, exact
- **Korlát:** A ggplot2 presidential 1953–2009 történeti forrásban szereplő 11 elnök. Az 1953 előtti és 2009 utáni elnökök szándékosan kívül vannak a kérdésen.
- **Értékelés:** Teljes a deklarált, de szűk 1953–2009-es időszakban.

## Ellenőrzési mérleg

- Pontozható rekord (12 kérdés **összesen**, a megismétlődő entitásokat és az adatbázisok eltérő jelentését nem szabad összekeverni): **121,592**.
- 0 pontot kapó, de forrásban szereplő rekord: **120,053**. A `TOO FAR` és `CROSSED LIMIT` kategória külön szerepel a CSV-ben.
- Mind a 12 kérdésben mind a hét pontértékhez (1200/1000/800/600/400/200/0) tartozik tényleges entitás.
- Két nap × hat különböző témakör és **12 eltérő forráscsalád**. Azonos mérőszám- vagy kérdéscsalád nem ismétlődik a két napon.
- **Különösen fontos:** az összes pontozható rekord 96%-át a CMUdict-szókatalógus adja. Az összesített 121 ezer rekord önmagában nem bizonyítja a többi tizenegy kategória teljességét.
- Bizonyíthatóan lefedett zárt kör: CSS4-színnevek, 30 megtartott nyári olimpia, irodalmi Nobel-díjasok 2026-ig, 50 amerikai állam + DC a 2009-es sorban; a korlátozott elnöki idősor csak saját szűk definícióján belül teljes.
- Nem megfelelően lefedett nyitott kategóriák: többek között emlősök, 2008-as autómodellek, texasi ingatlanpiacok, régi országpopulációk. Ezeket újbóli, nagyobb méretű, elsődleges adatimporttal kell leváltani ahhoz, hogy a felhasználó eredeti, teljes körű követelményének megfeleljenek.

## Technikai teszt

`python tests/test_day2_day3_release.py` minden entitás pontját újraszámolja, ellenőrzi a 0-sávokat, a 1200 pontos pontos-egyezést, a két nap 12 eltérő forrását, az entitás-azonosítók egyediségét és az első nap eredeti tartalmát.

`python tests/test_day2_day3_browser.py` Playwright/Chromium alatt 1440×900 és 390×844 méretben teszteli a 2×6 fordulót, a tényleges válaszbevitel 2 lépcsőjét, a kihagyást, a napi összegzést, a válaszkatalógus nyitását, részleges megjelenítését és keresését.

A háttér-statisztika továbbra is demó, nem valós játékosadat. A 4–7. nap a korábbi, tartalmilag még hiányos kutatási kiadásból származik. A két nap kész játékmenete **nem** jelent teljes szerkesztői publikálhatóságot.
