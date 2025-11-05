# -*- coding: utf-8 -*-
"""
Module: Core Security
Description: Sliding window rate limiting, JTI blacklist, account lockout, and security headers.
"""
import re
import time
import hashlib
from typing import Optional, Tuple
from datetime import datetime, timedelta
from fastapi import HTTPException, Request, Response
from core.config import get_settings
from core.redis_client import get_redis
from core.logger import APILogger

settings = get_settings()


class SecurityValidator:
    """Input validation and sanitization"""
    
    MAX_INPUT_LENGTH = 5000
    MAX_MESSAGE_LENGTH = 2000
    
    # XSS patterns
    XSS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'onerror\s*=',
        r'onload\s*=',
        r'onclick\s*=',
        r'eval\s*\(',
        r'expression\s*\(',
    ]
    
    # SQL injection patterns (for logging only, not blocking)
    SQL_PATTERNS = [
        r"(union|select|insert|update|delete|drop|create|alter|exec|execute)\s+",
    ]
    
    @staticmethod
    def sanitize_input(
        text: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> str:
        """
        Sanitize user input - prevent XSS and validate length
        
        Note: HTML sanitization removed from prompt flow per requirements.
        We only validate, not sanitize HTML in prompts.
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Length check
        if len(text) > SecurityValidator.MAX_INPUT_LENGTH:
            APILogger.log_security_event(
                "VALIDATION_ERROR",
                f"Input too long: {len(text)} chars",
                user_id,
                ip_address
            )
            raise HTTPException(
                status_code=400,
                detail=f"Input too long. Maximum {SecurityValidator.MAX_INPUT_LENGTH} characters."
            )
        
        # XSS pattern detection (log only, don't block in prompts)
        text_lower = text.lower()
        for pattern in SecurityValidator.XSS_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                APILogger.log_security_event(
                    "XSS_PATTERN_DETECTED",
                    f"XSS pattern detected: {pattern[:50]}",
                    user_id,
                    ip_address
                )
        
        # SQL injection pattern detection (log only)
        for pattern in SecurityValidator.SQL_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                APILogger.log_security_event(
                    "SQL_PATTERN_DETECTED",
                    f"SQL pattern detected: {pattern[:50]}",
                    user_id,
                    ip_address
                )
        
        return text.strip()
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """Validate username format"""
        if not username or len(username) < 3 or len(username) > 50:
            return False
        pattern = r'^[a-zA-Z0-9_]+$'
        return bool(re.match(pattern, username))


class SlidingWindowRateLimiter:
    """Redis-backed sliding window rate limiter using sorted sets"""
    
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    async def is_allowed(
        self,
        identifier: str,
        endpoint: Optional[str] = None
    ) -> Tuple[bool, int]:
        """
        Check if request is allowed using sliding window algorithm
        
        Returns:
            (is_allowed, remaining_requests)
        """
        try:
            redis = await get_redis()
            now = time.time()
            window_start = now - self.window_seconds
            
            # Create key: rate:{ip}:{user}:{endpoint}
            key_parts = ["rate", identifier]
            if endpoint:
                key_parts.append(endpoint)
            key = ":".join(key_parts)
            
            # Lua script for atomic sliding window check
            lua_script = """
            local key = KEYS[1]
            local window_start = ARGV[1]
            local max_requests = tonumber(ARGV[2])
            local window_seconds = tonumber(ARGV[3])
            local now = tonumber(ARGV[4])
            
            -- Remove old entries
            redis.call('ZREMRANGEBYSCORE', key, 0, window_start)
            
            -- Count current requests
            local count = redis.call('ZCARD', key)
            
            if count < max_requests then
                -- Add current request
                redis.call('ZADD', key, now, now)
                redis.call('EXPIRE', key, window_seconds)
                return {1, max_requests - count - 1}
            else
                return {0, 0}
            end
            """
            
            result = await redis.eval(
                lua_script,
                1,
                key,
                str(window_start),
                str(self.max_requests),
                str(self.window_seconds),
                str(now)
            )
            
            is_allowed = bool(result[0])
            remaining = int(result[1])
            
            return is_allowed, remaining
        
        except Exception as e:
            # If Redis fails, allow request (fail open)
            APILogger.log_security_event(
                "RATE_LIMIT_ERROR",
                f"Rate limit check failed: {str(e)}",
                None,
                identifier.split(":")[0] if ":" in identifier else identifier
            )
            return True, self.max_requests
    
    async def get_remaining(self, identifier: str, endpoint: Optional[str] = None) -> int:
        """Get remaining requests"""
        _, remaining = await self.is_allowed(identifier, endpoint)
        return remaining


class JTIBlacklist:
    """JWT ID (JTI) blacklist for revoked tokens"""
    
    async def add(self, jti: str, ttl: int) -> bool:
        """Add JTI to blacklist"""
        try:
            redis = await get_redis()
            key = f"jti:blacklist:{jti}"
            await redis.setex(key, ttl, "1")
            return True
        except Exception:
            return False
    
    async def is_blacklisted(self, jti: str) -> bool:
        """Check if JTI is blacklisted"""
        try:
            redis = await get_redis()
            key = f"jti:blacklist:{jti}"
            result = await redis.get(key)
            return result is not None
        except Exception:
            return False


class AccountLockout:
    """Account lockout after failed login attempts"""
    
    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_DURATION = 900  # 15 minutes
    
    async def record_failed_login(self, username: str) -> bool:
        """Record failed login attempt, return True if account should be locked"""
        try:
            redis = await get_redis()
            key = f"auth:lock:{username.lower()}"
            attempts_key = f"auth:attempts:{username.lower()}"
            
            # Get current attempts
            attempts = await redis.get(attempts_key)
            attempts = int(attempts) if attempts else 0
            
            # Increment attempts
            attempts += 1
            await redis.setex(attempts_key, self.LOCKOUT_DURATION, str(attempts))
            
            # Lock if threshold reached
            if attempts >= self.MAX_FAILED_ATTEMPTS:
                await redis.setex(key, self.LOCKOUT_DURATION, "1")
                return True
            
            return False
        
        except Exception:
            return False
    
    async def is_locked(self, username: str) -> bool:
        """Check if account is locked"""
        try:
            redis = await get_redis()
            key = f"auth:lock:{username.lower()}"
            result = await redis.get(key)
            return result is not None
        except Exception:
            return False
    
    async def unlock(self, username: str) -> bool:
        """Unlock account (on successful login)"""
        try:
            redis = await get_redis()
            lock_key = f"auth:lock:{username.lower()}"
            attempts_key = f"auth:attempts:{username.lower()}"
            
            await redis.delete(lock_key)
            await redis.delete(attempts_key)
            return True
        except Exception:
            return False


# Global instances
default_rate_limiter = SlidingWindowRateLimiter(
    max_requests=settings.RATE_LIMIT_REQUESTS,
    window_seconds=settings.RATE_LIMIT_WINDOW
)

strict_rate_limiter = SlidingWindowRateLimiter(max_requests=20, window_seconds=60)  # For login

jti_blacklist = JTIBlacklist()
account_lockout = AccountLockout()


def add_security_headers(response: Response) -> Response:
    """Add security headers to response"""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # Content Security Policy (nonce generator stub)
    nonce = hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]
    csp = (
        f"default-src 'self'; "
        f"script-src 'self' 'unsafe-inline' 'nonce-{nonce}'; "
        f"style-src 'self' 'unsafe-inline' 'nonce-{nonce}'; "
        f"img-src 'self' data: https:; "
        f"font-src 'self' data:; "
        f"connect-src 'self'"
    )
    response.headers["Content-Security-Policy"] = csp
    
    return response


