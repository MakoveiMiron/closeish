# CLOSEISH V17.8 – telepítési sorrend

1. **Adatbázismentés:** ha a Railway PostgreSQL már létezik és benne valós statisztika/előrehaladás van, készíts mentést a telepítés előtt. A már lefutott migrációfájlokat nem szabad módosítani.
2. **Backend repo:** a mellékelt ZIP `closeish-main/` mappájának **tartalmát** tedd a backend repo gyökerébe, a már meglévő tartalom frissítésével. A V17-es tartalmat és a `005_question_suggestions.sql` fájlt is vidd át. Az éles `NODE_ENV=production`, `DATABASE_URL`, `SIGNING_SECRET`, `PLAYER_HASH_SECRET` és `ALLOWED_ORIGINS` értékek legyenek rendben.
3. **Migráció:** a `railway.toml` pre-deploy lépése az `npm run migrate` parancsot futtatja. Ellenőrizd, hogy `005_question_suggestions.sql` bekerült a `schema_migrations` táblába. A `/readyz` most a javaslattáblát is ellenőrzi; migráció nélkül éles állapotban nem lesz ready.
4. **Frontend repo:** a `closeish-frontend-main/` mappa tartalmát töltsd fel. A scriptcache-verzió `17.8.0` lett, ezért a korábbi `community.js` helyett a javított töltődik be. Az `apiBase` továbbra is az eredeti külön Railway API-címre mutat.
5. **Éles ellenőrzés:** nyisd meg a Suggest modalt; ne legyen „DOWNLOAD IDEAS”, legyen „SEND IDEA”. Tesztelj egy próbajavaslatot, a Railway admin DB-ben ellenőrizd a beszúrást. GET `/api/v1/suggestions` nem listázhatja ki a korábbi javaslatokat (405).
6. **Tartalom:** a 2026-10-29–31-i napok továbbra is `draft`; élesítésük külön tartalomszerkesztői ellenőrzéshez kötött.

## Tesztkorlát

A 24 Node API-teszt átment a helyi környezetben memóriás javaslattárral; a 4 Node frontend-mock teszt átment. **Éles PostgreSQL-integrációt és valódi böngészős E2E-t nem tudtunk végrehajtani.** A helyi Node 22-es; a telepített projekt Node 24+-et céloz. A projekt `npm ci` telepítéséhez a környezetnek el kell érnie a csomagregisztert.
