**V17.7 kritikus telepítési követelmény:** A CLOSEISH első napja **2026-10-23**, az első kihívás #001. A korábbi V17.6 hét tartalomnapja +1 napot tolódott, és a metrikus kérdésre is módosítás történt. A `migrations/004_shift_launch_to_oct23.sql` egyszeri, **kötelező** adatmigrációja átrendezi az eredmények dátumát és a tartalomrevíziókat. Telepítés ELŐTT készíts adatbázis-mentést; kerüld a régi API egyidejű írásait a migráció alatt. Előbb az új backendet és az összes 001–004 migrációt, majd a V17.7 frontendet telepítsd. Olvasd el: `docs/LAUNCH-2026-10-23.md`. Ne hagyd ki a migrációt és ne hozz létre új adatbázist a réginek a helyére.

# Ezt add át a Railway agentnek a CLOSEISH V17 projekttel együtt

A mellékelt önálló CLOSEISH-backend (V17.7) projektet állítsd működő Railway-telepítésre PostgreSQL-lel. Hajtsd végre a beállítást, ne csak javaslatot adj. Először nézd meg a repót és az aktuális Railway-projektet; a meglévő működő erőforrásokat használd újra, ne hozz létre indokolatlan másolatokat. Olvasd el a README-HU.md, docs/RAILWAY.md, docs/API.md és docs/150-EZER-FELHASZNALO.md fájlokat. A frontend megjelenését és a kérdések/pontozás szabályait tartsd meg.

A cél külön statikus frontend és Railway backend. A napi kérdés- és válaszbank a content/days/YYYY-MM-DD.json fájlokban marad; ezeket ne migráld adatbázisba és ne tedd publikus statikus mappába. A frontend csak a kiválasztott, már közzétett nap nyilvános kérdéscsomagját kéri le. Az aktuális és korábbi játszható napok hiteles eredményei, válaszai és állapota PostgreSQL-ben maradnak; localStorage-ban az eszköz UUID-ja és az átmenetileg még nem szinkronizált műveletek vannak. A valódi napi eredményeloszlás és összehasonlítás közös PostgreSQL-adatokból készül, fiktív vagy seedelt játékosok nélkül.

## 1. Railway szolgáltatások és futtatás

- Használd a Node.js 24-es Dockerfile fájlt. A build npm ci --omit=dev paranccsal a mellékelt package-lock.json alapján telepít.
- Ha a repo gyökere a CLOSEISH-backend mappa tartalma: Root Directory /, Config File /railway.toml. Ha a repo tartalmaz külső CLOSEISH-backend/ mappát is, az útvonalakat a tényleges repository-gyökérhez igazítsd. Ellenőrizd, hogy a Railway tényleg beolvasta a konfigurációt.
- Pre-deploy command: npm run migrate. Start command: node src/server.mjs. A migráció hibája blokkolja a telepítést; alkalmazott SQL-t ne módosíts, új módosításhoz új migrációt készíts.
- 0.0.0.0-n a Railway PORT változóján figyeljen. Ne kényszeríts külön fix publikus portot.
- Healthcheck /readyz, 120 másodperc indulási türelem. /healthz a folyamat, /readyz az adatbázistáblák elérhetőségét is ellenőrzi.
- Hozz létre vagy kösd be a PostgreSQL szolgáltatást tartós kötettel, az API-val egy régióban. Az API a privát DATABASE_URL-t használja; szükségtelen publikus DB-hozzáférést ne nyiss.
- Az API-hoz ne csatolj adatmentési volume-ot, és ne írj JSON-fájlba eredményeket. Két API-replika ugyanazt a DB-t használja.
- Éles kiindulópont két API-replika, példányonként mérésre 1–2 vCPU / 1 GiB RAM; DB-hez 1–2 vCPU / 2 GiB RAM mérési keret. A projekt/csomag tényleges korlátait és költségkeretét ellenőrizd. A mérés alapján állítsd be a szükséges kereteket, ne ígérj méréstől független kapacitást. Kiszámítható induláshoz kapcsold ki a szolgáltatás alvását.

