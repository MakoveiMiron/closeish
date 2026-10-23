# CLOSEISH V17 API

JSON, HTTPS élesben. A kérés napját a frontend választja, de a szerver csak a mai vagy korábbi, scheduled állapotú napot engedi. Jövőbeli, draft és **2026-10-23 előtti** napok nem érhetők el. Éles dátumfelülírás nincs. A böngésző eredetét az ALLOWED_ORIGINS ellenőrzi; ez nem felhasználói hitelesítés.

| Metódus, útvonal | Feladat |
| --- | --- |
| `GET /healthz` | Folyamat él, tartalomnapok száma. |
| `GET /readyz` | API és a statisztikatáblák elérhetősége; DB-hibánál 503. |
| `GET /api/v1/today` | Aznapi 6 kérdés, `current_date`, elérhető dátumok, időzóna, revízió. |
| `GET /api/v1/days/YYYY-MM-DD` | Bármely már közzétett nap 6 kérdésének nyilvános adatai, válaszbank nélkül. Future/draft/hiányzó nap: 404. |
| `GET /api/v1/progress?playerId=UUID&day=YYYY-MM-DD&month=YYYY-MM` | A kiválasztott nap részletes szerveres előrehaladása; hónap összefoglaló. A `day` elhagyva az aktuális nap. |
| `POST /api/v1/progress/start` | A kiválasztott közzétett nap következő körének mentése. |
| `GET /api/v1/questions/:id/hints` | `date`, `revision`, `q`; legfeljebb négy névjavaslat, pont nélkül. |
| `POST /api/v1/questions/:id/answer` | Szerveroldali pontozás és aláírt részpont. |
| `GET /api/v1/questions/:id/catalogue` | `date`, `revision`, `q`, `filter`, `offset`, `limit`; limit legfeljebb 120. |
| `POST /api/v1/results` | Hat igazolásból első napi eredmény idempotens eltárolása. |
| `POST /api/v1/statistics` | Napi pontos eloszlás és saját összehasonlítás. |

A `today` nem fogad query paramétert, a `/days/:date` útvonal sem. A `questions/:id` végpontok JSON-ja vagy URL-paraméterei a kiválasztott `date`-et és annak `revision`-jét küldik; a szerver ellenőrzi, hogy a kérdés ID-ja valóban ehhez a naphoz tartozik. `statistics` értéke `postgres`, `memory` (kifejezett helyi teszt) vagy `disabled`. Az ETag újraellenőrzés használható; CDN-cache nincs. A többi válasz `no-store`, így személyes statisztikai összehasonlítás sem kerül közös cache-be.

## Válasz pontozása

```json
{
  "date": "2026-10-23",
  "revision": "A_TODAY_24_HEX_HASH_ERTEKE",
  "playerId": "VELETLEN_UUID_V4",
  "runId": "A_NAPI_FUTAS_UUID_V4_AZONOSITOJA",
  "raw": "a játékos válasza",
  "kind": "answer",
  "automatic": false
}
```

A `kind` lehet `answer`, `skipped`, `timeout`. Az utóbbi kettőnél `raw: ""`, a pont nulla. Azonosító nélkül a régi pontozási kliens továbbra is kaphat pontot, de nem kap statisztikához használható igazolást. A V17 frontend mindkét azonosítót elküldi. Válasz: `{ "result": { ...pontozási mezők, "receipt": "aláírt token" } }`.

A receipt a szerver által kiadott pontot, kérdést, napot, verziót, eszköz-hash-t és futást köti össze. Érvényesség: kiadástól 72 óra. A nyers eszközazonosító nem szerepel benne. A token nem titkosított személyazonosító és nem helyettesít belépést.

## Napi eredmény

```json
{
  "date": "2026-10-23",
  "revision": "A_TODAY_24_HEX_HASH_ERTEKE",
  "playerId": "VELETLEN_UUID_V4",
  "runId": "A_NAPI_FUTAS_UUID_V4_AZONOSITOJA",
  "receipts": ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6"]
}
```

