# CLOSEISH V23 – production tartalomkiadás

Ez a csomag a felhasználó által feltöltött V22 **production backendjét** tartalmazza; a szerver API, a Railway deployment és a PostgreSQL-alapú adatrögzítés útvonalait megőrzi. **Nem** tartalmaz privát tesztmódot vagy külön frontend HTML-t.

**Változás:** a 2026-10-25–2026-10-31 napok között 10 kérdés teljes, új, lezárt válaszbankot kapott; két másik kérdést áthelyeztünk, hogy október 28-án ne ismétlődjön a földrajz. A 2026-10-23, 2026-10-24 és 2026-11-01 napok bájtra pontosan változatlanok.

**Elsődleges dokumentumok:** `content/KERDES-VALASZ-SZABALYZAT.md` (V23), `content/reference-rules/AUDIT-V23-2026-10-24-HU.md`, `content/README-AI.md`, `content/source-snapshots/v23-*.csv`. A korábbi V22 dokumentumok archív megjegyzései nem az aktuális kérdésszövegek.

A teljes kérdésindex és az AI-csomag generálása: `npm run export:questions`. Tartalomellenőrzés: `npm run validate`; regresszió: `npm test` (a `pg` függőség telepítése után). Production indítás továbbra is `npm start` Railway alatt, Node 24+ ajánlott a megadott engines alapján. Nem kell új adatbázismigráció, mert az adatbázisséma nem változott.

**Fontos:** a ZIP-ben szereplő backend JSON-ok a hivatalos production válaszbankok. A különálló egyfájlos HTML csak helyi teszt, nem kerül productionre, és nem írhatja a nyilvános eredményeket.
