-- Complete Supabase Database Setup Script
-- Run this in your Supabase SQL Editor

-- Step 1: Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS btree_gin;

-- Step 2: Create the database schema
-- Categories table
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    color VARCHAR(7) DEFAULT '#3498db',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255),
    avatar_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Topics table
CREATE TABLE IF NOT EXISTS topics (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    category_id INTEGER REFERENCES categories(id),
    user_id INTEGER REFERENCES users(id),
    views INTEGER DEFAULT 0,
    posts_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Posts table
CREATE TABLE IF NOT EXISTS posts (
    id SERIAL PRIMARY KEY,
    topic_id INTEGER REFERENCES topics(id),
    user_id INTEGER REFERENCES users(id),
    post_number INTEGER NOT NULL,
    raw TEXT NOT NULL,
    cooked TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE,
    -- Vector column for embeddings (384 dimensions for all-MiniLM-L6-v2)
    embedding vector(384)
);

-- Post reactions table
CREATE TABLE IF NOT EXISTS post_reactions (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES posts(id),
    user_id INTEGER REFERENCES users(id),
    reaction_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(post_id, user_id, reaction_type)
);

-- Step 3: Create indexes for performance
-- Full-text search indexes
CREATE INDEX IF NOT EXISTS idx_posts_fulltext_search 
ON posts USING gin(to_tsvector('english', cooked || ' ' || raw));

CREATE INDEX IF NOT EXISTS idx_topics_fulltext_search 
ON topics USING gin(to_tsvector('english', title));

-- Vector similarity search index (HNSW is better than IVFFlat for most cases)
CREATE INDEX IF NOT EXISTS idx_posts_embedding_hnsw 
ON posts USING hnsw (embedding vector_cosine_ops);

-- Regular performance indexes
CREATE INDEX IF NOT EXISTS idx_posts_topic_id ON posts(topic_id);
CREATE INDEX IF NOT EXISTS idx_posts_user_id ON posts(user_id);
CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_topics_category_id ON topics(category_id);
CREATE INDEX IF NOT EXISTS idx_topics_created_at ON topics(created_at DESC);

-- Partial indexes for active content
CREATE INDEX IF NOT EXISTS idx_posts_visible_recent 
ON posts (created_at DESC) 
WHERE deleted_at IS NULL;

-- Step 4: Insert sample data
-- Insert default category
INSERT INTO categories (name, description, color) 
VALUES ('General', 'General discussion topics', '#3498db')
ON CONFLICT (name) DO NOTHING;

-- Insert sample user
INSERT INTO users (username, email) 
VALUES ('system', 'system@example.com')
ON CONFLICT (username) DO NOTHING;

-- Step 5: Verify setup
SELECT 'Extensions installed:' as check_type, extname as name 
FROM pg_extension 
WHERE extname IN ('vector', 'pg_trgm', 'btree_gin')

UNION ALL

SELECT 'Tables created:' as check_type, table_name as name
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_type = 'BASE TABLE'
ORDER BY check_type, name;

-- Test vector functionality
SELECT 'Vector test:' as check_type, 
       vector_dims('[1,2,3]'::vector) as result;

-- Show table sizes
SELECT 
    schemaname,
    tablename,
    attname as column_name,
    n_distinct,
    correlation
FROM pg_stats 
WHERE schemaname = 'public' 
AND tablename IN ('posts', 'topics', 'categories', 'users')
ORDER BY tablename, attname;
