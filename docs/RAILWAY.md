> **V17.7, 2026-10-23:** A frissítés előtt készíts PostgreSQL-mentést. A `npm run migrate` az új 004-es migrációt is lefuttatja, amely az eredményeket egy nappal átdátumozza. A régi API írásait erre az időre célszerű leállítani. Lásd `LAUNCH-2026-10-23.md`.

# Railway telepítés – CLOSEISH V17

A backend Node.js 24 + PostgreSQL. A frontend külön statikus oldal. A kérdésbank fájlokban marad a backenden, a befejezett napi eredmények közös adatbázisba kerülnek. A félbehagyott játék és a naptár hiteles állapota a PostgreSQL-ben él; a böngésző csak az UUID-t és a szinkronizálásra váró állapotot őrzi.

## Szolgáltatások

1. Hozz létre PostgreSQL szolgáltatást tartós kötettel, ugyanabban a régióban, mint az API. A meglévő működő adatbázist ne cseréld le. Kapcsold be a szolgáltatás által támogatott mentést, és külön staging környezetben ellenőrizd a visszaállítást.
2. API: repository root legyen a kicsomagolt `CLOSEISH-backend` tartalma. Railway **Root Directory: `/`**, **Config File: `/railway.toml`**. Ha a Git-repóban megmarad a külső `CLOSEISH-backend/` könyvtár, mindkét útvonal elé azt is írd be. A konfigurációs fájl helye a repository gyökeréhez viszonyított.
3. A mellékelt Dockerfile telepíti a `pg` függőséget a lockfile alapján. A Railway pre-deploy parancs `npm run migrate`; a start `node src/server.mjs`. A migráció hibája állítsa meg a telepítést.
4. A backend `0.0.0.0` címen, a Railway által átadott `PORT` porton figyel. Generálj hozzá HTTPS-domaint. A backendhez nem kell írható volume: a JSON az image része, a tartós eredmény a PostgreSQL-ben van.
5. Healthcheck: `/readyz`, 120 másodperc indulási türelem. A `/readyz` a szükséges adatbázistáblákat is ellenőrzi, a `/healthz` csak a futó folyamatot. Railway telepítési healthcheckje nem folyamatos rendelkezésreállás-figyelő; külön külső monitor szükséges.
6. Éles kiindulópont két API-replika azonos régióban, azonos image-dzsel és titkokkal. A kiválasztott csomag erőforrás- és költséghatáraihoz igazítsd; induló mérési keret példányonként 1–2 vCPU / 1 GiB RAM, adatbázisnak 1–2 vCPU / 2 GiB RAM. Ezek tesztelendő keretek, nem lefoglalt vagy garantált kapacitás. A szolgáltatás alvását kapcsold ki, ha a kiszámítható napi kiszolgálás a cél.

## Változók

| Változó | Beállítás |
| --- | --- |
| `NODE_ENV` | `production` |
| `HOST` | `0.0.0.0` |
| `PORT` | A Railway adja; ne írj be külön fix értéket. |
| `DATABASE_URL` | Railway reference a PostgreSQL privát címére, például `${{Postgres.DATABASE_URL}}`; a tényleges szolgáltatásnévvel. |
| `SIGNING_SECRET` | Legalább 32 karakteres, kriptográfiailag véletlen titok; javaslat 32 véletlen bájt hex formában. |
| `PLAYER_HASH_SECRET` | Másik, ugyanilyen erős titok. |
| `ALLOWED_ORIGINS` | A valódi frontend HTTPS-originje, záró `/` és útvonal nélkül. Több esetén vesszővel elválasztva. |
| `GAME_TIMEZONE` | `Europe/Budapest` |
| `PG_POOL_MAX` | Kezdetben `10` minden API-példányon. |
| `TRUST_PROXY` | `railway`, kizárólag közvetlen Railway HTTP-ingress mögött. |
| `RATE_LIMIT_PER_MINUTE` | Kezdetben `600`, kliens-IP-nként, példányonként. |
| `WRITE_RATE_LIMIT_PER_MINUTE` | Alap `120`: pontozás + eredménybeküldés, kliens-IP-nként, példányonként. Egy játék 6+1 írás. |
| `API_KEYS` | Opcionális, vesszővel elválasztott kulcsok (min. 24 karakter; több kulcs = rotáció). Ha be van állítva, minden `/api/` kéréshez `X-API-Key` kell. Böngészős frontendben a kulcs nyilvános: csak a hívó azonosítására és a véletlen/naiv scriptelés kiszűrésére alkalmas, nem titok. Valódi védelemhez azonos origines proxy tegye hozzá a kulcsot szerveroldalon. |

