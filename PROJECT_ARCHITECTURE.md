# ChatCore.AI - Proje Mimarisi ve Altyapı Dokümantasyonu

Bu dokümantasyon, ChatCore.AI projesinin tam mimarisini, klasör yapısını ve teknik altyapısını açıklar. ChatGPT'ye projeyi anlatmak için kullanılabilir.

## 📁 Proje Yapısı

```
ChatCore.AI/
├── backend/                          # FastAPI Backend Uygulaması
│   ├── api/                         # API Route modülleri (gelecekte ayrılacak)
│   │   └── __init__.py
│   ├── core/                        # Çekirdek modüller (yeni mimari)
│   │   ├── __init__.py
│   │   ├── config.py                # Pydantic Settings - Environment yönetimi
│   │   ├── database.py              # PostgreSQL async SQLModel setup
│   │   ├── redis_client.py          # Redis async client
│   │   ├── logger.py                # Structured JSON logging
│   │   └── security.py              # Rate limiting, input validation
│   ├── models/                      # SQLModel database modelleri
│   │   ├── __init__.py              # Metadata aggregate (Alembic için)
│   │   ├── user_model.py           # User, UserCreate, UserRead
│   │   ├── conversation_model.py    # Conversation, ConversationCreate, ConversationRead
│   │   ├── message_model.py        # Message, MessageCreate, MessageRead
│   │   ├── refresh_token_model.py  # RefreshToken, token rotation
│   │   ├── session_model.py        # Session tracking
│   │   └── document_model.py       # Document (JSONB) - company data
│   ├── services/                    # İş mantığı servisleri
│   │   ├── __init__.py
│   │   └── cache_service.py        # Redis cache wrapper
│   ├── scripts/                     # Yardımcı scriptler
│   │   ├── __init__.py
│   │   ├── migrate_tinydb_to_postgresql.py  # TinyDB → PostgreSQL migration
│   │   ├── seed_users.py            # Default user seeding
│   │   └── migrate.py               # Alembic helper
│   ├── alembic/                     # Database migrations
│   │   ├── env.py                   # Alembic async config
│   │   ├── script.py.mako           # Migration template
│   │   └── versions/                # Migration files
│   ├── data/                        # JSON data files (migration için)
│   │   ├── employees.json
│   │   ├── departments.json
│   │   ├── projects.json
│   │   ├── procedures.json
│   │   └── sessions.json            # TinyDB data (migration için)
│   ├── tests/                       # Pytest testleri
│   │   ├── __init__.py
│   │   ├── test_ai_service.py
│   │   ├── test_auth.py
│   │   ├── test_security.py
│   │   └── test_session_manager.py
│   ├── logs/                        # Log dosyaları
│   │   ├── api.log
│   │   ├── errors.log
│   │   └── security.log
│   ├── main.py                      # FastAPI ana uygulama (entry point)
│   ├── auth.py                      # JWT authentication (legacy)
│   ├── ai_service.py                # AI provider integration (legacy)
│   ├── rag_service.py               # RAG pipeline (legacy)
│   ├── session_manager.py           # Session management (legacy - TinyDB)
│   ├── user_manager.py              # User management (legacy - TinyDB)
│   ├── config.py                    # Config (legacy - backward compat)
│   ├── logger.py                    # Logger (legacy - backward compat)
│   ├── security.py                  # Security (legacy - backward compat)
│   ├── alembic.ini                  # Alembic configuration
│   ├── requirements.txt             # Eski dependencies
│   ├── requirements-refactored.txt  # Yeni dependencies (PostgreSQL, Redis)
│   ├── .env.example                 # Environment variables template
│   ├── REFACTORING_DB.md            # Database migration guide
│   ├── DB_IMPLEMENTATION_SUMMARY.md # Database implementation summary
│   └── REFACTORING_SUMMARY.md       # Genel refactoring özeti
│
├── frontend/                         # Streamlit Frontend
│   ├── app.py                       # Ana Streamlit uygulaması
│   └── static/
│       └── styles.css               # CSS stilleri
│
├── docker-compose.yml                # Docker services (PostgreSQL + Redis)
├── README.md                         # Genel proje dokümantasyonu
├── PROJECT_ANALYSIS.md               # Proje analizi
├── CHATGPT_PROMPT.md                # ChatGPT prompt'u
├── baslat.bat                        # Windows başlatma scripti
├── baslat.sh                         # Linux/macOS başlatma scripti
└── kurulum*.bat/sh                   # Kurulum scriptleri (AI provider'a göre)

```

