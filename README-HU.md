# V23 PRODUCTION – 2026. október 24.

**Aktuális szabályzat:** `content/KERDES-VALASZ-SZABALYZAT.md` (**V23**, a V22 korábbi szabályzat helyett). A 2026-10-25–31 közötti hét nap változatosabb kérdései és teljes, új bankjai bekerültek; a 2026-10-23/24 és 2026-11-01 nap változatlan. A teljes jelenlegi változáslista: `content/reference-rules/AUDIT-V23-2026-10-24-HU.md`. A lenti korábbi V19–V22 útmutatók történeti tájékoztatók, nem a friss kérdéseket sorolják.

---

# CLOSEISH Backend V22 PRODUCTION

**V22 tartalomkiadás, 2026-10-24.** A backend V21 production API- és PostgreSQL-folyamatai változatlanok; a 2026-10-25–2026-11-01 közötti napok felülvizsgált kérdései és a teljes új szerkesztői szabályzat kerültek bele. A frontend külön projekt, ezt a backend ZIP-et kell Railway-re telepíteni.

- **Szabályzat:** `content/KERDES-VALASZ-SZABALYZAT.md`
- **Részletes audit:** `content/reference-rules/AUDIT-V22-2026-10-24-HU.md`
- **Telepítés:** `docs/V22-PRODUCTION-KIADAS-HU.md`
- **Ellenőrzés:** `npm run validate`, `npm test`, `npm run export:questions`

---

# Korábbi V21/ V19 dokumentáció (történeti)

# CLOSEISH Backend V22 PRODUCTION

**V22 tartalomkiadás, 2026-10-24.** A backend V21 production API- és PostgreSQL-folyamatai változatlanok; a 2026-10-25–2026-11-01 közötti napok felülvizsgált kérdései és a teljes új szerkesztői szabályzat kerültek bele. A frontend külön projekt, ezt a backend ZIP-et kell Railway-re telepíteni.

- **Szabályzat:** `content/KERDES-VALASZ-SZABALYZAT.md`
- **Részletes audit:** `content/reference-rules/AUDIT-V22-2026-10-24-HU.md`
- **Telepítés:** `docs/V22-PRODUCTION-KIADAS-HU.md`
- **Ellenőrzés:** `npm run validate`, `npm test`, `npm run export:questions`

---

# Korábbi V21/ V19 dokumentáció (történeti)

# CLOSEISH – production backend V21 tartalomfrissítéssel

A **feltöltött V19 production backendből** készült: a Railway-telepítési modell, PostgreSQL-alapú statisztika és előrehaladás, a Suggest API, a publikus kérdés- és katalógusvégpontok és az egyéb futtatási logika megmaradt. **Nem tartalmaz admin/privát tesztmódot vagy `test.html` oldalt.**

## A tartalom kiadási állapota

- 2026. október 23. – november 1. között 10 nap, mindegyik 6 kérdéssel, `publication_status: scheduled` állapotban.
- A 2026-10-25 és 2026-10-31 közötti napok kérdései/válaszbankjai a V21 szabályzat szerinti felülvizsgálatot tartalmazzák (25 módosított kérdés).
- Október 23., október 24. és november 1. **változatlan**, így a már éles október 24-i napi válaszok nem változnak.
- A `scheduled` **nem teszi előre játszhatóvá** a jövőbeli napokat: a publikus API dátumkapuja továbbra is tiltja azokat.

**A legfrissebb kötelező kérdés–válasz szabályzat:** `content/KERDES-VALASZ-SZABALYZAT.md`. A cserebankok ellenőrzési jegyzőkönyve: `content/reference-rules/AUDIT-V21-2026-10-24-HU.md`. A tételes V21 forráslista: `content/source-snapshots/v21-*.csv`. A régebbi `reference-rules/` dokumentumok történeti források, nem a jelenlegi publikációs állapot leírásai.

## Telepítés Railway-en

A korábbi V19 backend szolgáltatást frissítsd ezzel a teljes projekttel. A korábban beállított production változókat, meglévő PostgreSQL-adatbázist és táblákat tartsd meg. A `NODE_ENV=production` esetén a kód továbbra is PostgreSQL-t követel, és letiltja a `DEV_DATE` előnézetet. Node.js **24 vagy újabb** szükséges (a Dockerfile és `package.json` nem változott).

```bash
npm ci
npm run validate
npm test
npm start
```

**Ehhez a tartalmi frissítéshez nincs új adatbázis-migráció.** Ne töröld a játékosadatokat vagy a már rögzített eredményeket. Nem szükséges admin kulcs és nincs `ADMIN_PREVIEW_KEY` konfiguráció.

## Fájlelhelyezés

- `content/days/`: a 10 teljes napi JSON, beleértve a nulla pontot érő válaszokat.
- `content/KERDES-VALASZ-SZABALYZAT.md`: az új V21 kötelező szerkesztői szabályrendszer.
- `content/README-AI.md`: az új napok készítésének és validálásának technikai menete.
- `content/question-index.json`: frissen generált, 60 kérdést felsoroló áttekintő index.
- `CLOSEISH-kerdescsomag-AI.zip`: frissen regenerált, önálló tartalomcsomag.
- `docs/README-V19-HISTORICAL.md`: a korábbi backend-dokumentáció változatlan, történeti referenciaként.

A külön **V18.4 production frontend** nem változott; a `config.js` továbbra is az éles backend API-originjét használja. A napi válaszbankokat **nem** szabad a frontendhez hozzáadni.

## Validálás

Az `npm run validate` beolvassa és ellenőrzi az összes napot. A `node scripts/export-content.mjs` parancs a napi JSON-okból újraépíti az indexet és a beágyazott kérdéscsomagot. A tesztek között a `tests/content-v21-production.test.mjs` a frissített bankokat, a `tests/content-30-31-complete.test.mjs` a korábban draft napokat ellenőrzi.

A helyi validáció nem helyettesíti az éles Railway/PG smoke testet. Telepítés után ellenőrizd a `/healthz` választ, az aktuális napi hat kérdést, valamint hogy egy jövőbeli nap a publikus API-n nem kérhető le.
