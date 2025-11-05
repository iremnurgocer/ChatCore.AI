# Database Migration Guide - TinyDB to PostgreSQL

This guide explains how to migrate ChatCore.AI from TinyDB to PostgreSQL.

## Prerequisites

- Python 3.10+
- PostgreSQL 15+ (or Docker)
- Redis (or Docker)
- Alembic installed

## Quick Start

### 1. Setup Environment

```bash
# Copy environment template
cp backend/.env.example backend/.env

# Edit backend/.env and set:
# DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/chatcore
# REDIS_HOST=localhost
# REDIS_PORT=6379
```

### 2. Start Services with Docker

```bash
# Start PostgreSQL and Redis
docker compose up -d postgres redis

# Wait for services to be healthy (check with: docker compose ps)
```

### 3. Install Dependencies

```bash
pip install -r backend/requirements-refactored.txt
```

### 4. Create Database Tables

```bash
cd backend

# Initialize Alembic and create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head

# Or use the helper script
python scripts/migrate.py init
python scripts/migrate.py upgrade
```

### 5. Seed Default Users

```bash
python scripts/seed_users.py
```

This creates:
- `admin` / `1234` (admin)
- `user2` / `1234` (user)
- `user3` / `12345` (user)

### 6. Migrate TinyDB Data

```bash
python scripts/migrate_tinydb_to_postgresql.py
```

This script:
- Migrates users from TinyDB
- Migrates conversations and messages
- Migrates sessions
- Migrates company documents (employees, departments, projects, procedures)
- Is idempotent (safe to run multiple times)

### 7. Verify Migration

```bash
# Check database tables
psql -U postgres -d chatcore -c "SELECT COUNT(*) FROM users;"
psql -U postgres -d chatcore -c "SELECT COUNT(*) FROM conversations;"
psql -U postgres -d chatcore -c "SELECT COUNT(*) FROM messages;"
```

## Database Schema

### Tables

- **users**: User accounts with password hashes
- **conversations**: Chat conversations (per user)
- **messages**: Chat messages (linked to conversations)
- **sessions**: Active user sessions
- **refresh_tokens**: JWT refresh tokens
- **documents**: Company data (employees, departments, projects, procedures)

### Relationships

- User → Conversations (1:N, CASCADE DELETE)
- User → Messages (1:N, CASCADE DELETE)
- User → Sessions (1:N, CASCADE DELETE)
- User → RefreshTokens (1:N, CASCADE DELETE)
- Conversation → Messages (1:N, CASCADE DELETE)

### Indexes

- `users.username` (unique)
- `conversations.user_id`, `updated_at`
- `messages.conversation_id`, `created_at`, `user_id`
- `refresh_tokens.user_id`, `expires_at`, `revoked`
- `sessions.user_id`, `last_activity`
- `documents.doc_type`, `created_at` (with GIN index on body)

## Migration Script Details

The migration script (`scripts/migrate_tinydb_to_postgresql.py`) is idempotent:

1. **Users**: Normalizes usernames (casefold), generates password hashes if missing
2. **Conversations**: Maps by conversation_id, preserves timestamps
3. **Messages**: Detects duplicates by hash, preserves order
4. **Sessions**: Maps by access_jti (token hash)
5. **Documents**: Migrates JSON files to documents table

## Redis Integration

Redis is used for:
- Rate limiting keys: `rate:{user_id}:{ip}`
- Session cache: `sess:{user_id}:{access_jti}`
- User cache: `user:{username}` (5 min TTL)
- AI response cache: `ai_cache:{hash}`

## Troubleshooting

### Database Connection Error

```bash
# Check PostgreSQL is running
docker compose ps

# Check connection
psql -U postgres -h localhost -d chatcore
```

### Redis Connection Error

```bash
# Check Redis is running
docker compose ps

# Test Redis
redis-cli ping
```

### Migration Errors

- Check logs for specific table errors
- Ensure database user has CREATE privileges
- Verify DATABASE_URL format: `postgresql+asyncpg://user:pass@host:port/dbname`

### Duplicate Key Errors

The migration script handles duplicates automatically. If you see errors:
- Check if data already exists in PostgreSQL
- Run migration script again (it's idempotent)

## Production Deployment

1. Set strong `SECRET_KEY` in `.env`
2. Use production PostgreSQL with backups
3. Set `ENVIRONMENT=production` in `.env`
4. Configure proper CORS origins (no wildcard)
5. Use Redis password authentication
6. Set up database backups
7. Monitor Redis memory usage

## Rollback

If you need to rollback:

```bash
# Downgrade migrations
alembic downgrade -1

# Or use helper
python scripts/migrate.py downgrade
```

## Next Steps

After migration:
1. Update API routes to use async database sessions
2. Remove TinyDB dependencies
3. Update session_manager to use PostgreSQL
4. Test all endpoints
5. Monitor performance

## Support

For issues, check:
- `backend/logs/` for application logs
- PostgreSQL logs: `docker compose logs postgres`
- Redis logs: `docker compose logs redis`
