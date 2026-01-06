-- Example stored function: Calculate batting strike rate
-- 
-- HOW TO USE THIS FILE:
-- 1. Write your function here
-- 2. Run it in pgAdmin OR via terminal:
--    docker exec -i cricket_postgres psql -U postgres -d cricket < sql/functions/batting_functions.sql
-- 3. The function is now saved in both:
--    - This file (goes to GitHub ✅)
--    - PostgreSQL database (for use in queries)

CREATE OR REPLACE FUNCTION calculate_strike_rate(
    p_runs INTEGER,
    p_balls_faced INTEGER
)
RETURNS NUMERIC AS $$
BEGIN
    IF p_balls_faced = 0 OR p_balls_faced IS NULL THEN
        RETURN 0;
    END IF;
    RETURN ROUND((p_runs::NUMERIC / p_balls_faced) * 100, 2);
END;
$$ LANGUAGE plpgsql;

-- Example usage:
-- SELECT calculate_strike_rate(45, 30);  -- Returns 150.00

COMMENT ON FUNCTION calculate_strike_rate IS 'Calculate batting strike rate: (runs/balls) * 100';


-- Another example: Get player batting average
CREATE OR REPLACE FUNCTION calculate_batting_average(
    p_total_runs INTEGER,
    p_innings INTEGER,
    p_not_outs INTEGER
)
RETURNS NUMERIC AS $$
DECLARE
    dismissals INTEGER;
BEGIN
    dismissals := p_innings - p_not_outs;
    IF dismissals <= 0 THEN
        RETURN p_total_runs;  -- Not out in all innings
    END IF;
    RETURN ROUND(p_total_runs::NUMERIC / dismissals, 2);
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calculate_batting_average IS 'Calculate batting average: runs / (innings - not_outs)';
