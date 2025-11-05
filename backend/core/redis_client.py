# -*- coding: utf-8 -*-
"""
Module: Core Redis Client
Description: Async Redis client for caching, rate limiting, and session storage.
"""
from typing import Optional
import redis.asyncio as redis
from redis.asyncio import ConnectionPool
from core.config import get_settings

settings = get_settings()

# Global Redis connection pool
redis_pool: Optional[ConnectionPool] = None
redis_client: Optional[redis.Redis] = None


def init_redis():
    """Initialize Redis connection pool"""
    global redis_pool, redis_client
    
    if settings.REDIS_HOST:
        redis_pool = ConnectionPool(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,
            max_connections=50,
        )
        redis_client = redis.Redis(connection_pool=redis_pool)


async def get_redis() -> redis.Redis:
    """Get Redis client instance"""
    global redis_client
    
    if redis_client is None:
        init_redis()
    
    if redis_client is None:
        raise RuntimeError("Redis not initialized. Check Redis connection settings.")
    
    return redis_client


async def close_redis():
    """Close Redis connections"""
    global redis_client, redis_pool
    
    if redis_client:
        await redis_client.close()
        redis_client = None
    
    if redis_pool:
        await redis_pool.disconnect()
        redis_pool = None


# Initialize on import
init_redis()

