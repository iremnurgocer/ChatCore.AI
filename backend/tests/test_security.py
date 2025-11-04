# -*- coding: utf-8 -*-
"""
Security modülü için testler
"""
import pytest
import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from security import SecurityValidator, RateLimiter

def test_sanitize_input_normal():
    """Normal input temizleme testi"""
    text = "Merhaba dünya"
    result = SecurityValidator.sanitize_input(text)
    assert result == "Merhaba dünya"

def test_sanitize_input_xss():
    """XSS koruması testi"""
    xss_attempt = "<script>alert('xss')</script>"
    with pytest.raises(Exception):
        SecurityValidator.sanitize_input(xss_attempt)

def test_sanitize_input_too_long():
    """Çok uzun input testi"""
    long_text = "a" * 10000
    with pytest.raises(Exception):
        SecurityValidator.sanitize_input(long_text)

def test_rate_limiter():
    """Rate limiting testi"""
    limiter = RateLimiter(max_requests=2, window_seconds=60)
    identifier = "test_ip"
    
    # İlk 2 istek geçmeli
    assert limiter.is_allowed(identifier) == True
    assert limiter.is_allowed(identifier) == True
    
    # 3. istek engellenmeli
    assert limiter.is_allowed(identifier) == False

