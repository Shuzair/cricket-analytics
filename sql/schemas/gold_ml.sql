-- Create the gold_ml schema
CREATE SCHEMA IF NOT EXISTS gold_ml ;

-- Grant usage to postgres user
GRANT ALL ON SCHEMA gold_ml TO postgres;

-- Set comment for documentation
COMMENT ON SCHEMA gold_ml IS 'Schema for gold layer to store data for machine learning models' ;