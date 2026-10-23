# CLOSEISH – kérdés- és válaszösszeállítási szabályzat, V16

Ez az új napi fájlok elsődleges szabályzata. A meglévő hat (2026-10-23–28-i) nap V15-import; megőrzésük nem új tényellenőrzés. A korábbi dokumentumok `reference-rules` alatt segédanyagként maradtak meg. Meglévő kérdés vagy pontozási határ átírása külön szerkesztői döntés, nem az új napok hozzáadásának mellékhatása.

## 1. A játék

- Naponta pontosan hat kérdés, angol szöveggel, szabad szöveges válasszal, kérdésenként 30 másodperccel.
- A válasz egy névvel azonosított entitás: például ország, város, elem, év, mű, faj vagy személy. Általában nem a mért számot kell beírni. Évkérdésnél maga az év az entitás neve.
- Egy kérdésnek pontosan egy előre rögzített megközelítési iránya van. A játékos nem választhatja meg.
- `below`: a megengedett oldal `érték ≤ limit`, felirat `AT MOST`, nyíl `↑`.
- `above`: a megengedett oldal `érték ≥ limit`, felirat `AT LEAST`, nyíl `↓`.
- Pontosan a határ eltalálása 1200 pont. A napi maximum 7200.
- A határt átlépő, túl távoli, kihagyott vagy ismeretlen válasz 0 játékpontot kap. A nulla játékpont nem jelent nulla mért értéket.

## 2. Kérdésválasztás és ismétlődés

Olvasd át az összes meglévő napot; a question-index.json csak gyors áttekintés. A kérdések témája és megoldási gondolata legyen változatos a napon belül és napok között. Hat azonos típusú országstatisztika nem változatos nap. A korábbi kérdés más limitre átírása önmagában nem új ötlet.

A jó kérdés tág, szabad választeret hagy, de az entitásosztály, mutató, időpont/kiadás, egység és irány egyértelmű. Ne szűkíts önkényes apró részletekkel pusztán a kutatás csökkentéséért. Ha a természetes kategória nagyon nagy – jellemzően 10 000 felett –, indokolható egy valós, ellenőrizhető, a szövegben kimondott szűkítés. Ez nem általános 10 000 soros adatbankkorlát: a meglévő angolszó-kérdés például 188 798 rekordos. Ne vágj le egy adatbankot technikai kényelemből.

## 3. Jogosultság és lefedettség

Először vizsgáld a kategóriatagságot, eseményt, dátumot és minden kimondott feltételt. Egy létező futballista nem automatikusan a 2022-es világbajnokság gólszerzője. Egy helynév nem automatikusan legalább 200 000 lakosú város. Az irány szerinti numerikus limit ettől külön pontozási feltétel.

A teljes ismert és megmért jogosult választeret őrizd meg, beleértve a rossz oldali és túl távoli válaszokat. Ne csak a pontot érő vagy a „jó” válaszokat add meg. Nincs általános kis mintaszám, amely minden kérdésnél megfelelő. Zárt kategóriánál – például kémiai elemek – a teljes lista az elvárás. Nyílt kategóriánál dokumentált forrásuniverzum, lefedettségi számok és a hiányok őszinte leírása szükséges.

- `answers`: az igazoltan jogosult, számszerűen megmért rekordok.
- `recognized_category_candidates`: ismert név, de hiányzó vagy nem összehasonlítható mérés; `metric_value: null`. Nem kaphat kitalált mért nullát vagy pozitív pontot.
- `excluded_answers`: ismert, de a kimondott körből kizárt név, `exclusion_reason` indokkal. Nem kerülhet a pontozható bankba.
- Ismeretlen vagy kétértelmű névnél ne válassz találomra egy entitást. Az azonos nevűeket a kanonikus névben pontosítsd, például ország vagy közigazgatási egység szerint.

## 4. Források és offline rekordok

Minden adatnál adj visszakereshető elsődleges vagy megfelelően dokumentált forrást. Rögzítsd a kiadását, mérési évét, a feldolgozás módját és a szükséges licenc/attribúciós feltételeket. Egy forrás főoldalára mutató link önmagában nem indokol egy tetszőleges értéket. A forrás nélküli AI-emlékezet nem ellenőrzés.

A futó játék a backendbe telepített, rögzített rekordokkal dolgozik. Nem hív generatív AI-t, nem keres az interneten és nem talál ki mérést válaszbeküldéskor. Azonos tartalomverzióban ugyanaz az érték és pontszám járjon ugyanarra az egyértelmű válaszra. Új forrásadatot előzetes importtal és validálással adj hozzá.

A 2026-10-26-i városkérdéshez a korábban használt, commitra rögzített worldcities CSV helyben beépített 200 000+ lakosságú rekordjai szerepelnek. A teljes bank 2035 városrekord. Ez történeti népességi állomány, nem 2026-os népszámlálás és nem bizonyított teljes világlista. Budapest koordinátája 47.497912, 19.040235; a gömbi Haversine-távolság 6371.0088 km sugárral, egész km-re kerekítve. A korábbi 106 rekordot megőriztük; a bővítés 1929 további rekordot adott. Eredeti CSV: https://github.com/PhilipWaldman/world-cities/blob/3151130cb4a2efd925f2afd6435215652f948463/WorldCities/worldcities.csv

## 5. Mérés, egység, kerekítés

