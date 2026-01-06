-- Views: Player summary statistics
-- 
-- HOW TO RUN:
-- docker exec -i cricket_postgres psql -U postgres -d cricket < sql/views/player_summary.sql

-- View: Player batting summary
CREATE OR REPLACE VIEW player_batting_summary AS
SELECT 
    p.player_id,
    p.name,
    p.country,
    COUNT(DISTINCT bs.match_id) as matches,
    COUNT(bs.stat_id) as innings,
    SUM(bs.runs) as total_runs,
    MAX(bs.runs) as highest_score,
    ROUND(AVG(bs.runs), 2) as average,
    SUM(bs.fours) as total_fours,
    SUM(bs.sixes) as total_sixes,
    SUM(bs.balls_faced) as total_balls,
    CASE 
        WHEN SUM(bs.balls_faced) > 0 
        THEN ROUND((SUM(bs.runs)::NUMERIC / SUM(bs.balls_faced)) * 100, 2)
        ELSE 0 
    END as strike_rate
FROM players p
LEFT JOIN batting_stats bs ON p.player_id = bs.player_id
GROUP BY p.player_id, p.name, p.country;

COMMENT ON VIEW player_batting_summary IS 'Aggregated batting statistics per player';


-- View: Match summary
CREATE OR REPLACE VIEW match_summary AS
SELECT 
    m.match_id,
    m.match_date,
    m.venue,
    m.team_1,
    m.team_2,
    m.winner,
    m.match_type,
    COUNT(DISTINCT bs.player_id) as players_batted,
    SUM(bs.runs) as total_runs_scored
FROM matches m
LEFT JOIN batting_stats bs ON m.match_id = bs.match_id
GROUP BY m.match_id, m.match_date, m.venue, m.team_1, m.team_2, m.winner, m.match_type;

COMMENT ON VIEW match_summary IS 'Summary of each match with aggregate stats';


-- View: Recent matches (last 30 days)
CREATE OR REPLACE VIEW recent_matches AS
SELECT * FROM match_summary
WHERE match_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY match_date DESC;

COMMENT ON VIEW recent_matches IS 'Matches from the last 30 days';
