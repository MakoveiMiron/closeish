# CLOSEISH – Kutatási és minőségellenőrzési jelentés a 2–7. naphoz

> **ÁLLAPOT: RESEARCH DRAFT / NOT PUBLISHABLE.** A hat új nap adatai működő, interaktívan kipróbálható kutatási előnézetet alkotnak, nem véglegesen hitelesített publikációt.

## Elkészült elemek

- 6 új nap, 2026. október 21–26., naponta 6 kérdéssel: **36 új kérdés**.
- **5254 pontozható, kérdéshez tartozó mérési rekord** és **452 ismert, de nem pontozható / ellenőrzésre váró rekord**.
- A fenti számok **nem egyedi entitások összegei**: ugyanaz az ország vagy elem különböző kérdésben több kérdés–válasz rekordot ad.
- A régi 1. napi hat kérdés és válaszaik megmaradtak; hét nap összesen 42 kérdés.
- 30 mp/kérdés, 7 pontkategória, tényleges véges pontozási ablak, mindkét 0 pontos oldal, kerekítési szabályok és saját válaszkijelzés működik.
- Az eredeti HTML nézet, az összesítő kártyák és a simított demóeloszlás megmaradtak.

## Milyen források szerepelnek?

| Forrás/megoldás | Származás | Követelmény / kockázat |
|---|---|---|
| UNESCO DataHub World Heritage List | A mellékelt 2026-os adatpillanatkép | Hiányzó helyszínterületet nem számol összegekkel; közös jelölésnél az egész helyszín területe minden érintett entitásra hivatkozik |
| RDKit periódusos rendszer | A futtatott RDKit rendszerből számolt 118 elem | Bizonyos sugarak/izotópadatok könyvtári 0-ja hiányadatnak számít; az ilyen elemek a névbankban megmaradnak |
| Gapminder / Plotly | 1952–2007 történeti adatbank | Csak az adott történeti évre érvényes; nem 2026-os statisztika |
| countryinfo | Csomagolt, régebbi ország-/terület-pillanatkép | Az országok népességét nem szabad aktuálisnak tekinteni; a határvonalgeometria és a középponti koordináták közelítőek |
| statsmodels Statewide Crime 2009 | 51 állam és DC, 2009/2010 | Illinois és Minnesota problémás 2009-es erőszakos bűncselekmény-számát nem pontoztam, a kategóriában megmaradnak |

## A 36 új kérdés

Minden kérdés angolul szerepel; a pontozás az importált és rögzített mérési pillanatképből származik.

