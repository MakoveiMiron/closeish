# CLOSEISH – V23 kérdés–válasz szerkesztési szabályzat

**Verzió:** 23.0; **2026. október 24.** A játék műfaja: **Obscure Knowledge Worldwide Quiz**. A 2026. november 1-jei, hat különböző tudásterületű nap a szerkesztői minőségmérce. Az élő, 2026. október 23–24-i napok változatlanok. A következő napokra a jelen V23 szabályzat irányadó; a korábbi V21/V22 dokumentumok csak történeti archívumok.

## 1. Mitől jó egy CLOSEISH-kérdés?

A játékos egy **valós, megnevezhető entitást** ad meg, amelynek egy **ellenőrizhető, előre rögzített számszerű tulajdonsága** a kérdésben rögzített határérték egyik kijelölt oldalához minél közelebb esik. A nehézség a világ érdekességeinek ismeretéből és a céltudatos becslésből fakad, nem az alapfokú számolásból. Minden kérdésnek legyen **saját, önálló tudásanyaga**, nem pusztán új címkéje.

**Azonnali elutasítás:** a tökéletes válasz 5–10 másodperc alatt közvetlenül kiszámolható vagy kitalálható (UNO ötös, dominó 4+3, római szám átírás, betűérték, Scrabble, ábécé-pozíció); ugyanaz az entitáslista szerepelt a közeli napokon; abszurd módon hosszú, kusza szöveg; USA-belső közéleti/geográfiai statisztika uralja a hetet; hiányos vagy önkényesen megválogatott bank; mennyiségi adat nélkül elfogadott név/év.

## 2. Globális tematikai változatosság – KÖTELEZŐ szerkesztői kapu

Minden napon **pontosan hat, makroszinten különböző témacsalád** legyen. A november 1-jei jó példa: zenei akusztika, meteorológia, motorsportmérnökség, hegymászás, űrrepülés, fantasyirodalom. A `topic` mező átnevezése nem számít önálló területnek. Egyszerre csak azonos témacsalád egy feladata szerepelhet, pl. két földrajz, két országdemográfia, két film vagy két évszámot soroltató díjátadó nem megfelelő.

**Tudásterület-javaslatok (nem zárt lista):** világirodalom és könyvtörténet; nyelvészet; vallás- és eszmetörténet; építészet és várostörténet; képzőművészet; dizájn és divat; fotográfia; zene és hangtechnika; gasztronómia; filmtörténet; színház; játék- és médiakultúra; régészet; antropológia; biológia; orvos- és tudománytörténet; genetika; matematika; geológia; paleontológia; csillagászat; meteorológia; vízrajz; űrkutatás; repülés; tengerészet; mérnöki technika; közlekedéstörténet; regionális és globális történelem; diplomáciatörténet; sporttörténet; természetvédelem; gazdasági rendszerek; oktatástörténet.

**Gördülő ablakok:**

1. Az utolsó **hét napon legalább 12 különböző makrotéma**; ugyanaz a makrotéma legfeljebb négyszer, kivéve dokumentált szerkesztői okból. Kulturális és tudományos területek is szerepeljenek minden héten, ne csak sport, geográfia és országstatisztika.
2. **14 napon belül tilos azonos entitáskészlet ismétlése** más határral vagy attribútummal. Ugyanazon feladatmechanika (pl. kitüntetés éve) legfeljebb kétszer három egymást követő napon; legalább négy eltérő metrikafajta naponta (helyezés, hossz, időtartam, fizikai mennyiség, eseményszám, év, index, teljesítmény stb.).
3. Egy napon **legfeljebb egy ország/főváros/népesség/államterület-lista**. Ugyanazon régióról, különösen az USA-ról szóló kérdés ne térjen vissza rendszeresen; gördülő hétben az USA-n belüli intézményekről kérdező feladatok aránya **legfeljebb 15%**.
4. Globális jelentőség nem azonos USA-központúsággal; legyen európai, afrikai, ázsiai, óceániai, latin-amerikai és összehasonlító nemzetközi tematika. Nem kell minden kontinensből kérdés minden nap, de a teljes 7–14 napot tekintve se legyen feltűnő földrajzi hiány.
5. Nem fogadható el az a nap, amelynek hat kérdéséből négy „mondj egy évszámot / díjazottat / országot” típusú. A kérdések gondolkodási feladata is különbözzön.

## 3. A válaszbank tényleges teljessége

