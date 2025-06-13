# Quick Deployment Guide

## 🚀 Deploy to Vercel (Bypass Network Issues)

Since your Supabase database is working but local connection is blocked, let's deploy directly:

### Step 1: Push to GitHub
```bash
# Initialize git if not already done
git init
git add .
git commit -m "Initial commit with Supabase setup"

# Push to GitHub (create repo first)
git remote add origin https://github.com/yourusername/your-repo-name.git
git push -u origin main
```

### Step 2: Deploy to Vercel
1. Go to [vercel.com](https://vercel.com)
2. Click "Import Project"
3. Connect your GitHub repository
4. Set these environment variables in Vercel:

```
DB_HOST=stwstxpljczaodeggtsx.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=Postgressw
VECTOR_DIMENSIONS=384
IVFFLAT_LISTS=100
EMBEDDING_MODEL=all-MiniLM-L6-v2
OPENAI_API_KEY=eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIzZjIwMDQ4NjdAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.ejGVBlcepyC6zfO8DtMYdQafxYUOyCwXVi2G_3weyX8
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=500
OPENAI_TEMPERATURE=0.3
ENVIRONMENT=production
LOG_LEVEL=INFO
BATCH_SIZE=100
```

5. Deploy!

### Step 3: Initialize Database Remotely
Once deployed, you can initialize the database using Vercel's function execution or the Supabase SQL Editor.

## 🔧 Alternative: Use Supabase API

If you want to continue local development, you can use Supabase's REST API instead of direct PostgreSQL connection.
