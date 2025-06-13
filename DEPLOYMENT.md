# Spider Web RAG Application - Vercel Deployment Guide

## 🚀 Quick Deploy to Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/spider-web-rag)

## 📋 Prerequisites

1. **Database**: You'll need a PostgreSQL database with pgvector extension
   - **Recommended**: Use [Neon](https://neon.tech) or [Supabase](https://supabase.com) for free PostgreSQL with pgvector
   - **Alternative**: Any PostgreSQL provider that supports pgvector

2. **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com)

## 🔧 Environment Variables for Vercel

Set these environment variables in your Vercel dashboard:

```bash
# Database Configuration
DB_HOST=your-db-host.neon.tech
DB_PORT=5432
DB_NAME=your-database-name
DB_USER=your-db-username
DB_PASSWORD=your-db-password

# Vector Settings
VECTOR_DIMENSIONS=384
IVFFLAT_LISTS=100

# Embedding Model
EMBEDDING_MODEL=all-MiniLM-L6-v2

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=500
OPENAI_TEMPERATURE=0.3

# API Settings
ENVIRONMENT=production
LOG_LEVEL=INFO

# Vercel Environment
VERCEL=1
```

## 📁 Project Structure

```
spider-web-rag/
├── vercel.json          # Vercel configuration
├── requirements.txt     # Python dependencies (simplified for serverless)
├── Frontend/           # Vue.js frontend
│   ├── package.json
│   ├── vite.config.js
│   └── src/
└── Backend/            # FastAPI backend
    ├── main.py         # Main application
    ├── requirements.txt # Full dependencies (for local dev)
    ├── api/
    ├── database/
    └── services/
```

## 🗄️ Database Setup

1. **Create PostgreSQL database** with pgvector extension
2. **Run migrations** (you'll need to do this manually):
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   -- Run your schema creation scripts
   ```
3. **Load your data** using the provided scripts

## 🌐 Frontend API Configuration

The frontend automatically detects the environment:
- **Development**: Uses `http://localhost:8000`
- **Production**: Uses the same Vercel domain

## 📝 Deployment Steps

1. **Fork/Clone** this repository
2. **Connect to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Import your repository
3. **Set Environment Variables** in Vercel dashboard
4. **Deploy**!

## 🔍 Verification

After deployment:
1. Check `/health` endpoint
2. Test the RAG functionality
3. Verify database connectivity

## ⚠️ Important Notes

- **Database**: Must be externally hosted (Vercel doesn't provide persistent storage)
- **Vector Embeddings**: May need to be pre-computed for better performance
- **Cold Starts**: First request may be slower due to serverless cold starts
- **Timeouts**: Functions have a 60-second timeout limit

## 🛠️ Local Development

```bash
# Frontend
cd Frontend
npm install
npm run dev

# Backend
cd Backend
pip install -r requirements.txt
uvicorn main:app --reload
```

## 📞 Support

- Check the logs in Vercel dashboard for deployment issues
- Ensure all environment variables are correctly set
- Verify database connectivity and pgvector extension
