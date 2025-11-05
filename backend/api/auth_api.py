# -*- coding: utf-8 -*-
"""
Module: Auth API
Description: JWT authentication endpoints with refresh token rotation, account lockout, and MFA support.
"""
import hashlib
import secrets
import binascii
import uuid
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Request, Header, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
import jwt

from core.config import get_settings
from core.database import get_async_session, get_async_session_optional
from core.security import (
    SecurityValidator,
    strict_rate_limiter,
    jti_blacklist,
    account_lockout
)
from core.logger import APILogger, ErrorCategory
from models.user_model import User
from models.refresh_token_model import RefreshToken
from models.session_model import Session

settings = get_settings()
router = APIRouter(prefix="/api", tags=["auth"])
security_scheme = HTTPBearer()


def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """Hash password using PBKDF2-HMAC-SHA256"""
    if salt is None:
        salt_bytes = secrets.token_bytes(16)
        salt_hex = salt_bytes.hex()
    else:
        salt_bytes = binascii.unhexlify(salt)
        salt_hex = salt
    
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt_bytes,
        100000
    )
    
    return password_hash.hex(), salt_hex


def verify_password(password: str, hashed_password: str, salt: str) -> bool:
    """Verify password"""
    try:
        salt_bytes = binascii.unhexlify(salt)
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt_bytes,
            100000
        )
        hashed_input = password_hash.hex()
        return secrets.compare_digest(hashed_input, hashed_password)
    except Exception:
        return False


