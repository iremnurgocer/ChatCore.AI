# ChatCore.AI - ChatGPT İçin Kapsamlı Proje Açıklama Prompt'u

Aşağıdaki metni ChatGPT'ye kopyala-yapıştır yaparak projeyi anlatabilirsin:

---

**ChatCore.AI Projesi - Tam Mimari ve Altyapı Açıklaması**

Merhaba! ChatCore.AI adında bir FastAPI + Streamlit tabanlı kurumsal AI chat uygulaması üzerinde çalışıyorum. Proje şu anda TinyDB'den PostgreSQL'e geçiş yapıyor. Size projenin tam mimarisini ve altyapısını anlatmak istiyorum.

## 📋 Proje Genel Bakış

ChatCore.AI, şirket içi verilerine (çalışanlar, departmanlar, projeler, prosedürler) dayalı RAG (Retrieval-Augmented Generation) teknolojisi kullanan bir AI asistanı. ChatGPT benzeri conversation yönetimi, çoklu AI provider desteği, ve enterprise-grade güvenlik özellikleri içeriyor.

**Teknoloji Stack:**
- Backend: FastAPI (Python 3.8+), async/await pattern
- Frontend: Streamlit (Python)
- Database: PostgreSQL 15 (migration yapılıyor), TinyDB (legacy)
- Cache: Redis 7
- AI: LangChain, FAISS, OpenAI, Gemini, Azure, Ollama
- Migrations: Alembic (async SQLModel support)
- Authentication: JWT + Refresh Tokens

## 📁 Klasör Yapısı ve Mimari

```
ChatCore.AI/
├── backend/                          # FastAPI Backend
│   ├── core/                        # ✅ YENİ: Çekirdek modüller (production-ready)
│   │   ├── config.py               # Pydantic Settings - env yönetimi
│   │   ├── database.py             # PostgreSQL async SQLModel setup
│   │   ├── redis_client.py         # Redis async client, connection pooling
│   │   ├── logger.py               # Structured JSON logging (Prometheus-ready)
│   │   └── security.py             # Redis-backed rate limiting, input validation
│   ├── models/                      # ✅ YENİ: SQLModel database modelleri
│   │   ├── __init__.py             # Metadata aggregate (Alembic için)
│   │   ├── user_model.py           # User, UserCreate, UserRead
│   │   ├── conversation_model.py  # Conversation, ConversationCreate, ConversationRead
│   │   ├── message_model.py        # Message, MessageCreate, MessageRead
│   │   ├── refresh_token_model.py # RefreshToken, token rotation
│   │   ├── session_model.py       # Session tracking
│   │   └── document_model.py      # Document (JSONB) - company data storage
│   ├── services/                    # ✅ YENİ: İş mantığı servisleri
│   │   └── cache_service.py       # Redis cache wrapper
│   ├── scripts/                     # ✅ YENİ: Yardımcı scriptler
│   │   ├── migrate_tinydb_to_postgresql.py  # Idempotent migration
│   │   ├── seed_users.py           # Default user seeding
│   │   └── migrate.py              # Alembic helper
│   ├── alembic/                     # ✅ YENİ: Database migrations
│   │   ├── env.py                  # Alembic async config
│   │   ├── script.py.mako           # Migration template
│   │   └── versions/                # Migration files
│   ├── api/                         # 🔄 GELECEK: API routes (henüz boş)
│   ├── tests/                       # Pytest testleri
│   ├── data/                        # JSON data files (migration için)
│   │   ├── employees.json
│   │   ├── departments.json
│   │   ├── projects.json
│   │   ├── procedures.json
│   │   └── sessions.json            # TinyDB data (migration için)
│   ├── main.py                      # ⚠️ LEGACY: FastAPI ana uygulama (async'e çevrilecek)
│   ├── auth.py                      # ⚠️ LEGACY: JWT authentication (refresh tokens eklenecek)
│   ├── ai_service.py                # ⚠️ LEGACY: AI provider integration
│   ├── rag_service.py               # ⚠️ LEGACY: RAG pipeline
│   ├── session_manager.py           # ⚠️ LEGACY: TinyDB session management
│   ├── user_manager.py              # ⚠️ LEGACY: TinyDB user management
│   ├── config.py                    # ⚠️ LEGACY: Backward compatibility
│   ├── logger.py                    # ⚠️ LEGACY: Backward compatibility
│   ├── security.py                  # ⚠️ LEGACY: Backward compatibility
│   ├── alembic.ini                  # Alembic configuration
│   ├── requirements.txt             # Eski dependencies
│   ├── requirements-refactored.txt  # ✅ YENİ: PostgreSQL, Redis, async dependencies
│   └── .env.example                 # Environment variables template
├── frontend/                         # Streamlit Frontend
│   ├── app.py                       # Ana Streamlit uygulaması
│   └── static/styles.css            # CSS stilleri
├── docker-compose.yml               # ✅ YENİ: PostgreSQL + Redis services
├── PROJECT_ARCHITECTURE.md          # ✅ YENİ: Detaylı mimari dokümantasyon
├── CHATGPT_PROJECT_EXPLANATION.md    # ✅ YENİ: ChatGPT için prompt
└── README.md                         # Genel proje dokümantasyonu
```

