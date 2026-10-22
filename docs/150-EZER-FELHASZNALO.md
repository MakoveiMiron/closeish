# Napi 150 000 felhasználó – Railway + PostgreSQL

A 150 000 napi felhasználó kapacitási cél, nem 150 000 egyidejű kapcsolat. A kód több API-replikára és közös PostgreSQL-re készült. A végleges kapacitást a konkrét Railway-erőforrásokon mért terhelés igazolhatja; ilyen mérést ez a csomag nem állít megtörténtnek.

## Kiinduló modell

| Forgalom | Napi mennyiség 150 000 főnél |
| --- | ---: |
| Napi kérdéscsomag betöltése | 150 000 |
| Hat pontozási kérés | 900 000 |
| Feltételezett 60 gépelési javaslat/fő | 9 000 000 |
| Két katalóguskérés/fő | 300 000 |
| Egy kész eredmény beküldése | 150 000 |
| Két statisztikalekérés/fő | 300 000 |
| Összesen | 10 800 000 |

Ez 125 HTTP-kérés/másodperc napi átlag, tízszeres csúcsra kb. 1250/s. A DB-be naponta legfeljebb 150 000 új napi eredmény kerül a feltételezés szerinti 150 000 külön böngészőből: átlag 1,74 befejezés/s, tízszeres csúcs kb. 17,4/s. A 30 másodperces nyitott eredményoldal-frissítés, percenkénti dátumellenőrzés, újrajátszás és visszatérés növeli a forgalmat. Ezek becslések, nem mért viselkedés.

A gépelési javaslat és pontozás nem ír DB-t. Csak a kész napi eredmény íródik, a személyes statisztika pedig indexelt eszköz/nap lekérdezést használ. Az összesítés 37 pontos pontérték 32 írási részhalmazának számlálóiból jön, nem a teljes játékostábla újraszámolásából. Az eredmény és számláló egy SQL-utasításban atomikus, a retry elsődleges kulccsal idempotens. Az összesítési cache 10 másodperces, replikánként korlátos.

## Railway kiindulópont

Két API-replika, azonos régió, image, titkok és DB. Tesztelendő keret példányonként 1–2 vCPU/1 GiB RAM, PostgreSQL 1–2 vCPU/2 GiB RAM. Nem szükséges Redis vagy felhasználónként szerveres session ehhez a megvalósításhoz. A frontend statikus tárhely/CDN-re tehető.

`PG_POOL_MAX=10` két API-n legfeljebb 20 API-kapcsolat; a DB limitjében hagyj tartalékot migrációra és adminisztrációra. Az API adatmentéshez nem használ helyi fájlt/volume-ot. Az eredmények újraindítás és replika-csere után is PostgreSQL-ben maradnak.

A napi kérdések és aliasindexek jelenleg mind induláskor betöltődnek. A mostani hét nap működik; sok száz nagy napnál a memóriát és indulási időt újra kell mérni, és az aktuális/következő napi indexre korlátozott betöltőt kialakítani. A DB növekedése 150 000 új sor/nap mellett évente 54,75 millió eredmény: mérd a tényleges adat/index méretet, tervezz megőrzést és archiválást, ne hagyd felügyelet nélkül nőni.

## Valódi staging terhelési teszt

Kizárólag saját staging API-val és elkülönített PostgreSQL-adatbázissal:

```sh
k6 run -e BASE_URL=https://SAJAT-STAGING-DOMAIN -e CONFIRM_STAGING=yes -e RATE=1200 -e COMPLETIONS_PER_SECOND=20 -e DURATION=10m tests/production.k6.js
```

A script ellenőrzi, hogy az API `postgres` módban fut és van aznapi tartalom. Másodpercenként 1200 vegyes olvasási kérés mellett 20 teljes játékot is beküld, egyenként hat aláírt nullás pontozási kéréssel és egy eredményírással. A retry-k miatt az összesen tervezett HTTP-ráta valamivel 1340/s fölött van. A szándékosan azonos ponton végzett írás a számlálók versenyhelyzetét is terheli. Ez gyorsított terhelési modell, nem valódi 30 másodperces játékosviselkedés.

A teszt játékosai valós adatbázissorokat hoznak létre, ezért **ne futtasd az éles napi statisztikán**. Az egy generátor-IP-re jutó forgalom limiterbe ütközhet. Ellenőrzött staging kivétel vagy több forrás-IP szükséges; az éles védelmet ne kapcsold ki. A `TRUST_PROXY=railway` helyes működését és a hamisított IP-headerek kezelését is külön ellenőrizd.

Először kisebb rátával működési próba, utána célterhelés, majd 30–60 perc tartós teszt. Legyen nagy szótáras nap, változó keresés, hideg indulás, replika-újraindítás, napváltás és DB-hiba/helyreállás is. Ha a telepítés napjához nincs jóváhagyott tartalom, ne találj ki és ne dátumozz át titokban kérdéscsomagot a mérés kedvéért.

Mérési célok: hibaarány <0,1%, p95 <300 ms, p99 <1000 ms, kihagyott iteráció 0. Mérd a CPU-t, RSS-t, DB-kapcsolatokat, lekérdezési időket, lock-várakozást, 429/5xx arányt és tárhelynövekedést. A célok projektcélok, nem Railway SLA-k.

Ellenőrizd, hogy a két tábla darabszámai egyeznek:

```sql
WITH r AS (
  SELECT game_date, content_revision, score, COUNT(*)::bigint AS n
  FROM daily_results GROUP BY 1,2,3
), c AS (
  SELECT game_date, content_revision, score, SUM(player_count)::bigint AS n
  FROM daily_score_counts GROUP BY 1,2,3
)
SELECT * FROM r FULL JOIN c USING(game_date,content_revision,score)
WHERE r.n IS DISTINCT FROM c.n;
```

Az elvárt eredmény nulla eltérő sor. Nagy éles táblán ez teljes audit, ezért időzítetten és megfelelő erőforráskerettel futtasd, ne minden API-kérésnél.

## Mit mértünk és mit nem?

A V17 API/statisztika tesztjei, a tényleges SQL PGlite PostgreSQL-motoros próbája és a Chromium-funkcionális tesztek sikeresek. Nem történt Railway infrastruktúra- vagy PostgreSQL-hálózati terhelési mérés. Részletek: `ELLENORZES.md`.

A megőrzött `load-local.json` a **korábbi V16**, adatbázis és aláírt napi eredményküldés nélküli 20 másodperces loopback-mérése: 122 646 kérés, 6129,77 kérés/s, 0 hiba. Ez történeti adat, **nem a V17 PostgreSQL-es rendszer kapacitásmérése**. A `npm run test:load` ma is csak a kérdéskiszolgálási útvonalak rövid helyi próbája, nem helyettesíti a fenti staging k6-tesztet.

Hivatalos referenciák: https://docs.railway.com/config-as-code/reference ; https://docs.railway.com/databases/postgresql ; https://node-postgres.com/features/pooling ; https://grafana.com/docs/k6/latest/using-k6/scenarios/executors/constant-arrival-rate/