def create_access_token(user_id: str, jti: str) -> str:
    """Create JWT access token (15 minutes)"""
    # Access token expires in 15 minutes (or from settings if configured differently)
    expire_minutes = min(settings.ACCESS_TOKEN_EXPIRE_MINUTES, 15)  # Max 15 minutes
    payload = {
        "sub": user_id,
        "jti": jti,
        "exp": datetime.utcnow() + timedelta(minutes=expire_minutes),
        "iat": datetime.utcnow(),
        "type": "access"
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def create_refresh_token_hash(token: str) -> str:
    """Create hash of refresh token for storage"""
    return hashlib.sha256(token.encode()).hexdigest()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    session: AsyncSession = Depends(get_async_session)
) -> User:
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    
    try:
        # Decode token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        
        # Check token type
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        # Check JTI blacklist
        jti = payload.get("jti")
        if jti and await jti_blacklist.is_blacklisted(jti):
            raise HTTPException(status_code=401, detail="Token revoked")
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        # Get user from database
        result = await session.execute(select(User).where(User.username == user_id))
        user = result.scalars().first()
        
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="User not found or inactive")
        
        # Set user ID in logger context
        APILogger.set_user_id(user_id)
        
        return user
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/login", response_model=dict)
async def login(
    request: Request,
    credentials: dict,
    session: Optional[AsyncSession] = Depends(get_async_session_optional)
):
    """
    User login - issues access token (15m) + refresh token (30d)
    
    Returns:
        {
            "access_token": "...",
            "refresh_token": "...",
            "token_type": "bearer",
            "expires_in": 900
        }
    """
    # Check if database is available
    if session is None:
        raise HTTPException(
            status_code=503,
            detail="Database not configured. Please set DATABASE_URL in .env file and restart the server."
        )
    
    username = credentials.get("username", "").strip()
    password = credentials.get("password", "")
    
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password required")
    
    # Rate limiting
    ip_address = request.client.host if request.client else "unknown"
    identifier = f"{ip_address}:login"
    is_allowed, remaining = await strict_rate_limiter.is_allowed(identifier, "/api/login")
    
    if not is_allowed:
        APILogger.log_security_event(
            "RATE_LIMIT",
            f"Login rate limit exceeded from {ip_address}",
            None,
            ip_address
        )
        raise HTTPException(
            status_code=429,
            detail="Too many login attempts",
            headers={"X-RateLimit-Remaining": "0", "Retry-After": "60"}
        )
    
    # Account lockout check
    normalized_username = username.strip().casefold()
    if await account_lockout.is_locked(normalized_username):
        APILogger.log_security_event(
            "ACCOUNT_LOCKED",
            f"Login attempt on locked account: {username}",
            None,
            ip_address
        )
        raise HTTPException(
            status_code=423,
            detail="Account locked due to too many failed login attempts. Please try again later."
        )
    
    # Validate username format
    if not SecurityValidator.validate_username(username):
        raise HTTPException(status_code=400, detail="Invalid username format")
    
    # Get user from database
    result = await session.execute(select(User).where(User.username == normalized_username))
    user = result.scalars().first()
    
    if not user:
        # Record failed attempt
        await account_lockout.record_failed_login(normalized_username)
        APILogger.log_security_event(
            "LOGIN_FAILED",
            f"Invalid username: {username}",
            None,
            ip_address
        )
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Verify password
    password_valid = verify_password(password, user.password_hash, user.salt)
    
    if not password_valid:
        # Record failed attempt
        locked = await account_lockout.record_failed_login(normalized_username)
        if locked:
            APILogger.log_security_event(
                "ACCOUNT_LOCKED",
                f"Account locked after failed attempts: {username}",
                str(user.id),
                ip_address
            )
        
        APILogger.log_security_event(
            "LOGIN_FAILED",
            f"Invalid password for user: {username}",
            str(user.id),
            ip_address
        )
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Unlock account on successful login
    await account_lockout.unlock(normalized_username)
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")
    
    # Generate tokens
    access_jti = str(uuid.uuid4())
    refresh_token_value = secrets.token_urlsafe(32)
    refresh_token_hash = create_refresh_token_hash(refresh_token_value)
    
    # Create access token (15 minutes)
    expire_minutes = min(settings.ACCESS_TOKEN_EXPIRE_MINUTES, 15)  # Max 15 minutes
    access_token = create_access_token(user.username, access_jti)
    access_expires = expire_minutes * 60  # Convert to seconds
    
    # Create refresh token (30 days)
    refresh_expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    # Store refresh token in database
    refresh_token = RefreshToken(
        token_hash=refresh_token_hash,
        user_id=user.id,
        expires_at=refresh_expires_at
    )
    session.add(refresh_token)
    await session.flush()
    
    # Create session
    db_session = Session(
        user_id=user.id,
        access_jti=access_jti,
        user_agent=request.headers.get("User-Agent"),
        ip_address=ip_address
    )
    session.add(db_session)
    await session.commit()
    
    APILogger.log_security_event(
        "LOGIN_SUCCESS",
        f"User logged in: {username}",
        str(user.id),
        ip_address
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token_value,
        "token_type": "bearer",
        "expires_in": access_expires,
        "refresh_expires_in": settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400
    }


