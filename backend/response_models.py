# -*- coding: utf-8 -*-
"""
API Response Standardization

Bu modül tüm API endpoint'leri için standardize edilmiş response formatı sağlar.
"""
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List
from datetime import datetime
from enum import Enum

class ResponseStatus(str, Enum):
    """Response status enum"""
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"

class APIResponse(BaseModel):
    """Standard API response model"""
    
    success: bool
    status: ResponseStatus = ResponseStatus.SUCCESS
    data: Optional[Any] = None
    message: Optional[str] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "status": "success",
                "data": {"key": "value"},
                "message": "İşlem başarılı",
                "timestamp": "2024-01-01T12:00:00"
            }
        }

def success_response(
    data: Any = None,
    message: str = None,
    metadata: Dict[str, Any] = None
) -> APIResponse:
    """
    Başarılı response oluştur
    
    Args:
        data: Response data
        message: Başarı mesajı
        metadata: Ek metadata
        
    Returns:
        APIResponse instance
    """
    return APIResponse(
        success=True,
        status=ResponseStatus.SUCCESS,
        data=data,
        message=message,
        metadata=metadata
    )

def error_response(
    error: str,
    error_code: str = None,
    status_code: int = 400,
    metadata: Dict[str, Any] = None
) -> APIResponse:
    """
    Hata response oluştur
    
    Args:
        error: Hata mesajı
        error_code: Hata kodu
        status_code: HTTP status code (metadata için)
        metadata: Ek metadata
        
    Returns:
        APIResponse instance
    """
    if metadata is None:
        metadata = {}
    metadata["status_code"] = status_code
    
    return APIResponse(
        success=False,
        status=ResponseStatus.ERROR,
        error=error,
        error_code=error_code,
        metadata=metadata
    )

def paginated_response(
    items: List[Any],
    total: int,
    page: int = 1,
    page_size: int = 10,
    message: str = None
) -> APIResponse:
    """
    Paginated response oluştur
    
    Args:
        items: Sayfa item'ları
        total: Toplam item sayısı
        page: Mevcut sayfa
        page_size: Sayfa boyutu
        message: Mesaj
        
    Returns:
        APIResponse instance
    """
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    
    return APIResponse(
        success=True,
        status=ResponseStatus.SUCCESS,
        data={
            "items": items,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1
            }
        },
        message=message
    )