Az adatbázis-kapcsolatot privát hálózaton használd; a publikus TCP proxyt ne nyisd meg csak az API kedvéért. Ha a tényleges végpont TLS-t igényel, ellenőrzött tanúsítvánnyal konfiguráld: `PG_SSL_MODE=verify-full`, szükség esetén `PG_SSL_CA`. Ne kapcsolj be `rejectUnauthorized:false` módot. A connection string SSL-paraméterei és a `PG_SSL_*` változók ne mondjanak egymásnak ellent.

A titkok minden replikán és újratelepítés után azonosak legyenek. A `SIGNING_SECRET` cseréje érvényteleníti a még függő igazolásokat. A `PLAYER_HASH_SECRET` cseréje megváltoztatja az eszközazonosítást, ezért külön migrációs terv nélkül ne rotáld. A titkok, a connection string és a játékosazonosítók ne kerüljenek válaszba, klienskódba vagy naplóba.

Élesben `DEV_DATE` nem engedélyezett. `STATS_MODE=memory` csak kifejezetten helyi tesztre használható; a production indulás ezt elutasítja. Nincs automatikus memóriás visszaesés adatbázishiba esetén.

## Frontend összekötése

A külön frontendcsomag `config.js` fájljában:

```js
window.CLOSEISH_CONFIG={apiBase:'https://A-VALODI-BACKEND-DOMAIN'};
```

Az `ALLOWED_ORIGINS` a frontend címét tartalmazza, nem a backendét. A statikus szolgáltató CSP `connect-src` szabályába is vedd fel az API HTTPS-originjét. A frontendnek nincs buildlépése; a `frontend/` tartalmát kell kiszolgálni. Ebben az önálló backendcsomagban nincs frontend vagy közös Compose-proxy.

Alternatíva az azonos origines `/api/` reverse proxy; ekkor az `apiBase` maradhat üres. A dátumfüggő API-t és a statisztikákat a CDN ne cache-elje. A statikus HTML/config frissítése újratelepítéskor jusson el a böngészőkhöz.

## Adatmodell és számítás

- `schema_migrations`: fájlnév, SHA-256, alkalmazási idő. Advisory lock védi a migrációt; a már alkalmazott SQL módosítását elutasítja. Új változáshoz új sorszámozott SQL kell.
- `daily_results`: nap, szerveroldali HMAC-es eszközazonosító, tartalomverzió, futásazonosító, összpont, befejezés ideje. A `(game_date, player_hash)` elsődleges kulcs miatt egy böngésző egy napra egyszer számít.
- `daily_score_counts`: nap + tartalomverzió + pontos összpont + 32 írási részhalmaz szerinti számláló. A megjelenített eloszlás a részhalmazok összege, **37 külön pontértékkel**: 0, 200, …, 7200. Nincsenek 600 pontos csoportok.

Az első sikeresen tárolt befejezett játék eredménye marad meg. Az újraküldés és újrajátszás nem növeli a számlálót és nem írja át a pontot. A rekord és számláló egyetlen atomikus PostgreSQL-utasításban íródik; az egyik hibája visszagörgeti a másikat is. Több API-replikán ugyanaz az egyedi kulcs védi az eredményeket.

A szerver hat aláírt részpontból adja össze a napi eredményt; kliens által beküldött összpontot nem fogad el. Az igazolások ugyanahhoz az eszközhöz, futáshoz, naphoz és kérdésverzióhoz tartoznak, hat különböző kérdéssel. A kihagyás és az üres időtúllépés is aláírt nulla pontot kap.

**Jobb voltál nála (%) = nálad szigorúan kevesebb pontot szerző többi játékos / az összes többi befejezett játékos × 100.** A saját eredményt kivesszük a nevezőből, a holtverseny nem megelőzés. Példa: pontok 0, 200, 200, 7200; a 200 pontos játékos a másik három közül egynél jobb, azaz 33,3%. Az első játékosnál nincs még százalék. Az átlag és kvartilis az összes befejezett eredményt tartalmazza; a kvartilis nearest-rank módszerű. A görbe csak vizuális simítás, a százalék mindig a pontos számlálókból jön.

