# CLOSEISH – kérdés- és válaszösszeállítási szabályzat, V17 – közérthetőség, tartalmi sokszínűség és forrásfüggetlen kérdésszöveg

Ez az új napi fájlok elsődleges szabályzata. **A V17 követelmények a már elkészült draft napok szerkesztői felülvizsgálatára is érvényesek.** A meglévő hat (2026-10-23–28-i) nap V15-import; megőrzésük nem új tényellenőrzés. A korábbi dokumentumok `reference-rules` alatt segédanyagként maradtak meg. Meglévő kérdés vagy pontozási határ átírása külön szerkesztői döntés, nem az új napok hozzáadásának mellékhatása.

## 1. A játék

- Naponta pontosan hat kérdés, angol szöveggel, szabad szöveges válasszal, kérdésenként 30 másodperccel.
- A válasz egy névvel azonosított entitás: például ország, város, elem, év, mű, faj vagy személy. Általában nem a mért számot kell beírni. Évkérdésnél maga az év az entitás neve.
- Egy kérdésnek pontosan egy előre rögzített megközelítési iránya van. A játékos nem választhatja meg.
- `below`: a megengedett oldal `érték ≤ limit`, felirat `AT MOST`, nyíl `↑`.
- `above`: a megengedett oldal `érték ≥ limit`, felirat `AT LEAST`, nyíl `↓`.
- Pontosan a határ eltalálása 1200 pont. A napi maximum 7200.
- A határt átlépő, túl távoli, kihagyott vagy ismeretlen válasz 0 játékpontot kap. A nulla játékpont nem jelent nulla mért értéket.

## 2. Kérdésminőség és valódi változatosság – KÖTELEZŐ, publikációt blokkoló feltételek

### 2.1 A játékosnak szóló angol kérdés: természetes, rövid, világos

A `prompt` a játékos kérdése, **nem adatforrási jegyzőkönyv**. Könnyen megérthető, jól megfogalmazott angol szöveg legyen; ne legyen szükség a háttéradatbázis vagy a kutatási eszköz ismeretére. A kérdésből egyértelműen derüljön ki:

1. **mit kell megnevezni** (például országot, várost, filmet, állatot, évet);
2. **milyen jellemzőt** vizsgálunk (például lakosságszám, hossz, életkor, szegénységi arány);
3. **mi a határ és az egyetlen megközelítési irány** (`at most` / `at least`);
4. **melyik év/idény/kiadás** tartozik a kérdéshez, ha a tény időfüggő;
5. az értelmezést befolyásoló **mértékegységet és lényeges kerekítést**.

A mondat maga legyen természetes. Lehetőleg egy, legfeljebb két rövid mondat; kerüld a fölösleges zárójeleket, technikai függelékeket és több egymásba ágyazott megszorítást. A `Name a ...` forma megfelelő, de nem kötelező; az angol nyelvtan és a félreérthetetlenség az elsődleges.

**A kérdésszövegben TILOS pusztán a forrás megnevezése miatt szerepeltetni** a forrás, könyvtár, táblázat, adatkészlet, programcsomag vagy verzió nevét (például `frozen dataset`, `sample`, `CountryInfo`, `pycountry`, `statsmodels`, `ggplot2`, `mtcars`, `Gapminder`). A forrásnév, URL, snapshot, kiválasztási szabály, licencek és mérési leírás a belső mezőkben (`source`, `source_refs`, `measurement`, `answer_scope`, `metric_provenance`, `editorial_note`) jelenjen meg. Az `ISO 3166-2` vagy más szabvány neve **csak akkor** lehet a kérdésben, ha *maga a szabvány szerinti kód* a játék tárgya, és ezt az átlagos játékos is kellően értheti. Az előbbi kivétel nem jogosít fel adathalmazfüggő, nehezen érthető kérdések gyártására.

**Nem elfogadható:** `Name a U.S. state or Washington, D.C., where at least 13% of people were below the poverty line in the frozen 2009 statecrime dataset.`