@router.post("/token/refresh", response_model=dict)
async def refresh_token(
    request: Request,
    refresh_token_data: dict,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Refresh access token - rotates refresh token
    
    Request body:
        {"refresh_token": "..."}
    
    Returns:
        New access_token + refresh_token pair
    """
    refresh_token_value = refresh_token_data.get("refresh_token")
    if not refresh_token_value:
        raise HTTPException(status_code=400, detail="Refresh token required")
    
    # Hash the provided refresh token
    refresh_token_hash = create_refresh_token_hash(refresh_token_value)
    
    # Find refresh token in database
    result = await session.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == refresh_token_hash,
            RefreshToken.revoked == False
        )
    )
    refresh_token = result.scalars().first()
    
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    # Check expiry
    if refresh_token.expires_at < datetime.utcnow():
        # Revoke expired token
        refresh_token.revoked = True
        await session.commit()
        raise HTTPException(status_code=401, detail="Refresh token expired")
    
    # Get user
    result = await session.execute(select(User).where(User.id == refresh_token.user_id))
    user = result.scalars().first()
    
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    
    # Revoke old refresh token
    refresh_token.revoked = True
    
    # Revoke old access token JTI (if we have it stored)
    # Note: We'd need to track access_jti in refresh token for this
    # For now, we'll revoke the refresh token chain
    
    # Revoke parent chain if exists
    if refresh_token.parent_id:
        parent_result = await session.execute(
            select(RefreshToken).where(RefreshToken.id == refresh_token.parent_id)
        )
        parent = parent_result.scalars().first()
        if parent:
            parent.revoked = True
    
    # Generate new tokens
    access_jti = str(uuid.uuid4())
    new_refresh_token_value = secrets.token_urlsafe(32)
    new_refresh_token_hash = create_refresh_token_hash(new_refresh_token_value)
    
    # Create new access token
    access_token = create_access_token(user.username, access_jti)
    
    # Create new refresh token with parent pointer
    new_refresh_token = RefreshToken(
        token_hash=new_refresh_token_hash,
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        parent_id=refresh_token.id  # Parent pointer for rotation tracking
    )
    session.add(new_refresh_token)
    
    # Update session
    ip_address = request.client.host if request.client else "unknown"
    db_session = Session(
        user_id=user.id,
        access_jti=access_jti,
        user_agent=request.headers.get("User-Agent"),
        ip_address=ip_address
    )
    session.add(db_session)
    
    await session.commit()
    
    APILogger.log_security_event(
        "TOKEN_REFRESHED",
        f"Token refreshed for user: {user.username}",
        str(user.id),
        ip_address
    )
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token_value,
        "token_type": "bearer",
        "expires_in": min(settings.ACCESS_TOKEN_EXPIRE_MINUTES, 15) * 60,
        "refresh_expires_in": settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400
    }


@router.post("/logout")
async def logout(
    request: Request,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Logout - revoke access token"""
    # Extract JTI from token
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            jti = payload.get("jti")
            if jti:
                # Blacklist access token (TTL = access token expiry)
                expire_minutes = min(settings.ACCESS_TOKEN_EXPIRE_MINUTES, 15)
                await jti_blacklist.add(jti, expire_minutes * 60)
        except Exception:
            pass
    
    # Revoke all refresh tokens for user
    result = await session.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == user.id,
            RefreshToken.revoked == False
        )
    )
    refresh_tokens = result.scalars().all()
    for rt in refresh_tokens:
        rt.revoked = True
    
    # Revoke session
    result = await session.execute(
        select(Session).where(
            Session.user_id == user.id,
            Session.revoked == False
        )
    )
    sessions = result.scalars().all()
    for sess in sessions:
        sess.revoked = True
    
    await session.commit()
    
    APILogger.log_security_event(
        "LOGOUT",
        f"User logged out: {user.username}",
        str(user.id),
        request.client.host if request.client else None
    )
    
    return {"success": True, "message": "Logged out successfully"}


@router.post("/mfa/setup")
async def setup_mfa(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Setup MFA (TOTP) - scaffolding"""
    # Generate TOTP secret (simplified - use pyotp in production)
    import secrets
    mfa_secret = secrets.token_hex(16)
    
    # Update user
    user.mfa_secret = mfa_secret
    user.mfa_enabled = False  # Not enabled until verified
    
    await session.commit()
    
    # In production, return QR code URL for TOTP app
    return {
        "success": True,
        "mfa_secret": mfa_secret,  # In production, don't expose this directly
        "message": "MFA setup initiated. Verify with /api/mfa/verify"
    }


@router.post("/mfa/verify")
async def verify_mfa(
    request: dict,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Verify MFA (TOTP) - scaffolding"""
    token = request.get("token")
    if not token:
        raise HTTPException(status_code=400, detail="MFA token required")
    
    # In production, verify TOTP token using pyotp
    # For now, just a placeholder
    if not user.mfa_secret:
        raise HTTPException(status_code=400, detail="MFA not set up")
    
    # Placeholder verification
    # In production: verify_totp(user.mfa_secret, token)
    
    user.mfa_enabled = True
    await session.commit()
    
    return {"success": True, "message": "MFA verified and enabled"}


@router.get("/me", response_model=dict)
async def get_current_user_info(user: User = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
        "mfa_enabled": user.mfa_enabled,
        "created_at": user.created_at.isoformat()
    }

