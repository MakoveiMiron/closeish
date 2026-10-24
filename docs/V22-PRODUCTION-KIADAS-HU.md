# CLOSEISH V22 – production tartalmi kiadás

Ez a **különálló production backend** a jóváhagyott V21 szerverből indul. A nyilvános HTTP API, a Railway konfiguráció, a PostgreSQL-migrációk és a Suggest/eredménymentési folyamat nincsenek megváltoztatva. Nincs privát/local test mód, sem teszt-admin végpont.

## Mi új?

- 2026-10-25–2026-11-01 között **26** felülvizsgált napi kérdés és azok teljes válaszbankja.
- `content/KERDES-VALASZ-SZABALYZAT.md` – új **V22 obscure worldwide** nehézségi és teljességi szabály.
- `content/reference-rules/AUDIT-V22-2026-10-24-HU.md` – kérdésenkénti változáslista, korlátok.
- `content/source-snapshots/v22-*.csv` – a módosított teljes entitáshalmazok és pontok.
- Újraexportált `content/question-index.json` és `CLOSEISH-kerdescsomag-AI.zip`.

## Telepítés

1. A meglévő Railway backend szolgáltatás tartalmát cseréld erre a ZIP-re (azonos `closeish-main` gyökér).
2. Ellenőrizd, hogy a korábbi Railway Variables (`DATABASE_URL`, `ALLOWED_ORIGINS`, az esetleges API-kulcsok) megmaradtak.
3. Build előtt: `npm ci` az eredeti backend függőségeivel. Az indítási parancs változatlan.
4. Ellenőrzés: `npm run validate` és `npm test`. Éles DB migráció ehhez a tartalomcseréhez nem szükséges.
5. Éles `2026-10-24.json` nem változott (SHA-256: `1cf1dd25bed3f58cce5bf8d9750290d2a733525baa5899e0371e09b12e6116d4`).

A frontendhez nincs módosítás: továbbra is a V18.4 production frontend használható. A későbbi napok a dátumzárnak megfelelően jelennek meg.