## 🏗️ Mimari Katmanlar

### 1. Core Layer (backend/core/)
**Amaç**: Uygulamanın çekirdek altyapısı

- **config.py**: Pydantic Settings ile environment variable yönetimi
  - PostgreSQL, Redis, AI provider, security ayarları
  - Validation ve type safety
  
- **database.py**: PostgreSQL async bağlantı yönetimi
  - SQLModel async engine
  - `get_async_session()` dependency
  - `init_db()` tablo oluşturma
  
- **redis_client.py**: Redis async client
  - Connection pooling
  - Async operations
  
- **logger.py**: Structured JSON logging
  - Prometheus-ready format
  - Error categories
  - Security event logging
  
- **security.py**: Güvenlik modülleri
  - Redis-backed rate limiting
  - Input validation
  - Security headers

### 2. Models Layer (backend/models/)
**Amaç**: Database schema tanımları (SQLModel)

- **user_model.py**: User, UserCreate, UserRead
  - Password hashing (PBKDF2-HMAC-SHA256)
  - Relationships: conversations, refresh_tokens, sessions, messages
  
- **conversation_model.py**: Conversation model
  - Short ID (URL-friendly)
  - message_count tracking
  - Updated_at indexing
  
- **message_model.py**: Message model
  - RAG metadata (used_documents, token_count)
  - Role enum (user/assistant)
  
- **refresh_token_model.py**: JWT refresh tokens
  - Token rotation (parent_id)
  - Expiry tracking
  
- **session_model.py**: User sessions
  - access_jti tracking
  - last_activity updates
  
- **document_model.py**: Company data storage
  - JSONB storage
  - GIN indexes for queries
  - doc_type enum (employee, department, project, procedure)

### 3. Services Layer (backend/services/)
**Amaç**: İş mantığı servisleri

- **cache_service.py**: Redis cache wrapper
  - AI response caching
  - Session caching
  - User caching (get_user_cache, set_user_cache, invalidate_user_cache)
  - Rate limiting support

### 4. API Layer (backend/api/)
**Amaç**: API route'ları (gelecekte buraya taşınacak)

- Şu anda `main.py` içinde, refactoring sonrası buraya taşınacak

### 5. Legacy Layer (backend/)
**Amaç**: Eski kod (backward compatibility için)

- **main.py**: FastAPI ana uygulama
  - Tüm endpoint'ler burada
  - Legacy TinyDB kullanımı
  - Refactoring sonrası async'e çevrilecek
  
- **auth.py**: JWT authentication (legacy)
- **ai_service.py**: AI provider integration (legacy)
- **rag_service.py**: RAG pipeline (legacy)
- **session_manager.py**: TinyDB session management (legacy)
- **user_manager.py**: TinyDB user management (legacy)

## 🔄 Veritabanı Mimarisı

### PostgreSQL Schema

```
users
├── id (PK)
├── username (unique, indexed)
├── password_hash
├── salt
├── email
├── is_active
├── is_admin
├── created_at (timezone-aware)
└── updated_at (timezone-aware)
    ├── → conversations (1:N, CASCADE DELETE)
    ├── → messages (1:N, CASCADE DELETE)
    ├── → sessions (1:N, CASCADE DELETE)
    └── → refresh_tokens (1:N, CASCADE DELETE)

conversations
├── id (PK)
├── conversation_id (unique, indexed, short ID)
├── user_id (FK → users.id, indexed)
├── title
├── is_active
├── message_count
├── created_at (timezone-aware)
└── updated_at (timezone-aware, indexed)
    └── → messages (1:N, CASCADE DELETE)

messages
├── id (PK)
├── message_id (unique, indexed, short ID)
├── conversation_id (FK → conversations.id, indexed)
├── user_id (FK → users.id, indexed)
├── role (enum: user, assistant)
├── content (Text)
├── used_documents (JSONB - RAG metadata)
├── token_count
└── created_at (timezone-aware, indexed)

refresh_tokens
├── id (PK)
├── token_hash (unique, indexed)
├── user_id (FK → users.id, indexed)
├── issued_at (timezone-aware)
├── expires_at (timezone-aware, indexed)
├── revoked (boolean, indexed)
└── parent_id (FK → refresh_tokens.id, nullable)

sessions
├── id (PK)
├── user_id (FK → users.id, indexed)
├── access_jti (unique, indexed)
├── user_agent
├── ip_address
├── created_at (timezone-aware)
├── last_activity (timezone-aware, indexed)
└── revoked (boolean, indexed)

documents
├── id (PK)
├── doc_type (enum: employee, department, project, procedure, indexed)
├── body (JSONB, GIN indexed)
├── created_at (timezone-aware, indexed)
└── updated_at (timezone-aware)
```

