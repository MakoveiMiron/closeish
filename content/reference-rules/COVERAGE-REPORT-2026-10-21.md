# CLOSEISH – szigorú tartalmi és lefedettségi audit

**ÁLLAPOT: NEM PUBLIKÁLHATÓ – kutatási részkiadás (2026-10-21).**

Ez a jelentés a szerkesztett új 36 kérdés teljes pontozási adatát ellenőrzi, de az ismert források teljes világbeli lefedettségét önmagában nem tudja igazolni.

## Összesítő

- Új kérdések: **36**; felismert számos rekord: **137,032**; mérési adatra vár: **258**.
- Forrásonként különböző kanonikus nevek a teljes időszakban: **121,364**. Ez nem feltétlenül egyenlő a valóban különböző biológiai/történeti entitások számával.
- Kérdésben használt forráscsalád-azonosítók: **17**; hard blokk: **9**; figyelmeztetés: **32**.

## Napokra bontott adatsorok

| Nap/Q | Téma | Felismert | Mért | Hiányzó | Adatforrás |
|---|---|---:|---:|---:|---|
| 2/Q1 | language | 117,493 | 117,493 | 0 | cmudict-0.7b |
| 2/Q2 | biology | 83 | 83 | 0 | msleep-body-mass |
| 2/Q3 | design | 148 | 148 | 0 | css4-named-colors |
| 2/Q4 | transport | 38 | 38 | 0 | mpg-2008-cars |
| 2/Q5 | economics | 46 | 46 | 0 | txhousing-2010-03 |
| 2/Q6 | sports | 118 | 118 | 0 | openfootball-fifa-worldcup-2022 |
| 3/Q1 | sports | 30 | 30 | 0 | summer-olympics-country-participation |
| 3/Q2 | literature | 123 | 123 | 0 | nobel-literature-official-1901-2026 |
| 3/Q3 | geography | 3,220 | 3,220 | 0 | uscounties-shape-geodesy |
| 3/Q4 | society | 51 | 51 | 0 | statecrime-2009-violent |
| 3/Q5 | demography | 231 | 231 | 0 | countryinfo-frozen-demographic |
| 3/Q6 | history | 11 | 11 | 0 | us-presidential-terms-1953-2009 |
| 4/Q1 | economics | 142 | 142 | 0 | gap-frozen-snapshot |
| 4/Q2 | science | 118 | 118 | 0 | element-frozen-snapshot |
| 4/Q3 | geography | 3,221 | 3,220 | 1 | basemap-county-shapes |
| 4/Q4 | culture | 174 | 121 | 53 | heritage_country-frozen-snapshot |
| 4/Q5 | housing | 46 | 46 | 0 | txhousing-2010-03 |
| 4/Q6 | geography | 233 | 230 | 3 | country-frozen-snapshot |
| 5/Q1 | economics | 142 | 142 | 0 | gap-frozen-snapshot |
| 5/Q2 | science | 118 | 95 | 23 | element-frozen-snapshot |
| 5/Q3 | geography | 3,221 | 3,220 | 1 | basemap-county-shapes |
| 5/Q4 | culture | 174 | 121 | 53 | heritage_country-frozen-snapshot |
| 5/Q5 | history | 11 | 11 | 0 | us-presidential-terms-1953-2009 |
| 5/Q6 | geography | 233 | 230 | 3 | country-frozen-snapshot |
| 6/Q1 | history | 142 | 142 | 0 | gap-frozen-snapshot |
| 6/Q2 | science | 118 | 118 | 0 | element-frozen-snapshot |
| 6/Q3 | geography | 3,221 | 3,220 | 1 | basemap-county-shapes |
| 6/Q4 | culture | 174 | 174 | 0 | heritage_country-frozen-snapshot |
| 6/Q5 | transport | 38 | 38 | 0 | mpg-2008-cars |
| 6/Q6 | geography | 233 | 158 | 75 | country-frozen-snapshot |
| 7/Q1 | geography | 142 | 142 | 0 | gap-frozen-snapshot |
| 7/Q2 | science | 118 | 117 | 1 | element-frozen-snapshot |
| 7/Q3 | geography | 3,221 | 3,220 | 1 | basemap-county-shapes |
| 7/Q4 | culture | 174 | 174 | 0 | heritage_country-frozen-snapshot |
| 7/Q5 | public-safety | 51 | 51 | 0 | statecrime-2009-violent |
| 7/Q6 | geography | 233 | 190 | 43 | country-frozen-snapshot |

