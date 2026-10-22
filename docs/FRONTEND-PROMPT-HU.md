# Prompt a frontendhez – CLOSEISH V17 backend-szerződés

Ezt add át a frontenden dolgozó agentnek/fejlesztőnek. A frontend meglévő megjelenését és a játékszabályokat ne változtasd; ez a dokumentum azt írja le, mit vár a backend, hova és hogyan.

---

A CLOSEISH frontend egy build nélküli statikus oldal a `https://closeish.eu` címen. A backend külön Railway-szolgáltatás:

- **API-origin:** `https://closeish-production.up.railway.app`
- **Formátum:** JSON, UTF-8. Minden POST-hoz `Content-Type: application/json` kell, különben 415.
- **CORS:** csak a `https://closeish.eu` origin engedélyezett (záró `/` nélkül). Más origin 403 `ORIGIN_REJECTED`. Helyi fejlesztéshez a `http://localhost:5173` csak akkor működik, ha a backend `ALLOWED_ORIGINS` változójába is felvették.
- **Nincs süti, nincs login.** `credentials` ne legyen `include`.

## 1. Konfiguráció

`config.js`:

```js
window.CLOSEISH_CONFIG = {
  apiBase: 'https://closeish-production.up.railway.app',
  apiKey: ''            // csak ha a backenden API_KEYS be van állítva
};
```

- Ha azonos origines `/api/` proxy működik a `closeish.eu` alatt, az `apiBase` maradjon üres, és a relatív `/api/...` útvonalakat használd.
- **API-kulcs:** ha az `apiKey` nem üres, minden `/api/` kérés `X-API-Key: <apiKey>` fejlécet kapjon. Ha üres, a fejléc ne kerüljön a kérésbe. Ez a kulcs a böngészőben látható, ezért nem titok. Ne kezeld biztonsági garanciaként, és ne tegyél a frontendbe más titkot (pl. `SIGNING_SECRET`, adatbázis-URL).
- **CSP:** `connect-src 'self' https://closeish-production.up.railway.app`.
- Az `/api/` válaszokat a CDN/statikus tárhely ne cache-elje. A `config.js` és az `index.html` frissítése jusson el a böngészőkhöz (rövid cache vagy verziózott URL).

Közös fetch-segéd javaslat:

```js
const cfg = window.CLOSEISH_CONFIG || {};
async function api(path, body) {
  const headers = {};
  if (cfg.apiKey) headers['X-API-Key'] = cfg.apiKey;
  if (body !== undefined) headers['Content-Type'] = 'application/json';
  const res = await fetch((cfg.apiBase || '') + path, {
    method: body === undefined ? 'GET' : 'POST',
    headers, body: body === undefined ? undefined : JSON.stringify(body),
  });
  const data = res.status === 304 ? null : await res.json().catch(() => null);
  return { status: res.status, data, headers: res.headers };
}
```

## 2. Helyi azonosítók (localStorage)

- `playerId`: egyszer generált `crypto.randomUUID()` (UUID v4), tartósan localStorage-ban. Ez az eszközazonosító. A szerver csak HMAC-elt formában tárolja.
- `runId`: minden új napi játékfutásnál új UUID v4. Egy futás hat válasza és a végső beküldés **ugyanazt** a `runId`-t használja.
- A félbehagyott játék, a korábbi napok állapota, a kapott `receipt`-ek és a beküldési várólista localStorage-ban marad.
- Régi, aláírás nélküli (V16) mentést ne küldj be hiteles eredményként.

## 3. Végpontok

### `GET /api/v1/today`
Query paramétert nem fogad (ha van, 400 jön). ETag-et ad: a következő lekérésnél `If-None-Match` mehet, ilyenkor 304 jön, és a helyi példány marad érvényes.

