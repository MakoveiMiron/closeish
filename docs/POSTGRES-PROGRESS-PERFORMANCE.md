# CLOSEISH V17.5 – PostgreSQL progress & gyorsítás

## Mit tárolunk és hol?

- **PostgreSQL – hiteles:** `player_progress` napi sorai: a játékos azonosítójának csak HMAC-SHA256 hash-e, nap, tartalomrevízió, első `run_id`, a szerver által kiszámolt 0–6 válasz és az aktív kör határideje. Az adat *append-only* logikával kerül mentésre: a korábbi válasz és run nem írható felül. `daily_results` + `daily_score_counts`: végleges pontszámok és darabszámok (a korábbi táblák változatlanok).
- **Böngésző – minimális:** `closeish-player-v1` (UUID v4), `closeish-pending-v1` (csak a folyamatban lévő kör helyi vázlata vagy el nem küldött válasza), `closeish-statistics-v1` (csak a sikertelen aláírt eredménybeküldések), valamint a *SUGGEST* funkció fel nem adott ötletei. Az `allProgress` archívum már nem íródik minden gépeléskor. A régi `closeish-progress-v2` és `closeish-first-completed-v1` csak migrálási célra maradnak, és sikeres migráláskor eltűnnek.
- A napi hat kérdés változatlanul a backend JSON-jéből érkezik; a teljes válaszkatalógus **nem** kerül a kliensre. A 30 másodperces időzítő továbbra is teljesen frontendoldali, nincs másodpercenkénti API-kérés.

### Adatvesztési és migrációs korlátok

A V17-es, kriptográfiailag aláírt, **még érvényes** receiptet tartalmazó régi mentést a frontend egyszer feltöltheti az `/api/v1/progress/import` címre. A szerver ellenőrzi az aláírásokat, az eredeti pontszámot és a kérdésrevíziót. A receipt 72 óra után lejár: az annál régebbi, *kizárólag helyi* részletes mentés önmagában már nem bizonyítható, ezért a frontend **nem törli automatikusan**, amíg migrálás nem sikerült. Korábbi, `daily_results` táblában már hitelesített napok a hónap-lekérdezésben `legacyResult: true` jelzéssel DONE állapotban megmaradnak; teljes válaszrészletek ilyenkor nem feltétlenül állnak rendelkezésre. Egy eltávolított/lost böngészős UUID-t bejelentkezési mechanizmus nélkül nem lehet visszaállítani.

Az anonim UUID **nem fiókhitelesítés**: akinek az UUID-ja megszerezhető, elérheti a hozzá tartozó előzményeket. Éles használatban csak HTTPS legyen, az UUID-t ne írjuk naplóba; a szerver HMAC hash-t tárol, és a szekréteket ne forgassuk migráció nélkül.

## API

`GET /api/v1/progress?playerId=<uuid-v4>&month=2026-10`

Válasz: `{date,month,progress,days,counted,officialScore}`. A `progress` **csak a mai** teljes, szerveres állapot; a `days` a kiválasztott hónap rövid státuszai. Nincs egyben többéves vagy teljes történetlekérdezés. Cache: private no-store. A hónapot a frontend a MY DAYS nézetében igény szerint tölti.

`POST /api/v1/progress/start`

JSON: `{playerId,runId,date,revision,activeRound,activeDeadline}`. Csak ma és az adott revízióra. Létrehozza/naprakészen tartja az aktív kör határidejét; nem indít újra befejezett futást. Gépelés közben *nem* hívjuk. `409 DAY_ALREADY_STARTED` vagy `DAY_ALREADY_COMPLETED` az ütközés.

`POST /api/v1/questions/:id/answer`

A régi válasz-séma + `playerId`/`runId` változatlan. A hitelesített szerverválaszt **ugyanebben a kérésben** tárolja PostgreSQL-ben; az új válasz `{result,progress,counted}`. A korábban tárolt kör megismétlése az eredeti választ adja vissza. A hatodik mentett válasznál a backend a hivatalos napi eredményt is megpróbálja menteni (válaszként `counted: true` ha sikerült). Az el nem fogadott eredményekhez megmarad a receipt-alapú, tartós kliensoldali várólista a `/api/v1/results` végponton.

`POST /api/v1/progress/import`