**Elfogadható:** `Name a U.S. state or the District of Columbia where at least 13% of residents lived below the poverty line in 2009.`

A történeti mérési év (itt 2009) megmarad, a háttéradatbázis neve viszont eltűnik. Egy adatbázis nevének törlésével **nem szabad szélesebb jogosultságot sugallni annál, mint amennyit a tényleges válaszbank igazolni tud**. Ha a közérthető, forrásnév nélküli kérdéshez nincs megfelelően széles bank, a kérdést új forrásokkal kell bővíteni **vagy teljesen le kell cserélni**. Nem megoldás a szűk adatbázist más szavakkal elrejteni.

### 2.2 A hat kérdés egy napra: hat különböző ötlet, nem hat adatbázis-lekérdezés

**Kötelező a jelentős koncepcionális eltérés**. Lehetőleg hat eltérő nagy témacsaládot válassz (például természet, kultúra, sport, történelem, technológia, hétköznapi élet), és változtasd a gondolkodási feladat jellegét is: összehasonlítás, időbeli becslés, helyszín/objektum, rekord, fizikai tulajdonság, kulturális ismeret stb. Nem elegendő hat eltérő `topic` címkét kitölteni.

**Alapszabály egy napon belül:** legfeljebb egy ország-/államstatisztikára és legfeljebb két „nevezz meg egy évet, amelyben X mutató...” típusú kérdésre építs. Egyetlen szűk forrásuniverzum vagy válasz-entitáskategória sem ismétlődhet ugyanazon a napon. Különösen kerülendő, hogy ugyanazon a napon több, tetszőleges küszöbértékre vágott idősor alkossa a kihívást. Ha a kérdés könnyen kicserélhető egy másik adatmezőre úgy, hogy a megoldási ötlet változatlan, **túl hasonló**.

### 2.3 Az összes korábbi naphoz mérten újnak kell lennie

Kérdésírás **előtt** olvasd át az összes korábbi nap 6-6 kérdését (nem elegendő a `question-index.json` összefoglalása), és hasonlítsd össze az új ötletet legalább négy szempontból: témacsalád; válasz-entitások köre; vizsgált mérőszám/korszak; megoldási logika. A legutóbbi **14 napnál** fokozott szerkesztői ellenőrzés szükséges, de a teljes korábbi archívum is kötelező összehasonlítási alap.

- **Tilos** egy korábbi kérdést egyszerűen más határral, más évvel, más pontsávval vagy új megfogalmazással újrakiadni.
- **Tilos** ugyanazon entitáskészletet rövid időn belül csupán más attribútumra újrahasznosítani (például 83 emlősből testtömeg után alvásidő; 148 CSS-színből fényesség után telítettség; 118 elemből atomtömeg után rendszám). Ez **külön kérdéscsaládnak nevezve is ismétlésnek számít**.
- **Tilos** egymást követő napokon ugyanazt a mechanikát dominánssá tenni (például több egymás utáni, főként országstatisztika- vagy éves idősor-kérdésekből álló napot).
- Ha visszatér egy tág témakör (például földrajz vagy zene), annak az entitásköre és a gondolkodási ötlete legyen egyértelműen más. A visszatérés okát az auditban indokold meg; az ismétlés nem lehet adatgyűjtési kényelem kérdése.

**Nem tekinthető változatosságnak** az sem, ha hat különböző csomagból származó, de azonos szerkezetű „nevezz meg egy évet / országot, amelynek X mutatója legalább Y” kérdés kerül egymás mellé. Minőségi döntést emberi/szerkesztői szemmel is hozz, ne csak a téma-címkék különbözőségét mérd.

### 2.4 Előbb a játékötlet, utána az adatforrás – ne fordítva