### Indexes

- **users**: username (unique)
- **conversations**: user_id, updated_at, conversation_id (unique)
- **messages**: conversation_id, created_at, user_id, message_id (unique)
- **refresh_tokens**: user_id, expires_at, revoked, token_hash (unique)
- **sessions**: user_id, last_activity, access_jti (unique), revoked
- **documents**: doc_type, created_at, body (GIN for JSONB queries)

## 🔐 Güvenlik Mimarisi

### Authentication Flow
1. User login → JWT access token (24h) + refresh token (30 days)
2. Access token → API requests (Bearer token)
3. Token expiry → Refresh token ile yenileme
4. Refresh token rotation → Parent-child relationship

### Password Security
- **Algorithm**: PBKDF2-HMAC-SHA256
- **Iterations**: 100,000
- **Salt**: 16-byte random (hex encoded)
- **Storage**: password_hash + salt in database

### Rate Limiting
- **Backend**: Redis-backed
- **Keys**: `rate:{user_id}:{ip}`
- **Default**: 60 requests / 60 seconds
- **Login**: 20 requests / 60 seconds (strict)

### Input Validation
- XSS pattern detection (log only, don't block in prompts)
- SQL injection pattern detection (log only)
- Length validation (MAX_INPUT_LENGTH: 5000 chars)
- Username normalization (casefold + strip)

### Security Headers
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Strict-Transport-Security: max-age=31536000
- Referrer-Policy: strict-origin-when-cross-origin
- Content-Security-Policy: (configured)

## 🚀 AI & RAG Mimarisi

### AI Providers
- **Gemini**: Google Gemini API (default)
- **OpenAI**: GPT models
- **Azure**: Azure OpenAI
- **Ollama**: Local models
- **Hugging Face**: Inference API

### RAG Pipeline
1. **Vector Store**: FAISS (persistent index)
2. **Embeddings**: OpenAI or SentenceTransformers
3. **Retrieval**: 
   - Semantic search (FAISS similarity)
   - Hybrid search (dense + BM25) - planned
   - Re-ranking - planned
4. **Context Formatting**: Type-aware formatting (employee, department, project, procedure)
5. **Response Generation**: AI provider with context

### Caching
- **Redis**: AI response cache
- **Key**: `ai_cache:{hash(prompt+provider+user_id+context)}`
- **TTL**: 3600 seconds (1 hour)
- **User-specific**: Per-user cache (user_id in key)

## 📊 Logging & Monitoring

### Log Structure
- **Format**: JSON (structured)
- **Levels**: DEBUG, INFO, WARNING, ERROR
- **Files**:
  - `api.log`: General API logs
  - `errors.log`: Error logs
  - `security.log`: Security events

### Log Events
- **Request**: endpoint, method, user_id, response_time, status_code
- **Error**: endpoint, error_type, error_category, error_message
- **Security**: event_type, description, user_id, ip_address
- **Chat**: user_id, query_preview, response_length, response_time, conversation_id

### Metrics (Planned)
- Prometheus metrics endpoint (`/metrics`)
- Request latency
- RAG hit rate
- Token usage
- Error rates

## 🔄 Migration Stratejisi

### Phase 1: Parallel Operation (Current)
- Old code runs alongside new code
- Gradual migration endpoint by endpoint
- Both databases maintained (TinyDB + PostgreSQL)

### Phase 2: Full Migration
- Switch all endpoints to async
- Remove TinyDB dependency
- Remove old files

### Phase 3: Enhancements
- Celery workers for index rebuild
- BM25 hybrid retrieval
- Prometheus metrics dashboard

## 🐳 Docker & Deployment

### Services
- **PostgreSQL**: Database (port 5432)
- **Redis**: Cache & rate limiting (port 6379)
- **Backend**: FastAPI (port 8000)
- **Frontend**: Streamlit (port 8501)

### docker-compose.yml
```yaml
services:
  postgres:
    image: postgres:15-alpine
    healthcheck: enabled
    volumes: postgres_data
  
  redis:
    image: redis:7-alpine
    healthcheck: enabled
    volumes: redis_data
```

## 📦 Dependencies

### Core
- FastAPI: Web framework
- SQLModel: Database ORM
- asyncpg: PostgreSQL async driver
- redis: Redis client
- Alembic: Database migrations

### AI & RAG
- langchain: LLM framework
- faiss-cpu: Vector store
- sentence-transformers: Embeddings
- openai: OpenAI API
- google-generativeai: Gemini API

### Frontend
- streamlit: Web UI framework

### Development
- pytest: Testing
- pytest-asyncio: Async testing

## 🔧 Environment Variables

### Database
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_HOST`: Redis host
- `REDIS_PORT`: Redis port
- `REDIS_DB`: Redis database number

### Security
- `SECRET_KEY`: JWT secret key
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Access token expiry (default: 1440)
- `REFRESH_TOKEN_EXPIRE_DAYS`: Refresh token expiry (default: 30)

### Application
- `APP_NAME`: Application name
- `COMPANY_NAME`: Company name
- `ENVIRONMENT`: development/staging/production
- `ALLOWED_ORIGINS`: CORS origins (comma-separated)

### AI Provider
- `AI_PROVIDER`: GEMINI/OPENAI/AZURE/OLLAMA/HUGGINGFACE
- `GEMINI_API_KEY`: Gemini API key
- `OPENAI_API_KEY`: OpenAI API key
- etc.

## 🚦 API Endpoints

### Authentication
- `POST /api/login`: User login (JWT + refresh token)
- `POST /api/logout`: User logout

### Chat
- `POST /api/chat`: Send chat message
- `POST /api/ask`: RAG query

### Conversations
- `GET /api/conversations`: List user conversations
- `POST /api/conversations/new`: Create new conversation
- `POST /api/conversations/{id}/switch`: Switch active conversation
- `DELETE /api/conversations/{id}`: Delete conversation
- `GET /api/conversation/{id}/restore`: Restore session from conversation

### Sessions
- `GET /api/sessions/{session_id}`: Get session data
- `DELETE /api/sessions/{session_id}`: Clear session

### Data
- `GET /api/employees`: Get employees
- `GET /api/departments`: Get departments
- `GET /api/projects`: Get projects
- `GET /api/procedures`: Get procedures
- `GET /api/procedures/new`: Get new procedures

### Analytics
- `GET /api/stats`: Get statistics
- `GET /api/status`: Health check

## 🧪 Testing

### Test Structure
- `tests/test_auth.py`: Authentication tests
- `tests/test_security.py`: Security tests
- `tests/test_ai_service.py`: AI service tests
- `tests/test_session_manager.py`: Session tests

### Running Tests
```bash
pytest backend/tests/
```

## 📚 Documentation Files

- **README.md**: Genel proje dokümantasyonu
- **REFACTORING_DB.md**: Database migration guide
- **DB_IMPLEMENTATION_SUMMARY.md**: Database implementation summary
- **REFACTORING_SUMMARY.md**: Genel refactoring özeti
- **PROJECT_ANALYSIS.md**: Proje analizi
- **CHATGPT_PROMPT.md**: ChatGPT prompt'u

## 🔄 Current State & Future

### Completed ✅
- Database models (SQLModel)
- Core infrastructure (database, redis, logger, security)
- Migration scripts (TinyDB → PostgreSQL)
- Seed scripts
- Docker setup
- Redis cache service

### In Progress 🔄
- API routes migration to async
- Session manager migration to PostgreSQL
- Frontend async updates

### Planned 📋
- Celery workers
- BM25 hybrid retrieval
- Prometheus metrics
- Frontend UX improvements

## 💡 Key Design Decisions

1. **Async First**: All new code uses async/await
2. **SQLModel**: Type-safe ORM with Pydantic integration
3. **Redis**: Centralized caching and rate limiting
4. **Structured Logging**: JSON format for log aggregation
5. **CASCADE DELETE**: User deletion removes all related data
6. **Idempotent Migrations**: Safe to run multiple times
7. **Backward Compatibility**: Legacy code maintained during migration
8. **Security by Default**: Rate limiting, input validation, secure headers

## 🎯 Architecture Principles

1. **Separation of Concerns**: Core, Models, Services, API layers
2. **Dependency Injection**: Database sessions, Redis clients
3. **Type Safety**: Pydantic models, type hints everywhere
4. **Fail-Safe**: Redis failures don't break the app (fail-open)
5. **Observability**: Structured logging, metrics ready
6. **Scalability**: Async operations, connection pooling
7. **Security**: Multi-layer security (auth, rate limiting, validation)

---

**Bu dokümantasyon ChatGPT'ye projeyi anlatmak için kullanılabilir. Tüm mimari detaylar, klasör yapısı ve teknik altyapı burada açıklanmıştır.**



