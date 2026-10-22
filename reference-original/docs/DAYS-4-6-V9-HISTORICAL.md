# CLOSEISH V9 – A 4., 5. és 6. nap átadása

## Megvalósítás

- 18 új, egymástól különböző mérési és forráscsaládot tartalmazó kérdés.
- Az 1–3. napi tartalom JSON-szinten érintetlen; a 7. nap a régi kutatási bank maradt.
- A V8-as diagram / felület megőrizve, szerver nélkül működő, önálló HTML.
- Kérdésenként a hét pontkategória valamely valós, rögzített forrásértékű válasszal rendelkezik; az audit minden rekordon újraszámolta a pontokat.
- A `datasets/new-d4-*`, `new-day5-*` és `new-day6-*` TSV-k az importált, tényleges entitás/mérési párokat tartalmazzák.

## Kritikus lefedettségi figyelmeztetés

**Ez nem tekinthető a korábbi, teljes adatbázisos publikálási feltétel szerint véglegesnek.** A 4. napi film- és zenei adatbank csak kb. 100 címes importált részhalmaz; az 5. napi játéklista mindössze 40 címet tartalmaz, a vízesésekből 41-et, a 6. napi bestsellerlista 27 címet. Ebből **nem szabad arra következtetni**, hogy minden kérdésszöveg által megengedett valós válasz szerepel az offline adatbázisban. Az ilyen kérdések új, valós, jogosult entitásokra téves elutasítást adhatnak. A program nem talál ki hiányzó méréseket.

Külön szerkesztői ellenőrzést igényel a Titanic 891 fős *tanító mintája* (nem teljes utasjegyzék), az F1 155 rekordos részhalmaza, az IMDb 100-as és Spotify 100-as ranglistakivágása, a legkelendőbb könyvek becsült adatai, a parkok 2026. október 20-i befagyasztott névsora, a VGChartz-alapú becsült platformeladások és a Wikipedia vízesésmagasságainak módszertani bizonytalansága. A pénznemek ISO-számkódja és az éves folyóvíz-adatsor tényadat, de a kérdéstípusok kevésbé közérthetők. A két egymást követő nap időponttal válaszolható kérdései további szerkesztői változatossági felülvizsgálatot igényelnek.

## Játékmenet

30 másodperc fordulónként; pontos egyezés 1200 pont, majd 1000/800/600/400/200, helytelen oldal és túl nagy távolság 0. A szűrés kizárólag a kérdés jogosult entitástípusára vonatkozik; a jogosulatlan személy/film/terület nem kap mérési értéket vagy automatikusan 0 pontos érvényes választ. Az 1–3. napban korábban is voltak lefedettségi hiányok, ezeken a mostani munka nem változtatott.

## Fájlok

- `CLOSEISH-standalone.html`: önálló játszható webalkalmazás
- `days/day-04.json`, `day-05.json`, `day-06.json`: 18 lecserélt kérdés és minden ténylegesen betöltött válasz
- `datasets/new-d4-*.tsv`, `new-day5-*.tsv`, `new-day6-*.tsv`: forrás-érték importok
- `tools/shell-v8.html` + `tools/build.py`: reprodukálható HTML-építés
- `docs/DAYS-4-6-AUDIT.csv`: értékenként újraszámolt pontozási audit

## Publikálási állapot

**RESEARCH PREVIEW / NEM VÉGLEGES** az átfogó, minden jogosult válaszra kiterjedő szabályrendszer értelmében. A műszaki implementáció működőképes, a tartalmi lefedettség még nem igazolt.
