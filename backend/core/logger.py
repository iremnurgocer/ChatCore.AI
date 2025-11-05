# -*- coding: utf-8 -*-
"""
Module: Core Logger
Description: Structured JSON logging with request ID tracking and trace correlation.
"""
import logging
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from enum import Enum
from contextvars import ContextVar

from core.config import get_settings

settings = get_settings()

# Context variables for request tracking
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar('user_id', default=None)
conversation_id_var: ContextVar[Optional[str]] = ContextVar('conversation_id', default=None)

# Log directory
logs_dir = Path(__file__).parent.parent / "logs"
logs_dir.mkdir(exist_ok=True)

# Log files
log_file = logs_dir / "api.log"
error_log_file = logs_dir / "errors.log"
security_log_file = logs_dir / "security.log"

# Loggers
logger = logging.getLogger("chatcore_api")
error_logger = logging.getLogger("chatcore_api.errors")
security_logger = logging.getLogger("chatcore_api.security")

# Set log levels
log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
logger.setLevel(log_level)
error_logger.setLevel(logging.ERROR)
security_logger.setLevel(logging.WARNING)


class JSONFormatter(logging.Formatter):
    """Structured JSON log formatter with request ID and trace correlation"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add request context from context vars
        request_id = request_id_var.get()
        user_id = user_id_var.get()
        conversation_id = conversation_id_var.get()
        
        if request_id:
            log_data["request_id"] = request_id
        if user_id:
            log_data["user_id"] = user_id[:8] + "..." if len(user_id) > 8 else user_id  # Masked
        if conversation_id:
            log_data["conversation_id"] = conversation_id
        
        # Add extra fields
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        
        # Add exception info
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add trace correlation (for distributed tracing)
        if hasattr(record, "trace_id"):
            log_data["trace_id"] = record.trace_id
        if hasattr(record, "span_id"):
            log_data["span_id"] = record.span_id
        
        return json.dumps(log_data, ensure_ascii=False)


class TextFormatter(logging.Formatter):
    """Human-readable text formatter"""
    
    def __init__(self):
        super().__init__(
            fmt='%(asctime)s | %(levelname)-8s | %(name)s | [%(request_id)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    def format(self, record: logging.LogRecord) -> str:
        """Format with request ID"""
        if not hasattr(record, 'request_id'):
            record.request_id = request_id_var.get() or '-'
        return super().format(record)


# Choose formatter based on settings
formatter = JSONFormatter() if settings.LOG_FORMAT == "json" else TextFormatter()

# File handlers
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

error_file_handler = logging.FileHandler(error_log_file, encoding='utf-8')
error_file_handler.setLevel(logging.ERROR)
error_file_handler.setFormatter(formatter)

security_file_handler = logging.FileHandler(security_log_file, encoding='utf-8')
security_file_handler.setLevel(logging.WARNING)
security_file_handler.setFormatter(formatter)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# Add handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)

error_logger.addHandler(error_file_handler)
error_logger.addHandler(console_handler)

security_logger.addHandler(security_file_handler)
security_logger.addHandler(console_handler)


class ErrorCategory(Enum):
    """Error categories"""
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
    """Structured API logger with request ID and trace correlation"""
    
    @staticmethod
    def set_request_id(request_id: str):
        """Set request ID in context"""
        request_id_var.set(request_id)
    
    @staticmethod
    def set_user_id(user_id: str):
        """Set user ID in context"""
        user_id_var.set(user_id)
    
    @staticmethod
    def set_conversation_id(conversation_id: str):
        """Set conversation ID in context"""
        conversation_id_var.set(conversation_id)
    
    @staticmethod
    def log_request(
        endpoint: str,
        method: str,
        user_id: Optional[str] = None,
        response_time: Optional[float] = None,
        status_code: Optional[int] = None,
        **extra
    ):
        """Log API request"""
        log_data = {
            "event_type": "request",
            "endpoint": endpoint,
            "method": method,
            "user_id": user_id[:8] + "..." if user_id and len(user_id) > 8 else user_id,
            "response_time_ms": round(response_time * 1000, 2) if response_time else None,
            "status_code": status_code,
            **extra
        }
        
        logger.info(
            f"REQUEST | {method} {endpoint} | User: {log_data['user_id'] or 'Anonymous'} | "
            f"Time: {log_data['response_time_ms']}ms | Status: {status_code}",
            extra=log_data
        )
    
    @staticmethod
    def log_error(
        endpoint: str,
        error: Exception,
        user_id: Optional[str] = None,
        category: ErrorCategory = ErrorCategory.UNKNOWN_ERROR,
        **extra
    ):
        """Log error"""
        log_data = {
            "event_type": "error",
            "endpoint": endpoint,
            "error_type": type(error).__name__,
            "error_category": category.value,
            "error_message": str(error),
            "user_id": user_id[:8] + "..." if user_id and len(user_id) > 8 else user_id,
            **extra
        }
        
        error_logger.error(
            f"ERROR | Category: {category.value} | Type: {type(error).__name__} | "
            f"Endpoint: {endpoint} | User: {user_id[:8] + '...' if user_id and len(user_id) > 8 else user_id or 'Anonymous'} | Message: {str(error)}",
            extra=log_data,
            exc_info=error
        )
    
    @staticmethod
    def log_security_event(
        event_type: str,
        description: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        **extra
    ):
        """Log security event"""
        log_data = {
            "event_type": "security",
            "security_event_type": event_type,
            "description": description,
            "user_id": user_id[:8] + "..." if user_id and len(user_id) > 8 else user_id,
            "ip_address": ip_address,
            **extra
        }
        
        security_logger.warning(
            f"SECURITY | Event: {event_type} | User: {user_id[:8] + '...' if user_id and len(user_id) > 8 else user_id or 'Anonymous'} | "
            f"IP: {ip_address or 'Unknown'} | Description: {description}",
            extra=log_data
        )
    
    @staticmethod
    def log_chat_query(
        user_id: str,
        query: str,
        response: str,
        response_time: float,
        conversation_id: Optional[str] = None,
        **extra
    ):
        """Log chat query"""
        log_data = {
            "event_type": "chat",
            "user_id": user_id[:8] + "..." if len(user_id) > 8 else user_id,
            "query_preview": query[:100],
            "query_length": len(query),
            "response_length": len(response),
            "response_time_ms": round(response_time * 1000, 2),
            "conversation_id": conversation_id,
            **extra
        }
        
        logger.info(
            f"CHAT | User: {user_id[:8] + '...' if len(user_id) > 8 else user_id} | Query: {query[:50]}... | "
            f"Response: {len(response)} chars | Time: {log_data['response_time_ms']}ms",
            extra=log_data
        )


