# -*- coding: utf-8 -*-
"""
Refresh Token Model - SQLModel definition for refresh_tokens table
"""
from datetime import datetime, timedelta
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, String, Boolean, Index
from sqlalchemy.sql import func

if TYPE_CHECKING:
    from models.user_model import User


class RefreshToken(SQLModel, table=True):
    """Refresh token model"""
    __tablename__ = "refresh_tokens"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    token_hash: str = Field(unique=True, index=True, max_length=255)
    user_id: int = Field(foreign_key="users.id", index=True)
    issued_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    expires_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True))
    )
    revoked: bool = Field(default=False)
    parent_id: Optional[int] = Field(
        default=None,
        foreign_key="refresh_tokens.id",
        nullable=True
    )
    
    # Relationships
    user: "User" = Relationship(back_populates="refresh_tokens")
    
    # Indexes
    __table_args__ = (
        Index("idx_refresh_tokens_user_id", "user_id"),
        Index("idx_refresh_tokens_expires_at", "expires_at"),
        Index("idx_refresh_tokens_revoked", "revoked"),
        Index("idx_refresh_tokens_token_hash", "token_hash", unique=True),
    )


class RefreshTokenCreate(SQLModel):
    """Refresh token creation model"""
    token_hash: str
    expires_at: datetime
    parent_id: Optional[int] = None


class RefreshTokenRead(SQLModel):
    """Refresh token read model"""
    id: int
    user_id: int
    issued_at: datetime
    expires_at: datetime
    revoked: bool
    
    class Config:
        from_attributes = True



