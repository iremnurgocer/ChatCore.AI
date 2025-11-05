# ChatCore.AI

Enterprise-grade RAG-powered AI assistant built with FastAPI and Streamlit.

## Overview

ChatCore.AI is a production-ready AI assistant platform that combines Retrieval-Augmented Generation (RAG) with enterprise security, multi-provider AI support, and document management. It provides a ChatGPT-like interface for querying company knowledge bases with persistent conversations, document uploads, and advanced analytics.

## Features

- **RAG Pipeline**: Hybrid retrieval (FAISS + BM25) with cross-encoder re-ranking
- **Multi-Provider AI**: Support for Gemini, OpenAI, Azure OpenAI, Ollama, and Hugging Face
- **Document Management**: Upload and index PDF, DOCX, XLSX, TXT files
- **Conversation Memory**: Persistent conversations with auto-summarization
- **Persona System**: Customizable AI personas (Finance, IT, HR, Legal)
- **Security**: JWT authentication, refresh token rotation, MFA support, rate limiting
- **Analytics**: Usage statistics, knowledge gap detection, intent distribution
- **Per-Department Indexes**: Separate FAISS indexes for department-specific documents

## Project Structure

```
ChatCore.AI/
├── backend/                    # FastAPI backend
│   ├── api/                    # API route modules
│   │   ├── auth_api.py        # Authentication endpoints
│   │   ├── chat_api.py        # Chat endpoints
│   │   ├── files_api.py       # File upload endpoints
│   │   ├── search_api.py      # Search endpoints
│   │   ├── user_api.py        # User preferences endpoints
│   │   └── analytics_api.py   # Analytics endpoints
│   ├── core/                   # Core infrastructure
│   │   ├── config.py          # Configuration management
│   │   ├── database.py        # PostgreSQL async setup
│   │   ├── redis_client.py    # Redis client
│   │   ├── logger.py          # Structured logging
│   │   └── security.py        # Rate limiting, validation
│   ├── models/                 # SQLModel database models
│   │   ├── user_model.py
│   │   ├── conversation_model.py
│   │   ├── message_model.py
│   │   ├── document_model.py
│   │   └── ...
│   ├── services/               # Business logic services
│   │   ├── ai_service.py      # AI provider integration
│   │   ├── rag_service.py     # RAG pipeline
│   │   ├── document_service.py # Document parsing
│   │   ├── session_service.py  # Session management
│   │   └── ...
│   ├── scripts/                # Utility scripts
│   │   ├── seed_users.py      # User seeding
│   │   └── migrate_tinydb_to_postgresql.py
│   ├── workers/                # Celery workers
│   │   └── index_rebuild_worker.py
│   ├── alembic/                # Database migrations
│   ├── data/                   # Data files and uploads
│   ├── main.py                 # FastAPI application
│   └── requirements-refactored.txt
├── frontend/                   # Streamlit frontend
│   ├── app.py                  # Main Streamlit app
│   ├── components/             # UI components
│   │   ├── file_uploader.py
│   │   ├── summary_panel.py
│   │   ├── suggestion_box.py
│   │   └── persona_selector.py
│   └── static/
├── docker-compose.yml          # Docker services (PostgreSQL, Redis)
├── install.bat                 # Windows installation script
├── install.sh                  # Linux/Mac installation script
├── start.bat                   # Windows startup script
├── start.sh                    # Linux/Mac startup script
└── README.md                   # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- PostgreSQL 15+ (or Docker)
- Redis 7+ (or Docker)
- Git

### Quick Install (Windows)

```batch
install.bat
```

### Quick Install (Linux/Mac)

```bash
chmod +x install.sh start.sh
./install.sh
```

### Manual Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ChatCore.AI
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r backend/requirements-refactored.txt
   ```

4. **Configure environment**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your settings
   ```

## Configuration

Edit `backend/.env` with your configuration:

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/chatcore

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30

# AI Provider
AI_PROVIDER=GEMINI
GEMINI_API_KEY=your-gemini-api-key

# CORS
ALLOWED_ORIGINS=http://localhost:8501,http://127.0.0.1:8501

# Application
COMPANY_NAME=YourCompany
ENVIRONMENT=development
```

### Environment Variables