## Publikálást akadályozó hibák

- **daily_topics_not_distinct** (4/QALL): 5 topics across 6 rounds: ['economics', 'science', 'geography', 'culture', 'housing', 'geography']
- **daily_topics_not_distinct** (5/QALL): 5 topics across 6 rounds: ['economics', 'science', 'geography', 'culture', 'history', 'geography']
- **source_repeated_across_adjacent_days** (5/QALL): basemap-county-shapes, country-frozen-snapshot, element-frozen-snapshot, gap-frozen-snapshot, heritage_country-frozen-snapshot
- **daily_topics_not_distinct** (6/QALL): 5 topics across 6 rounds: ['history', 'science', 'geography', 'culture', 'transport', 'geography']
- **source_repeated_across_adjacent_days** (6/QALL): basemap-county-shapes, country-frozen-snapshot, element-frozen-snapshot, gap-frozen-snapshot, heritage_country-frozen-snapshot
- **daily_topics_not_distinct** (7/QALL): 4 topics across 6 rounds: ['geography', 'science', 'geography', 'culture', 'public-safety', 'geography']
- **source_repeated_across_adjacent_days** (7/QALL): basemap-county-shapes, country-frozen-snapshot, element-frozen-snapshot, gap-frozen-snapshot, heritage_country-frozen-snapshot
- **source_concentration** (ALL/QALL): 36 questions from 17 source-family identifiers, most repeated: [('gap-frozen-snapshot', 4), ('element-frozen-snapshot', 4), ('basemap-county-shapes', 4), ('heritage_country-frozen-snapshot', 4), ('country-frozen-snapshot', 4), ('mpg-2008-cars', 2), ('txhousing-2010-03', 2), ('statecrime-2009-violent', 2), ('us-presidential-terms-1953-2009', 2)]
- **source_family_overrepresented** (ALL/QALL): [('gap-frozen-snapshot', 4), ('element-frozen-snapshot', 4), ('basemap-county-shapes', 4), ('heritage_country-frozen-snapshot', 4), ('country-frozen-snapshot', 4), ('mpg-2008-cars', 2), ('txhousing-2010-03', 2), ('statecrime-2009-violent', 2)]

## Nyitott minőségi figyelmeztetések

