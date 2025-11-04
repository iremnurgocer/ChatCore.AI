# -*- coding: utf-8 -*-
"""
Loglama Sistemi

Bu modül API isteklerini ve hataları kategorize şekilde loglar.
Farklı log seviyeleri (INFO, ERROR, WARNING) ve kategorileri kullanır.

Ne İşe Yarar:
- API isteklerini loglama
- Hata logları (errors.log)
- Güvenlik olaylarını loglama (security.log)
- Genel API logları (api.log)
- Hata kategorileri (AUTH_ERROR, VALIDATION_ERROR, vb.)

Kullanım:
- APILogger.log_request() - İstek logla
- APILogger.log_error() - Hata logla
- APILogger.log_security_event() - Güvenlik olayı logla
"""
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
from enum import Enum

# Log klasörünü oluştur
logs_dir = Path(__file__).parent / "logs"
logs_dir.mkdir(exist_ok=True)

# Logger yapılandırması
log_file = logs_dir / "api.log"
error_log_file = logs_dir / "errors.log"
security_log_file = logs_dir / "security.log"

# Ana logger
logger = logging.getLogger("enterprise_ai_api")
logger.setLevel(logging.INFO)

# Hata logger'ı
error_logger = logging.getLogger("enterprise_ai_api.errors")
error_logger.setLevel(logging.ERROR)

# Güvenlik logger'ı
security_logger = logging.getLogger("enterprise_ai_api.security")
security_logger.setLevel(logging.WARNING)

# File handler - Genel loglar
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(name)s | %(message)s')
file_handler.setFormatter(file_formatter)

# File handler - Hata logları
error_file_handler = logging.FileHandler(error_log_file, encoding='utf-8')
error_file_handler.setLevel(logging.ERROR)
error_file_handler.setFormatter(file_formatter)

# File handler - Güvenlik logları
security_file_handler = logging.FileHandler(security_log_file, encoding='utf-8')
security_file_handler.setLevel(logging.WARNING)
security_file_handler.setFormatter(file_formatter)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(message)s')
console_handler.setFormatter(console_formatter)

# Handler'ları ekle
logger.addHandler(file_handler)
logger.addHandler(console_handler)

error_logger.addHandler(error_file_handler)
error_logger.addHandler(console_handler)

security_logger.addHandler(security_file_handler)
security_logger.addHandler(console_handler)


class ErrorCategory(Enum):
    """Hata kategorileri"""
    AUTH_ERROR = "AUTH_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AI_ERROR = "AI_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"
    CONFIG_ERROR = "CONFIG_ERROR"
    RATE_LIMIT_ERROR = "RATE_LIMIT_ERROR"
    SECURITY_ERROR = "SECURITY_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


class APILogger:
    """API isteklerini ve hataları loglar"""
    
    @staticmethod
    def log_request(endpoint: str, method: str, user_id: Optional[str] = None, 
                   params: Optional[dict] = None, response_time: Optional[float] = None):
        """
        API isteğini loglar
        
        Args:
            endpoint: İstek yapılan endpoint
            method: HTTP metodu (GET, POST, etc.)
            user_id: Kullanıcı ID (varsa)
            params: İstek parametreleri (opsiyonel)
            response_time: Yanıt süresi (saniye)
        """
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "method": method,
            "user_id": user_id,
            "params": params,
            "response_time_ms": round(response_time * 1000, 2) if response_time else None
        }
        logger.info(f"REQUEST | {method} {endpoint} | User: {user_id or 'Anonymous'} | Time: {log_data['response_time_ms']}ms")
    
    @staticmethod
    def log_error(endpoint: str, error: Exception, user_id: Optional[str] = None, 
                 category: ErrorCategory = ErrorCategory.UNKNOWN_ERROR):
        """
        Hata durumunu loglar
        
        Args:
            endpoint: Hatanın oluştuğu endpoint
            error: Hata exception'ı
            user_id: Kullanıcı ID (varsa)
            category: Hata kategorisi
        """
        error_type = type(error).__name__
        error_message = str(error)
        
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "error_type": error_type,
            "error_category": category.value,
            "error_message": error_message,
            "user_id": user_id
        }
        
        error_logger.error(
            f"ERROR | Category: {category.value} | Type: {error_type} | "
            f"Endpoint: {endpoint} | User: {user_id or 'Anonymous'} | Message: {error_message}"
        )
        
        return log_data
    
    @staticmethod
    def log_security_event(event_type: str, description: str, user_id: Optional[str] = None, 
                          ip_address: Optional[str] = None):
        """
        Güvenlik olaylarını loglar (rate limit, XSS, injection attempts, etc.)
        
        Args:
            event_type: Olay tipi (RATE_LIMIT, XSS_ATTEMPT, INVALID_TOKEN, etc.)
            description: Olay açıklaması
            user_id: Kullanıcı ID (varsa)
            ip_address: IP adresi (varsa)
        """
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "description": description,
            "user_id": user_id,
            "ip_address": ip_address
        }
        
        security_logger.warning(
            f"SECURITY | Event: {event_type} | User: {user_id or 'Anonymous'} | "
            f"IP: {ip_address or 'Unknown'} | Description: {description}"
        )
    
    @staticmethod
    def log_chat_query(user_id: str, query: str, response: str, response_time: float):
        """
        Chat sorgusunu loglar
        
        Args:
            user_id: Kullanıcı ID
            query: Kullanıcı sorgusu
            response: AI yanıtı
            response_time: Yanıt süresi (saniye)
        """
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "query": query[:100],  # İlk 100 karakter
            "response_length": len(response),
            "response_time_ms": round(response_time * 1000, 2)
        }
        logger.info(
            f"CHAT | User: {user_id} | Query: {query[:50]}... | "
            f"Response: {len(response)} chars | Time: {log_data['response_time_ms']}ms"
        )
