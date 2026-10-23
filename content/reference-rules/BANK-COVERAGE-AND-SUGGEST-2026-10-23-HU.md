# CLOSEISH – teljes fájlbank és hiányok auditja (2026-10-23)

**Státusz: technikailag ép, de a 29–31-i napok szakmailag továbbra is `draft` státuszúak.** A „teljes válaszbank” két dolgot jelenthet: (1) a ZIP-ben minden meglevő rekord bent van; ez teljesül; (2) a természetes nyelvű kérdés bármely valós válasza szerepel benne; ez **nem igazolható** több kérdésnél. Az elsőt nem szabad összetéveszteni a másodikkal.

- Dátumok: **9**, kérdések: **54**, JSON-válaszrekordok: **202,790**.
- A 29–31-i három nap: **18 kérdés, 2255 válaszrekord**, és minden tárolt pontozási sávban legalább egy válasz.
- Minden nap teljes `answers`, `aliases`, `recognized_category_candidates`, `excluded_answers`, forrás- és provenienciamezőivel együtt került az átadott ZIP-be. A nem listázott, még nem ellenőrzött választ a backend **0 ponttal, `unlisted` eredménnyel** jelöli; nincs külső adatokon történő élő ellenőrzés.

## Napi rekorddarabszám
| Dátum | Publikáció | Bankrekord |
| --- | --- | ---: |
| 2026-10-23 | `scheduled` | 1,942 |
| 2026-10-24 | `scheduled` | 189,604 |
| 2026-10-25 | `scheduled` | 3,700 |
| 2026-10-26 | `scheduled` | 2,832 |
| 2026-10-27 | `scheduled` | 1,261 |
| 2026-10-28 | `scheduled` | 1,196 |
| 2026-10-29 | `draft` | 1,010 |
| 2026-10-30 | `draft` | 719 |
| 2026-10-31 | `draft` | 526 |

## Október 29–31: kérdésenkénti nyitott kockázatok
| Nap/kérdés | Válasz | 0 / 200 / 400 / 600 / 800 / 1000 / 1200 | Hiány és szerkesztői teendő |
| --- | ---: | --- | --- |
| 29 q1 (biology) | 83 | 43 / 4 / 5 / 5 / 8 / 12 / 6 | Az emlősök köre csak 83 megfigyelés, és ismétli a 24-i állatbankot. |
| 29 q2 (international-standards) | 249 | 215 / 5 / 7 / 7 / 7 / 5 / 3 | ISO-alkódok darabszáma technikai, nem valamennyi közigazgatási egység száma. |
| 29 q3 (oceanography) | 61 | 3 / 1 / 5 / 7 / 11 / 28 / 6 | A megadott 61 év lefedett; a történeti hőmérsékleti forrás pillanatfelvétel, külső újramérés nincs. |
| 29 q4 (automotive-history) | 32 | 15 / 2 / 4 / 3 / 4 / 1 / 3 | Csak 32 Motor Trend tesztautó, a 1973–74-es modellkör nem teljes. |
| 29 q5 (local-demography) | 437 | 225 / 89 / 62 / 26 / 16 / 17 / 2 | 437 megye öt középnyugati államból, nem az USA teljes Midwest régiójából. |
| 29 q6 (digital-design) | 148 | 106 / 12 / 10 / 5 / 9 / 5 / 1 | A 148 CSS-szín zárt lista, de október 24. Q3 választerének ismétlése. |
| 30 q1 (public-health) | 142 | 67 / 29 / 26 / 7 / 8 / 2 / 3 | Csak 142 Gapminder-ország, nem valamennyi ország; korábbi ország-GDP kérdéshez közeli kategória. |
| 30 q2 (political-geography) | 232 | 107 / 27 / 28 / 26 / 22 / 13 / 9 | 232 CountryInfo-szomszédság; vitatott/historikus határok, független teljes ellenőrzés nincs. |
| 30 q3 (food-industry) | 80 | 49 / 7 / 7 / 6 / 5 / 5 / 1 | A 80 dokumentált év szerepel, de nem teljes külső, rekordonkénti újraellenőrzés. |
| 30 q4 (chemistry) | 118 | 73 / 10 / 10 / 9 / 8 / 7 / 1 | A 118 elem teljes, de megismétli a 23-i kémia válaszkört. |
| 30 q5 (lake-science) | 97 | 53 / 9 / 4 / 10 / 6 / 10 / 5 | Az 1876–1972 közti 97 összehasonlítható év teljes, de időjárási/történeti idősor típus. |
| 30 q6 (economic-history) | 50 | 29 / 6 / 3 / 4 / 5 / 2 / 1 | 50 év teljes a rögzített gazdasági idősorból, de hasonló évmegnevezős kérdések közel vannak. |
| 31 q1 (social-history) | 51 | 24 / 4 / 6 / 3 / 4 / 6 / 4 | Mind az 50 állam + DC szerepel, de 25-én hasonló állami statisztika szerepel. |
| 31 q2 (industrial-history) | 25 | 15 / 2 / 2 / 2 / 1 / 2 / 1 | Mind a 25 megadott év szerepel; a felhasználási jog/licenc nincs tisztázva. |
| 31 q3 (car-engineering) | 76 | 44 / 8 / 9 / 3 / 8 / 2 / 2 | 76 modell–év kulcs a ggplot2 mpg részhalmazból, NEM a két év összes autója. |
| 31 q4 (financial-history) | 107 | 66 / 5 / 5 / 10 / 12 / 8 / 1 | 107 történeti negyedév szerepel; niche idősoros kérdés és ismétlődő típusséma. |
| 31 q5 (population-geography) | 224 | 157 / 13 / 14 / 13 / 14 / 11 / 2 | 224 állam/terület vegyes korú népesség-/területadatokkal; nincs egységes mérési dátum. |
| 31 q6 (atmospheric-science) | 43 | 27 / 3 / 4 / 3 / 3 / 2 / 1 | 43 teljes év szerepel; 1958 részleges, forrásjelöléssel nem pontozott jelölt. |

