-- Anonymous, write-only public suggestion endpoint; reviewing ideas requires private DB access.
-- No player identifiers, IP addresses or browser-side history is collected here.
CREATE TABLE IF NOT EXISTS question_suggestions (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  question TEXT NOT NULL CHECK (char_length(question) BETWEEN 8 AND 350),
  direction TEXT NOT NULL CHECK (direction IN ('above','below')),
  submitted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  review_status TEXT NOT NULL DEFAULT 'pending' CHECK (review_status IN ('pending','reviewed','accepted','rejected'))
);
CREATE INDEX IF NOT EXISTS idx_question_suggestions_review ON question_suggestions (review_status, submitted_at DESC);
