-- Table to store files that failed to process into bronze layer
CREATE TABLE IF NOT EXISTS bronze.cricket_match_file_processing_failures (
    id SERIAL PRIMARY KEY,
    file_path TEXT NOT NULL,
    failed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    error_message TEXT,
    error_type VARCHAR(100),
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);