## Források, adathiány és elfogadási logika

- Minden kérdésnél a JSON `source`, `source_refs`, `measurement`, `answer_scope` mezője az audit alapja, de sem ezek megléte, sem az integritásteszt nem bizonyítja a világ összes jogosult entitásának felvételét.
- A 32 autó mintajellege: https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/mtcars.html . A 234 soros mpg-adatkészlet válogatottsága: https://search.r-project.org/CRAN/refmans/ggplot2/html/mpg.html .
- Az október 29-i 5 államos county-adat, a korábbról ismétlődő entitáskörök és a 31-i vegyes dátumú népességadatsor cserére vagy új, bizonyított teljes forrásbeli lefedésre szorul. Az ismeretlen, de ténylegesen helyes szövegválaszok ellenőrzése és újrarögzítése szerkesztői folyamat; automatikusan kitalált méréssel nem pótolható.

## Suggest szétválasztás
- `POST /api/v1/suggestions` PostgreSQL-be ír; nincs publikus GET/list/export API, és a frontendben nincs Download Ideas, sem helyi javaslattörténet. A böngésző a saját szövegét elküldésig nyilvánvalóan láthatja/szerkesztheti; mások javaslatait nem.
- A régi frontendben létezett `closeish-question-suggestions-v1` és `closeish-question-draft-v1` helyi demótár: az új frontend ezeket törli, **nem képes a már más eszközön lévő adatokat átemelni**.
- A backendkód npm-tesztek futtatásával lett ellenőrizve tesztmemória-store-ral (24/24 sikeres). Élő Railway/PostgreSQL és böngészős E2E teszt továbbra szükséges.

## Kiadási döntés

**29–31-et ne állítsd `scheduled` értékre**, amíg a részleges autós/megyei/országos bankok, az ismétlődő kérdéscsaládok és a dokumentált forrás-/licenchiányok nem szűnnek meg. Ez a csomag teljes rekordanyagot ad át, de nem állít világméretű, függetlenül hitelesített teljességet.
