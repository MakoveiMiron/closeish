# V17 ellenőrzési jegyzőkönyv – 2026-10-22

## API és számítás

`npm test`: **11 tesztcsoport sikeres**.

- Mind a 42 kérdés pontozásának és rendelkezésre álló pontszintjeinek feloldása.
- Csak aznapi hat kérdés, válaszbank nélküli payload, jövőbeli kérdés és fájlrendszer-hozzáférés tiltása.
- Aliasok, hibás klienspont, revision-ütközés, lapozás, testméret, CORS, rate limit.
- Budapesti éjfél, téli időszámítás, hiányzó/draft nap, éles dátumfelülírás elutasítása.
- Nagy szótár, rögzített városbank, Aksu 1200 pontja, hibás tartalom elutasítása.
- Hamisított aláírás, másik eszköz, kevert futás, ismételt kérdés és lejárt igazolás elutasítása.
- 37 pontos hisztogram, saját eredmény kizárása, holtverseny, nulla/egy játékos, átlag/kvartilis.
- Ismételt/párhuzamos beküldés és újrajátszás idempotenciája, verziók elkülönítése.
- HTTP-végpontokon hat aláírt pont összesítése, hamis összpont figyelmen kívül hagyása, DB-hibánál 503 és readiness-hiba; liveness közben továbbra is 200.

A tartalomvalidálás mind a hét napi JSON-ra, 42 kérdésre és 204 429 tárolt mért válaszra kiterjed. Ez strukturális/pontozási ellenőrzés, nem az összes történeti forrás új szakmai auditja.

## Tényleges SQL

A `tests/postgres.test.mjs` **sikeresen futott PGlite PostgreSQL-motorral**. A tényleges SQL-migrációt és a PgStatsStore lekérdezéseit hajtotta végre, nem SQL-szövegeket utánzó mockot.

Ellenőrizve: migráció kétszeri futtatása; egyedi kulcs; 24 ismételt beküldés két store-példányból; újrajátszás; számláló helyessége; hibás pont elutasítása; a számlálóírás mesterséges hibájánál a játékoseredmény visszagörgetése; tartalomverziók különválasztása; teljes eredmény/számláló egyezési audit.

**Korlát:** a PGlite helyben, egy beágyazott motoron fut. Ez nem valódi hálózati PostgreSQL-pool, több DB-kapcsolat közötti zárolási teszt vagy Railway-terhelési mérés. A teszt `TEST_DATABASE_URL` beállítással a rendes `pg` poolon is futtatható; ezt külön, eldobható PostgreSQL-en kell elvégezni. A teszt ideiglenes DDL-t és tesztadat-törlést használ, éles DB-re tilos kapcsolni.

## Chromium böngésző

Az eredeti közös V17 projekt `tests/browser.mjs` tesztje sikeres három napra: 2026-10-21, 22, 23, böngészős JavaScript-hiba nélkül. A teszt saját, kifejezetten memóriás statisztikaszervert használ; a képernyőn LOCAL TEST DATA jelzés szerepel.

Ellenőrizve:

- Teljes játék, valódi szerverpontozás és aláírás, eredményoldal.
- Félbehagyott kérdés/draft/eredeti időzítő és lezárt válasz visszaállása frissítéskor.
- Második játéklap blokkolása Web Locks mellett.
- Offline pontozási kérés mentése és online újrapróbálása.
- Időben beírt válasz automatikus lezárása lejárt idővel újranyitáskor.
- A kész eredmény API-jának mesterséges 503 hibája, tartós várólista frissítés után, sikeres egyszeri újraküldés.
- Első játékosnál null százalék; második külön böngésző után két eredmény, megfelelő összehasonlítás.
- Teljes újrajátszás után változatlan számított napi eredmény és létszám; Practice run felirat.
- Mentett nap naptára, 120-as katalóguslapozás, névkeresés, 188 798 szavas bank, Aksu-válasz.
- Desktop 1440×1000 és mobil 390×844, képernyőképes vizuális ellenőrzés, vízszintes mobil-túlcsordulás nélkül.

A naplózott böngészős hálózati kérések mind a helyi alkalmazáshoz irányultak. Külső válaszkeresés nem történt.

## Ami nincs élő infrastruktúrán ellenőrizve

Railway-telepítés, élő PostgreSQL-hálózat, privát DNS/TLS, konténerbuild és Compose-futtatás, külső domain/CORS/CSP, Railway IP-headerek, backup/restore és éles kapacitás. Docker és k6 itt nem futott. A külön Railway agent-prompt és a staging terhelési script ezek elvégzésére is kitér.

A `load-local.json` megőrzött V16-mérés, nem V17 PostgreSQL-es teljesítménybizonyíték. Napi 150 ezer felhasználóra nincs ellenőrizetlen kapacitásgarancia.