```js
{
  date: "2026-10-22",            // Europe/Budapest szerinti mai nap
  timezone: "Europe/Budapest",
  available: true,                // false => "Ma nincs napi játék" állapot
  day_number: 3,
  revision: "fb3029da186b169c678ebe8b", // 24 hex; minden további kérésben vissza kell küldeni
  legacy_progress_key: "...",
  start_date: "2026-10-20",
  published_dates: ["2026-10-20", "2026-10-21", "2026-10-22"],
  questions: { q1: {...}, q2: {...}, ..., q6: {...} },  // available=false esetén {}
  preview: false,
  statistics: "postgres"          // "disabled" => statisztika UI rejtve/üzenet
}
```

Egy kérdés (`questions.qN`): `id`, `date`, `day_number`, `topic`, `prompt`, `metric`, `unit`, `limit`, `direction` (`"below"`/`"above"`), `time_limit_seconds` (30), `score_bands[] {max_gap_inclusive, points, tier}`, `scoring_window {max_scoring_distance, units, outside_window_points, wrong_side_points, exact_match_points}`, `input_max_length`, `source`, `content_revision`, `answer_count`, `candidate_count`. Válaszlistát nem tartalmaz.

Ha `available === false`, mutasd a „ma nincs napi játék” állapotot. A dátumot ne írd át, és ne kérj le másik napot.

### `GET /api/v1/questions/:id/hints?date=&revision=&q=`
Gépelés közbeni javaslat, debounce-szal (≥250 ms). 4 karakter alatt csak pontos egyezést ad. Válasz: `{ candidates: [{ ent: {canonical}, isAlias, match: "exact"|"prefix", dist }] }`, legfeljebb 4 elem, pont nélkül.

### `POST /api/v1/questions/:id/answer`
```json
{ "date": "...", "revision": "...", "playerId": "UUID", "runId": "UUID",
  "raw": "a játékos szövege", "kind": "answer", "automatic": false }
```
- `kind`: `answer` | `skipped` | `timeout`. Kihagyásnál és időtúllépésnél `raw: ""`. A szerver ezekre is aláírt 0 pontot ad.
- `automatic: true`, ha a lejáratkor a beírt szöveget automatikusan küldöd be.
- Üres `answer` esetén 400 `EMPTY_ANSWER` jön. A `raw` hossza legfeljebb `input_max_length`.
- Válasz: `{ result: { raw, canonical, points, tier, kind, metric_value, autoLocked, aliasUsed?, reason?, receipt } }`. A `kind` lehet `scored`, `unlisted`, `invalid`, `unverified`, `skipped` vagy `timeout`.
- **A `receipt`-et kérdésenként mentsd el.** A végső beküldéshez mind a hat kell. A pontot a szerver adja: a kliens ne számoljon és ne küldjön be összpontot.

### `GET /api/v1/questions/:id/catalogue?date=&revision=&q=&filter=&offset=&limit=`
A válasz utáni „lehetséges válaszok” lista. `limit` legfeljebb 120, `filter`: `all`, `other` vagy egy pontérték (`0`, `200`, …, `1200`). Válasz: `{ total, offset, limit, entries: [{ canonical, metric_value, points, membership_status? }] }`. Csak a kérdés megválaszolása után kérd le.

### `POST /api/v1/results`
A hatodik kérdés után:
```json
{ "date": "...", "revision": "...", "playerId": "UUID", "runId": "UUID",
  "receipts": ["r1","r2","r3","r4","r5","r6"] }
```
- Pontszámot ne küldj. A szerver hat **különböző** kérdés igazolásából összegez.
- Idempotens: az első sikeresen tárolt eredmény számít. Újraküldésre vagy újrajátszásra 200 jön a meglévő hivatalos eredménnyel. A hálózati retry ezért biztonságos.
- Válasz: `{ statistics: {...} }`, ugyanolyan szerkezetű, mint lent.