## 2. Kötelező környezeti változók

NODE_ENV=production
HOST=0.0.0.0
GAME_TIMEZONE=Europe/Budapest
PG_POOL_MAX=10
TRUST_PROXY=railway
RATE_LIMIT_PER_MINUTE=600

DATABASE_URL: Railway reference a tényleges Postgres szolgáltatás privát URL-jére, például ${{Postgres.DATABASE_URL}}.
ALLOWED_ORIGINS: a tényleges frontend HTTPS-originje, útvonal és záró perjel nélkül; több origin esetén vesszővel elválasztva.
SIGNING_SECRET és PLAYER_HASH_SECRET: két KÜLÖN, kriptográfiailag generált, legalább 32 karakteres titok; javasolt 32 véletlen bájt hex kódolással. Ha már megfelelően be vannak állítva, tartsd meg őket. Minden replikán ugyanazokat használd, újratelepítéskor ne generáld újra. Ne írd ki a titkokat vagy a DB connection stringet a jelentésbe/logba, ne commitold és ne juttasd a frontendbe.

DEV_DATE ne legyen élesben. STATS_MODE=memory ne legyen élesben. DB-hiba esetén ne válts SQLite-ra, JSON-ra vagy memóriára. Ha a DB-végpont TLS-t igényel, ellenőrzött tanúsítvánnyal állítsd be; ne használj rejectUnauthorized:false beállítást. A PostgreSQL kapcsolatkeretet számold ki: replika × PG_POOL_MAX, plusz migráció, staging és admin tartalék.

## 3. Frontend

Találd meg a projektből vagy a meglévő telepítésből a frontend címét. Ha ez nem derül ki, ezt az egy hiányzó adatot kérdezd meg. A a külön frontend config.js apiBase mezőjébe az API tényleges HTTPS-originje kerüljön, az ALLOWED_ORIGINS-be a frontendé. A frontend külön ZIP-ben/repóban van. A frontend statikus fájljaihoz nincs buildlépés. A 30 másodperces visszaszámláló kizárólag a böngészőben fusson; ne vezess be másodpercenkénti timer API-t, WebSocket-üzenetet vagy szerveres tick-küldést. A határidő helyben mentődik és frissítéskor nem indul újra. Ha már azonos origines /api/ proxy működik, azt tartsd meg, apiBase maradjon üres.

A statikus tárhely CSP connect-src szabálya engedje az API-t. Az /api/ és a napi statisztika ne kapjon CDN-cache-t. A helyi Compose Nginx-konfigurációját ne alkalmazd változtatás nélkül a külön Railway-domainre.

## 4. Adatbázis és statisztika – a meglévő megvalósítást használd

Futtasd a migrations/001_daily_statistics.sql migrációt a mellékelt migrációs programon keresztül. Ellenőrizd a schema_migrations, daily_results, daily_score_counts táblákat, kulcsokat, check constraint-eket és indexeket.

- Egy böngésző naponta az első sikeresen eltárolt BEFEJEZETT eredményével számít. Kulcs: game_date + player_hash. A player_hash a nyers böngésző-UUID szerveroldali HMAC-je.
- Az újraküldés és az újrajátszás ne növelje a létszámot és ne javítsa fel a számított napi pontot.
- A hat kérdés pontja szerveroldalon számolódik, HMAC-aláírt igazolásokkal. A végső beküldésnél hat különböző kérdés, azonos eszköz, futás, nap és tartalomverzió kell. Ne fogadj el kliens által diktált összpontot. A kihagyás/időtúllépés is aláírt nulla pont.
- A napi eredmény és a hozzá tartozó számláló atomikusan íródjon. A meglévő CTE + ON CONFLICT és 32 írási részhalmaz ezt kezeli; ne cseréld versenyhelyzetes read-then-write megoldásra.
- Ponteloszlás: 37 PONTOS érték, 0, 200, …, 7200. Ne csoportosítsd 600 vagy 1000 pontos sávokba. A görbe vizuális simítása megmaradhat, de a számítás az eredeti darabszámokból jöjjön.
- „Hány százaléknál voltam jobb”: a nálam SZIGORÚAN kevesebb pontot elérő többi játékos / összes többi befejezett játékos × 100. Saját eredmény a nevezőből kizárva, holtverseny nem megelőzés. Nulla másik játékosnál nincs százalék.
- Átlag/medián/kvartilis valós adatokból; külön tartalomverziók külön csoportok. A módosított napi tartalmat ne keverd a korábbi változattal.
- A 10 másodperces összesítési cache és a 30 másodperces böngészős frissítés maradhat. Az eredménybeküldés után friss lekérés kell.
- A böngésző tartós várólistája hálózati hiba után újraküld. Az aláírt, teljes napi eredmény 72 óráig összesíthető, régi kérdést viszont másnap már nem pontozunk.
- Régi, aláírás nélküli mentést ne tölts be hiteles eredményként. Memóriás/szintetikus tesztadatot ne másolj éles DB-be.

