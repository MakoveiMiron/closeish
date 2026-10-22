# CLOSEISH V10 — javítások és tényleges lefedettség

## Lecserélt kérdés
- 4. nap / Q2: Titanic utasjegyek helyett az iPhone-modellek bevezetésének éve.
- 54 egyedi, hivatalos Apple-modellnév, mindegyik dokumentált évvel.
- Cél 2018, FROM BELOW, 5 éves pontozási ablak.
- Valódi ponteloszlás: 1200: 3, 1000: 3, 800: 3, 600: 2, 400: 2, 200: 2, 0: 39.
- Forrás: https://support.apple.com/en-us/108044

## Megfogalmazás
- A 4. nap film- és zenekérdéséből, valamint az 5. nap videojáték-kérdéséből eltávolítottuk a „frozen chart / frozen selection” technikai fordulatot.
- A ranglista lényegi körülhatárolása megmaradt, különben nem lenne pontos a jogosult válaszkör.

## Új jogosultsági szerkesztési szabály
- A természetes válaszkör 10 000 entitás fölött igényelhet külön szűkítést.
- 10 000 alatt nem szabad pusztán kényelmi okból kisebb Top N mintát teljes körűnek állítani.
- A kategóriaalapú jogosultság minden esetben megmarad, a 0 pont pedig pontozási állapot.

## A korábbi kérdésbankok korlátai
- A 4–6. nap többi kérdésében korábbi, dokumentált részhalmazok maradtak; a korábbi kiadás teljes lefedettségre vonatkozó hiányosságai továbbra is fennállnak.
- Ezért az új forrás- és kérdésszöveg-javítás nem egyenlő a teljes háromnapos bank véglegesítésével.

## Ezen kívül javított pontozási peremhiba
- 6. nap / Q3 napfoltok: a tárolt 1.0999999999999943 értéket egzakt 1.1 ponthatárra javítottuk; a 1840-es év azonos helyre kerül mindkét pontozásban.
