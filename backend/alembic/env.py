# -*- coding: utf-8 -*-
"""
Alembic Environment Configuration - Async SQLModel Support

This module configures Alembic to work with async SQLModel and PostgreSQL.
"""
from logging.config import fileConfig
from sqlalchemy import pool, create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
import asyncio
from pathlib import Path
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import SQLModel metadata
from models import metadata
from core.config import get_settings
from core.database import sync_engine, init_database

# this is the Alembic Config object
config = context.config

# Override sqlalchemy.url from config with actual DATABASE_URL
settings = get_settings()
# Initialize database if not already initialized
if settings.DATABASE_URL:
    init_database()
    # Use sync URL for Alembic (it handles async internally)
    sync_url = settings.database_url_sync
    if sync_url:
        # Ensure URL is properly formatted
        if not sync_url.startswith("postgresql+psycopg2://"):
            # Clean and rebuild URL
            if "+asyncpg" in sync_url:
                sync_url = sync_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
            elif sync_url.startswith("postgresql://"):
                sync_url = sync_url.replace("postgresql://", "postgresql+psycopg2://", 1)
        config.set_main_option("sqlalchemy.url", sync_url)
    else:
        # Fallback: convert async URL to sync
        db_url = settings.DATABASE_URL
        if "+asyncpg" in db_url:
            db_url = db_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
        elif db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)
        config.set_main_option("sqlalchemy.url", db_url)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata for autogenerate
target_metadata = metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in async mode."""
    configuration = config.get_section(config.config_ini_section)
    db_url = config.get_main_option("sqlalchemy.url")
    
    # Ensure URL is async format for async engine
    if db_url and "+asyncpg" not in db_url and "+psycopg2" in db_url:
        db_url = db_url.replace("postgresql+psycopg2://", "postgresql+asyncpg://")
    elif db_url and "postgresql://" in db_url and "+" not in db_url:
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
    
    configuration["sqlalchemy.url"] = db_url
    
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Try sync engine first (preferred)
    if sync_engine:
        with sync_engine.connect() as connection:
            do_run_migrations(connection)
    else:
        # Fallback: create sync engine directly from URL
        sync_url = config.get_main_option("sqlalchemy.url")
        if sync_url:
            # Ensure URL is sync format
            if "+asyncpg" in sync_url:
                sync_url = sync_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
            
            # Create temporary sync engine
            temp_engine = create_engine(sync_url, poolclass=pool.NullPool)
            try:
                with temp_engine.connect() as connection:
                    do_run_migrations(connection)
            finally:
                temp_engine.dispose()
        else:
            # Last resort: async migration
            asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()



