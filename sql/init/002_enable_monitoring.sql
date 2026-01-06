-- Enable monitoring extensions
-- This file runs automatically on first database start

-- pg_stat_statements: Track query performance
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Additional useful extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";    -- Generate UUIDs
CREATE EXTENSION IF NOT EXISTS "pgcrypto";      -- Cryptographic functions

-- Create a view for easy query monitoring
CREATE OR REPLACE VIEW query_stats AS
SELECT 
    calls,
    round(total_exec_time::numeric, 2) as total_time_ms,
    round(mean_exec_time::numeric, 2) as avg_time_ms,
    round(min_exec_time::numeric, 2) as min_time_ms,
    round(max_exec_time::numeric, 2) as max_time_ms,
    rows,
    query
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 50;

-- Grant access to the view
GRANT SELECT ON query_stats TO postgres;

-- Helpful comment
COMMENT ON VIEW query_stats IS 'Top 50 queries by total execution time - use for performance monitoring';
