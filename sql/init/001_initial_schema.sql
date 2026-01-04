-- Initial schema for cricket analytics
-- This file runs automatically when PostgreSQL container starts for the first time

-- Example: Matches table
CREATE TABLE IF NOT EXISTS matches (
    match_id SERIAL PRIMARY KEY,
    match_date DATE NOT NULL,
    venue VARCHAR(255),
    team_1 VARCHAR(100) NOT NULL,
    team_2 VARCHAR(100) NOT NULL,
    winner VARCHAR(100),
    match_type VARCHAR(50),  -- ODI, T20, Test
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Example: Players table
CREATE TABLE IF NOT EXISTS players (
    player_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    country VARCHAR(100),
    role VARCHAR(50),  -- Batsman, Bowler, All-rounder, Wicket-keeper
    date_of_birth DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Example: Batting stats table
CREATE TABLE IF NOT EXISTS batting_stats (
    stat_id SERIAL PRIMARY KEY,
    match_id INTEGER REFERENCES matches(match_id),
    player_id INTEGER REFERENCES players(player_id),
    runs INTEGER DEFAULT 0,
    balls_faced INTEGER DEFAULT 0,
    fours INTEGER DEFAULT 0,
    sixes INTEGER DEFAULT 0,
    is_out BOOLEAN DEFAULT FALSE,
    dismissal_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add more tables as your project grows
-- Example: bowling_stats, team_scores, tournaments, etc.
