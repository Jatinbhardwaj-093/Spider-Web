#!/bin/bash

# Vercel Deployment Script for Spider Web RAG

echo "🚀 Starting Vercel Deployment Process..."
echo "=====================================  "

# Check if we're in the right directory
if [ ! -f "vercel.json" ]; then
    echo "❌ Error: vercel.json not found. Please run this from the project root."
    exit 1
fi

echo "✅ Found vercel.json configuration"

# Check if git is clean
if ! git diff-index --quiet HEAD --; then
    echo "⚠️  Warning: You have uncommitted changes. Consider committing them first."
    echo "Uncommitted files:"
    git status --porcelain
    echo ""
fi

# Check Frontend dependencies
echo "📦 Checking Frontend dependencies..."
cd Frontend
if [ ! -d "node_modules" ]; then
    echo "Installing Frontend dependencies..."
    npm install
else
    echo "✅ Frontend dependencies already installed"
fi
cd ..

# Check Backend dependencies (simplified requirements for Vercel)
echo "🐍 Checking Backend requirements..."
if [ ! -f "requirements.txt" ]; then
    echo "Creating simplified requirements.txt for Vercel..."
    cat > requirements.txt << EOF
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-dotenv==1.0.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pgvector==0.2.4
openai==0.28.1
sentence-transformers==2.2.2
huggingface-hub==0.20.3
scikit-learn==1.3.2
pydantic==2.4.2
python-jose[cryptography]==3.3.0
python-multipart==0.0.6
aiofiles==23.2.1
EOF
    echo "✅ Created requirements.txt"
else
    echo "✅ requirements.txt already exists"
fi

echo ""
echo "🔧 Environment Variables Needed:"
echo "================================="
echo "Set these in your Vercel dashboard:"
echo ""
echo "DB_HOST=stwstxpljczaodeggtsx.supabase.co"
echo "DB_PORT=5432"
echo "DB_NAME=postgres"
echo "DB_USER=postgres"
echo "DB_PASSWORD=Postgressw"
echo "VECTOR_DIMENSIONS=384"
echo "IVFFLAT_LISTS=100"
echo "EMBEDDING_MODEL=all-MiniLM-L6-v2"
echo "OPENAI_API_KEY=your-openai-api-key"
echo "OPENAI_MODEL=gpt-3.5-turbo"
echo "OPENAI_MAX_TOKENS=500"
echo "OPENAI_TEMPERATURE=0.3"
echo "ENVIRONMENT=production"
echo "LOG_LEVEL=INFO"
echo "BATCH_SIZE=100"
echo ""

echo "🚀 Ready to deploy!"
echo "Run: npx vercel --prod"
echo ""
echo "Or go to https://vercel.com and import your GitHub repository"
