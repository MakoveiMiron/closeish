# CLOSEISH – V17 szerkesztői audit: 2026. október 29–31.

**Állapot:** az új, természetesebb angol promtok elkészültek, a szabályzatot és a folytatási útmutatót aktualizáltuk. **A 3 új nap NEM tekinthető teljesen szabálykövetőnek vagy publikálhatónak.** Mindhárom `draft` maradt.

## Mi változott?

- 18 prompt (2026-10-29–31) közérthetőbb megfogalmazása, a forrásnevek, `frozen`, `dataset` és `sample` kifejezések elhagyása.
- Az azonos jelentésű mutatók, időpontok és limitek megmaradtak; **pontozási értéket, válaszrekordot, pontsávot és előírt megközelítési irányt nem változtattunk**.
- `KERDES-VALASZ-SZABALYZAT.md`: kötelező írásminőségi, lefedettségi, korábbi napokra tekintő változatossági kapuk, szabálytalan részleges minták tiltása.
- `question-index.json`, `README-AI.md` és az új draft napok szerkesztői revíziói követik a módosításokat.

## Publikáció előtt kötelező tartalmi javítás vagy teljes kérdéscsere

| Nap, kérdés | Probléma | Teendő |
|---|---|---|
| 10-29 Q1 | Ugyanaz a 83 emlős, mint 10-24 Q2 – csak alvásidő a testtömeg helyett | Új entitásuniverzumra épülő kérdés |
| 10-29 Q2 | A 249 ISO-kódszámláló technikai, a játékosnak nehezen értelmezhető; nem azonos a közigazgatási egységek tényleges számával | Természetesebb, közismert mutató teljes lefedettséggel vagy kérdéscsere |
| 10-29 Q4 | A 32 autó a Motor Trend 1973–74 **részleges válogatása**, nem minden korabeli autó | Jelentős bankbővítés vagy kérdéscsere |
| 10-29 Q5 | 437 középnyugati megye csak egy minta, az egyszerű prompt ennél többet ígér | Minden releváns megye felvétele vagy kérdéscsere |
| 10-29 Q6 | Azonos 148 CSS-névszín, mint 10-24 Q3, csak fényesség helyett telítettség | Új entitásuniverzumra épülő kérdés |
| 10-30 Q1 | Gapminder 142 ország, ugyanaz a válaszuniverzum, mint 10-23 Q5; sok korábbi országstatisztika | Változatosabb új ötlet; hiányzó országok ellenőrzése |
| 10-30 Q2 | CountryInfo forrásuniverzum korábban is szerepelt, a border code nem minden esetben igazolt teljes valós szomszédsági kör | Teljes határszomszédsági forrás és névazonosítás vagy kérdéscsere |
| 10-30 Q4 | Ugyanaz a 118 kémiai elem, mint 10-23 Q2, csak atomtömeg helyett atomrendszám | Új entitásuniverzumra épülő kérdés |
| 10-30 Q6 | Ismét éves gazdasági idősor, az egymáshoz közeli napokban több hasonló évmegnevezős feladat van | A napi kihívásmixben lecserélendő lehet |
| 10-31 Q1 | A szövegezést javítottuk; az amerikai állam-statisztikák viszont 10-25 Q4 óta ismétlődnek | A szerkesztő döntsön a sokszínűségről a többi ötlettel együtt |
| 10-31 Q2 | 25 éves, szűk rézpiaci idősor, adatjogi/licenc-kérdés is nyitott | Licenc tisztázása, szélesebb koncepció vagy kérdéscsere |
| 10-31 Q3 | 76 autómodell–év kombináció csupán egy 234 soros EPA mintából; nem teljes 1999/2008 autókör | Teljes bank vagy kérdéscsere; közel van a 10-29-i autós kérdéshez is |
| 10-31 Q4 | Kifejezetten niche, 1972–98 negyedéves német kamatidősor; az éves/negyedéves sorok dominálnak | Érthetőség és napon belüli diverzitás újraszerkesztése |
| 10-31 Q5 | CountryInfo történeti népesség és terület eltérő, nem garantáltan azonos korú adatok; nem lehet megbízható közös dátumot megadni, ismételt országuniverzum | Időben konzisztens nemzetközi adatforrás vagy új kérdés |

**További felülvizsgálandó tételek:** 10-29 Q3, 10-30 Q3 és Q5, 10-31 Q6 értelmezhetőbb lett, de tartalmi hitelességük külső egyedi ellenőrzését nem végeztük el. A több idősor-kérdés felhalmozódását a napi teljes cserék során kell megszüntetni.

## Az ismert adatuniverzumokra vonatkozó elsődleges dokumentáció

- Motor Trend / R `mtcars`: 1973–74-es autókról **32 megfigyelés**, nem teljes korszakos járműjegyzék: https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/mtcars.html
- ggplot2 `mpg`: **234 soros EPA-részhalmaz**, 1999/2008 adat, nem a teljes autópiac: https://search.r-project.org/CRAN/refmans/ggplot2/html/mpg.html
- A pontosan becsomagolt forrás-snapshotok minden kérdés `measurement` / `answer_scope` / `source_refs` mezőjében találhatók. E dokumentum nem állítja, hogy minden egyes forrásértéket újra hitelesített.

## Az újrafogalmazás megőrzési elve

A publikus kérdésből eltűntek az adatbázisnevek, de ez **nem javította ki** a hiányos bankok lefedettségét. A természetes kérdés és a részleges bank eltérése jelenleg **publikációs blokkoló**; nem szabad erre azt mondani, hogy már teljes, ellenőrzött nap készült. A backend nélkül azt sem állítjuk, hogy listán kívüli, de tényszerűen helyes válaszokat megfelelően ellenőriz.

## Ellenőrzés

- 9 nap, 54 kérdés; a 2026-10-29–31-i 18 prompt változott.
- A 2026-10-29–31-i 2 255 válaszrekord, mérési érték, tier, score-band, időkeret és irány változatlan.
- Gépileg ellenőrizhető konzisztencia nem pótolja a fent megnevezett szerkesztői cseréket és a hiányzó forráshitelesítést.