Pontszámot nem kell és nem lehet megadni: a szerver összegez. A hat receipt hat külön kérdéshez, ugyanahhoz a naphoz/verzióhoz/eszközhöz/futáshoz tartozzon. Az első sikeres beszúrás számít. Azonos vagy későbbi újrajátszás beküldése 200-zal a már meglévő hivatalos napi eredményt adja vissza. Ezért hálózati retry biztonságos, még több replikán is.

A teljes napi eredmény egy korábban közzétett napra is összesíthető. A napi részpontozás és a kérdések is elérhetők a korábbi napokra; a hatodik válasz PostgreSQL-mentésekor az adott nap statisztikája frissül. Egy nap hitelesen rögzített első futása változatlanul nem ismételhető meg. Ugyanazon nap szerkesztett verziói külön eloszlásban maradnak.

## Statisztika

Bemenet: `{ "date": "YYYY-MM-DD", "revision": "24 hex karakter", "playerId": "UUID v4" }`. Dátum legfeljebb a szerver mai napja. A `playerId` a JSON body-ban van, nem az URL-ben. Mindkét statisztikai útvonal válasza:

```js
{
  statistics: {
    date, revision, asOf, mode,
    histogram: [{score: 0, count: 0}, /* minden 200 pontos érték */ {score: 7200, count: 0}],
    total, mean, q25, median, q75,
    comparison: null /* vagy {score, others, lower, equal, higher, betterThanPercent} */,
    official: null /* vagy {score, revision, runId, completedAt} */
  }
}
```

A `count`, `total` darabszám; a `mean` lehet tört. Üres eloszlásnál átlag/kvartilis null. A `comparison` csak akkor létezik, ha a játékosnak ehhez a verzióhoz van tárolt napi eredménye. Másik verzióban lévő eredménye az `official` mezőben továbbra is látszik; a frontend ezt a verziót kéri le a diagramhoz. Mások azonosítóit vagy egyéni eredménysorait az API nem adja ki.

`betterThanPercent = 100 * lower / others`, saját eredmény nélkül, szigorúan kisebb ponttal. `others=0` esetén null. A küldés utáni saját lekérés friss, egyéb összesítések legfeljebb 10 másodperces belső cache-ből jöhetnek.

## Hibák és korlátok

Válasz: `{ error: { code, message }, date }`.

- 400: hibás mező, aláírás, futáskeverés, ismételt kérdés, lejárt receipt (`RECEIPT_EXPIRED`), hibás lapozás.
- 403 `ORIGIN_REJECTED`: nem engedélyezett böngésző-origin.
- 404 `DAY_NOT_AVAILABLE`: hiányzó/draft/jövőbeli nap; más 404: nincs ilyen kérdés vagy útvonal; nincs publikus fájlrendszer-hozzáférés.
- 409 `DAY_CHANGED`: a kiválasztott nap tartalomrevíziója változott; a kiválasztott játék újratöltendő.
- 413: normál kérés 4096 bájtnál, eredmény/statisztika 16384 bájtnál nagyobb.
- 415: POST nem application/json.
- 401 `API_KEY_REQUIRED`: be van állítva `API_KEYS`, de a kérés `X-API-Key` fejléce hiányzik vagy hibás. A `/healthz` és `/readyz` kulcs nélkül is elérhető.
- 429 `RATE_LIMIT`: IP-korlát, `Retry-After: 60`. Két szint replikánként: minden `/api/` kérés (`RATE_LIMIT_PER_MINUTE`, alap 600/perc), valamint a `POST .../answer` és `POST /api/v1/results` írások külön (`WRITE_RATE_LIMIT_PER_MINUTE`, alap 120/perc).
- 503 `STATS_NOT_CONFIGURED`: nincs bekötött statisztikatár.
- 503 `STATS_UNAVAILABLE`: eredmény/statisztika DB-művelet nem sikerült; a küldés később ismételhető.
- 503 `DATABASE_UNAVAILABLE`: readiness DB-ellenőrzése hibás.

Hálózati időtúllépés után a kliens nem feltételez sikert vagy végleges kudarcot: eltárolja és újraküldi az azonos eredményt. Egy sikeres DB-commit után elveszett HTTP-válasz sem duplázza az eredményt.
