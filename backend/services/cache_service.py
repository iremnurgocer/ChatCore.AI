# -*- coding: utf-8 -*-
"""
Module: Cache Service
Description: Redis-backed caching service for AI responses, sessions, and user data.
"""
from typing import Optional
import json
import hashlib
from datetime import timedelta
from core.redis_client import get_redis
from core.config import get_settings

settings = get_settings()


class CacheService:
    """Redis-backed cache service"""
    
    def __init__(self, default_ttl: int = 3600):
        self.default_ttl = default_ttl  # 1 hour default
    
    async def get(self, key: str) -> Optional[str]:
        """Get cached value"""
        try:
            redis = await get_redis()
            value = await redis.get(key)
            return value
        except Exception:
            return None
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """Set cached value"""
        try:
            redis = await get_redis()
            ttl = ttl or self.default_ttl
            await redis.setex(key, ttl, value)
            return True
        except Exception:
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete cached value"""
        try:
            redis = await get_redis()
            await redis.delete(key)
            return True
        except Exception:
            return False
    
    async def get_json(self, key: str) -> Optional[dict]:
        """Get cached JSON value"""
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return None
    
    async def set_json(self, key: str, value: dict, ttl: Optional[int] = None) -> bool:
        """Set cached JSON value"""
        try:
            json_str = json.dumps(value, ensure_ascii=False)
            return await self.set(key, json_str, ttl)
        except Exception:
            return False
    
    async def get_ai_response(
        self,
        prompt: str,
        provider: str,
        user_id: str = "",
        context_hash: str = ""
    ) -> Optional[str]:
        """Get cached AI response"""
        cache_key = self._generate_ai_cache_key(prompt, provider, user_id, context_hash)
        return await self.get(cache_key)
    
    async def set_ai_response(
        self,
        prompt: str,
        provider: str,
        response: str,
        user_id: str = "",
        context_hash: str = "",
        ttl: int = 3600
    ) -> bool:
        """Cache AI response"""
        cache_key = self._generate_ai_cache_key(prompt, provider, user_id, context_hash)
        return await self.set(cache_key, response, ttl)
    
    def _generate_ai_cache_key(
        self,
        prompt: str,
        provider: str,
        user_id: str,
        context_hash: str
    ) -> str:
        """Generate cache key for AI response"""
        key_parts = [prompt, provider, user_id, context_hash]
        key_str = "|".join(key_parts)
        key_hash = hashlib.md5(key_str.encode()).hexdigest()
        return f"ai_cache:{key_hash}"
    
    async def get_session(self, session_id: str) -> Optional[dict]:
        """Get cached session"""
        return await self.get_json(f"session:{session_id}")
    
    async def set_session(self, session_id: str, session_data: dict, ttl: int = 7200) -> bool:
        """Cache session (2 hour default)"""
        return await self.set_json(f"session:{session_id}", session_data, ttl)
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete cached session"""
        return await self.delete(f"session:{session_id}")
    
    # User caching helpers
    async def get_user_cache(self, username: str) -> Optional[dict]:
        """Get cached user data"""
        normalized = username.strip().casefold()
        return await self.get_json(f"user:{normalized}")
    
    async def set_user_cache(self, username: str, payload: dict, ttl: int = 300) -> bool:
        """Cache user data (5 min default)"""
        normalized = username.strip().casefold()
        return await self.set_json(f"user:{normalized}", payload, ttl)
    
    async def invalidate_user_cache(self, username: str) -> bool:
        """Invalidate user cache"""
        normalized = username.strip().casefold()
        return await self.delete(f"user:{normalized}")


# Global cache service instance
_cache_service: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """Get global cache service instance"""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service

