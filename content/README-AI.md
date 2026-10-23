# CLOSEISH – önálló kérdéscsomag AI-nak

Ezt a teljes `content` mappát add át ZIP-ben. Minden nap teljes kérdés- és válaszbankja benne van; más projektfájl nem szükséges a tartalom folytatásához.

- `days/YYYY-MM-DD.json`: egy dátum, hat kérdés, minden válasz és forráshivatkozás.
- `KERDES-VALASZ-SZABALYZAT.md`: az új tartalom elsődleges összeállítási szabályzata.
- `day.schema.json`: a JSON formai sémája.
- `question-index.json`: a 54 kérdés (36 eredeti és 18 új, utóbbiak draft) gyors, szerkesztői áttekintése. Segédindex, nem az alkalmazás adatforrása.
- `reference-rules/`: a V15-ből megőrzött részletes szabályok és korábbi jelentések. Eltérésnél az elsődleges szabályzat és a napi fájl tényleges mezői az irányadók; történeti jelentés nem bizonyít új ellenőrzést.

## Másolható folytatási kérés

Olvasd végig a KERDES-VALASZ-SZABALYZAT.md fájlt, a day.schema.json sémát és a meglévő napokat. Készíts új napi CLOSEISH-kérdéscsomagot a kért dátumra, pontosan hat, változatos angol nyelvű kérdéssel. Ne ismételd meg a meglévő kérdéseket pusztán más határértékkel. A válaszbank legyen a kimondott kategória és a rögzített forráskészlet lehető legteljesebb lefedése, a rossz oldali és túl távoli ismert válaszokkal együtt. Minden mérési értéket, jogosultsági feltételt és aliast forrással ellenőrizz. Hiányzó számot ne találj ki és ne helyettesíts nullával. Az új fájl neve YYYY-MM-DD.json, publication_status értéke először draft legyen. Tartsd meg a dokumentált pontozást, pontosan egy megközelítési irányt és a kérdésenkénti 30 másodpercet. Adj rövid magyar auditot a lefedettségről, hiányokról, forrásokról és lehetséges névütközésekről. Ha egy teljes, ellenőrzött nap nem állítható elő, jelezd pontosan a hiányokat; ne állítsd késznek.

## Beillesztés

1. Másold a kapott új fájlt a `content/days` mappába.
2. Futtasd a projekt gyökerében: `npm run validate`.
3. Ellenőrizd a szakmai auditot, majd állítsd a nap `publication_status` mezőjét `scheduled` értékre.
4. Újra validálj és indítsd újra / telepítsd újra **mindegyik** backendpéldányt. A kiszolgáló induláskor olvassa be a tartalmat.
5. `npm run export:questions`: friss segédindexet és új AI-ZIP-et készít. Ne a régi ZIP-et egészítsd ki kézzel.

A tartalom nem töltődik fel magától sehova. Az új dátumú fájlokhoz nem kell frontendkódot vagy kézi schedule-listát módosítani. A sémán túl a backend validátora ellenőrzi a pontokat és a dátumok/azonosítók összhangját.

## V17.7 nyitónap és egységrendszer

A CLOSEISH első játszható napja **2026-10-23** (CHALLENGE #001), az utolsó jelenleg mellékelt nap **2026-10-31** (#009); **2026-10-29–31** (#007–#009) egyelőre draft. Új kérdéscsomaghoz csak metrikus fizikai mértékegységet használj; a prompt, a limit, a válaszértékek és a score-bands ugyanabban az egységben legyenek.

## 2026-10-29–31 tartalomellenőrzés

A részletes gépi és szakmai ellenőrzés: `reference-rules/AUDIT-2026-10-23-31-HU.md`. A V15 importált napok három azonosított belső konzisztenciahibáját kijavítottuk; a többi mérés külső szakmai hitelesítése változatlanul nem teljes. A három új nap `draft`; ne állítsd `scheduled` értékre a blokkoló auditpontok és szerkesztői forrásellenőrzés nélkül. A mellékelt generálószkript dokumentáció, futtatásához külön Python-függőségek kellenek, a backendnek nem.

## Konkrét javítások és utóellenőrzés (2026-10-23)

- `2026-10-23/q6`: `approach_rule` javítása a kérdés eredeti `below`/`at_most` irányához.
- `2026-10-25/q3` és `2026-10-26/q5`: csak a különböző entitások között ütköző rövid aliasokat töröltük, a teljes és egyértelmű nevek megmaradtak.
- A `days` fájlok és a `question-index.json` megfelelő `revision`/`content_revision` azonosítói frissültek.
- Futatható tartalmi konzisztenciateszt: `python reference-rules/validate-content-consistency.py`. Ehhez Python 3 szükséges, a `jsonschema` opcionális.
- A részleteket a `reference-rules/AUDIT-CORRECTIONS-2026-10-23-HU.md` fájl tartalmazza. Ez **nem** jelent külső adathitelesítést, illetve a 2026-10-29–31-i napok továbbra is `draft` állapotúak.
