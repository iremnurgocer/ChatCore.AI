# ChatCore.AI - ChatGPT İçin Proje Açıklama Prompt'u

Aşağıdaki metni ChatGPT'ye kopyala-yapıştır yaparak projeyi anlatabilirsin:

---

**ChatCore.AI Projesi - Mimari ve Altyapı Açıklaması**

Merhaba! ChatCore.AI adında bir FastAPI + Streamlit tabanlı kurumsal AI chat uygulaması üzerinde çalışıyorum. Projenin mimarisini ve altyapısını anlatmak istiyorum.

## Proje Genel Bakış

ChatCore.AI, şirket içi verilerine (çalışanlar, departmanlar, projeler, prosedürler) dayalı RAG (Retrieval-Augmented Generation) teknolojisi kullanan bir AI asistanı. Backend FastAPI, frontend Streamlit ile yapılmış. Şu anda TinyDB'den PostgreSQL'e geçiş yapıyoruz.

## Klasör Yapısı

```
ChatCore.AI/
├── backend/                    # FastAPI Backend
│   ├── core/                  # Çekirdek modüller (yeni mimari)
│   │   ├── config.py         # Pydantic Settings - env yönetimi
│   │   ├── database.py       # PostgreSQL async SQLModel setup
│   │   ├── redis_client.py   # Redis async client
│   │   ├── logger.py         # Structured JSON logging
│   │   └── security.py       # Rate limiting, validation
│   ├── models/               # SQLModel database modelleri
│   │   ├── user_model.py     # User, UserCreate, UserRead
│   │   ├── conversation_model.py
│   │   ├── message_model.py
│   │   ├── refresh_token_model.py
│   │   ├── session_model.py
│   │   └── document_model.py # JSONB - company data
│   ├── services/             # İş mantığı servisleri
│   │   └── cache_service.py # Redis cache wrapper
│   ├── scripts/              # Yardımcı scriptler
│   │   ├── migrate_tinydb_to_postgresql.py  # Migration
│   │   ├── seed_users.py     # Default users
│   │   └── migrate.py        # Alembic helper
│   ├── alembic/              # Database migrations
│   ├── api/                  # API routes (gelecekte)
│   ├── tests/                # Pytest testleri
│   ├── data/                 # JSON data files
│   ├── main.py               # FastAPI ana uygulama (legacy)
│   ├── auth.py               # JWT auth (legacy)
│   ├── ai_service.py         # AI providers (legacy)
│   ├── rag_service.py        # RAG pipeline (legacy)
│   ├── session_manager.py    # TinyDB sessions (legacy)
│   └── user_manager.py       # TinyDB users (legacy)
├── frontend/                 # Streamlit Frontend
│   ├── app.py
│   └── static/styles.css
└── docker-compose.yml        # PostgreSQL + Redis

```

## Mimari Katmanlar

### 1. Core Layer (`backend/core/`)
- **config.py**: Pydantic Settings ile environment variable yönetimi (PostgreSQL, Redis, AI provider, security)
- **database.py**: PostgreSQL async SQLModel setup, `get_async_session()` dependency, `init_db()` tablo oluşturma
- **redis_client.py**: Redis async client, connection pooling
- **logger.py**: Structured JSON logging (Prometheus-ready)
- **security.py**: Redis-backed rate limiting, input validation, security headers

### 2. Models Layer (`backend/models/`)
SQLModel ile database schema:
- **User**: password_hash (PBKDF2), salt, relationships (conversations, messages, sessions, refresh_tokens)
- **Conversation**: short ID (URL-friendly), message_count, updated_at indexed
- **Message**: role enum, RAG metadata (used_documents, token_count)
- **RefreshToken**: token rotation (parent_id), expiry tracking
- **Session**: access_jti tracking, last_activity updates
- **Document**: JSONB storage, GIN indexes, doc_type enum

### 3. Services Layer (`backend/services/`)
- **cache_service.py**: Redis cache wrapper (AI responses, sessions, users)

### 4. Legacy Layer (`backend/`)
- **main.py**: FastAPI ana uygulama, tüm endpoint'ler burada (henüz async'e çevrilmedi)
- **auth.py, ai_service.py, rag_service.py**: Eski kod (backward compatibility için)

## Veritabanı Mimarisi

**PostgreSQL Schema:**
- `users` → `conversations` (1:N, CASCADE DELETE)
- `users` → `messages` (1:N, CASCADE DELETE)
- `users` → `sessions` (1:N, CASCADE DELETE)
- `users` → `refresh_tokens` (1:N, CASCADE DELETE)
- `conversations` → `messages` (1:N, CASCADE DELETE)
- `documents`: JSONB storage (employees, departments, projects, procedures)

**Indexes:** username (unique), conversation_id (unique), message_id (unique), user_id, updated_at, created_at, expires_at, revoked, doc_type, body (GIN for JSONB)

## Güvenlik

- **Authentication**: JWT access token (24h) + refresh token (30 days) with rotation
- **Password**: PBKDF2-HMAC-SHA256, 100k iterations, 16-byte salt
- **Rate Limiting**: Redis-backed, 60 req/min default, 20 req/min for login
- **Input Validation**: XSS/SQL pattern detection (log only), length validation
- **Security Headers**: CSP, HSTS, Referrer-Policy, X-Frame-Options

## AI & RAG

- **Providers**: Gemini (default), OpenAI, Azure, Ollama, Hugging Face
- **Vector Store**: FAISS (persistent index)
- **Embeddings**: OpenAI or SentenceTransformers
- **Retrieval**: Semantic search (FAISS), hybrid search planned (BM25 + dense)
- **Caching**: Redis cache for AI responses (user-specific)

## Deployment

- **Docker**: PostgreSQL 15 + Redis 7 (docker-compose.yml)
- **Ports**: Backend 8000, Frontend 8501, PostgreSQL 5432, Redis 6379
- **Migrations**: Alembic (async SQLModel support)
- **Environment**: `.env.example` template

## Migration Stratejisi

**Phase 1 (Current)**: Parallel operation - old code + new code, both databases
**Phase 2**: Full migration - async endpoints, remove TinyDB
**Phase 3**: Enhancements - Celery workers, BM25 hybrid retrieval, Prometheus

## Önemli Özellikler

- ✅ Async-first architecture (yeni kod)
- ✅ Type-safe (SQLModel + Pydantic)
- ✅ Redis caching & rate limiting
- ✅ Structured JSON logging
- ✅ CASCADE DELETE relationships
- ✅ Idempotent migrations
- ✅ Backward compatibility (legacy code maintained)

## Teknik Stack

- **Backend**: FastAPI, SQLModel, asyncpg, Redis, Alembic
- **AI**: LangChain, FAISS, OpenAI, Gemini
- **Frontend**: Streamlit
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Testing**: pytest, pytest-asyncio

## Durum

- ✅ Database models ve core infrastructure tamamlandı
- ✅ Migration scriptleri hazır
- 🔄 API routes async'e çevriliyor
- 📋 Frontend async güncellemeleri planlanıyor

Bu proje hakkında sorularınız varsa veya belirli bir konuda yardım istiyorsanız sorabilirsiniz!

---

**Not**: Detaylı mimari dokümantasyon için `PROJECT_ARCHITECTURE.md` dosyasına bakabilirsiniz.



