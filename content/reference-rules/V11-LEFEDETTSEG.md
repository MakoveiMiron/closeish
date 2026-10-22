# CLOSEISH V11 — a 5. nap három adatbankjának bővítése

**Fontos: NEM teljes, publikálásra kész adatlefedettség.** Az importált valós részhalmazt bővítettem, nem állítom, hogy a 11 ezer+ videojátékot vagy az összes vízesést beimportáltam.

## Rekordok

- Videojátékok: 40 → 349 ellenőrizhetően forrásban szereplő cím (új: 309).
- Vízesések: 41 → 79 név és mért magasság (új: 38).
- Nílus: 100 dokumentált év (1871–1970) + 56 későbbi év (1971–2026) felismerhető. Az utóbbiak teljes éves, összehasonlítható mérési adata NINCS a telepített sorozatban. Ha ilyen év a válasz, 0 játékpontot ad, „NO VERIFIED DATA” jelzéssel. Nem tulajdonít a Nílusnak nulla tényleges vízhozamot.

## Módszertani figyelmeztetések

A videojátékoknál a különböző platformokon kiadott játékok teljes összevetéséhez a VGChartz teljes, történeti platformadatbázisának importja szükséges. Az egyes importált platformos adatok ezért részmérések lehetnek. A 2020-as adatok nem a 2026-os aktuális eladásokat jelzik. A vízesések magassága az atlaszokban eltérhet a mérési módszer miatt; a játék kiinduló 41-es adatbankját és a Cascadyas online atlaszának további, ténylegesen dokumentált sorait egyesítettem. Az Aszuán 1871–1970-es adatsorához más mérőállomás modern mérését nem keverem.

## Források

- https://github.com/sayuen0/vggames-scraping/tree/master/data/20201003-012640
- https://www.cascadyas.com/find/
- https://www.statsmodels.org/stable/datasets/generated/nile.html

## Megőrzött tartalom

Az 1–4., 6. és 7. nap kérdés- és válaszadatbankjának JSON-ja változatlan. A módosított 5. napi források offline is be vannak ágyazva a HTML-be.
