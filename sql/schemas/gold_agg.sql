-- Create the gold_agg schema
CREATE SCHEMA IF NOT EXISTS gold_agg ;

-- Grant usage to postgres user
GRANT ALL ON SCHEMA gold_agg TO postgres;

-- Set comment for documentation
COMMENT ON SCHEMA gold_agg IS 'Schema for gold layer to store aggregated data for analytics' ;