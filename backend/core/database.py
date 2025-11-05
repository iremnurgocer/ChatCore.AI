# -*- coding: utf-8 -*-
"""
Module: Core Database
Description: PostgreSQL async database connection and session management using SQLModel.
"""
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker, AsyncEngine
from sqlalchemy.engine import Engine
from sqlmodel import SQLModel, create_engine, Session
from core.config import get_settings

settings = get_settings()

# Async database engine
async_engine: Optional[AsyncEngine] = None
async_session_maker: Optional[async_sessionmaker] = None

# Sync database engine (for migrations, etc.)
sync_engine: Optional[Engine] = None


def init_database():
    """Initialize database connections"""
    global async_engine, async_session_maker, sync_engine
    
    if settings.DATABASE_URL:
        # Async engine
        async_database_url = settings.database_url_async
        if async_database_url:
            async_engine = create_async_engine(
                async_database_url,
                echo=settings.ENVIRONMENT == "development",
                future=True,
            )
            async_session_maker = async_sessionmaker(
                async_engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
        
        # Sync engine (for migrations)
        sync_database_url = settings.database_url_sync
        if sync_database_url:
            sync_engine = create_engine(
                sync_database_url,
                echo=settings.ENVIRONMENT == "development",
            )


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for async database sessions"""
    if async_session_maker is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_async_session_optional() -> AsyncGenerator[Optional[AsyncSession], None]:
    """Optional dependency for async database sessions - returns None if database not configured"""
    if async_session_maker is None:
        yield None
        return
    
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_session() -> Session:
    """Get synchronous database session"""
    if sync_engine is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    return Session(sync_engine)


async def init_db():
    """Initialize database - create tables if they don't exist"""
    if async_engine is None:
        init_database()
    
    if async_engine is None:
        raise RuntimeError("Database not configured. Set DATABASE_URL in .env")
    
    # Import all models to register them
    from models import User, Conversation, Message, RefreshToken, Session, Document
    
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


# Initialize on import if database URL is set
if settings.DATABASE_URL:
    init_database()

