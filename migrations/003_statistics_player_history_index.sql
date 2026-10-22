-- Backfill history for pre-progress official results, without a full daily_results scan.
CREATE INDEX IF NOT EXISTS daily_results_player_month_idx ON daily_results(player_hash,game_date DESC);
