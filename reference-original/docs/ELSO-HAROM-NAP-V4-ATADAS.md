# CLOSEISH – 1–3. nap, V4 fejlesztési átadás, 2026-10-21

## Publikálhatósági állapot

**NEM VÉGLEGES.** Az alábbi állomány a kért végleges, offline, nagy adatlefedettségű kiadás helyett a ténylegesen ellenőrizhető jelenlegi eredmény. Nem teljesíti minden esetben az összes valós entitás felismerését és mérését. A jelen dokumentum nem hivatkozható a teljesítő nyilatkozat helyett.

Az **első három nap** 18 kérdése változatlanul játszható, a játékmechanika és a metrikus/amerikai megjelenítési mód megmaradt. Az eredeti **1. napi day-01.json változatlan**: SHA-256 `68e4814e92f1b37c08fe2247ab835be885e8716872e65ffef9aab0db11a2853e`.

## Ténylegesen a ZIP-ben tárolt kategóriák

- **2. nap, emlősök:** a régi `msleep` mintából **83 ellenőrzött mért érték** található meg az önálló HTML-ben. A fajuniverzum **nem teljes**. Az online taxonómiai névjegyzék megpróbálja hozzáadni a MDD v2.0 neveit, ezekhez *nem állít be kitalált testtömeget*. A megvalósított offline importáló MDD v2.5 + PanTHERIA összekapcsolásra is képes, de mivel a nagy eredeti források nem voltak innen letölthetők, az így létrehozható új, teljes mért állomány **nincs ebben a ZIP-ben**.
- **2. nap, 2008-as autók:** **436 külön modellnév**, ebből **411 ellenőrzött fogyasztási érték** és **25 mérés nélkül** a 2008-as amerikai forrásban. Ez nem az összes 2008-ban világszerte eladott modell, és nem is minden autóévjárat.
- **2. nap, 2022-es vb-futballisták:** **118 pontozható gólszerző** és **158 ellenőrzött, 2022-es vb-n szereplő, a külön góllistában nem szereplő játékos** szerepel az offline kérdésbankban. Az önálló HTML a 2. nap megnyitásakor megpróbálja külön letölteni a Reep v0 `people.csv` állományát, és **csak a `type=player` rekordokat** hozzáadni a kereshető, de mérésre váró identitásokhoz. A Reep **444 707** rekordja személyeket tartalmaz, tehát játékosokat **és edzőket**, nem lehet 444 707 focistának nevezni. A teljes többszázezres névbank **nincs offline beépítve**; a letöltés hálózatfüggő, és az offline működés csak az egyszer már szinkronizált és gyorsítótárazott névjegyzékek esetén lehetséges, ha a böngésző tárolása működik.
- **A további kérdések** részletes pontozási és fedettségi auditját a `FIRST-THREE-AUDIT-HU.md` és `FIRST-THREE-AUDIT.csv` tartalmazza.

Az összesített **123 941 pontozott rekord** közül **117 493 egyetlen szókérdésből** származik. Ez nem 123 941 focista vagy emlős, és nem 123 941 egymástól független válaszkategória.

## Online névfelismerés állapota

A `registry-loader.js` egy külön Web Worker segítségével letölti és szűri a források nyilvántartását, az adatforrást megnevezve. A `game.js` az esetleges eredményeket pontozott mérés kitalálása nélkül adja a katalógushoz. Reep-adatokból hozzáadott játékosnál **NEEDS REVIEW** státusz jelenik meg addig, amíg az egyértelmű személyazonosság és a 2022-es gólforrás összevetése nem igazolt. A nem ellenőrzött hiányzást **nem szabad automatikusan bizonyított nulla vb-gólnak tekinteni**. A 30 másodperces játékóra nem indul újra a háttérszinkronizálás eredményeként.

## Valódi nagy források reprodukálható offline importálása

A kiegészítő importot **hálózattal rendelkező számítógépen** kell elvégezni a projekt gyökeréből:

```sh
python tools/download_public_sources.py
python tools/import_full_universes.py \
  --people datasets/external-original/Reep_v0_2026.25_people.csv \
  --mdd datasets/external-original/MDD_v2.5_species.csv \
  --pantheria datasets/external-original/PanTHERIA_1-0_WR05_Aug2008.txt \
  --min-players 10000 --min-measured-mammals 2000 --strict
python tools/build.py
python tools/audit_first_three.py
```

A forrásokat SHA-256 lenyomatokkal menti a letöltő. A `--strict` **megszakítja** az átadást, ha a minimumok nem teljesülnek. A MDD és a PanTHERIA neveinek különböző taxonómiai kiadása miatt a keresztkulcsok egyezését nem lehet automatikusan tökéletesnek minősíteni. Az import után is szükséges kézi forráslefedettségi, méréstartomány- és pontkategóriaellenőrzés. A forrásletöltési/taxonómiai hibák ugyanilyen publikálási akadályok.

**Megjegyzés:** ez a menetrend végrehajtásra előkészített, de a teljes nagyforrású importot ebben a környezetben a hálózati korlátozás miatt **nem sikerült végrehajtani**. Nem állítjuk, hogy az összes dokumentált emlősnek van értékelhető testtömegadata, vagy hogy a 2008-as autók száma 436-ban lezárható.

## Futtatott ellenőrzések

- `python tools/audit_first_three.py`: **PASS**, mind a 18 kérdés meglevő pontjai a megadott pontsávokkal konzisztensen újraszámolhatók; továbbra is 10 `RESEARCH` állapotú kérdés.
- `python tests/test_football_non_goal.py`: **PASS**, az offline 158 szereplő értékei nem kapnak hamis gólpercet.
- `python tests/test_large_registry_import.py`: **PASS**, 13 000 **mesterséges TESZT-NÉV** szerepelhet a böngészőben, kereshető és **mérés nélküli**. Ez **nem 13 000 valós, beimportált focista**.
- `python -m py_compile tools/download_public_sources.py tools/import_full_universes.py`: **PASS**.
- Az eredeti első napi JSON hash ellenőrizve.

## Nyitott, publikálást kizáró hibák

1. A százezres Reep CSV, az aktuális MDD v2.5 és a PanTHERIA állomány **nincs fizikailag a ZIP-ben**, ezért a felhasználó által kért offline teljesség nem bizonyított.
2. A Reep hivatalosan a jelenlegi v1 regiszter felé tereli az új integrációkat; a projekt a dokumentált, lefagyasztott v0 kiadást használja. Ez verzió- és karbantartási kockázat.
3. A MDD–PanTHERIA testtömeg összekapcsolás után még le kell ellenőrizni, hogy mind a hét pontkategóriához van valódi válasz, különösen a kerekítés és az 56 kg-os határ mellett.
4. A 2008-as autós forrás amerikai és kiadásspecifikus; a globális modellsokaság, névváltozatok és összes motorváltozat teljes összehasonlítása nincs kész.
5. A 2022-es góleseményekhez minden Reep játékos entitásazonosítóját egyeztetni kell. Az egyező név önmagában nem elég a pontszám véglegesítéséhez.
6. Az első napi korábbi kutatási kategóriák lefedettségi hiányai változatlanok, mert az első napi tartalom megőrzését kérték.

**Végső státusz: ellenőrizhető fejlesztési kiadás, NEM a felhasználó által kért végleges teljes tartalmi kiadás.**