### `POST /api/v1/statistics`
```json
{ "date": "...", "revision": "...", "playerId": "UUID" }
```
Válasz:
```js
{ statistics: {
  date, revision, asOf, mode,
  histogram: [{score:0,count}, {score:200,count}, ..., {score:7200,count}], // 37 pontos érték
  total, mean, q25, median, q75,          // üresnél null
  comparison: null | {score, others, lower, equal, higher, betterThanPercent}, // others=0 -> betterThanPercent=null
  official: null | {score, revision, runId, completedAt}
}}
```
- „Jobb voltál X%-nál” = `betterThanPercent`. Ha `null`, ne mutass százalékot (még nincs más játékos). A kliens ne számolja újra.
- Ha `official.revision` eltér az aktuálistól, a diagramhoz annak a verziónak a statisztikáját kérd le.
- A görbe vizuálisan simítható, a számok viszont mindig a `histogram` darabszámaiból jönnek. Ne csoportosítsd 600/1000 pontos sávokba.
- Nyitott eredményoldalon látható lap esetén 30 másodpercenként frissíts. Beküldés után azonnal kérj friss adatot.

### `GET /healthz`, `GET /readyz`
Monitorozásra valók, a frontendnek nem kell hívnia őket.

## 4. Időzítő

A 30 másodperces visszaszámláló **csak a böngészőben** fut. Nincs timer API, WebSocket vagy szerveres tick. A kérdés határidejét (abszolút időpont) mentsd localStorage-ba, így frissítéskor nem indul újra. Lejáratkor `kind: "timeout"` vagy a beírt szöveg `automatic: true`-val megy be.

## 5. Hibakezelés

Hibaválasz: `{ error: { code, message }, date }`.

| Státusz / kód | Teendő |
| --- | --- |
| 400 `INVALID_RESULT`, `RECEIPT_EXPIRED`, `INVALID_REQUEST`, `EMPTY_ANSWER`, `INPUT` | Ne próbáld újra ugyanazzal. Lejárt receiptnél a helyi eredmény megmarad, de nem számít bele a statisztikába. |
| 401 `API_KEY_REQUIRED` | Hibás vagy hiányzó `apiKey` a config.js-ben. Konfigurációs hiba, jelezd a konzolban. |
| 403 `ORIGIN_REJECTED` | Rossz origin vagy rossz `ALLOWED_ORIGINS` a backenden. |
| 404 `NO_DAILY_GAME`, `QUESTION_NOT_TODAY` | „Ma nincs napi játék” vagy napváltás: töltsd újra a `today`-t. |
| 409 `DAY_CHANGED` | Napváltás vagy tartalomfrissítés történt: töltsd újra a `today`-t, és kezdj új futást. |
| 413 / 415 | Kliens-hiba: túl nagy body vagy hiányzó JSON content-type. |
| 429 `RATE_LIMIT` | Várj a `Retry-After` (másodperc) szerint. Ne indíts gyors ciklusú újrapróbát. |
| 503 `STATS_UNAVAILABLE` / hálózati hiba / timeout | Eredménynél tedd a tartós várólistába, és küldd újra. Ne feltételezz se sikert, se végleges kudarcot. |

**Beküldési várólista:** a localStorage-ban tárolt, teljes `results` body-t újraküldöd oldalbetöltéskor, `online` eseménynél és látható lapnál 30 másodpercenként, a `Retry-After`-t betartva. Siker (200) vagy végleges 400 után töröld a sorból. A teljes, aláírt eredmény a receipt kiadásától 72 óráig küldhető be. Régi nap kérdését viszont már nem lehet pontoztatni.

## 6. Korlátok, amelyekre a UI-nak számítania kell

- **Rate limit** replikánként és kliens-IP-nként: minden `/api/` kérésre 600/perc, a pontozás és az eredménybeküldés együtt 120/perc. Egy normál játék kb. 6 pontozás + 1 beküldés, plusz a hints-kérések. A hints-et debounce-old, és ne kérd újra ugyanarra a szövegre.
- Body-korlát: 4 KB normál kérésnél, 16 KB eredménynél és statisztikánál.
- Mások eredménysorait az API nem adja ki, csak összesítést.
- Ez anonim, böngészőalapú összehasonlítás, nem csalásbiztos ranglista. A UI ne állítsa az ellenkezőjét.