- **incomplete_open_category** (2/Q2): 83 measured + 0 pending; source subset NOT proven globally complete
- **incomplete_open_category** (2/Q4): 38 measured + 0 pending; source subset NOT proven globally complete
- **incomplete_open_category** (2/Q5): 46 measured + 0 pending; source subset NOT proven globally complete
- **incomplete_open_category** (2/Q6): 118 measured + 0 pending; source subset NOT proven globally complete
- **alias_ambiguity** (3/Q3): 14 aliases refer to multiple IDs; examples: ['baltimoremd', 'baltimoremaryland', 'stlouismo', 'stlouismissouri', 'bedfordva', 'bedfordvirginia', 'fairfaxva', 'fairfaxvirginia']
- **incomplete_open_category** (3/Q4): 51 measured + 0 pending; source subset NOT proven globally complete
- **incomplete_open_category** (3/Q5): 231 measured + 0 pending; source subset NOT proven globally complete
- **incomplete_open_category** (3/Q6): 11 measured + 0 pending; source subset NOT proven globally complete
- **incomplete_open_category** (4/Q1): 142 measured + 0 pending; source subset NOT proven globally complete
- **incomplete_open_category** (4/Q2): 118 measured + 0 pending; source subset NOT proven globally complete
- **alias_ambiguity** (4/Q3): 14 aliases refer to multiple IDs; examples: ['baltimoremd', 'baltimoremaryland', 'stlouismo', 'stlouismissouri', 'bedfordva', 'bedfordvirginia', 'fairfaxva', 'fairfaxvirginia']
- **incomplete_open_category** (4/Q4): 121 measured + 53 pending; source subset NOT proven globally complete
- **incomplete_open_category** (4/Q5): 46 measured + 0 pending; source subset NOT proven globally complete
- **incomplete_open_category** (4/Q6): 230 measured + 3 pending; source subset NOT proven globally complete
- **incomplete_open_category** (5/Q1): 142 measured + 0 pending; source subset NOT proven globally complete
- **incomplete_open_category** (5/Q2): 95 measured + 23 pending; source subset NOT proven globally complete
- **alias_ambiguity** (5/Q3): 14 aliases refer to multiple IDs; examples: ['baltimoremd', 'baltimoremaryland', 'stlouismo', 'stlouismissouri', 'bedfordva', 'bedfordvirginia', 'fairfaxva', 'fairfaxvirginia']
- **incomplete_open_category** (5/Q4): 121 measured + 53 pending; source subset NOT proven globally complete
- **incomplete_open_category** (5/Q5): 11 measured + 0 pending; source subset NOT proven globally complete
- **incomplete_open_category** (5/Q6): 230 measured + 3 pending; source subset NOT proven globally complete
- **incomplete_open_category** (6/Q1): 142 measured + 0 pending; source subset NOT proven globally complete
- **incomplete_open_category** (6/Q2): 118 measured + 0 pending; source subset NOT proven globally complete
- **alias_ambiguity** (6/Q3): 14 aliases refer to multiple IDs; examples: ['baltimoremd', 'baltimoremaryland', 'stlouismo', 'stlouismissouri', 'bedfordva', 'bedfordvirginia', 'fairfaxva', 'fairfaxvirginia']
- **incomplete_open_category** (6/Q4): 174 measured + 0 pending; source subset NOT proven globally complete
- **incomplete_open_category** (6/Q5): 38 measured + 0 pending; source subset NOT proven globally complete
- **incomplete_open_category** (6/Q6): 158 measured + 75 pending; source subset NOT proven globally complete
- **incomplete_open_category** (7/Q1): 142 measured + 0 pending; source subset NOT proven globally complete
- **incomplete_open_category** (7/Q2): 117 measured + 1 pending; source subset NOT proven globally complete
- **alias_ambiguity** (7/Q3): 14 aliases refer to multiple IDs; examples: ['baltimoremd', 'baltimoremaryland', 'stlouismo', 'stlouismissouri', 'bedfordva', 'bedfordvirginia', 'fairfaxva', 'fairfaxvirginia']
- **incomplete_open_category** (7/Q4): 174 measured + 0 pending; source subset NOT proven globally complete
- **incomplete_open_category** (7/Q5): 51 measured + 0 pending; source subset NOT proven globally complete
- **incomplete_open_category** (7/Q6): 190 measured + 43 pending; source subset NOT proven globally complete

## Új helyi források és korlátjaik

- Az állatok a ggplot2 `msleep` 83 rekordos történeti mintájából származnak, nem az állatfajok teljes jegyzékéből.
- A CSS4 színnevek a Matplotlib 148 elemű, CSS4-kompatibilis listájából kerültek be.
- A texasi ingatlanárak a `txhousing` 2010. márciusi MLS-városi mintáján alapulnak.
- A korábbi elnökök csak 1953–2009 hivatalba lépett személyeinek helyi, 11 elemű mintájából származnak.
- A járművek csak az `mpg` 2008. évi, 38 darabos népszerűmodell-mintájából származnak.
- A `statecrime` 2009. évi adatai 50 államot és DC-t fednek le. Illinois és Minnesota erőszakos bűnözési rátáinál a forrás külön UCR-módszertani hiányt jelez.
- Más új kérdések továbbra is a korábbi Gapminder, elemtáblázat, megyei térképi és UNESCO-adatbankokon osztoznak.

## Nem teljesült követelmények

A 36 kérdés még nem alkot 36 egymástól független, kreatív tudásfeladatot. A teljes globális forráslefedettség nincs meg, és több nap szomszédos forrásokat ismétel. Nem állítható, hogy minden jogosult válasz szerepel. A böngészőtesztek a működést, nem a világszintű teljességet bizonyítják.

A `QUESTION-AUDIT-36-DETAILED.csv` mind a 36 kérdés mind a hét pontkategóriáját és a két nulla pontos okot rögzíti.
