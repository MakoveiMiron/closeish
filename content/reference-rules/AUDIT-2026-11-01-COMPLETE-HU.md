# CLOSEISH — 2026-11-01 (#010) teljes szerkesztői és gépi audit

**Kiadási döntés: `scheduled`**. Hat végleges, angol nyelvű kérdés; **320** egyenként névvel azonosított, számszerűen mért rekord. A teljes, a kérdésből értelmezhető forrásuniverzumot felsoroltuk, a nullapontos (rossz oldali és túl távoli) válaszokat is. A bank és az ellenőrizhető CSV-snapshotok a backend `content` mappájában vannak. **Nem előzetes draft**, és nem csak a pontot érő válaszok listája.

## Kérdések és ellenőrzött lefedettség

| Kör | Téma és ötlet | Teljes kör | Határ | 0 / 200 / 400 / 600 / 800 / 1000 / 1200 |
| --- | --- | ---: | --- | --- |
| Q1 | Zene és akusztika: a 88 billentyűs zongora hangmagassága | 88 / 88 | legalább 440 Hz | 68 / 8 / 5 / 3 / 2 / 1 / 1 |
| Q2 | Meteorológia: az összes névvel rendelkező 2024-es atlanti vihar csúcsszele | 18 / 18 | legfeljebb 167 km/h | 10 / 1 / 1 / 1 / 1 / 1 / 3 |
| Q3 | Motorsport és pályatervezés: a 2025-ös F1-versenyek pályahossza | 24 / 24 | legalább 5412 m | 13 / 3 / 1 / 2 / 1 / 2 / 2 |
| Q4 | Hegymászás: a hagyományosan elismert 14 nyolcezres főcsúcs magassága | 14 / 14 | legfeljebb 8611 m | 3 / 4 / 3 / 1 / 1 / 1 / 1 |
| Q5 | Űrtörténet: a Space Shuttle 135 repülésének teljes napokban számolt időtartama | 135 / 135 | legfeljebb 12 teljes nap | 49 / 21 / 14 / 13 / 15 / 11 / 12 |
| Q6 | Fantasyirodalom: a 41 Discworld-regény első megjelenési éve | 41 / 41 | legfeljebb 2005 | 8 / 11 / 6 / 6 / 5 / 4 / 1 |
| **Összesen** | **hat érdemben más gondolkodási feladat** | **320** |  | |

### Q1 — zongorabillentyűk