Egyszeri régi mentésfelvitel. JSON: `{playerId,runId,date,revision,responses}`. Minden részválaszhoz érvényes `receipt` szükséges. Nem képes felülírni már létező napot.

A `/api/v1/today`, `/api/v1/statistics`, `/api/v1/results`, `GET /api/v1/questions/:id/hints|catalogue` szerződés megmarad.

## Bevezetés Railwayen

1. Az API és a PostgreSQL ugyanabban a Railway projektkörnyezetben és lehetőleg ugyanabban a régióban fusson. Az API `DATABASE_URL` értéke a **privát** PostgreSQL kapcsolati URL legyen (a Postgres szolgáltatásra hivatkozó változó).
2. **Mielőtt az új API elindul, futtasd:** `npm run migrate` (Railway `preDeployCommand` már be van állítva). A három verziózott migrációt sorban alkalmazza, a korábbi statisztikai adatokat nem törli. A `/readyz` ellenőrzi az új `player_progress` táblát is.
3. A korábbi `SIGNING_SECRET` és `PLAYER_HASH_SECRET` változókat változatlanul tartsd meg! Ha megváltoztatod, a régi UUID-k más hash-t kapnak és a korábbi receipt-ek nem lesznek ellenőrizhetők.
4. Az API és a frontend verzióját **együtt** telepítsd (17.5), mert a frontend induláskor már hívja a progress végpontot. A frontenden a `config.js` API címe és a backend `ALLOWED_ORIGINS` egyezzen a végleges webcímmel.
5. Erős javaslat: Railway API **Serverless / App Sleeping: OFF**, mert a nagy napi válaszkészletek hidegindításkor további késleltetést jelenthetnek.
6. Kövesd a DB CPU/IO/kapcsolatszám és az API p95/p99 késleltetést. A 150 000 játékos/nap *kapacitáscél*, nem bizonyított teljesítménygarancia; évente körülbelül 54,75 millió `player_progress` sor keletkezhet. Tervezd meg a tárhelyet, backupot és szükség szerint havi particionálást.

## Mit optimalizáltunk?

- **Lusta napi betöltés:** a szerver nem parse-olja/kompilálja egyszerre az összes (köztük ~52 MB-os) napi JSON-t. Csak a szükséges napot tölti, legfeljebb két napot tart gyorsítótárban. A `npm run validate` továbbra is az összes napot ellenőrzi telepítés előtt.
- **Válasz-mentés egyetlen roundtripben:** a frontend válaszbeküldésekor egyben elkészül a tartós `player_progress` mentés; a kliens nem küld külön DB-szinkron hívást válaszonként.
- **Külön napi archívum:** csak a megnyitott hónapot kérdezzük le, nem a felhasználó minden eddigi napját.
- **HTTP gyorsítótár:** a mai nyilvános (nem személyes) kihívás `ETag`-et kap; a böngésző saját HTTP cache-ével revalidálunk, nem másoljuk `localStorage`-ba.
- **Kevesebb polling:** a napi váltás ellenőrzése ötpercenként és tab-visszaváltáskor, a befejezett statisztikáké kétpercenként történik. Nincs időzítő-tick az API felé.
- **`Server-Timing` fejléc:** `app;dur=<ms>` – segít elválasztani a szerveren belüli feldolgozást a hálózati/Railway késleltetéstől. A frontend szükséges öt JS-fájlja párhuzamosan töltődik és `preload` linket kap.

## Diagnosztika és tesztek

```bash
npm ci
npm run migrate            # PostgreSQL DATABASE_URL szükséges
npm run validate
npm test                   # HTTP és memóriás regressziós tesztek
npm run test:postgres      # TEST_DATABASE_URL vagy PGLITE_MODULE szükséges
npm run latency -- https://closeish-production.up.railway.app <UUID-v4>
```

A latency script 8 egymás utáni `today` és opcionálisan `progress` kérést mér; az első és a felmelegedett válaszidők eltérése különösen informatív. Ne közzétegyél valódi UUID-t. A `Server-Timing` csak a szerver saját feldolgozását méri, nem tartalmazza a böngésző–szerver hálózati utat.

Felhívás: az SQL/PostgreSQL-integrációt éles/teszt PostgreSQL mellett is tesztelni kell a migráció utáni rollout előtt. A helyi Node HTTP-tesztek nem helyettesítik ezt és nem igazolják a 150 ezer napi felhasználós célterhelést.
