CREATE TABLE daily_results (
  game_date date NOT NULL,
  player_hash char(64) NOT NULL,
  content_revision varchar(64) NOT NULL,
  run_id uuid NOT NULL,
  score smallint NOT NULL CHECK (score BETWEEN 0 AND 7200 AND score % 200 = 0),
  completed_at timestamptz NOT NULL DEFAULT clock_timestamp(),
  PRIMARY KEY (game_date, player_hash)
);
CREATE INDEX daily_results_revision_idx ON daily_results (game_date, content_revision, score);
-- 37 actual attainable scores, split into 32 write shards to avoid one hot counter.
CREATE TABLE daily_score_counts (
  game_date date NOT NULL,
  content_revision varchar(64) NOT NULL,
  score smallint NOT NULL CHECK (score BETWEEN 0 AND 7200 AND score % 200 = 0),
  shard smallint NOT NULL CHECK (shard BETWEEN 0 AND 31),
  player_count bigint NOT NULL CHECK (player_count >= 0),
  PRIMARY KEY (game_date, content_revision, score, shard)
);
