-- Create the ref schema
CREATE SCHEMA IF NOT EXISTS ref ;

-- Grant usage to postgres user
GRANT ALL ON SCHEMA ref TO postgres;

-- Set comment for documentation
COMMENT ON SCHEMA ref IS 'Schema for reference data storage' ;