**Az összes fizikai mennyiség a játékos felületén kizárólag SI/metrikus egységben jelenhet meg.**
A kérdés angol szövegében, a limitben, a `unit` mezőben, az `answers[*].metric_value` rekordokban,
valamint a `score_bands` és `scoring_window` mezőkben ugyanaz a metrikus egység legyen.
Tilos például mérföldben megfogalmazni a határértéket, miközben a UI kilométert mutat,
vagy fordítva. Ha az elsődleges forrás angolszász mértékegységeket használ,
az eredeti forrásadatot és a pontos átváltási arányt a provenienciában dokumentáld,
de a játékban csak az átváltott, konzisztens metrikus érték szerepeljen.
Átváltás után minden választ és az összes pontozási sávot számold újra, majd ellenőrizd
hogy a pontértékek helyesek-e.

A kérdés, a forrásmutató és a `metric_value` ugyanazt jelentse. Ne keverd például a nagyvárost a várostérséggel, a bruttó adatot a nettóval, az állományt az éves változással vagy a folyó különböző mérőállomásait. A kerekítési lépést a kérdésben és a provenienciában is közöld. A forrásértéket a rögzített szabály szerint **pontozás előtt** kerekítsd. A `%` egységnél a rendszer egész százalékot használ, a limit is egész. Ne legyen a játékos elől elrejtett tizedes határ.

## 6. Pontozás

`gap = limit - value` below iránynál, `gap = value - limit` above iránynál.

| Feltétel | Pont |
| --- | ---: |
| `gap < 0` | 0, CROSSED LIMIT |
| `gap = 0` | 1200, PERFECT HIT |
| `0 < gap ≤ b1` | 1000, RAZOR EDGE |
| `b1 < gap ≤ b2` | 800, CLOSE CALL |
| `b2 < gap ≤ b3` | 600, SOLID HIT |
| `b3 < gap ≤ b4` | 400, IN THE ZONE |
| `b4 < gap ≤ b5` | 200, ON THE BOARD |
| `gap > b5` | 0, TOO FAR |

**Számábrázolás:** amikor nem egész a mérési egység (például 0,01 km), a tárolt, már kerekített decimalis számokból számolj pontos tizedes aritmetikával (vagy megfelelően skálázott egészekkel). Az IEEE-754 lebegőpontos ábrázolás önmagában tévesen 0 pontra vihet egy sávhatáron álló rekordot; bináris kerekítési maradék miatt nem változhat a pontszám. A backendnek is ezeket a határokat kell követnie.

A `score_bands` öt eleme ebben a sorrendben tartalmazza a pozitív, szigorúan növekvő `max_gap_inclusive` értékeket és az 1000, 800, 600, 400, 200 pontot. A `scoring_window.max_scoring_distance` pontosan b5. A tárolt `points` és `tier` számításból származzon. A backend a pontot maga számolja, a kliens pontszámát figyelmen kívül hagyja.

Új kérdéshez ellenőrizd, hogy mind a hat pozitív szint és a releváns nullaeredmények elérhetők-e. A limitet és sávokat a tényleges adatbank eloszlása alapján válaszd. Külön auditban jelezd, ha valamelyik szint üres; ne gyárts új „tényt” a szint kitöltéséhez. A meglévő V15 tartalom importellenőrzése a numerikus egyezést vizsgálja, nem állítja, hogy minden szerkesztői cél teljesült.

## 7. Nevek és aliasok

Egy entitásnak legyen stabil `entity_id` és egyértelmű `canonical` neve. Az `aliases` objektumai `input`, `kind`, `action` mezőkkel készüljenek; ne egyszerű szövegtömböt használj. Rögzíthető közismert rövidítés, kód, tudományos név, névváltozat, ékezet nélküli alak. Egy alias nem kapcsolhat önkényesen két különböző entitást össze. Az automatikus kiegészítés nem helyettesíti a jogosultság- és értékellenőrzést.

## 8. Fájlformátum és kiadás

A `days/YYYY-MM-DD.json` felső szintje: `schema_version: 1`, `date`, `day_number`, `revision`, `publication_status`, opcionális `editorial_note`, és a `questions` objektum `q1`–`q6` sorrendben. A belső kérdések dátuma és napszáma egyezzen a fájléval, az összes kérdés-ID globálisan egyedi. Új napi szám a következő szabad egész; nem kell 7-nél megállni.

A meglévő napi fájlok teljes, valós minták. Ne távolítsd el a proveniencia-, forrás-, jogosultsági és auditmezőket csak azért, mert a felület nem jeleníti meg őket. A fő séma plusz kérdésszintű metadata mezőket megenged. A szerkesztői `revision` emberi címke; az API emellett a teljes napi fájl tartalmából hash-t számol, így a véletlenül változatlanul hagyott címke sem rejt el egy módosítást.

`draft`: nem publikus. `scheduled`: csak az adott vagy egy korábbi napon érhető el, de legkorábban a 2026-10-23-i indulástól. A múltbeli közzétett napok a `/api/v1/days/YYYY-MM-DD` útvonalon játszhatók, a jövőbeli kérdések nem publikusak. A kérdésfájlok kizárólag backendoldalon legyenek.

Az átadási audit tartalmazza: rekordok száma; forrás és snapshot; kihagyott körök; kétértelmű aliasok; sávonkénti darabszámok; kerekítés; ismétlődés-ellenőrzés; ismert kutatási bizonytalanságok. A kódbeli validálás nem helyettesíti a szakmai forrásellenőrzést.