| Nap | Q | Kérdés | Mért | Várakozik | Pontozható ablak |
|---|---|---|---:|---:|---|
| 2 | Q1 | Name a country or territory listed by Gapminder whose population in 1982 was at least 28,000,000 people. (Rounded to the nearest million people.) | 142 | 0 | 10000000 people |
| 2 | Q2 | Name a chemical element with atomic number at least 85. (Values rounded to the nearest whole unit.) | 118 | 0 | 29  |
| 2 | Q3 | Name a country or territory whose land area is at least 236,800 km². (Values rounded to the nearest 100 square kilometres.) | 224 | 9 | 87000 km² |
| 2 | Q4 | Name a country or territory named in the UNESCO World Heritage dataset whose total inscribed UNESCO World Heritage site area is at least 96,300 hectares. (Values rounded to the nearest whole unit.) | 121 | 53 | 35419 hectares |
| 2 | Q5 | Name a US state or Washington, DC with a 2009 violent-crime incident rate of at most 358 per 100,000 residents. (Rates are rounded to the nearest whole incident.) | 49 | 2 | 134 per 100k |
| 2 | Q6 | Name a country or territory whose population density in the source snapshot is at least 67 people/km². (Values rounded to the nearest whole unit.) | 223 | 10 | 25 people/km² |
| 3 | Q1 | Name a country or territory listed by Gapminder whose life expectancy in 2007 was at least 56 years. (Rounded to the nearest whole year.) | 142 | 0 | 20 years |
| 3 | Q2 | Name a chemical element with covalent radius at most 151 pm. (Values rounded to the nearest whole unit.) | 118 | 0 | 32 pm |
| 3 | Q3 | Name a country or territory whose international telephone country calling code is at most 420. (Values rounded to the nearest whole unit.) | 230 | 3 | 160  |
| 3 | Q4 | Name a country or territory named in the UNESCO World Heritage dataset whose average area of its inscribed UNESCO sites is at most 18,714 hectares. (Values rounded to the nearest whole unit.) | 121 | 53 | 6932 hectares |
| 3 | Q5 | Name a US state or Washington, DC with at least 62% of residents living in a US Census urbanized area in 2010. (Percentages are rounded to the nearest whole percent.) | 51 | 0 | 28 % |
| 3 | Q6 | Name a country or territory whose absolute longitude of its mapped country centre is at most 115 degrees. (Values rounded to the nearest whole unit.) | 232 | 1 | 43 degrees |
| 4 | Q1 | Name a country or territory listed by Gapminder with 1972 GDP per person of at most US$12,800. (Rounded to the nearest US$100.) | 142 | 0 | 4800 $ |
| 4 | Q2 | Name a chemical element with van der Waals radius at least 202 pm. (Values rounded to the nearest whole unit.) | 118 | 0 | 38 pm |
| 4 | Q3 | Name a country or territory whose latitude of its capital away from the equator is at least 51 degrees. (Values rounded to the nearest whole unit.) | 230 | 3 | 11 degrees |
| 4 | Q4 | Name a country or territory named in the UNESCO World Heritage dataset whose area of its largest UNESCO World Heritage site is at least 2,441,200 hectares. (Values rounded to the nearest whole unit.) | 121 | 53 | 925241 hectares |
| 4 | Q5 | Name a US state or Washington, DC where at most 86% of residents had graduated from high school in 2009. (Percentages are rounded to the nearest whole percent.) | 51 | 0 | 5 % |
| 4 | Q6 | Name a country or territory whose east-west equatorial arc distance of its capital longitude from Greenwich is at least 6,250 km. (Values rounded to the nearest 10 kilometres.) | 230 | 3 | 2320 km |
| 5 | Q1 | Name a country or territory listed by Gapminder whose inflation-adjusted GDP per person increased by at most US$29,000 between 1952 and 2007. (Rounded to the nearest US$100.) | 142 | 0 | 7600 $ |
| 5 | Q2 | Name a chemical element with Rb0 atomic radius parameter at most 235 pm. (Values rounded to the nearest whole unit.) | 95 | 23 | 89 pm |
| 5 | Q3 | Name a country or territory whose equatorial arc distance of its country-centre longitude from Greenwich is at most 7,340 km. (Values rounded to the nearest 10 kilometres.) | 232 | 1 | 2320 km |
| 5 | Q4 | Name a country or territory named in the UNESCO World Heritage dataset whose median inscribed area of its UNESCO World Heritage sites is at most 119 hectares. (Values rounded to the nearest whole unit.) | 121 | 53 | 46 hectares |
| 5 | Q5 | Name a US state or Washington, DC where at least 24% of family households had a householder with no spouse present in 2009. (Percentages are rounded to the nearest whole percent.) | 51 | 0 | 5 % |
| 5 | Q6 | Name a country or territory whose north-south separation of its capital from its mapped centre is at most 350 km. (Values rounded to the nearest 10 kilometres.) | 230 | 3 | 140 km |
| 6 | Q1 | Name a country or territory listed by Gapminder whose population grew by at least 34% between 1952 and 2007. (Percentages are rounded to the nearest whole percent.) | 142 | 0 | 19 % |
| 6 | Q2 | Name a chemical element with mass of its most common isotope at least 208 u. (Values rounded to the nearest whole unit.) | 118 | 0 | 73 u |
| 6 | Q3 | Name a country or territory whose east-west equatorial arc separation of its capital from the country centre is at least 320 km. (Values rounded to the nearest 10 kilometres.) | 230 | 3 | 120 km |
| 6 | Q4 | Name a country or territory named in the UNESCO World Heritage dataset whose share of its listed UNESCO sites classified as natural is at least 16%. (Values rounded to the nearest whole percent.) | 174 | 0 | 9 % |
| 6 | Q5 | Name a US state or Washington, DC where at most 85% of residents reported their race as white alone in the 2009 American Community Survey. (Percentages are rounded to the nearest whole percent.) | 51 | 0 | 22 % |
| 6 | Q6 | Name a country or territory whose inhabitants per land-bordering neighbor is at least 7,700,000 people. (Values rounded to the nearest 100,000 people.) | 158 | 75 | 2700000 people |
| 7 | Q1 | Name a country or territory listed by Gapminder whose population rose by at least 18,000,000 people between 1952 and 2007. (Rounded to the nearest million people.) | 142 | 0 | 6000000 people |
| 7 | Q2 | Name a chemical element with neutron count in its most abundant isotope at most 176 neutrons. (Values rounded to the nearest whole unit.) | 117 | 1 | 59 neutrons |
| 7 | Q3 | Name a country or territory whose total mapped polygon-boundary length in a simplified geographic dataset is at most 6,780 km. (Values rounded to the nearest 10 kilometres.) | 173 | 60 | 2630 km |
| 7 | Q4 | Name a country or territory named in the UNESCO World Heritage dataset whose share of its listed UNESCO sites inscribed since 2000 is at most 47%. (Values rounded to the nearest whole percent.) | 174 | 0 | 22 % |
| 7 | Q5 | Name a US state or Washington, DC with a poverty rate of at least 10% in 2009. (Percentages are rounded to the nearest whole percent.) | 51 | 0 | 5 % |
| 7 | Q6 | Name a country or territory whose land area per listed time zone is at most 390,800 km². (Values rounded to the nearest 100 square kilometres.) | 190 | 43 | 149200 km² |

