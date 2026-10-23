# CLOSEISH – javítási audit (2026-10-23–31), 2026-10-23

**Eredmény:** az ismert belső ellentmondásokat és a kiterjesztett automatikus ellenőrzés során előkerült további technikai hibákat javítottuk. **Ez nem jelenti az összes külső mérési érték és licenc önálló hitelesítését.**

## Konkrét fájlmódosítások

| Nap / kérdés | Megoldott hiba | Javítás | Válaszszám / mérési értékek / pontszámok |
|---|---|---|---|
| 2026-10-23 / q6 | A `below`/`at_most` és a `from_above`/`>=` ellentmondott | `approach_rule.required_side = from_below`, `operator = <=` | Változatlan |
| 2026-10-25 / q3 | 14 kétértelmű County/City név (Baltimore, St. Louis, Bedford, Fairfax, Franklin, Richmond, Roanoke; kétféle államnév-alak) | **28 többértelmű alias-hozzárendelés törlése**, 14 entitásból; County/City pontos név megmaradt | Változatlan |
| 2026-10-26 / q5 | 19 kétértelmű, akár országonként többször előforduló városnév | **41 többértelmű alias-hozzárendelés törlése**, 38 entitásból; országgal kiegészített nevek megmaradtak | Változatlan |
| 2026-10-26 / q2 | `unit: year`, de `scoring_window.units: years` | Mindkettő `year` | Változatlan |
| 2026-10-30 / q1 | Két entitás ugyanazt a `gapminder-2007-KOR` technikai azonosítót kapta; a rögzített Plotly Gapminderben mindkét Korea `iso_alpha = KOR` értéket használ | Külön azonosítók: `gapminder-2007-korea-dem-rep` és `gapminder-2007-korea-rep`; pontosított rekordforrás-lokátor, eredeti forráskód bizonyítékként megmaradt | Változatlan |
| 2026-10-24 / q4 | 13 sávszéli tizedes adatot a bináris lebegőpont-hiba hamisan jelölhet nem egyezőnek | A csatolt ellenőrző **pontos tízes számrendszerű** összehasonlítást használ; az adatokat nem módosítottuk, mert a tárolt 200 pont helyes | Változatlan |

**Újraellenőrzés összesítése:** 9 napi fájl, 54 kérdés, 202 790 pontozható válasz; 0 belső konzisztenciahiba. A `day.schema.json` ellenőrzés, az irány/operátor/határ, az 5 pontsáv, a 30 másodperc, a teljes és diakritikamentes névütközés-ellenőrzés, a rekordonkénti számított pont/tier, az entitásazonosítók, a hiányzó számértékek és a `question-index.json` összhangja része volt a futásnak.

Futtatás a csomagból (Python 3, `jsonschema` opcionális):

```bash
python content/reference-rules/validate-content-consistency.py
```

A natív backend kódját **nem tartalmazza ez a ZIP**, ezért a játék szerveroldali kétértelmű névfeloldását és a JS numerikus határok kiértékelését nem lehetett itt végigtesztelni. Ott tilos találomra első egyezésre feloldani olyan inputot, mint a puszta `London` vagy `Baltimore, MD`, és a 2026-10-24/q4 168,98 km-es sávszélét tizedes pontosságra normalizálva kell kezelni.

## Még nyitott hitelesítési / publikációs blokkolók

1. A 2026-10-29–31-i **18 új kérdés változatlanul `draft`**; több rekord kizárólag lefagyasztott csomagforrásból igazolt, nem egyedi külső primer ellenőrzésből. Válaszszámuk: 2255. Az importált napok forrásigazolása sem lett újra elvégezve 200 000 feletti tételen.
2. **2026-10-31/q2 rézpiaci sor licenc:** a statsmodels hivatalos dokumentációja szerint az eredeti szerző megtart minden jogot; a statsmodels saját terjesztési engedélye nem bizonyítja, hogy a CLOSEISH korlátlanul újraközölheti. Forrás: https://www.statsmodels.org/stable/datasets/generated/copper.html . Szerkesztői és felhasználási jogi rendezés szükséges.
3. A `CountryInfo`, Gapminder és egyes történeti minták hiányos vagy történeti forrásuniverzumot fednek. A hiányzó mérések `recognized_category_candidates` alatt `metric_value: null` értékkel maradnak; ez nem 0 pontos mérési érték.
4. A backend `npm run validate`, valamint a valódi API/felhasználói névfeloldási és lebegőpontos pontozási integrációs teszt itt nem történt meg. Nem állítjuk, hogy az összes előzetes publikálási követelmény teljesült.

## Fájlok SHA-256 az új ZIP-ben

- `2026-10-23.json` – 1,428,784 bájt, SHA-256: `ba5c9e0d6486224835e31f9185929af00bcb30fe5e13cdb62ebf35bb18d5d788`; `scheduled`.
- `2026-10-24.json` – 53,779,554 bájt, SHA-256: `1cf1dd25bed3f58cce5bf8d9750290d2a733525baa5899e0371e09b12e6116d4`; `scheduled`.
- `2026-10-25.json` – 3,471,987 bájt, SHA-256: `2a26534b2e4bb33e7b4284dd063a261bb32d6c511c73844b545bd0d150792538`; `scheduled`.
- `2026-10-26.json` – 2,376,258 bájt, SHA-256: `68d8625b73c1cbc5669b7b60c0bdd11772294acb534d92adfa98f52b205df20d`; `scheduled`.
- `2026-10-27.json` – 770,810 bájt, SHA-256: `33c1e692df2cc5197e3e2e02bcae163f82a4c77e3d83e7a2cdddc1ad3c7967a3`; `scheduled`.
- `2026-10-28.json` – 591,833 bájt, SHA-256: `5f6d6eae9cb44bbb2eb0d5f1b4c44133180c4dee8854f71b462a7e19e0153371`; `scheduled`.
- `2026-10-29.json` – 785,502 bájt, SHA-256: `b39bd89f248d53de04b9d8de1ffd3723c775cc6a664f8b640dffc5f6f2b2a367`; `draft`.
- `2026-10-30.json` – 456,305 bájt, SHA-256: `52ebeaef32bdd0049a0cfd800ad2bcef5f56b2813eea5dabf1be49a9223240ed`; `draft`.
- `2026-10-31.json` – 336,935 bájt, SHA-256: `d2b7c7d5c9e4c42fdf15998c901021f71d0942ab84ea5d9111fbb5eecd9a4ec9`; `draft`.

## Integritási elv

Csak javítással érintett mezők és szerkesztői revíziók változtak. Egyetlen napi fájl válaszrekordjainak száma, kanonikus neve, mért értéke, pontszáma, tierje, kérdés-limitje vagy sávhatára sem változott. A `question-index.json` érintett `content_revision` mezői frissültek.