A statisztika replikánként 10 másodperces összesítési cache-t használ; saját eredmény beküldése után friss összesítést kér. A nyitott eredményoldal 30 másodpercenként frissít. Emiatt mások új eredménye tipikusan legfeljebb kb. 40 másodpercen belül látszik, sikeres hálózati kérések mellett.

A szerkesztett napi kérdéscsomag új hash-t kap. A különböző változatokat nem keverjük egy eloszlásba. Ha már volt számított eredményed, a diagram annak változatát mutatja.

## Hibák, adatmegőrzés és korlátok

A böngésző tartós beküldési várólistát vezet. Hálózati vagy DB-hiba után újranyitáskor, online eseményre és látható lapnál 30 másodpercenként újrapróbálja. A hat részpont igazolása a kiadásától 72 óráig fogadható el, ezért egy teljesen befejezett játék összesítése másnap is beküldhető. A régi nap félbehagyott kérdését viszont már nem pontozzuk. A befejezett eredmény helyi mentése lejárt igazolás esetén is megmarad.

A régebbi V16-mentésekben nincs aláírás: ezek nem kerülnek visszamenőleg a statisztikába. A mai nap teljes újrajátszása már kaphat érvényes, számítható eredményt, ha az eszközhöz még nincs tárolt napi eredmény.

Ez anonim, böngészőalapú összehasonlítás, nem hitelesített személyek ranglistája. A localStorage törlésével új azonosító keletkezik; nincs belépés vagy több eszköz összevonása. A szerver aláírása nem helyettesít versenybiztos munkamenetet: a kliensoldali időzítő, a nyilvános katalógus és több válasz kipróbálása hozzáértő felhasználó által megkerülhető. A szerver nem tárol nyers válaszszöveget, e-mailt vagy IP-címet az eredménytáblákban.

Az adatbázis automatikus törlés nélkül nő. 150 000 új eredmény/nap évente 54,75 millió sor. Mérd meg a tényleges adat- és indexméretet; állíts tárhelyriasztást, majd egyeztetett megőrzési idő alapján tervezz archiválást vagy particionálást. A JSON-ok és indexek jelenleg mind betöltődnek induláskor: a hét nap memóriája tesztelt, többéves tartalomhoz csak az aktuális/következő nap indexét tartó betöltőre kell továbbfejleszteni.

## Ellenőrzés telepítés után

- Migráció, újraindítás és két replika: nincs duplikált napi eredmény, a teljes számláló egyezik a rekordok számával.
- `/readyz` és `/healthz` 200; a nap, időzóna, tartalomhash helyes. DB-kiesés stagingen: readiness 503, nincs hamis siker a beküldésnél.
- Teljes játék, lapfrissítés, offline eredmény és újraküldés, újrajátszás, két külön böngésző százaléka.
- Valódi frontend-origin engedélyezett, idegen origin tiltott. A CORS nem hitelesítés.
- A Railway `X-Real-IP` kezelését ellenőrizd valós hálózaton, hamis kliens-headerrel is. Az alkalmazás ezt csak `TRUST_PROXY=railway` esetén használja, `X-Forwarded-For` alapján nem bízik meg a kliensben. Más proxyútvonalhoz külön ellenőrzött konfiguráció kell.
- Terhelés: `150-EZER-FELHASZNALO.md`, külön staging DB-vel. Ne szennyezd az éles napi statisztikát tesztjátékosokkal.

## Hivatalos referenciák (ellenőrizve: 2026-10-22)

- https://docs.railway.com/config-as-code
- https://docs.railway.com/config-as-code/reference
- https://docs.railway.com/deployments/pre-deploy-command
- https://docs.railway.com/deployments/healthchecks
- https://docs.railway.com/databases/postgresql
- https://docs.railway.com/networking/public-networking/specs-and-limits
- https://node-postgres.com/features/pooling

### 17.5-es frissítés

A PostgreSQL a játékos-előrehaladás elsődleges tárolója is lett. Kötelező mindhárom SQL-migráció (különösen `002_player_progress.sql` és `003_statistics_player_history_index.sql`) és a közös frontend/backend 17.5 verzió. Az API hidegindulási késleltetése érdekében célszerű kikapcsolni a Railway **Serverless / App Sleeping** módot. A privát Postgres URL, az azonos régió és a folyamatos p95/p99 mérés kiemelten fontos. Teljes útmutató: `docs/POSTGRES-PROGRESS-PERFORMANCE.md`.
