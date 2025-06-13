# 🕷️ Spider Web RAG Application

A production-ready Retrieval-Augmented Generation (RAG) application built with FastAPI, PostgreSQL with pgvector, and Vue.js frontend.

## 🚀 Quick Deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/spider-web-rag)

## ✨ Features

- 🔍 **Semantic Search**: Advanced vector search using pgvector and Sentence Transformers
- 🤖 **RAG Integration**: OpenAI GPT-3.5-turbo for intelligent answer generation
- 🗄️ **Forum Data**: Complete discourse forum with 103+ posts and semantic embeddings
- 🎨 **Modern UI**: Responsive Vue.js frontend with beautiful design
- ⚡ **Fast API**: High-performance FastAPI backend
- 🔒 **Production Ready**: Proper security, error handling, and deployment configuration

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Vue.js        │    │   FastAPI       │    │  PostgreSQL     │
│   Frontend      │───▶│   Backend       │───▶│  + pgvector     │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   OpenAI API    │
                    │   GPT-3.5-turbo │
                    └─────────────────┘
```

## 📋 Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL with pgvector extension
- OpenAI API key

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/spider-web-rag.git
cd spider-web-rag
```

### 2. Setup Environment
```bash
cd Backend
cp .env .env.local  # Create your local environment file
# Edit .env.local with your actual credentials
```

### 3. Install Dependencies
```bash
# Backend
cd Backend
pip install -r requirements.txt

# Frontend
cd ../Frontend
npm install
```

### 4. Run Application
```bash
# Backend (Terminal 1)
cd Backend
uvicorn main:app --reload

# Frontend (Terminal 2)
cd Frontend
npm run dev
```

## 🌐 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions to Vercel.

## 📁 Project Structure

```
spider-web-rag/
├── 🔧 vercel.json              # Vercel deployment config
├── 📝 requirements.txt         # Python dependencies (serverless)
├── 🎨 Frontend/               # Vue.js application
│   ├── src/components/
│   ├── src/resources/
│   └── package.json
├── ⚡ Backend/                # FastAPI application
│   ├── main.py               # Application entry point
│   ├── api/routes.py         # API endpoints
│   ├── database/models.py    # SQLAlchemy models
│   ├── services/             # Business logic
│   └── scripts/              # Utility scripts
└── 📖 DEPLOYMENT.md          # Deployment guide
```

## 🔧 Key Components

### Backend Services
- **Search Service**: Vector similarity search with pgvector
- **OpenAI Service**: RAG answer generation
- **Database Models**: Complete forum schema with embeddings

### Frontend Features
- **Smart Search**: Real-time semantic search interface
- **Image Support**: Upload and analyze images with questions
- **Responsive Design**: Mobile-friendly UI
- **Loading States**: Smooth user experience

## 🗄️ Database Schema

- **Posts**: Forum posts with vector embeddings (384 dimensions)
- **Topics**: Discussion topics with title embeddings
- **Users**: User management and profiles
- **Categories**: Content organization

## 🛡️ Security Features

- Environment variable protection
- CORS configuration
- Input validation with Pydantic
- SQL injection prevention with SQLAlchemy

## 📊 Performance

- **Vector Search**: Sub-second semantic search on 100+ posts
- **RAG Pipeline**: ~2-3 second response time for AI answers
- **Embedding Coverage**: 100% posts with vector embeddings
- **Frontend**: Optimized Vite build with code splitting

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [Deployment Guide](DEPLOYMENT.md)
- [API Documentation](http://localhost:8000/docs) (when running locally)
- [Live Demo](https://your-vercel-app.vercel.app) (after deployment)

---

Built with ❤️ for intelligent information retrieval