## Automatikusan ellenőrizhető kritériumok

- Mind a 36 kérdéshez létezik legalább egy 1200, 1000, 800, 600, 400, 200 és 0 pontos rekord.
- Az 1200 pont kizárólag a ténylegesen kerekített határértéket eltaláló rekordokhoz tartozik.
- Nem töröltem ki válaszokat a ponteloszlás kedvéért; csak a kérdésforrásban szereplő entitásokat importáltam.
- A hiányzó mérések nem kapnak elképzelt mérési értéket, és külön megjeleníthetők.
- A százalékok minden kérdésnél egész százalékra kerekítettek, és a kérdésszöveg ezt közli.
- A 200 pontos pontsávnak is véges, a célértékhez viszonyítva ellenőrzött távolsági maximuma van.
- Az egyes napi mentések külön azonosítót kapnak; az aktív kérdésből a logóval visszalépés tiltva.

## Miért NEM nevezhető még publikálhatónak?

1. **Forrás- és témadiverzitás:** több feladat még mindig ország-/területstatisztikára, UNESCO-listára, elemadatokra és Gapminderre épül. A forráscsaládok változatosabbak lettek, de a 36 önálló „obscure knowledge” kutatási ötletről szóló szabályt nem teljesítik meggyőzően.
2. **Független mérésellenőrzés:** a `countryinfo` egyes értékei elavultak, a geometriából származó peremhosszak közelítőek. A széles körű, forrás-szintű dokumentáció nélküli mezőket további keresztellenőrzés nélkül nem szabad hitelesítettnek tekinteni.
3. **Összetett UNESCO-aggregátumok:** egy államhoz rendelt transznacionális helyszín teljes területe a forrás szerinti jelölés alapján jelenik meg; ez nem az országban fekvő rész földrajzi területe. A hiányos területadatok miatt bizonyos országoknál pontot nem lehet megállapítani.
4. **Szabályzat és szerkesztés:** a számítógépes 7 pontos teszt nem dönti el, hogy a kérdés kellően érdekes, változatos és azonnal érthető-e. Ennek további független szerkesztői ellenőrzés kell.
5. **Adatbank teljessége:** minden mellékelt forrás snapshotjának teljes ismert névállományát tartalmazza a kérdés, de a pillanatkép nem feltétlenül a világ összes ismert entitása. Ezeket a katalógus PARTIAL jelzés nélkül nem szabad teljesnek nevezni.

**Tehát:** interaktívan kipróbálható 36 új kutatási kérdés/adatbank elkészült. A projekt nem állítja, hogy ezek már teljesen megfelelnek a szigorú publikálási feltételeknek.

## Hogyan futtasd és ellenőrizd?

- A gyökérben lévő `CLOSEISH-standalone.html` önállóan futó hét napos weboldal; a `?preview` tesztmód a későbbi napok kipróbálására szolgál.
- A napi JSON fájlok a `days/day-02.json`–`days/day-07.json` útvonalon találhatók.
- A generálás: `python tools/generate_six_days.py` (RDKit szükséges). Az offline HTML építése: `python tools/build.py`.
- A gépi tartalomellenőrzés: `python tests/test_seven_days.py`, valamint a meglévő tesztek.
- A valódi böngészős teljesfolyamat-teszt: `python tests/test_all_new_days_browser.py` (Chromium / Playwright szükséges).

## Publikálási döntés

Jelen állapot: **RESEARCH_DRAFT_NOT_PUBLISHABLE**. A szigorú szabályzat megsértését nem rejti el a játékban használt sikeres pontozási teszt. Az adatforrások frissítését, a mérés ellenőrzését és a teljesen eltérő témák bővítését még el kell végezni a kiadás előtt.
