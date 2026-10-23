# CLOSEISH – javaslatok adminisztrátori kezelése

A publikus frontend kizárólag a `POST /api/v1/suggestions` műveletet használhatja. A táblához nincs publikus listázás vagy export; a játékos egykori helyi adatai sem tölthetők le az új felületről.

Az adminisztrátor **privát Railway PostgreSQL konzolból / DB kliensből** érheti el a beérkezett javaslatokat (a DB hozzáférési adatait SOHA ne másold a frontendbe):

```sql
SELECT id, question, direction, submitted_at, review_status
FROM question_suggestions
WHERE review_status = 'pending'
ORDER BY submitted_at ASC
LIMIT 100;
```

Admin ellenőrzés után egyetlen javaslat állapotának állítása:

```sql
UPDATE question_suggestions SET review_status = 'reviewed' WHERE id = 123;
```

A példában szereplő `123` helyére kizárólag egy valódi, a saját adatbázisodban található rekordazonosító kerüljön. Az itt látható SQL nem fut le önmagától.

A funkció beüzemelése: `npm run migrate`, Railway-n pedig a `railway.toml` pre-deploy lépése futtatja az új `005_question_suggestions.sql` migrációt. Ezután együtt telepítsd a V17.8 backendet és frontendet. Az éles adatbázist és a CORS engedélyezett frontend-origint a Railway változói adják; az `ALLOWED_ORIGINS` értékét az éles domainekkel kell egyeztetni.

Korlátok: az API anonim, a CORS nem autentikáció; a per-IP órás limit API-példányonként számol, így több replikánál ajánlott edge/WAF szintű globális spam/rate-limit. A privát tábla nem titkosított a DB-felhasználó előtt, az adminnak a legkisebb szükséges jogosultságot kell adni.
