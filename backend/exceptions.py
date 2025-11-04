# -*- coding: utf-8 -*-
"""
Custom Exception Sınıfları

Bu modül proje için özel exception sınıfları içerir.
Daha iyi error handling ve logging için kullanılır.
"""

class ChatCoreException(Exception):
    """Base exception class - Tüm custom exception'ların üst sınıfı"""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.details = details or {}
        super().__init__(self.message)

class AIServiceError(ChatCoreException):
    """AI servis ile ilgili hatalar"""
    
    def __init__(self, message: str, provider: str = None, details: dict = None):
        self.provider = provider
        super().__init__(
            message=message,
            error_code="AI_SERVICE_ERROR",
            details=details or {}
        )

class AITimeoutError(AIServiceError):
    """AI servis timeout hatası"""
    
    def __init__(self, provider: str, timeout: int):
        super().__init__(
            message=f"AI servis timeout ({provider}): {timeout}s",
            provider=provider,
            details={"timeout": timeout}
        )
        self.error_code = "AI_TIMEOUT_ERROR"

class AIProviderNotFoundError(AIServiceError):
    """AI sağlayıcı bulunamadı"""
    
    def __init__(self, provider: str):
        super().__init__(
            message=f"AI sağlayıcı bulunamadı: {provider}",
            provider=provider
        )
        self.error_code = "AI_PROVIDER_NOT_FOUND"

class DatabaseError(ChatCoreException):
    """Veritabanı ile ilgili hatalar"""
    
    def __init__(self, message: str, operation: str = None, details: dict = None):
        self.operation = operation
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            details=details or {}
        )

class ValidationError(ChatCoreException):
    """Input validation hataları"""
    
    def __init__(self, message: str, field: str = None, details: dict = None):
        self.field = field
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details or {}
        )

class AuthenticationError(ChatCoreException):
    """Kimlik doğrulama hataları"""
    
    def __init__(self, message: str, reason: str = None, details: dict = None):
        self.reason = reason
        super().__init__(
            message=message,
            error_code="AUTH_ERROR",
            details=details or {}
        )

class AuthorizationError(ChatCoreException):
    """Yetkilendirme hataları"""
    
    def __init__(self, message: str, resource: str = None, details: dict = None):
        self.resource = resource
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            details=details or {}
        )

class RateLimitError(ChatCoreException):
    """Rate limit aşımı"""
    
    def __init__(self, message: str, retry_after: int = None, details: dict = None):
        self.retry_after = retry_after
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_ERROR",
            details=details or {}
        )

class CacheError(ChatCoreException):
    """Cache ile ilgili hatalar"""
    
    def __init__(self, message: str, operation: str = None, details: dict = None):
        self.operation = operation
        super().__init__(
            message=message,
            error_code="CACHE_ERROR",
            details=details or {}
        )

class ConfigurationError(ChatCoreException):
    """Yapılandırma hataları"""
    
    def __init__(self, message: str, config_key: str = None, details: dict = None):
        self.config_key = config_key
        super().__init__(
            message=message,
            error_code="CONFIG_ERROR",
            details=details or {}
        )

class NotFoundError(ChatCoreException):
    """Kaynak bulunamadı"""
    
    def __init__(self, message: str, resource_type: str = None, resource_id: str = None, details: dict = None):
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            details=details or {}
        )

