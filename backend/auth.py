# -*- coding: utf-8 -*-
"""
Kimlik Doğrulama Modülü - JWT Token Yönetimi

Bu modül kullanıcı girişi ve çıkışı işlemlerini yönetir. JWT token oluşturma,
doğrulama ve şifre hash'leme işlemlerini gerçekleştirir.

Ne İşe Yarar:
- Kullanıcı login/logout işlemleri
- JWT token oluşturma ve doğrulama
- Şifre hash'leme ve güvenli saklama (PBKDF2-HMAC-SHA256)
- Rate limiting ile brute force koruması
- Session oluşturma ve yönetimi

Kullanım:
- Login endpoint: POST /api/login
- Logout endpoint: POST /api/logout
- Token doğrulama: verify_token() fonksiyonu
"""
from fastapi import APIRouter, HTTPException, Request, Depends, Header
from typing import Optional, Tuple
import jwt
import datetime
import os
import hashlib
import secrets
from security import SecurityValidator, strict_rate_limiter
from logger import APILogger, ErrorCategory
from user_manager import user_manager

router = APIRouter()

# Router prefix kontrolü
# Router başlatıldığında route'ları göster

SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")

def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """
    Şifreyi güvenli bir şekilde hash'ler
    
    Args:
        password: Hash'lenecek şifre
        salt: Opsiyonel salt (hex string veya None)
        
    Returns:
        (hashed_password, salt_hex) tuple'ı
    """
    import binascii
    
    if salt is None:
        # Yeni salt oluştur (bytes olarak, sonra hex'e çevir)
        salt_bytes = secrets.token_bytes(16)
        salt_hex = salt_bytes.hex()
    else:
        # Salt hex string ise bytes'a çevir
        if isinstance(salt, str):
            salt_bytes = binascii.unhexlify(salt)
            salt_hex = salt
        else:
            # Zaten bytes ise
            salt_bytes = salt
            salt_hex = salt.hex()
    
    # PBKDF2-HMAC-SHA256 ile hash'le (100,000 iterasyon)
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt_bytes,  # ✅ Bytes kullan
        100000  # Güvenlik için yüksek iterasyon sayısı
    )
    
    # Hex formatına çevir
    hashed_password = password_hash.hex()
    
    return hashed_password, salt_hex

def verify_password(password: str, hashed_password: str, salt: str) -> bool:
    """
    Şifreyi doğrular
    
    Args:
        password: Doğrulanacak şifre
        hashed_password: Hash'lenmiş şifre
        salt: Salt değeri (hex string)
        
    Returns:
        Şifre doğruysa True, değilse False
    """
    try:
        import binascii
        # Salt hex string'i bytes'a çevir
        salt_bytes = binascii.unhexlify(salt)
        
        # Aynı hash algoritması ile hash'le
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt_bytes,  # ✅ Bytes kullan
            100000
        )
        
        # Hex formatına çevir ve karşılaştır
        hashed_input = password_hash.hex()
        
        # Güvenli karşılaştırma (timing attack'a karşı)
        result = secrets.compare_digest(hashed_input, hashed_password)
        return result
    except Exception as e:
        return False

# Kullanıcı yönetimi artık user_manager modülünde TinyDB ile yapılıyor
# user_manager başlangıçta varsayılan kullanıcıları otomatik oluşturuyor

