#!/bin/bash

# Supabase Configuration Helper Script
# This script helps you configure your environment variables for Supabase

echo "🔧 Supabase Configuration Helper"
echo "================================"
echo
echo "Please provide the following information from your Supabase project:"
echo
echo "1. Go to your Supabase project dashboard"
echo "2. Navigate to Settings > Database"
echo "3. Copy the connection details"
echo

read -p "Enter your Supabase Project Reference (found in URL): " PROJECT_REF
read -p "Enter your Database Password: " -s DB_PASSWORD
echo
read -p "Enter your OpenAI API Key: " -s OPENAI_API_KEY
echo

# Create the .env file
cat > .env << EOF
# Database Configuration - SUPABASE
DB_HOST=db.stwstxpljczaodeggtsx.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=${Supabasesw}

# Vector Settings
VECTOR_DIMENSIONS=384
IVFFLAT_LISTS=100

# Embedding Model
EMBEDDING_MODEL=all-MiniLM-L6-v2

# OpenAI Configuration (Required for RAG functionality)
OPENAI_API_KEY=${OPENAI_API_KEY}
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=500
OPENAI_TEMPERATURE=0.3

# API Settings
ENVIRONMENT=production
LOG_LEVEL=INFO

# Batch Processing
BATCH_SIZE=100
EOF

echo "✅ .env file created successfully!"
echo
echo "Next steps:"
echo "1. Run the Supabase setup SQL script in your Supabase SQL Editor"
echo "2. Initialize the database: python scripts/setup_database.py"
echo "3. Generate embeddings: python scripts/generate_embeddings.py"
echo "4. Start the application: uvicorn main:app --reload"
