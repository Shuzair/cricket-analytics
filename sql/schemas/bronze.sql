-- Create the bronze schema
CREATE SCHEMA IF NOT EXISTS bronze ;

-- Grant usage to postgres user
GRANT ALL ON SCHEMA bronze TO postgres;

-- Set comment for documentation
COMMENT ON SCHEMA bronze IS 'Schema for bronze layer raw data storage' ;