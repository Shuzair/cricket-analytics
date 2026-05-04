-- Create the gold_ba schema
CREATE SCHEMA IF NOT EXISTS gold_ba;

-- Grant usage to postgres user
GRANT ALL ON SCHEMA gold_ba TO postgres;

-- Set comment for documentation
COMMENT ON SCHEMA gold_ba IS 'Schema for gold layer to store business analytics aggregations';