Ez böngészőalapú, nem hitelesített személyazonosságú rangsorolás. Ne állítsd csalásbiztosnak: a helyi tárolás törölhető, a kliensoldali időzítő és a katalógus technikailag megkerülhető. Ne vezess be új login-rendszert vagy új játékszabályt ebben a telepítési feladatban.

## 5. Próbák és terhelés

Először külön staging környezetet és külön adatbázist használj. A produkciós mód ott is maradjon production. Ha az aktuális naphoz nincs tartalom, jelenjen meg a korrekt „nincs napi játék” állapot. A mellékelt JSON-ok 2026-10-20–26-ra szólnak: ne írd át titokban a dátumokat, ne oldd fel az éles dátumtiltást. Terhelési játékhoz a tulajdonos által jóváhagyott aktuális napi tartalom szükséges; ennek hiányát jelezd.

Futtasd a projekt gyökerében: npm ci, npm run validate, npm test. Elkülönített, eldobható PostgreSQL-en TEST_DATABASE_URL változóval futtasd az npm run test:postgres parancsot. A teszt DDL-t és tesztadat-törlést is végez, ezért SOHA ne kapjon éles adatbázist.

Ellenőrizd két replikán a párhuzamos azonos eredménybeküldést, újrajátszást, hibás aláírást, másik eszköz igazolását, nulla/egy/több játékost, holtversenyt és eltérő tartalomverziókat. DB-kiesésnél a /readyz legyen 503, a felület várakoztassa az eredményt; helyreálláskor csak egyszer számolja be. Ellenőrizd a mentett játék folytatását, offline/online váltást, frissítést, mobilnézetet és a budapesti napváltást.

A napi cél 150 000 felhasználó. Kiinduló staging terhelés:

k6 run -e BASE_URL=https://VALODI-STAGING-DOMAIN -e CONFIRM_STAGING=yes -e RATE=1200 -e COMPLETIONS_PER_SECOND=20 -e DURATION=10m tests/production.k6.js

Ez 1200 vegyes olvasási kérés/másodperc MELLÉ másodpercenként 20 teljes hatválaszos eredményt is beküld, több mint 1340 összes kérés/másodperc tervezett terheléssel. Először kisebb terhelésen ellenőrizd a működést, majd futtasd a célterhelést és egy 30–60 perces tartós szakaszt. A teszt mesterséges eredményei kizárólag a staging DB-be kerüljenek. Egy generátor IP-je limiterbe ütközhet: ellenőrzött staging kivételt vagy több generátor-IP-t használj, az éles védelmet ne kapcsold ki.

Cél: hiba <0,1%, p95 <300 ms, p99 <1000 ms, kihagyott iteráció 0; rögzítsd a CPU/RAM, DB-kapcsolat, lock-wait és tárhelyméréseket is. Ellenőrizd SQL-lel, hogy a napi számlálók összege egyezik a daily_results valódi darabszámával. Ha valamelyik cél nem teljesül, a mérés alapján javítsd a konfigurációt/kódot. Terhelési mérés nélkül ne nyilvánítsd igazoltnak a 150 ezres napi kapacitást.

