> **TÖRTÉNETI DOKUMENTUM (2026-10-20).** A benne szereplő 25 692-es szám és kérdések a korábbi kiadásra vonatkoznak. Az aktuális értékeket a `COVERAGE-REPORT-2026-10-21.md` tartalmazza.

# CLOSEISH – hét napos kibővített kutatási előnézet (2026-10-20)

## Valós mennyiségek

- Hat új nap, összesen **36 új kérdés** (2026-10-21–26). A korábbi első nap változatlan.
- Az új hat nap együtt **25,692 pontozható kérdés–válasz rekord**, **3,864 különböző megjelenített válasznév** és **324 felismert, de mérésre váró rekord**. A kérdés–válasz rekord nem egyedi entitás!
- Az első nappal együtt a teljes hét napban **27,634** pontozható kérdés–válasz rekord található.
- Az adatbázis egyetlen rekordját sem töltöttük fel kitalált mértékegységgel vagy tippelt névvel.

## Új adatforrások és korlátaik

**Amerikai megyei térképi állomány (Basemap UScounties):** 3221 névvel és 5 jegyű FIPS-azonosítóval szereplő megye, közülük 3220 közelítő geodéziai mérés. A dátumvonalat keresztező Aleutians West Census Area azonosítható, de nem pontozható. A mérés az archivált térkép poligonjaiból (WGS84 geodézia és közelítő bounding-box) származik; nem hivatalos mai terület- vagy közigazgatási statisztika. **Hat külön kérdés** használja, tehát továbbra is forráskoncentráció van.

**2000-es Census-alapú középnyugati megyék (ggplot2/plotnine `midwest.csv`):** 437 névvel és PID-vel azonosított rekord Illinois, Indiana, Michigan, Ohio és Wisconsin államokból. A hat kérdés a népesség, felnőttek száma, oktatás és szegénységi mutatók különböző értékeit méri. A forrás maga jelzi, hogy egyes változók leírása feltételezésen alapul; ezért nem hitelesített aktuális hivatalos népszámlálásként jelennek meg. A százalékos értékeket egészre kerekítve pontozzuk.

**UNESCO DataHub `whc001`:** a 240 *Natural* besorolású világörökségi helyszín első felvételi éve, a más típusú helyszínek külön felismert, nem jogosult válaszok. Ez valóban más metrika, mint az első napi hektár-alapú feladat. A helyszín besorolását az adatforrás szerinti pillanatképből használjuk.

**Megmaradt korábbi források:** RDKit elemek, Gapminder 1952–2007, régebbi országpillanatkép és UNESCO országonként aggregált mutatók. Ezek jelenleg továbbra is szűk, tematikailag ismétlődő kategóriák, ezért a hat nap **nem tekinthető végleges szerkesztői tartalomnak**. Nem állítjuk, hogy a 36 kérdés 36 teljesen független ötlet.

## Felületi módosítások

- Névfelismerés: gépelés közbeni **inputon belüli** halk kiegészítés és instrukció, legördülő nélkül. Első Enter megerősít, a második Enter küldi be; a küldés előtt a játékos tovább módosíthatja a szöveget.
- `ALL` válaszkatalógus: 1200-tól 0-ig csökkenő, a pontkategóriákat követő rendezés; a teljes nulla pontos kategória látható.
- Archívum: a teljes hét nap azonnal megnyitható, az időzítés nem kerülhető meg a logós visszalépéssel, az aktív kör abszolút határideje megmarad.
- Az összesítő háromoszlopos struktúrája, a százalékos statisztikai mutató és a simított eloszlási görbe változatlan. A játékoseloszlás továbbra is **demo**, nem valós többjátékosos adat.

## Technikai ellenőrzések és publikálhatóság

A `QUESTION-AUDIT-EXPANDED.csv` mind a 42 kérdésre tartalmazza a teljes 1200/1000/800/600/400/200/0 bontást, a még ellenőrizetlen és kizárt nevek számát is. A hét nap pontozási és adatintegritási ellenőrzése, valamint a két Enteres működés, a 3220 soros ALL rendezése és a két nézetméret böngészős tesztje teljesült. Egy hosszú, ötnézetes regressziós futtatás időkorlátba ütközött: az nem tekinthető sikeres teljes tesztnek.

**Státusz: RESEARCH_DRAFT_NOT_PUBLISHABLE.** A legnagyobb továbbra is fennálló hiány a témaköri forráskoncentráció, a régi demográfiai pillanatképek és a tényleges független külső adatexportok további ellenőrzése. Egy többezer rekordos katalógus nem önmagában minőségi kérdés; a kreatív szerkesztői kritériumokat külön kell alkalmazni.

## Források

- UNESCO: https://data.unesco.org/explore/dataset/whc001/?flg=en-us
- ggplot2 Midwest (és a változóleírások bizonytalansága): https://ggplot2.tidyverse.org/reference/midwest.html
- Basemap adatterjesztés: https://matplotlib.org/basemap/stable/users/geography.html
- Egyéb korábbi források: `docs/SOURCE-NOTICES.md`
