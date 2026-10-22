# Külön frontend/backend csomag ellenőrzése – V17.1, 2026-10-22

A V17-ből két önálló projekt készült. A napi kérdés-JSON-ok és a pontozás változatlanok. A frontend saját helyi statikus webszervert/API-proxyt kapott, a backend saját teszt- és tartalomexport-parancsokat. A Railway gyökérútvonalak az önálló backend-repositoryhoz igazodnak.

Elvégzett próbák:

- `npm ci` a külön backendben: sikeres, lockfile alapján 14 csomag telepítve.
- `npm test` a külön backendben: mind a 11 API- és statisztikai tesztcsoport sikeres; a frontend fájljaira nincs tesztfüggőség.
- `npm run export:questions` a külön backendben: sikeres, 42 kérdés, önálló AI-tartalom-ZIP. Az export során a teljes tartalomvalidálás is lefutott.
- Valódi Chromium: külön Node-folyamatban indított frontend és backend, a két projekt saját indítófájljával.
- Valós idejű 30 másodperces kör: a kijelzett idő csökkenése alatt **0 időközi HTTP-kérés**; sem timer-polling, sem másodpercenkénti üzenet.
- Offline böngészőben is csökkenő idő, lapfrissítés után változatlan mentett határidő.
- Offline lejáratkor pontosan 1 válasz/időtúllépés-kérés; sikertelenségekor mentett függő beküldés. Online visszatérés után aláírt nulla ponttal lezárás.
- Mind a hat kör befejezése, eredményoldal és egyetlen tárolt napi eredmény a kifejezetten helyi memóriás statisztikatárban.
- Böngészős JavaScript-hiba: 0.

Az opcionális reprodukálható integrációs teszt a frontend `tests/countdown.browser.mjs` fájlja. Playwright és Chromium szükséges hozzá; a BACKEND_DIR környezeti változó mutasson a külön backendmappára. A frontend hétköznapi futtatásához nem kell Playwright vagy npm-telepítés.

A teszt hálózati eseményeket figyelt és tényleges 30 másodperces időt hagyott lejárni. Nem csupán a timer forráskódját ellenőrizte. A backend a kérdéscsomagban egyszer adja át a time_limit_seconds=30 mezőt; a határidő és hátralévő idő kezelése kliensoldali.

Az élő Railway-környezet, a Docker build és a PostgreSQL-es kapacitásmérés ebben a körben nem futott. A V17 SQL-motoros és korábbi böngészőtesztjeinek részletei az ELLENORZES.md fájlban maradtak meg; a backend érdemi adatbázis- és pontozáskódja nem változott.