## 🏗️ Mimari Katmanlar

### 1. Core Layer (`backend/core/`) - ✅ YENİ MİMARİ

**config.py** - Pydantic Settings ile environment variable yönetimi:
- PostgreSQL connection (asyncpg)
- Redis connection
- AI provider settings
- Security settings (JWT secrets, token expiry)
- CORS origins (no wildcard in production)
- Logging configuration

**database.py** - PostgreSQL async SQLModel setup:
- `init_database()`: Async ve sync engine oluşturma
- `get_async_session()`: FastAPI dependency (async session)
- `init_db()`: Tablo oluşturma (startup'ta çağrılır)
- SQLModel metadata aggregation

**redis_client.py** - Redis async client:
- Connection pooling (max 50 connections)
- Async operations
- Graceful error handling (fail-open)

**logger.py** - Structured JSON logging:
- Prometheus-ready format
- Error categories (AUTH_ERROR, VALIDATION_ERROR, vb.)
- Security event logging
- Request/response logging

**security.py** - Güvenlik modülleri:
- Redis-backed rate limiting (async)
- Input validation (XSS, SQL injection detection)
- Security headers (CSP, HSTS, Referrer-Policy)
- Username/email validation

### 2. Models Layer (`backend/models/`) - ✅ YENİ MİMARİ

SQLModel ile type-safe database schema:

**user_model.py**:
- User (id, username unique, password_hash, salt, is_active, is_admin, timestamps)
- Relationships: conversations, messages, sessions, refresh_tokens
- CASCADE DELETE (user silinince tüm ilgili data silinir)

**conversation_model.py**:
- Conversation (id, conversation_id short unique, user_id FK, title, message_count, timestamps)
- Indexes: user_id, updated_at, conversation_id (unique)
- Relationship: messages (CASCADE DELETE)

**message_model.py**:
- Message (id, message_id short unique, conversation_id FK, user_id FK, role enum, content Text, timestamps)
- RAG metadata: used_documents (JSONB), token_count
- Indexes: conversation_id, created_at, user_id, message_id (unique)

**refresh_token_model.py**:
- RefreshToken (id, token_hash unique, user_id FK, issued_at, expires_at, revoked bool, parent_id FK nullable)
- Token rotation support (parent-child relationship)
- Indexes: user_id, expires_at, revoked

**session_model.py**:
- Session (id, user_id FK, access_jti unique, user_agent, ip_address, timestamps, revoked bool)
- Indexes: user_id, last_activity, access_jti (unique), revoked

**document_model.py**:
- Document (id, doc_type enum, body JSONB, timestamps)
- doc_type: employee, department, project, procedure
- GIN index on body (JSONB queries için)
- Indexes: doc_type, created_at

### 3. Services Layer (`backend/services/`) - ✅ YENİ MİMARİ

**cache_service.py** - Redis cache wrapper:
- AI response caching (`get_ai_response`, `set_ai_response`)
- Session caching (`get_session`, `set_session`, `delete_session`)
- User caching (`get_user_cache`, `set_user_cache`, `invalidate_user_cache`)
- JSON serialization/deserialization
- TTL management

### 4. Legacy Layer (`backend/`) - ⚠️ MİGRASYON YAPILACAK

**main.py** - FastAPI ana uygulama:
- Tüm endpoint'ler burada (henüz sync, async'e çevrilecek)
- Legacy TinyDB kullanımı
- Rate limiting (memory-based, Redis'e geçilecek)

**auth.py** - JWT authentication:
- Token oluşturma/doğrulama
- Refresh token desteği eklenecek

**ai_service.py** - AI provider integration:
- Multi-provider support (Gemini, OpenAI, Azure, Ollama, Hugging Face)
- RAG integration
- Fallback mechanism
- Cache support

**rag_service.py** - RAG pipeline:
- Vector store (FAISS)
- Multi-query expansion
- Re-ranking
- Context formatting

**session_manager.py** - TinyDB session management:
- Conversation management
- Message storage
- PostgreSQL'e migrate edilecek

**user_manager.py** - TinyDB user management:
- User CRUD operations
- Password hashing
- PostgreSQL'e migrate edilecek

## 🔄 Veritabanı Mimarisi

### PostgreSQL Schema (✅ YENİ)

```
users (PK: id)
├── username (unique, indexed)
├── password_hash (PBKDF2-HMAC-SHA256)
├── salt (hex)
├── email
├── is_active
├── is_admin
├── created_at (timezone-aware)
└── updated_at (timezone-aware)
    ├── → conversations (1:N, CASCADE DELETE)
    ├── → messages (1:N, CASCADE DELETE)
    ├── → sessions (1:N, CASCADE DELETE)
    └── → refresh_tokens (1:N, CASCADE DELETE)

conversations (PK: id)
├── conversation_id (unique, indexed, short ID)
├── user_id (FK → users.id, indexed)
├── title
├── is_active
├── message_count
├── created_at (timezone-aware)
└── updated_at (timezone-aware, indexed)
    └── → messages (1:N, CASCADE DELETE)

messages (PK: id)
├── message_id (unique, indexed, short ID)
├── conversation_id (FK → conversations.id, indexed)
├── user_id (FK → users.id, indexed)
├── role (enum: user, assistant)
├── content (Text)
├── used_documents (JSONB - RAG metadata)
├── token_count
└── created_at (timezone-aware, indexed)

refresh_tokens (PK: id)
├── token_hash (unique, indexed)
├── user_id (FK → users.id, indexed)
├── issued_at (timezone-aware)
├── expires_at (timezone-aware, indexed)
├── revoked (boolean, indexed)
└── parent_id (FK → refresh_tokens.id, nullable)

sessions (PK: id)
├── user_id (FK → users.id, indexed)
├── access_jti (unique, indexed)
├── user_agent
├── ip_address
├── created_at (timezone-aware)
├── last_activity (timezone-aware, indexed)
└── revoked (boolean, indexed)

documents (PK: id)
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
- **Backend**: Redis-backed (async)
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
1. **Vector Store**: FAISS (persistent index - planned)
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

### Core (Yeni)
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
- `DATABASE_URL`: PostgreSQL connection string (postgresql+asyncpg://...)
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
- `ALLOWED_ORIGINS`: CORS origins (comma-separated, no wildcard in production)

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
- **PROJECT_ARCHITECTURE.md**: Detaylı mimari dokümantasyon
- **REFACTORING_DB.md**: Database migration guide
- **DB_IMPLEMENTATION_SUMMARY.md**: Database implementation summary
- **REFACTORING_SUMMARY.md**: Genel refactoring özeti
- **CHATGPT_PROJECT_EXPLANATION.md**: ChatGPT için prompt

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

Proje hakkında sorularınız varsa veya belirli bir konuda yardım istiyorsanız sorabilirsiniz!
