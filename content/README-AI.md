# CLOSEISH V23 – AI kérdéscsomag

**Elsődleges szerkesztői szabályzat:** `content/KERDES-VALASZ-SZABALYZAT.md` (V23). A 2026. november 1-jei napon szereplő hat különböző témacsaládot vedd minőségi mércének. A V21/V22 és régebbi szabályok csak történeti dokumentumok; a V23 elsőbbséget élvez.

## A kérdésbank szerkezete

- `content/days/YYYY-MM-DD.json` – naponta pontosan hat kérdés és a teljes, 0 pontos válaszokat is tartalmazó válaszkatalógus.
- `content/source-snapshots/v23-*.csv` – a V23 új kérdéseinek forrás- és pontadatainak önálló, tételes kivonata.
- `content/question-index.json` – újragenerált keresőindex; nem a backend éles adatforrása.
- `content/reference-rules/AUDIT-V23-2026-10-24-HU.md` – a V23 cserejegyzék, források és témalefedettség.

Minden következő nap készítése előtt **az összes korábbi napot** vizsgáld át a tematika és entitáslista ismétlődése miatt. Önálló tudásfeladatokat tervezz; ugyanazon a napon ne legyen két országföldrajzos vagy két évszámba rejtett díjazási kérdés. Csak ellenőrizhető, természetesen teljes és megfelelő nehézségű bank kerülhet `scheduled` státuszba.

A szerveres validáció `npm run validate`, a tesztek `npm test`, az index és AI csomag generálása `npm run export:questions`. A backend production: Railway + PostgreSQL. A V23 játékosoldali HTML-t **nem** szabad szerverkóddal vagy admin/test végpontokkal együtt productionre telepíteni.