- `DATABASE_URL`: PostgreSQL connection string (asyncpg format)
- `REDIS_HOST`: Redis host address
- `REDIS_PORT`: Redis port number
- `SECRET_KEY`: JWT secret key (change in production)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Access token expiry (default: 15)
- `REFRESH_TOKEN_EXPIRE_DAYS`: Refresh token expiry (default: 30)
- `AI_PROVIDER`: AI provider (GEMINI, OPENAI, AZURE, OLLAMA, HUGGINGFACE)
- `GEMINI_API_KEY`: Google Gemini API key
- `OPENAI_API_KEY`: OpenAI API key (if using OpenAI)
- `AZURE_OPENAI_API_KEY`: Azure OpenAI API key (if using Azure)
- `AZURE_OPENAI_ENDPOINT`: Azure OpenAI endpoint URL
- `ALLOWED_ORIGINS`: Comma-separated list of allowed CORS origins
- `COMPANY_NAME`: Company name for AI prompts
- `ENVIRONMENT`: Environment (development, staging, production)

## Startup

### Using Helper Scripts

**Windows:**
```batch
start.bat
```

**Linux/Mac:**
```bash
./start.sh
```

### Manual Startup

1. **Start PostgreSQL and Redis (Docker)**
   ```bash
   docker compose up -d postgres redis
   ```

2. **Run database migrations**
   ```bash
   cd backend
   alembic upgrade head
   ```

3. **Seed default users**
   ```bash
   python scripts/seed_users.py
   ```

4. **Start backend**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Start frontend** (new terminal)
   ```bash
   cd frontend
   streamlit run app.py
   ```

6. **Access the application**
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Docker Usage

Start PostgreSQL and Redis:
```bash
docker compose up -d
```

View logs:
```bash
docker compose logs -f
```

Stop services:
```bash
docker compose down
```

## Default Users

After seeding, the following users are available:

- Username: `admin`, Password: `1234` (Admin)
- Username: `user2`, Password: `1234` (User)
- Username: `user3`, Password: `12345` (User)

**Security Note**: Change default passwords in production!

## API Endpoints

### Authentication
- `POST /api/login` - User login
- `POST /api/token/refresh` - Refresh access token
- `POST /api/logout` - User logout
- `GET /api/me` - Get current user info

### Chat
- `POST /api/chat` - Send chat message
- `GET /api/conversations` - List conversations
- `POST /api/conversations/new` - Create conversation
- `DELETE /api/conversations/{id}` - Delete conversation

### Files (V2)
- `POST /api/v2/files/upload` - Upload document
- `GET /api/v2/files` - List files
- `DELETE /api/v2/files/{id}` - Delete file

### Search (V2)
- `GET /api/v2/search` - Search documents/conversations
- `GET /api/v2/search/suggestions` - Autocomplete

### User (V2)
- `GET /api/v2/user/profile` - Get profile
- `PUT /api/v2/user/preferences` - Update preferences
- `POST /api/v2/user/mfa/setup` - Setup MFA

### Analytics (V2)
- `GET /api/v2/analytics/stats` - Admin analytics
- `GET /api/v2/analytics/user` - User analytics

Full API documentation: http://localhost:8000/docs

## Troubleshooting

### Database Connection Error

Ensure PostgreSQL is running and `DATABASE_URL` is correct:
```bash
docker compose up -d postgres
```

### Redis Connection Error

Ensure Redis is running:
```bash
docker compose up -d redis
```

### Migration Errors

Reset database (development only):
```bash
cd backend
alembic downgrade base
alembic upgrade head
```

### Port Already in Use

Change ports in startup commands or stop conflicting services.

### Import Errors

Ensure virtual environment is activated and dependencies are installed:
```bash
pip install -r backend/requirements-refactored.txt
```

## Development

### Running Tests

```bash
cd backend
pytest tests/
```

### Code Quality

```bash
# Linting
ruff check backend/

# Type checking
mypy backend/
```

### Database Migrations

Create new migration:
```bash
cd backend
alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
alembic upgrade head
```

## Production Deployment

### Security Checklist

1. Change `SECRET_KEY` to a strong random value
2. Set `ENVIRONMENT=production` in `.env`
3. Configure `ALLOWED_ORIGINS` (no wildcards)
4. Enable HTTPS/TLS
5. Use strong database passwords
6. Enable MFA for admin users
7. Configure firewall rules
8. Set up monitoring and logging

### Environment Variables for Production

```env
ENVIRONMENT=production
SECRET_KEY=<strong-random-key>
ALLOWED_ORIGINS=https://yourdomain.com
DATABASE_URL=postgresql+asyncpg://user:pass@db-host:5432/chatcore
REDIS_HOST=redis-host
```

## License

[Add your license information here]

## Credits

ChatCore.AI - Enterprise RAG-Powered AI Assistant

Built with FastAPI, Streamlit, PostgreSQL, Redis, and FAISS.
