# Supabase Setup Guide for Spider Web RAG

## 🎯 Quick Setup Steps

### 1. Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Click "New Project"
3. Fill in project details:
   - **Name**: `spider-web-rag`
   - **Password**: Choose a strong password (save this!)
   - **Region**: Choose closest to your users
4. Wait for project to be created (2-3 minutes)

### 2. Enable Extensions

1. In your Supabase dashboard, go to **SQL Editor**
2. Run the SQL script from `Backend/scripts/supabase_setup.sql`:

```sql
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS btree_gin;

-- Verify extensions are installed
SELECT * FROM pg_extension WHERE extname IN ('vector', 'pg_trgm', 'btree_gin');
```

### 3. Get Connection Details

1. Go to **Settings** > **Database**
2. Copy the following information:
   - **Host**: `db.YOUR_PROJECT_REF.supabase.co`
   - **Database name**: `postgres`
   - **Port**: `5432`
   - **User**: `postgres`
   - **Password**: (the one you set during project creation)

### 4. Configure Environment Variables

#### Option A: Use the Configuration Script
```bash
cd Backend
./scripts/supabase_config.sh
```

#### Option B: Manual Configuration
Update your `Backend/.env` file:

```env
# Database Configuration - SUPABASE
DB_HOST=db.YOUR_PROJECT_REF.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=YOUR_DATABASE_PASSWORD

# Vector Settings
VECTOR_DIMENSIONS=384
IVFFLAT_LISTS=100

# Embedding Model
EMBEDDING_MODEL=all-MiniLM-L6-v2

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=500
OPENAI_TEMPERATURE=0.3

# API Settings
ENVIRONMENT=production
LOG_LEVEL=INFO

# Batch Processing
BATCH_SIZE=100
```

### 5. Initialize Database

```bash
cd Backend
source .venv/bin/activate
python scripts/setup_database.py
```

### 6. Load Data and Generate Embeddings

```bash
# Load forum data
python scripts/load_forum_data.py

# Generate embeddings
python scripts/generate_embeddings.py
```

### 7. Test Locally

```bash
uvicorn main:app --reload
```

Visit `http://localhost:8000/health` to verify everything works.

### 8. Deploy to Vercel

1. Push your code to GitHub
2. Connect to Vercel
3. Set environment variables in Vercel dashboard (same as in .env file)
4. Deploy!

## 🔍 Environment Variables for Vercel

Set these in your Vercel dashboard under **Settings** > **Environment Variables**:

- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `VECTOR_DIMENSIONS`
- `IVFFLAT_LISTS`
- `EMBEDDING_MODEL`
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `OPENAI_MAX_TOKENS`
- `OPENAI_TEMPERATURE`
- `ENVIRONMENT`
- `LOG_LEVEL`
- `BATCH_SIZE`

## 🚨 Important Notes

1. **Database Limits**: Supabase free tier has limits on:
   - Database size (500MB)
   - Bandwidth (5GB)
   - API requests (50,000/month)

2. **Connection Pooling**: Supabase handles connection pooling automatically

3. **Security**: 
   - Your database password should be strong
   - Never commit your `.env` file to git
   - Use Vercel environment variables for production

4. **Monitoring**: Check your Supabase dashboard for:
   - Database usage
   - Query performance
   - Connection statistics

## 🔧 Troubleshooting

### Can't connect to database
- Check your connection details
- Ensure your IP is not blocked (Supabase allows all IPs by default)
- Verify the password is correct

### Extensions not working
- Make sure you ran the setup SQL script
- Check if pgvector is available in your Supabase project

### Performance issues
- Monitor your database size
- Check if you need to upgrade your Supabase plan
- Optimize your queries

## 📞 Support

- Supabase Documentation: [supabase.com/docs](https://supabase.com/docs)
- Discord: [discord.supabase.com](https://discord.supabase.com)
