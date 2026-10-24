# CLOSEISH V21 – production tartalmi kiadás

## Alap és hatókör

- Backend: a felhasználó által feltöltött `CLOSEISH-backend-V19-2026-11-01-COMPLETE(3).zip`.
- Frontend: a felhasználó által feltöltött `CLOSEISH-frontend-V18.4-full-score-table(2).zip`, változatlanul.
- A V21 helyi csomagból **csak** a V21 napi JSON-ok, a kérdés–válasz szabályzat, a kérdésindex és a forrás-/auditállományok kerültek át.
- Nincs `test.html`, admin belépés, privát teszt API vagy PostgreSQL-migráció.

## Napi státuszok

2026-10-23–2026-11-01: 10/10 nap `scheduled`, 60 kérdés. A 2026-10-23, 2026-10-24 és 2026-11-01 JSON-ok az eredeti V19-hez képest nem módosultak. A többi hét nap V21-változat.

## Összehangolt fájlok

`content/days/*.json`, `content/KERDES-VALASZ-SZABALYZAT.md`, `content/README-AI.md`, `content/question-index.json`, `content/source-snapshots/v21-*.csv`, `content/reference-rules/AUDIT-V21-2026-10-24-HU.md`, `CLOSEISH-kerdescsomag-AI.zip`.

A V19 specifikus, történetileg elavult README a `docs/README-V19-HISTORICAL.md` fájlban található. A `tests` API/content elvárásokat a már végleges `scheduled` napokhoz frissítettük. Futásidejű API-kódhoz és PostgreSQL-mentési logikához nem nyúltunk.

## Ellenőrzések és korlátok

- 10 nap / 60 kérdés: `node src/validate.mjs` – sikeres.
- Tartalmi, alias- és pontozási ellenőrzés: sikeres.
- 35 célzott Node-teszt sikeres egy offline, csak tesztelésre létrehozott PostgreSQL-modul-helyettesítővel. Ez nem került bele a ZIP-be, a tényleges PostgreSQL integrációt nem igazolja.
- Node 22-vel történt az offline teszt; a production kód deklarált követelménye Node 24 vagy újabb. Railway-en szükséges a `npm ci && npm run validate && npm test` futtatása, valamint az éles PostgreSQL-kapcsolat ellenőrzése.
- A mai, 2026-10-24-i napi JSON SHA-256 ellenőrzése: `1cf1dd25bed3f58cce5bf8d9750290d2a733525baa5899e0371e09b12e6116d4`.