1. Írj több egymástól valóban eltérő, *forrás említése nélkül is értelmes* kérdésötletet.
2. Válaszd ki a hat legerősebb, jól érthető kérdést, és hasonlítsd össze az archívummal.
3. Ezután keress hozzájuk elsődleges vagy megfelelően dokumentált, ellenőrizhető forrást, és építs a kimondott körhöz illő lehető legteljesebb válaszbankot.
4. Ha csak egy véletlenszerűen szűk, részleges minta áll rendelkezésre, **ne a játékos számára kimondhatatlan mintakorlátot írd a promptba, hanem bővítsd a bankot vagy válassz másik kérdést**.
5. Csak az így elkészült bankhoz válaszd ki a határt, a pontsávokat és a ponteloszlást. A játékos ne az adatforrás szerkezetét próbálja megfejteni.

A széles, szabad választeret biztosító kérdés előnyt élvez az önkényesen leszűkített, csak néhány tucat rekordot kínáló kérdéssel szemben. A kategória lehet természeténél fogva kicsi (például 118 kémiai elem), de **ne legyen mesterségesen kicsi csak azért, mert egy letöltött minta ennyit tartalmaz**. Nincs kötelező, általános 10 000 soros korlát, és nincs olyan mágikus minimális darabszám sem, ami önmagában garantálná a minőséget.

### 2.5 Kötelező, dokumentált szerkesztői kapu

Minden új vagy átírt napnál külön, kérdésenként dokumentáld:

- a játékosnak megjelenő prompt forrásnévmentességét, angol nyelvhelyességét és laikus számára egyértelmű jelentését;
- a hat kérdésen belüli sokszínűséget, valamint a teljes archívumhoz és külön a legutóbbi 14 naphoz viszonyított ismétlődésvizsgálatot;
- a természetes szövegből kikövetkeztethető jogosult univerzum és a tényleges bank egyezését; ha eltér, a **hiányzó jogosult válaszok számát / osztályát és a bővítés akadályát**;
- az összes pontot érő, rossz oldali és túl távoli, de mérhető jogosult választ; ismert hiányzó mérési adatok külön listáját;
- minden forrás, adatvintage, mérési egység és releváns kerekítés visszakereshetőségét, aliasütközéseket és a backend-ellenőrzés szükségességét;
- melyik régi kérdést/kérdéscsaládot kerülte el az új ötlet, illetve ha volt kivétel, a szakmai indokot.

**Publikálást tiltó hiba:** (a) forrásnév- vagy mintafüggő, természetellenes kérdésszöveg; (b) jelentős, indokolatlan tartalmi ismétlés; (c) a prompt által ígért, de a bankban nem ellenőrzött jogosult kategória; (d) nem igazolt mérési szabály; (e) kétértelmű névfeloldás. Ilyenkor `publication_status: draft` marad, a kérdés cseréje/bankbővítése szükséges, és **a nap nem jelenthető késznek**. A séma és pontozási teszt sikeressége önmagában nem old fel szerkesztői blokkolót.

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

A kérdés, a forrásmutató és a `metric_value` ugyanazt jelentse. Ne keverd például a nagyvárost a várostérséggel, a bruttó adatot a nettóval, az állományt az éves változással vagy a folyó különböző mérőállomásait. A pontozást érdemben befolyásoló kerekítést a kérdésben **közérthetően**, a provenienciában pedig részletesen közöld; ne terheld a kérdést kód- vagy táblázatnevekkel. A forrásértéket a rögzített szabály szerint **pontozás előtt** kerekítsd. A `%` egységnél a rendszer egész százalékot használ, a limit is egész. Ne legyen a játékos elől elrejtett tizedes határ.

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

Az átadási audit tartalmazza: közérthetőség és forrásnévmentesség; valódi napon belüli és korábbi napokhoz mért változatosság; rekordok száma; forrás és snapshot; kihagyott körök; kétértelmű aliasok; sávonkénti darabszámok; kerekítés; ismétlődés-ellenőrzés; ismert kutatási bizonytalanságok. A kódbeli validálás nem helyettesíti a szakmai forrásellenőrzést.