def get_current_user(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """Token'dan kullanıcıyı çıkar ve doğrula"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    token_parts = authorization.split(" ")
    if len(token_parts) < 2:
        raise HTTPException(status_code=401, detail="Invalid token format")
    
    token = token_parts[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return user_id
    except jwt.ExpiredSignatureError:
        APILogger.log_security_event("TOKEN_EXPIRED", "Token expired", None, None)
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        APILogger.log_security_event("INVALID_TOKEN", "Invalid token", None, None)
        raise HTTPException(status_code=401, detail="Invalid token")

def verify_token(token: str) -> dict:
    """
    JWT token'ı doğrular ve payload döndürür
    
    Args:
        token: JWT token string'i
        
    Returns:
        Dekode edilmiş token payload dictionary'si

    Raises:
        HTTPException: Token süresi dolmuşsa veya geçersizse
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        APILogger.log_error("/api/login", jwt.ExpiredSignatureError("Token expired"), None, ErrorCategory.AUTH_ERROR)
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        APILogger.log_error("/api/login", jwt.InvalidTokenError("Invalid token"), None, ErrorCategory.AUTH_ERROR)
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/api/login")
def login(user: dict, request: Request):
    """
    Kullanıcı kimlik doğrulama endpoint'i

    Kimlik bilgilerini doğrular ve authenticated istekler için JWT token döndürür.
    Brute force saldırılarını önlemek için rate limiting içerir.
    Her başarılı login sonrası yeni bir conversation oluşturulur (ChatGPT gibi).

    Args:
        user: 'username' ve 'password' anahtarlarına sahip dictionary
        request: FastAPI Request objesi (IP adresi için)

    Returns:
        'token' ve 'expires_in' anahtarlarına sahip dictionary

    Raises:
        HTTPException: Kimlik bilgileri geçersizse veya rate limit aşıldıysa
    """
    try:
        # Login için rate limiting (strict - brute force koruması)
        client_ip = request.client.host if request.client else "unknown"
        
        if not strict_rate_limiter.is_allowed(client_ip):
            APILogger.log_security_event("RATE_LIMIT", f"Login rate limit exceeded from {client_ip}", None, client_ip)
            raise HTTPException(
                status_code=429,
                detail="Too many login attempts. Please try again later."
            )
        
        username = user.get("username", "")
        password = user.get("password", "")

        # Input doğrulama
        if not username or not password:
            APILogger.log_error("/api/login", ValueError("Missing username or password"), None, ErrorCategory.VALIDATION_ERROR)
            raise HTTPException(status_code=400, detail="Username and password required")

        # Kullanıcı adı format doğrulama
        username_valid = SecurityValidator.validate_username(username)
        
        if not username_valid:
            APILogger.log_security_event("INVALID_USERNAME", f"Invalid username format: {username}", None, client_ip)
            raise HTTPException(status_code=400, detail="Invalid username format")

        # Temel kimlik doğrulama - TinyDB'den kullanıcı kontrolü
        # Şifreler hash'lenmiş olarak saklanır ve güvenli bir şekilde kontrol edilir
        
        # Username'i normalize et (user_manager'ın normalize fonksiyonunu kullan)
        username = user_manager.normalize_username(username.strip())
        
        # Kullanıcıyı TinyDB'den kontrol et (user_manager kullanarak)
        user_exists = user_manager.user_exists(username)
        
        if user_exists:
            # Şifreyi doğrula (user_manager kullanarak)
            password_valid = user_manager.verify_password(username, password)
            
            if password_valid:
                # Başarılı login sonrası rate limiter'ı reset et
                from security import _rate_limit_storage
                if client_ip in _rate_limit_storage:
                    _rate_limit_storage[client_ip].clear()
                
                # JWT token oluştur
                payload = {
                    "sub": username,
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)  # 24 saat geçerli
                }
                token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
                
                # Session oluştur veya güncelle
                from session_manager import session_manager
                session_data = session_manager.get_or_create_session(username, token=token)
                
                # Login sonrası yeni conversation oluştur (ChatGPT gibi)
                try:
                    new_conv_id = session_manager.create_conversation(username, "Yeni Sohbet")
                    session_manager.set_active_conversation(username, new_conv_id)
                except Exception as e:
                    # Hata olsa bile login başarılı olmalı
                    pass
                
                APILogger.log_request("/api/login", "POST", username)
                return {"token": token, "expires_in": 86400}  # 24 saat = 86400 saniye
        
        # Şifre yanlış veya kullanıcı bulunamadı
        APILogger.log_security_event("LOGIN_FAILED", f"Failed login attempt for username: {username}", None, client_ip)
        APILogger.log_error("/api/login", ValueError("Invalid credentials"), None, ErrorCategory.AUTH_ERROR)
        raise HTTPException(status_code=401, detail="Invalid username or password")
        
    except HTTPException:
        raise
    except Exception as e:
        APILogger.log_error("/api/login", e, None, ErrorCategory.AUTH_ERROR)
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@router.post("/api/logout")
def logout(user_id: str = Depends(get_current_user)):
    """
    Kullanıcı çıkış endpoint'i
    
    Session'ı temizler ve token'ı geçersiz kılar.
    """
    try:
        from session_manager import session_manager
        # Session'ı tamamen temizle (conversation'lar dahil)
        session_manager.clear_session(user_id)
        
        APILogger.log_request("/api/logout", "POST", user_id)
        return {"success": True, "message": "Logged out successfully"}
    except Exception as e:
        APILogger.log_error("/api/logout", e, user_id, ErrorCategory.AUTH_ERROR)
        raise HTTPException(status_code=500, detail=f"Failed to logout: {str(e)}")
