-- Create the silver schema
CREATE SCHEMA IF NOT EXISTS silver ;

-- Grant usage to postgres user
GRANT ALL ON SCHEMA silver TO postgres;

-- Set comment for documentation
COMMENT ON SCHEMA silver IS 'Schema for silver layer processed data storage' ;