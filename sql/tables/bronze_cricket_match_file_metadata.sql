CREATE TABLE bronze.cricket_match_file_metadata (
    id BIGSERIAL PRIMARY KEY,
    start_date DATE NOT NULL,
    team_type VARCHAR(20) NOT NULL CHECK (team_type IN ('club', 'international')),
    match_type VARCHAR(50) NOT NULL,
    gender VARCHAR(10) NOT NULL CHECK (gender IN ('male', 'female')),
    match_id VARCHAR(100) NOT NULL,
    teams VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_hash CHAR(64) NOT NULL,
    ingestion_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_modified_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_processed BOOLEAN DEFAULT FALSE,
    
    CONSTRAINT unique_file_hash UNIQUE (file_hash),
    CONSTRAINT unique_match_file UNIQUE (match_id, file_path)
);

-- Indexes for common query patterns
CREATE INDEX idx_cricket_metadata_start_date ON bronze.cricket_match_file_metadata(start_date);
CREATE INDEX idx_cricket_metadata_match_id ON bronze.cricket_match_file_metadata(match_id);
CREATE INDEX idx_cricket_metadata_team_type ON bronze.cricket_match_file_metadata(team_type);
CREATE INDEX idx_cricket_metadata_match_type ON bronze.cricket_match_file_metadata(match_type);
CREATE INDEX idx_cricket_metadata_is_processed ON bronze.cricket_match_file_metadata(is_processed);

-- Comment on table
COMMENT ON TABLE bronze.cricket_match_file_metadata IS 'Bronze layer metadata for cricket match data files';