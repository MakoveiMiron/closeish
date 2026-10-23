# CLOSEISH – önálló Railway backend (V17.1)

Ez a ZIP a külön telepíthető backendet tartalmazza, saját package.json-nal, lockfile-lal, Dockerfile-lal, railway.toml konfigurációval, adatbázis-migrációval és tesztekkel. A frontend másik ZIP-ben van; az API futtatásához nem kell a frontend mappája.

## Helyi indítás

Node.js 24+ szükséges. A kicsomagolt `CLOSEISH-backend` mappában:

```sh
npm ci
npm run demo
```

Az API alapértelmezés szerint http://127.0.0.1:3000 címen fut. A demo a mellékelt kérdéscsomagokkal használható; az első játszható nap 2026-10-23. A külön frontend mappájában, másik terminálban `npm run dev`, utána http://localhost:5173.

A backendhez egyszer szükséges az `npm ci` a PostgreSQL-kliens telepítéséhez. Railway-en ezt a Dockerfile automatikusan elvégzi. A frontendhez nincs telepítendő csomag.

Mai szervernaphoz: `npm run dev`. Ez helyi fejlesztéshez opcionálisan beolvassa a `.env` fájlt. A `npm start` és a Railway-futtatás a környezetből kapja a változókat. A `.env.example` éles konfigurációs minta; ne másold változtatás nélkül a helyi demo elé.

Adatbázis nélkül a helyi kérdésjáték működik, a statisztika nincs konfigurálva. PostgreSQL-es helyi statisztikához állítsd a DATABASE_URL, SIGNING_SECRET és PLAYER_HASH_SECRET környezeti változókat, futtasd az `npm run migrate` parancsot, majd indítsd az API-t. A migráció a folyamat környezeti változóit olvassa. Memóriás statisztika csak kifejezett helyi tesztre használható: STATS_MODE=memory. Élesben nincs ilyen visszaesés.

## Railway – önálló repository

A repo gyökerébe ennek a backendmappának a **tartalma** kerüljön. Root Directory: `/`, konfiguráció: `/railway.toml`, Dockerfile: `Dockerfile`. Ha a repóban a külső `CLOSEISH-backend/` mappát is megtartod, Root Directory `/CLOSEISH-backend`, konfiguráció `/CLOSEISH-backend/railway.toml`.

A külön backendhez igazított agent-prompt itt van: **RAILWAY-AGENT-PROMPT-HU.md**. Ezt használd; a korábbi közös projekt `/backend` útvonalai erre a külön repositoryra már nem vonatkoznak.

A konfiguráció pre-deploy lépésben migrál, a Node API-t indítja, és a `/readyz` végponton ellenőrzi az adatbázist is. PostgreSQL-adatbázis, DATABASE_URL, két stabil titok és a frontendhez pontos ALLOWED_ORIGINS szükséges. Részletek: `docs/RAILWAY.md`. Napi 150 000 felhasználóhoz a tényleges Railway-staging terhelési próbát is el kell végezni: `docs/150-EZER-FELHASZNALO.md`.

## Adatok és kérdéscsomag

- `content/days/YYYY-MM-DD.json`: naponta egy JSON, teljes kérdés- és válaszbankkal.
- `content/KERDES-VALASZ-SZABALYZAT.md`: összeállítási szabály.
- `content/day.schema.json`: séma.
- `content/question-index.json`: az eddigi kérdések áttekintése.
- `CLOSEISH-kerdescsomag-AI.zip`: az AI-nak külön átadható aktuális tartalomcsomag.
- `migrations/`: PostgreSQL-séma a napi eredményekhez és pontos pontonkénti számlálókhoz.
- `reference-original/`: megőrzött történeti források és auditok, nem publikus adat.

Új nap beillesztése után:

```sh
npm run validate
npm run export:questions
```

Mindkét parancs önállóan, ebben a backendmappában működik. A friss AI-ZIP ide, a mappa gyökerébe készül. Az új napi JSON szakmai ellenőrzés és `scheduled` állapot után backend-újratelepítéssel kerül kiszolgálásra. A frontendbe nem kerül teljes kérdésbank.

A mellékelt hét nap 2026-10-23–29-re szól. Hiányzó napon nincs napi kérdéscsomag; az éles szerver nem dátumozza át a játékot.

## Számláló, mentés, statisztika

A **30 másodperces visszaszámlálót a frontend futtatja helyben**. A backend csak a kérdés egyszeri időkeretét adja át, nem küld másodpercenként időadatot. Nincs timer endpoint, WebSocket vagy szerveres tick. A lejáratkor elküldött válasz/időtúllépés a normál pontozási útvonalat használja.

Az előrehaladás a böngészőben mentődik. A befejezett napi pontszám aláírt részpontok alapján PostgreSQL-be kerül. Az első sikeresen tárolt napi eredmény számít; retry és újrajátszás nem dupláz. A napi eloszlás, átlag és százalék valódi tárolt eredményekből készül. A saját eredmény a „hány százaléknál voltál jobb” összehasonlításból ki van véve; a holtverseny nem megelőzés. Teljes leírás: `docs/RAILWAY.md`, `docs/API.md`.

## Tesztek

```sh
npm test
```

A 11 API- és statisztikai tesztcsoporthoz nem kell frontendmappa. Az SQL-integrációs teszthez `TEST_DATABASE_URL` mutasson külön, eldobható adatbázisra, majd `npm run test:postgres`. Ez DDL-t és tesztadat-törlést is végez, ezért éles DB-n tilos futtatni.

A `docs/ELLENORZES.md` a V17 közös projekt ellenőrzési történetét őrzi. A külön csomagok új ellenőrzése: `docs/KULON-CSOMAG-ELLENORZES.md`. Az élő Railway-telepítés és terhelés nem lett elvégezve ebben a környezetben.

## V17.5 – Hivatalos PostgreSQL-előrehaladás

A napi állapot már nem a `localStorage`-ban él: a hat szerver által ellenőrzött választ a `player_progress` PostgreSQL-tábla tartósan rögzíti. A részletek, az API szerződése, a 002–003 migrációk, a Railway deploy és a teljesítményellenőrzés: **[docs/POSTGRES-PROGRESS-PERFORMANCE.md](docs/POSTGRES-PROGRESS-PERFORMANCE.md)**.

Fontos: a V17.5 frontend csak a V17.5 backenddel együtt működik, és újraindítás előtt futnia kell a migrációnak.


## V17.6 – kihagyott napok

A `GET /api/v1/days/YYYY-MM-DD` lehetővé teszi a már megjelent napi kérdések lekérését; a `progress` GET `day` paramétert kap. Az indulás és a pontozás már a kiválasztott napon működik, a szerver nem enged jövőbeli vagy draft napot, és egy nap első érvényes futása nem játszható újra. Az eredmény az eredeti napi összesítésbe kerül. A V17.6 frontend szükséges hozzá. Nincs új SQL-migráció; a Railway/PG integrációt a kiadáskor külön teszteld.

## V17.7: fontos dátumváltás és adatbázis-migráció

A nyitónap 2026-10-23 (#001). A korábbi V17.6 hét tartalomnapja +1 napot tolódott.
**Kötelező a `004_shift_launch_to_oct23.sql` migráció** egy már használt PostgreSQL esetén.
A migráció a korábbi eredményeket és számlálókat is egy nappal előrébb helyezi, és
a napi tartalomhash-eket az új JSON-okhoz igazítja. Telepítés előtt készíts
adatbázis-mentést és ütemezz karbantartást. A részletek a
`docs/LAUNCH-2026-10-23.md` dokumentumban találhatók.
