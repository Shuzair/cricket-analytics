-- Migration: Add bowling stats table
-- Created: [DATE]
-- 
-- HOW TO RUN:
-- docker exec -i cricket_postgres psql -U postgres -d cricket < sql/migrations/003_add_bowling_stats.sql

CREATE TABLE IF NOT EXISTS bowling_stats (
    stat_id SERIAL PRIMARY KEY,
    match_id INTEGER REFERENCES matches(match_id),
    player_id INTEGER REFERENCES players(player_id),
    overs NUMERIC(4,1) DEFAULT 0,
    maidens INTEGER DEFAULT 0,
    runs_conceded INTEGER DEFAULT 0,
    wickets INTEGER DEFAULT 0,
    wides INTEGER DEFAULT 0,
    no_balls INTEGER DEFAULT 0,
    economy_rate NUMERIC(5,2) GENERATED ALWAYS AS (
        CASE WHEN overs > 0 THEN ROUND(runs_conceded / overs, 2) ELSE 0 END
    ) STORED,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add index for common queries
CREATE INDEX IF NOT EXISTS idx_bowling_stats_player ON bowling_stats(player_id);
CREATE INDEX IF NOT EXISTS idx_bowling_stats_match ON bowling_stats(match_id);

COMMENT ON TABLE bowling_stats IS 'Bowling statistics per player per match';
