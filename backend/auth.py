"""
Kimlik Doğrulama Modülü - JWT Token Yönetimi
"""
from fastapi import APIRouter, HTTPException, Request
import jwt
import datetime
import os
from security import SecurityValidator, strict_rate_limiter
from logger import APILogger, ErrorCategory

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")

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

    Args:
        user: 'username' ve 'password' anahtarlarına sahip dictionary
        request: FastAPI Request objesi (IP adresi için)

    Returns:
        'token' ve 'expires_in' anahtarlarına sahip dictionary

    Raises:
        HTTPException: Kimlik bilgileri geçersizse veya rate limit aşıldıysa
    """
    # Login için rate limiting
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
    if not SecurityValidator.validate_username(username):
        APILogger.log_security_event("INVALID_USERNAME", f"Invalid username format: {username}", None, client_ip)
        raise HTTPException(status_code=400, detail="Invalid username format")

    # Temel kimlik doğrulama (production'da veritabanı kullan)
    # Varsayılan kimlik bilgileri: admin/1234 (PRODUCTION'DA DEĞİŞTİR)
    if username == "admin" and password == "1234":
        payload = {
            "sub": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        
        # Session oluştur veya güncelle
        from session_manager import session_manager
        session_manager.get_or_create_session(username, token=token)
        
        APILogger.log_request("/api/login", "POST", username)
        return {"token": token, "expires_in": 7200}
    else:
        APILogger.log_security_event("LOGIN_FAILED", f"Failed login attempt for username: {username}", None, client_ip)
        APILogger.log_error("/api/login", ValueError("Invalid credentials"), None, ErrorCategory.AUTH_ERROR)
        raise HTTPException(status_code=401, detail="Invalid username or password")
