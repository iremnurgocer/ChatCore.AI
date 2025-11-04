# -*- coding: utf-8 -*-
"""
Güvenlik Modülü - Rate Limiting, Input Doğrulama, XSS Koruması

Bu modül API'nin güvenliğini sağlamak için rate limiting, input validation
ve XSS koruması gibi özellikler sunar.

Ne İşe Yarar:
- Rate limiting (IP ve kullanıcı bazlı)
- Input sanitization ve validation
- XSS (Cross-Site Scripting) koruması
- SQL injection koruması
- Güvenli string karşılaştırma

Kullanım:
- SecurityValidator.sanitize_input() - Input temizleme
- SecurityValidator.validate_username() - Username doğrulama
- RateLimiter.is_allowed() - Rate limit kontrolü
"""
import re
import time
from typing import Optional, Dict
from collections import defaultdict
from functools import wraps
from fastapi import HTTPException, Request
from logger import APILogger

# Rate limiting depolama (bellekte, production'da Redis kullan)
_rate_limit_storage: Dict[str, list] = defaultdict(list)

class SecurityValidator:
    """Input doğrulama ve güvenlik kontrolleri"""
    
    MAX_INPUT_LENGTH = 5000
    MAX_MESSAGE_LENGTH = 2000
    
    # XSS pattern tespiti
    XSS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'onerror\s*=',
        r'onload\s*=',
        r'onclick\s*=',
        r'eval\s*\(',
        r'expression\s*\(',
    ]
    
    # SQL injection pattern'leri
    SQL_PATTERNS = [
        r"('|(\\')|(;)|(--)|(\|\|)|(\/\*)|(\*\/))",
        r"(union|select|insert|update|delete|drop|create|alter|exec|execute)",
    ]
    
    @staticmethod
    def sanitize_input(text: str, user_id: Optional[str] = None, ip_address: Optional[str] = None) -> str:
        """
        Kullanıcı input'unu temizler ve XSS/injection saldırılarını önler
        
        Args:
            text: Temizlenecek input string'i
            user_id: Kullanıcı ID (log için)
            ip_address: IP adresi (log için)
            
        Returns:
            Temizlenmiş input string'i
            
        Raises:
            HTTPException: Eğer input zararlı pattern içeriyorsa veya uzunluk limitini aşıyorsa
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Uzunluk kontrolü
        if len(text) > SecurityValidator.MAX_INPUT_LENGTH:
            if user_id or ip_address:
                APILogger.log_security_event("VALIDATION_ERROR", f"Input too long: {len(text)} chars", user_id, ip_address)
            raise HTTPException(
                status_code=400,
                detail=f"Input too long. Maximum {SecurityValidator.MAX_INPUT_LENGTH} characters."
            )
        
        # XSS kontrolü
        text_lower = text.lower()
        for pattern in SecurityValidator.XSS_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                if user_id or ip_address:
                    APILogger.log_security_event("XSS_ATTEMPT", f"XSS pattern detected: {pattern[:50]}", user_id, ip_address)
                raise HTTPException(
                    status_code=400,
                    detail="Invalid characters detected."
                )
        
        # SQL injection kontrolü (temel)
        for pattern in SecurityValidator.SQL_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                # Log ama engelleme (false positive olabilir)
                if user_id or ip_address:
                    APILogger.log_security_event("SQL_INJECTION_ATTEMPT", f"SQL pattern detected: {pattern[:50]}", user_id, ip_address)
                pass
        
        # HTML escape (temel)
        text = text.replace('<', '&lt;').replace('>', '&gt;')
        text = text.replace('"', '&quot;').replace("'", "&#x27;")
        
        return text.strip()
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Email doğrulama"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """Kullanıcı adı doğrulama"""
        if not username or len(username) < 3 or len(username) > 50:
            return False
        pattern = r'^[a-zA-Z0-9_]+$'
        return bool(re.match(pattern, username))

class RateLimiter:
    """Rate limiting implementasyonu"""
    
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    def is_allowed(self, identifier: str) -> bool:
        """Rate limit kontrolü"""
        now = time.time()
        window_start = now - self.window_seconds
        
        # Eski kayıtları temizle
        _rate_limit_storage[identifier] = [
            req_time for req_time in _rate_limit_storage[identifier]
            if req_time > window_start
        ]
        
        # Limit kontrolü
        if len(_rate_limit_storage[identifier]) >= self.max_requests:
            return False
        
        # Yeni isteği ekle
        _rate_limit_storage[identifier].append(now)
        return True
    
    def get_remaining(self, identifier: str) -> int:
        """Kalan istek sayısını getirir"""
        now = time.time()
        window_start = now - self.window_seconds
        
        _rate_limit_storage[identifier] = [
            req_time for req_time in _rate_limit_storage[identifier]
            if req_time > window_start
        ]
        
        return max(0, self.max_requests - len(_rate_limit_storage[identifier]))

# Global rate limiter instance'ları
default_rate_limiter = RateLimiter(max_requests=60, window_seconds=60)
strict_rate_limiter = RateLimiter(max_requests=20, window_seconds=60)  # Login için (artırıldı: 10 -> 20)

def rate_limit(max_requests: int = 60, window_seconds: int = 60):
    """Rate limiting decorator'ı"""
    limiter = RateLimiter(max_requests, window_seconds)
    
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # IP adresi veya user_id'yi identifier olarak kullan
            identifier = request.client.host if request.client else "unknown"
            
            # Mümkünse user_id kullan
            if hasattr(request.state, 'user_id'):
                identifier = f"{identifier}:{request.state.user_id}"
            
            if not limiter.is_allowed(identifier):
                remaining = limiter.get_remaining(identifier)
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Try again in {remaining} seconds.",
                    headers={"Retry-After": str(window_seconds)}
                )
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator
