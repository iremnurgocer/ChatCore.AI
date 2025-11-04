# -*- coding: utf-8 -*-
"""
Authentication modülü için testler
"""
import pytest
import sys
from pathlib import Path

# Backend modüllerini import etmek için path ekle
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from fastapi.testclient import TestClient
from main import app
from auth import hash_password, verify_password

client = TestClient(app)

def test_login_success():
    """Başarılı login testi"""
    response = client.post(
        "/api/login",
        json={"username": "admin", "password": "1234"}
    )
    assert response.status_code == 200
    assert "token" in response.json()

def test_login_failure():
    """Başarısız login testi"""
    response = client.post(
        "/api/login",
        json={"username": "admin", "password": "wrong"}
    )
    assert response.status_code == 401

def test_password_hashing():
    """Şifre hash'leme testi"""
    password = "test123"
    hashed, salt = hash_password(password)
    
    assert hashed is not None
    assert salt is not None
    assert len(hashed) > 0
    assert len(salt) > 0
    
    # Aynı şifre farklı hash üretmeli (salt nedeniyle)
    hashed2, salt2 = hash_password(password)
    assert hashed != hashed2  # Farklı salt kullanıldı
    
    # Doğrulama çalışmalı
    assert verify_password(password, hashed, salt) == True
    assert verify_password("wrong", hashed, salt) == False

def test_protected_endpoint_without_token():
    """Token olmadan protected endpoint erişimi"""
    response = client.get("/api/employees")
    assert response.status_code == 401

def test_protected_endpoint_with_token():
    """Token ile protected endpoint erişimi"""
    # Login
    login_response = client.post(
        "/api/login",
        json={"username": "admin", "password": "1234"}
    )
    token = login_response.json()["token"]
    
    # Protected endpoint'e eriş
    response = client.get(
        "/api/employees",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