- Természetes kategória: a **szabványos 88 billentyű** A0–C8; MIDI 21–108 (nincsenek kihagyott hangok).
- Forrás: [ISO 16:1975, hangolási referencia](https://committee.iso.org/standard/3601.html) és [88 billentyűs hangjegylista](https://piano.org/theory/how-many-notes-on-a-piano/).
- Következetes mérés: A4=440 Hz, 12 fokú egyenletes temperálás, `f=440*2^((MIDI-69)/12)`, minden érték legközelebbi **egész Hz-re kerekítve a pontozás előtt**.
- Írásmódok: C#4/Db4 és a további 5 fekete billentyűosztály éles/bés aliasai; a backendbe bekerült az általános `#`, `♯` és `♭` feloldás az oktávszámos billentyűneveknél. Az ütközésellenőrzés nulla kétértelmű nevet adott.
- Nincs hiányzó tag vagy hiányzó mérés; az adatok számításból determinisztikusak.

### Q2 — 2024 atlanti trópusi viharok

- Elsődleges forrás: [NOAA/NHC, 2024 North Atlantic Tropical Weather Summary](https://www.nhc.noaa.gov/data/tcr/index.php?season=2024), **2026. február 17-i adatsorfrissítés**.
- Minden névvel rendelkező vihar szerepel, Alberto–Sara (18 rekord); a *Potential Tropical Cyclone Eight* nem kapott nevet, ezért nem tartozik a kimondott körbe, nem egy elveszett adat.
- NHC legnagyobb tartós szélértékek csomóban → `km/h = knots × 1.852`, egész km/h-ra fél-felfelé kerekítés. Mind a 18 mérés adott.
- Szélsebesség, nem széllökés, és nem a napi/átlagos viharintenzitás.

### Q3 — 2025 Formula–1 futamok helyszínei

- A 24 forduló teljes eseménylistája: [Formula 1 hivatalos 2025-ös versenynaptára](https://www.formula1.com/en/latest/article/fia-and-formula-1-announces-calendar-for-2025.48ii9hOMGxuOJnjLgpA5qS).
- Pálya szerinti körhossz (nem versenytáv), a 2025-ös konkrét versenyoldalakon közölt **0,001 km** pontosságú értékekből átszámítva egész méterre: például [Ausztria](https://www.formula1.com/en/racing/2025/austria), [Szingapúr](https://www.formula1.com/en/racing/2025/singapore), [Mexikó](https://www.formula1.com/en/racing/2025/mexico), [Las Vegas](https://www.formula1.com/en/racing/2025/las-vegas), [Katar](https://www.formula1.com/en/racing/2025/qatar).
- **Kritikus forrásellenőrzési korrekció:** a független történeti versenylistában Ausztria 4318m volt 4326m helyett, Szingapúr 4928m 4927m helyett, Mexikóváros 4303m 4304m helyett, Las Vegas 6120m 6201m helyett, Katar 5380m 5419m helyett. **A hivatalos 2025-ös F1-versenyoldalak értékei kerültek be.**
- Mind a 24 forduló külön névvel; Monza és Imola nem olvad össze azért, mert mindkettő olasz pálya. Nincs hiányzó mérés.

### Q4 — 14 nyolcezres

- Névjegyzék: [UIAA, 14 tradicionális nyolcezres](https://www.theuiaa.org/uiaa-position-on-8000m-peaks/). Mért magasság: [Seven Summit Treks / 8000ers.com csúcsadatok](https://sevensummittreks.com/expedition/8000ers.html).
- **Pontosan a tizennégy hagyományos főcsúcs**, nem minden, a 8000 m-t meghaladó mellékcsúcs; utóbbiak felismerése a bank által ígért kategórián kívül esik. A felhasználói prompt utal a tizennégy ismert hegyre.
- Magasság egész méterben. Everest: 8848,86 m → 8849 m; a többinél a megnevezett magasságforrás rögzített értéke. Más topográfiai felmérések között előfordulhat 1–13m eltérés; a választott forrásvintage rögzített.
- K2 tökéletes találat; Mount Everest rossz oldali találat; a 14 rekord hiánytalan.

### Q5 — a NASA Space Shuttle repülései

- [ESA teljes Space Shuttle-missziójegyzék](https://www.esa.int/Science_Exploration/Human_and_Robotic_Exploration/Space_Shuttle/Space_Shuttle_missions): **135** külön STS-jelű indítás repülési idővel; a légköri Enterprise/ALT tesztrepülések nem tartoznak ide. A [NASA](https://www.nasa.gov/space-shuttle/) is 135 missziót ad meg.
- Egység: **teljes eltelt nap**, vagyis 24 órás periódusok egész része; a később megkezdett, de nem teljes napot nem számítjuk. ESA `dd d hh h` ⇒ `dd` teljes nap.
- Speciális, fontos kivételek: `STS-51L` mindössze 73 másodpercig tartott ⇒ 0 teljes nap; a `STS-135`-nél az ESA egész napra közelítő **„13 days”** kifejezésével szemben [a NASA részletes adata](https://www.nasa.gov/mission/sts-135/) **12 nap 18 óra 28 perc 50 másodperc**, tehát **12 teljes nap**.
- A Challenger és a Columbia tragikusan végződő útjai is megmaradnak a teljes repülés-univerzumban (sajnos az esemény megtörtént, a történeti név érvényes). A 135 adat ellenőrzött, hiányzó mission ID nem ismert.

### Q6 — Discworld-regények

- [Terry Pratchett hivatalos kiadói sorozatlistája](https://www.terrypratchettbooks.com/book-series/discworld/) **mind a 41 regényt** felsorolja. Évek: [Pratchett hagyatékának kronológiája](https://terrypratchett.com/terry-pratchett/) és [Oxford Academic táblázat](https://academic.oup.com/view-large/396874599).
- A Tiffany Aching fiatal felnőtteknek szóló regények is beleszámítanak, mert a sorozat teljes, hivatalos 41-es listájának tagjai. Novellák, társ-kézikönyvek, köteten kívüli művek nem.
- Első megjelenési év, nem új kiadások éve. Központi határ: `Thud!` (2005); pontozható több régebbi könyv és minden későbbi könyv is bekerült a nulla-, illetve pozitív pontos bankba.

## Hasonlósági és szerkesztői kapuk

- A teljes `2026-10-23` – `2026-10-31` archívum **54 eredeti promptja** kézzel összevetve: sem azonos mérőszám, sem azonos válasz-entitáskészlet, sem más határértékkel újrakiadott korábbi kérdés nincs. Korábbi F1-**versenyző** 2026-10-26-os kérdés helyett 2025-ös **versenypálya-hossz**; korábbi Nobel-/Shakespeare-irodalom helyett teljes Discworld-regénysorozat **megjelenési évek**; korábbi csillagkép/napfolt/CO₂ helyett NASA **ember alkotta űrjármű-repülések**; korábbi ország-/nemzeti park statisztikák helyett **14 természetesen zárt magashegyi főcsúcs**. Azaz a tág témacsalád visszatérhet, de a konkrét feladat nem ismétlődik.
- A hat új feladat **hat különböző témacsalád**, hat különböző entitáskészlet és különböző megoldási ötlet; nincs ország-/államstatisztika, és nincs „nevezz meg egy évet az idősorból” kérdés.
- Mind a hat angol prompt forrásnév- és programkönyvtár-névmentes, tartalmazza az entitást, a numerikus irányt (`at most`/`at least`), a határt, az egységet (ahol értelmezhető), és az időfüggő kérdéseknél az évszámot.
- A frontend által látott prompt egyik kérdésnél sem ír le mesterséges mintakorlátot. Az egyező nevekre a backend `Core.norm` indexelővel ellenőrzött **nulla kereszt-entitás aliasütközés** van. A különböző kategóriákban azonos szavak nem akadályai a napi működésnek.
- A rossz oldali és túl távoli mérhető tényeket a pontozás 0 ponttal, de hiteles névvel kezeli, nem törli a bankból.
- Mindegyik sáv — **0, 200, 400, 600, 800, 1000, 1200** — mind a hat körben legalább egy tényleges forrásrekorddal előáll.
- Nincs ismert hiányzó, jogosult entitás vagy mérés az itt pontosan meghatározott, véges kategóriákból. Ez **nem** állítás arra, hogy minden elképzelhető földi természeti jelenségre, könyvre vagy űrutazásra kiterjedne a bank.

## Kiadási kontroll

- `publication_status: scheduled` = a 2026. november 1-jei dátum előtt nem adható ki a publikus API-n, ugyanakkor már teljesen kész / automatikusan kiadható a dátum beköszöntével.
- `schema_version: 1`, `day_number: 10`, hat kérdés, minden válasznál `metric_value`/`points`/`tier`, forráshivatkozás és stabil `entity_id`.
- A `/content/source-snapshots/closeish-2026-11-01-q[1-6]-full.csv` hat teljes, újra ellenőrizhető rekordlistát tartalmazza; `content/days/2026-11-01.json` maga a teljes backend-betölthető bank.
- Az eredeti 2026-10-29–31 napok fájljait **nem módosítottuk**; a csatolt forrás-archívum szerint ezek továbbra is `draft` állapotúak. Ez nem akadályozza a 11-01-es nap teljességét, de a draft napokat a backend nem fogja közzétenni, amíg külön publikációs jóváhagyás nem történik.
- A `src/core.cjs` új hangjegy-normalizálását (D#/D♭ stb. biztos megkülönböztetése) és korábbi `dateForDay(9)` plafonjának eltávolítását a csomag tartalmazza; a következő további naphoz nem kell újabb kódos felső korlátot írni.
- Az elsődleges forrásszintű magasság- és időpontpontossági eltérések, valamint kiadói/bibliográfiai évjáratok különböző forrásváltozatai továbbra is adatszolgáltatói kockázatot jelentenek. A konkrét, forrás-vintage mellett végzett ellenőrzés ezekhez képest teljes.
- Nem történt éles Railway/PostgreSQL-deployment: a csomag elkészítése nem helyettesíti a publikáció előtti telepítési és end-to-end próbát.
