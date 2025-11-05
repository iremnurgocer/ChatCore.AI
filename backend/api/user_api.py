# -*- coding: utf-8 -*-
"""
Module: User API
Description: User preferences, profile management, and MFA setup endpoints.
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from core.database import get_async_session
from core.logger import APILogger, ErrorCategory
from api.auth_api import get_current_user
from models.user_model import User
from services.persona_service import persona_service

router = APIRouter(prefix="/api/v2", tags=["user"])


class UserPreferencesUpdate(BaseModel):
    """User preferences update model"""
    theme: Optional[str] = None  # light, dark
    persona: Optional[str] = None  # default, finance, it, hr, legal
    language: Optional[str] = None  # tr, en


class MFAVerifyRequest(BaseModel):
    """MFA verification request"""
    token: str


@router.get("/user/profile")
async def get_profile(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Get current user profile and preferences"""
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
        "mfa_enabled": user.mfa_enabled,
        "preferences": {
            "theme": user.theme or "light",
            "persona": user.persona or "default",
            "language": user.language or "tr"
        },
        "created_at": user.created_at.isoformat()
    }


@router.put("/user/preferences")
async def update_preferences(
    preferences: UserPreferencesUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Update user preferences"""
    # Validate theme
    if preferences.theme and preferences.theme not in ["light", "dark"]:
        raise HTTPException(status_code=400, detail="Invalid theme. Must be 'light' or 'dark'")
    
    # Validate persona
    if preferences.persona:
        available_personas = persona_service.get_available_personas()
        if preferences.persona not in available_personas:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid persona. Available: {', '.join(available_personas.keys())}"
            )
    
    # Validate language
    if preferences.language and preferences.language not in ["tr", "en"]:
        raise HTTPException(status_code=400, detail="Invalid language. Must be 'tr' or 'en'")
    
    # Update preferences
    if preferences.theme is not None:
        user.theme = preferences.theme
    if preferences.persona is not None:
        user.persona = preferences.persona
    if preferences.language is not None:
        user.language = preferences.language
    
    await session.commit()
    await session.refresh(user)
    
    APILogger.log_request(
        "/api/v2/user/preferences",
        "PUT",
        str(user.id),
        None,
        200
    )
    
    return {
        "success": True,
        "preferences": {
            "theme": user.theme,
            "persona": user.persona,
            "language": user.language
        }
    }


@router.get("/user/preferences/personas")
async def get_available_personas():
    """Get list of available personas"""
    return {
        "personas": persona_service.get_available_personas()
    }


@router.post("/user/mfa/setup")
async def setup_mfa(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Setup MFA (TOTP) - generates secret"""
    import secrets
    
    # Generate TOTP secret
    mfa_secret = secrets.token_hex(16)
    
    # Update user
    user.mfa_secret = mfa_secret
    user.mfa_enabled = False  # Not enabled until verified
    
    await session.commit()
    
    # In production, use pyotp to generate QR code URL
    # For now, return secret (in production, don't expose this directly)
    return {
        "success": True,
        "mfa_secret": mfa_secret,  # In production, generate QR code instead
        "message": "MFA setup initiated. Verify with /api/v2/user/mfa/verify"
    }


@router.post("/user/mfa/verify")
async def verify_mfa(
    request: MFAVerifyRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Verify MFA token and enable MFA"""
    if not user.mfa_secret:
        raise HTTPException(status_code=400, detail="MFA not set up. Call /api/v2/user/mfa/setup first")
    
    # In production, verify TOTP token using pyotp
    # For now, simple placeholder verification
    token = request.token.strip()
    
    if not token or len(token) != 6:
        raise HTTPException(status_code=400, detail="Invalid token format")
    
    # Placeholder: In production, use pyotp.TOTP(user.mfa_secret).verify(token)
    # For now, accept any 6-digit token (NOT SECURE - replace in production)
    try:
        int(token)  # Validate it's numeric
    except ValueError:
        raise HTTPException(status_code=400, detail="Token must be numeric")
    
    # Enable MFA
    user.mfa_enabled = True
    await session.commit()
    
    APILogger.log_security_event(
        "MFA_ENABLED",
        f"MFA enabled for user: {user.username}",
        str(user.id),
        None
    )
    
    return {
        "success": True,
        "message": "MFA verified and enabled"
    }


@router.post("/user/mfa/disable")
async def disable_mfa(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Disable MFA"""
    user.mfa_enabled = False
    user.mfa_secret = None
    await session.commit()
    
    APILogger.log_security_event(
        "MFA_DISABLED",
        f"MFA disabled for user: {user.username}",
        str(user.id),
        None
    )
    
    return {
        "success": True,
        "message": "MFA disabled"
    }

