-- Supabase Database Setup Script
-- Run this in the Supabase SQL Editor

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS btree_gin;

-- Note: pg_stat_statements might not be available in Supabase
-- CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- The tables will be created automatically by SQLAlchemy when you run the application
-- But you can also create them manually if needed by running:
-- python -c "from database.connection import initialize_database; initialize_database()"

-- Verify extensions are installed
SELECT * FROM pg_extension WHERE extname IN ('vector', 'pg_trgm', 'btree_gin');