A bank tartalmazza a kérdés által **elvileg megengedett teljes természetes halmazt**, minden tag tényleges számértékével, **a rossz oldalra eső és nullapontos neveket is**. A jó bank nem az ismert helyes válaszok szűk listája. A kategória legyen lezárt hivatalos lista, jól meghatározott történeti intervallum, teljes versenymezőny vagy pontosan számolható véges természetes halmaz.

- Szerkesztői preferencia **40–400 rekord**, de 12–39 elem elfogadható, ha a teljes kategória természetesen ilyen kicsi (pl. 12 geológiai periódus). 400–500 fölött külön audit; több tízezres nyitott Spotify/videojáték/könyvlista tilos.
- Egy *ranglista* megnevezhető, pontosan rögzített teljes felső N helyezése használható, ha a forrás minden pozíciót közöl; a játékos szövegéből derüljön ki az esemény és év. Ne téveszd össze a „top 20” természetes lezárását a világszerte létező összes repülőtérrel.
- Az időszak teljes legyen az elejétől a végéig, hiányzó évek nélkül. Pontatlan évjárat/adathiány esetén ne találj ki értéket, és ne hagyd a bankból a kedvezőtlen válaszokat. Ha a mérték időfüggő, rögzítsd a kiadást.
- Az összes canonical név és **valóban egyértelmű alias** legyen rögzítve. Egyező alias nem jelölhet több entitást. Elütésből nem szabad helyes valós választ találomra összepárosítani.
- `source`, `source_refs`, `metric`, `unit`, `measurement`, `answer_scope`, `score_bands`, `metric_value` és a külön CSV snapshot konzisztensen fedjék a publikált adatot. Hivatalos forrás és második kontrollforrás előnyben; ha a publikált lista és a számok nem egyeztethetők, ne publikáld a kérdést.

## 4. A kérdés angol szövege

**Egy mondat, lehetőleg 150 karakter alatt**, világosan kezdődjön `Name a...` / `Name an...`; pontosan jelezze a csoportot, a számszerű attribútumot, a határt és a felülről/alulról való közelítés irányát (`at least`, `at most`). Az egység legyen metrikus és az adatokkal azonos. Pontos időszakot csak indokolt esetben nevezzen meg; a túl sok kitétel nem teheti a kérdést szövegértési rejtvénnyé. Belső adatbázis vagy API neve nem kerülhet a promptba.

A pontos értékhez adathalmaz kell, de a kategória leírható hétköznapi szavakkal. A kétértelmű „ranked 30th or higher” helyett „ranked 30th or better (rank ≤ 30)” alak használható. Ne tegyél úgy, mintha a helyes megoldás tudományos konszenzus volna, ha a kérdés egy adott díj vagy vallási hagyomány szerinti katalóguson alapul; nevezd meg a körülhatárolást.

## 5. Pontozás és kiadási minőségkapu

A backend a döntő forrás: `below`: `metric_value <= limit`, `above`: `metric_value >= limit`; pontos találat 1200, öt egymástól növekvő pozitív sáv 1000, 800, 600, 400, 200, ezen kívül 0. Napi maximum 7200, köridő 30 másodperc. Előbb jogosultsági/banki névfeloldás, azután mérés, azután pontozás. Minden új bankban legyen 1200, 1000, 800, 600, 400, 200 és 0 pontot érő valós válasz, kivéve ha külön igazoltan matematikailag lehetetlen.

**A `scheduled` állapot előfeltétele mind a hat kérdésnél:** (a) teljes forrásjegyzék és minden tag; (b) valós számszerű érték és pontos egység; (c) aliasütközés-mentesség; (d) backendtel pontosan egyező pontok; (e) eltérő makrotéma és módszer a hat körben; (f) az előző 14 nap összevetése; (g) nem túl könnyű vagy USA-túlsúlyos; (h) `npm run validate`, `npm test`, `node scripts/export-content.mjs`, éles publikálásnál külön Railway / PostgreSQL próba.

## 6. A V23 átadására érvényes szerződés

- A 2026. október **23., 24. és november 1.** napi JSON-jai változatlanok; november 1. minőségi minta.
- Október **25–31.** szerkesztői cseréit és keresztnapos témakiegyenlítését a `reference-rules/AUDIT-V23-2026-10-24-HU.md` rögzíti.
- Az összes nap `scheduled`, de a jövőbeli napok **a nyilvános API-n dátumzár alatt maradnak**. A helyi teszt HTML önálló, nem kerül a production backendbe.
- Minden nap pontosan hat kérdés; production adatmentés, meglévő API, Suggest és pontozó működés érintetlen. Admin/test endpointot, titkos tesztkulcsot, helyi mock adatbázist tilos a production csomagba keverni.
