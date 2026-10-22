-- Authoritative, per-player per-day progress. Results are appended by the API,
-- never replaced by browser-supplied score/state. No plaintext device UUIDs.
CREATE TABLE player_progress (
  player_hash char(64) NOT NULL,
  game_date date NOT NULL,
  content_revision varchar(64) NOT NULL,
  run_id uuid NOT NULL,
  responses jsonb NOT NULL DEFAULT '[]'::jsonb
    CHECK(jsonb_typeof(responses) = 'array' AND jsonb_array_length(responses) <= 6),
  active_round smallint CHECK(active_round BETWEEN 0 AND 5),
  active_deadline timestamptz,
  phase varchar(16) NOT NULL DEFAULT 'intro'
    CHECK(phase IN ('intro','play','reveal','end')),
  updated_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (player_hash,game_date)
);
-- The primary key already supports per-player month range scans.