## 6. Üzemeltetés és átadás

Állíts mentést, tárhely- és hibariasztást, külső /readyz monitorozást. A Railway telepítési healthcheck önmagában nem folyamatos monitor. Vizsgáld meg a X-Real-IP viselkedését hamis kliens-headerrel is; a TRUST_PROXY=railway kizárólag a megfelelő ingress mögött legyen aktív. Több replika esetén az alkalmazás limiterje nem globális; szükség szerint megbízható edge/WAF adjon közös védelmet.

Napi 150 ezer eredmény évente 54,75 millió sor. Mérd a sorok/indexek tényleges tárhelyét, javasolj konkrét megőrzési és későbbi archiválási tervet; jóváhagyás nélkül ne törölj korábbi eredményeket. A hét nap JSON-ja jelenleg induláskor mind memóriába kerül; a tartalom jelentős bővülése előtt tervezd meg az aktuális/következő napi indexre korlátozott betöltést.

A végén magyarul add át: backend HTTPS-URL, frontend kapcsolata, szolgáltatások és régió, replika/erőforrás-beállítás, migráció és tesztek eredménye, mért terhelés és korlátai, backup/restore státusz, valamint az új napi JSON telepítésének lépései. Titkos értékeket ne írj ki. Ami nem lett ténylegesen végrehajtva vagy megmérve, azt nevezd meg egyértelműen.

## V17.5 KIEGÉSZÍTÉS – kötelező, ez felülírja a régebbi csak-statisztika tervet

A **PostgreSQL most már a játékosok részletes előrehaladásának is a hiteles forrása**. A `migrations/002_player_progress.sql` és a `003_statistics_player_history_index.sql` migrációk kötelezőek az API indítása előtt; a korábbi `001_daily_statistics.sql` adatait meg kell őrizni. Az API `/api/v1/progress`, `/api/v1/progress/start` és `/api/v1/progress/import` végpontokat biztosít. Minden kör pontozott válasza a szerveren mentődik; a 6. kör hivatalos napi eredményt is rögzít. V17.5 frontendet csak az új API-val telepíts. A két szolgáltatás ugyanabban a régióban/környezetben legyen; DATABASE_URL a PostgreSQL privát elérési útjára mutasson. A Railway Serverless / App Sleeping legyen kikapcsolva az API-n a hidegindítás csökkentésére, ha a költségkeret engedi. Végezz DB-migrációt, readiness checket, szerveres/perf/rollback ellenőrzést, és őrizd meg a meglévő SIGNING_SECRET és PLAYER_HASH_SECRET változókat. Részletek: `docs/POSTGRES-PROGRESS-PERFORMANCE.md`.


## V17.6 kiegészítés – korábban közzétett napok

A jelenlegi kód `/api/v1/days/YYYY-MM-DD` útvonalon már közzétett múltbeli napokat is kiszolgál, és a `/api/v1/progress?day=YYYY-MM-DD` a megfelelő dátum állapotát adja vissza. A `/progress/start`, `/questions/:id/hints`, `/questions/:id/answer`, `/questions/:id/catalogue` a kiválasztott nap kérdésazonosítóját és revízióját vizsgálja, de **nem kötelező ma** legyen. Csak `scheduled` státuszú és nem jövőbeli nap engedélyezett; jövő/draft 404. Egy játékos/nap első hiteles futása marad érvényben, nincs újrajátszás. A nap másik napon történt teljesítése **az eredeti napi** `daily_results` és `daily_score_counts` statisztikáját gyarapítja, nem az aktuális napét. A frontend V17.6 ezzel együtt telepítendő. Futtasd `npm test` (beleértve az `archive-play` regressziót), majd az éles adatbázis integrációs és load teszteket is. Ne írj felül/állíts vissza semmilyen adatbázist, és tartsd meg az existing `SIGNING_SECRET`, `PLAYER_HASH_SECRET` változókat. Nincs új migráció.
