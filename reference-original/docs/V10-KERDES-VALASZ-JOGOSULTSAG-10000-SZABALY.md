# CLOSEISH V10 — Jogosultsági küszöbszabály és természetes kérdésszöveg

1. A kérdésben szereplő alap-entitástípus minden esetben kötelező (iPhone -> iPhone-modellek, játékos -> játékosok stb.).
2. Külön, mesterséges jogosultsági megszorításra akkor lehet szükség, ha a természetes válaszhalmaz meghaladná a 10 000 valós entitást; ilyenkor a szűkítés legyen nyilvánvaló a kérdésből, és az adatbank pontosan ezt fedje le.
3. Legfeljebb 10 000 elemű, természetesen véges kategóriáknál ne használjunk önkényes Top N listát vagy forrásrészletet jogosultsági korlátként. A teljes valós kategóriát importáljuk; a hiányzó ellenőrzést külön jelezzük, ne állítsunk teljes fedést.
4. A pontszám 0 lehet valóban jogosult válasznál is: a rossz irány vagy túl nagy távolság NEM teszi a névazonosságot érvénytelenné. A hiányzó mérés önálló státusz.
5. Kérdésszövegben ne szerepeljen forráskezelési zsargon (pl. „frozen chart”, „frozen dataset”). A forrás pontos címe, verziója, időpontja és módszertana a forrásmetaadatokban található.
6. Ha egy kérdés szükségszerűen forrás által körülhatárolt Top N ranglistára épül, ezt közérthetően, a témakör részeként ki kell mondani, mert különben a kérdés tágabb válaszokat ígérne, mint amennyit a játék képes pontozni.
7. 2018 előtti iPhone-modellnél a 2019 utáni iPhone is valós, azonosítható entitás, de 0 pont, CROSSED LIMIT; más mobiltelefon-márka nem tartozik a természetes válaszkategóriába.
8. Minimum 1 valódi válasz az összes pontértéken: 1200, 1000, 800, 600, 400, 200, 0.

Állapot: a V10 javítja a Titanic-kérdést és a három „frozen” szöveget. A 4–6. nap egyes korábbi kérdésbankjai továbbra is részleges forráskivonatok; nem tekinthetők teljes lefedettségű kiadásnak.
