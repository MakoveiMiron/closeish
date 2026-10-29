# CLOSEISH V23 – AI kérdéscsomag

**Újrafelhasználható átadási prompt:** `../prompt.md` (minden következő teljes backend-ZIP-ben változatlanul kötelező).

**Elsődleges szerkesztői szabályzat:** `content/KERDES-VALASZ-SZABALYZAT.md` (V23). A 2026. november 1-jei napon szereplő hat különböző témacsaládot vedd minőségi mércének. A V21/V22 és régebbi szabályok csak történeti dokumentumok; a V23 elsőbbséget élvez.

## A kérdésbank szerkezete

- `content/days/YYYY-MM-DD.json` – naponta pontosan hat kérdés és a teljes, 0 pontos válaszokat is tartalmazó válaszkatalógus.
- `content/source-snapshots/v23-*.csv` és `v24-*.csv` – a kérdések forrás- és pontadatainak önálló, tételes kivonata.
- `content/question-index.json` – újragenerált keresőindex; nem a backend éles adatforrása.
- `content/reference-rules/AUDIT-V23-2026-10-24-HU.md` – a V23 cserejegyzék, források és témalefedettség.

Minden következő nap készítése előtt **az összes korábbi napot** vizsgáld át a tematika és entitáslista ismétlődése miatt. Önálló tudásfeladatokat tervezz; ugyanazon a napon ne legyen két országföldrajzos vagy két évszámba rejtett díjazási kérdés. Csak ellenőrizhető, természetesen teljes és megfelelő nehézségű bank kerülhet `scheduled` státuszba.

A szerveres validáció `npm run validate`, a tesztek `npm test`, az index és AI csomag generálása `npm run export:questions`. A backend production: Railway + PostgreSQL. A V23 játékosoldali HTML-t **nem** szabad szerverkóddal vagy admin/test végpontokkal együtt productionre telepíteni.

## Új, ütemezett tartalom – 2026. november 2–3.

A 11. és 12. nap (`2026-11-02.json` és `2026-11-03.json`) összesen 12 eltérő kérdést, 366 teljesen enumerált forrásrekordot, 12 új CSV snapshotot tartalmaz. A `content/reference-rules/GENERATE-2026-11-02-03.py` reprodukálja az új napokat; régi napot nem érint. A `tests/content-v24-nov02-03.test.mjs` a backend valódi normalizálását és pontozását használja. A nyilvános API továbbra sem adja ki az új napokat a helyi dátumuk előtt.

## Új, ütemezett tartalom – 2026. november 4–5. (V25)

A 13. és 14. nap (`2026-11-04.json` és `2026-11-05.json`) további **12 eltérő kérdést, 377 forráslistához kötött válaszrekordot és 12 új V25 CSV pillanatképet** tartalmaz. A teljes backend így **14 napból, 84 kérdésből** áll. A régebbi napok JSON-állományai változatlanok; a 2026. november 5-ig kibővített dátumhatár mellett az idő előtt közzététel tiltása megmarad.

Újrafuttatható generátor: `content/reference-rules/GENERATE-2026-11-04-05.py` (kizárólag a két új napot érinti). Tételes forrás- és szerkesztői audit: `content/reference-rules/AUDIT-V25-2026-10-29-HU.md`. Teszt: `tests/content-v25-nov04-05.test.mjs`. Az új forrásfájlok `content/source-snapshots/v25-*.csv` néven találhatók. A teljes tesztcsomaghoz PostgreSQL-kliens (`pg`) és a `package.json` által előírt Node.js verzió szükséges.
