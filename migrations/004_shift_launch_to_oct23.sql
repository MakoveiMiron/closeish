-- V17.7 changes the publication schedule by exactly +1 day, retaining challenge numbers.
-- Railway pre-deploy runs this ONCE, before the V17.7 server starts.
-- Take a DB backup and coordinate maintenance if the old API is receiving writes.
-- Move from newest date backwards to avoid intermediate unique-key conflicts.
DO $migration$
DECLARE
  old_day date;
  new_day date;
  old_revision text;
  new_revision text;
BEGIN
  FOR old_day IN SELECT generate_series(date '2026-10-28',date '2026-10-22',interval '-1 day')::date LOOP
    new_day := old_day + 1;
    CASE old_day
      WHEN date '2026-10-22' THEN old_revision := '84b3ef595b2496cb57d81e2f'; new_revision := 'a71f3ab56dd7d4c813b6159e';
      WHEN date '2026-10-23' THEN old_revision := 'ae9a5ed914972a0203ddd23a'; new_revision := '1cf1dd25bed3f58cce5bf8d9';
      WHEN date '2026-10-24' THEN old_revision := '4757322b5401ec178f368e7a'; new_revision := '4b345abd75c17c6dbc2044e0';
      WHEN date '2026-10-25' THEN old_revision := '18a4985d8727d4ee99c97969'; new_revision := 'b2c1f8327a7c5bb92055799a';
      WHEN date '2026-10-26' THEN old_revision := '0d02e7182d50f9e2ccde2e63'; new_revision := '33c1e692df2cc5197e3e2e02';
      WHEN date '2026-10-27' THEN old_revision := '1cdc3e7aeb0ef8752a9293ef'; new_revision := '5f6d6eae9cb44bbb2eb0d5f1';
      WHEN date '2026-10-28' THEN old_revision := '8e1f6dffabbee9b05e3b264a'; new_revision := '7f300072eedfa2cfbfd20b4e';
    END CASE;
    -- The revision is a hash of the whole day JSON, which changes after moving dates.
    -- The existing stored results remain bound to the same six-question content.
    UPDATE daily_results
      SET game_date=new_day, content_revision=CASE WHEN content_revision=old_revision THEN new_revision ELSE content_revision END
      WHERE game_date=old_day;
    UPDATE daily_score_counts
      SET game_date=new_day, content_revision=CASE WHEN content_revision=old_revision THEN new_revision ELSE content_revision END
      WHERE game_date=old_day;
    UPDATE player_progress
      SET game_date=new_day, content_revision=CASE WHEN content_revision=old_revision THEN new_revision ELSE content_revision END
      WHERE game_date=old_day;
  END LOOP;
END $migration$;
