# -*- coding: utf-8 -*-
"""
Session Model - SQLModel definition for sessions table
"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, String, Boolean, Index
from sqlalchemy.sql import func

if TYPE_CHECKING:
    from models.user_model import User


class Session(SQLModel, table=True):
    """Session model"""
    __tablename__ = "sessions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    access_jti: str = Field(unique=True, index=True, max_length=255)  # JWT ID
    user_agent: Optional[str] = Field(default=None, max_length=500)
    ip_address: Optional[str] = Field(default=None, max_length=50)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    last_activity: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    revoked: bool = Field(default=False)
    
    # Relationships
    user: "User" = Relationship(back_populates="sessions")
    
    # Indexes
    __table_args__ = (
        Index("idx_sessions_user_id", "user_id"),
        Index("idx_sessions_last_activity", "last_activity"),
        Index("idx_sessions_access_jti", "access_jti", unique=True),
        Index("idx_sessions_revoked", "revoked"),
    )


class SessionCreate(SQLModel):
    """Session creation model"""
    access_jti: str
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None


class SessionRead(SQLModel):
    """Session read model"""
    id: int
    user_id: int
    access_jti: str
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime
    last_activity: datetime
    revoked: bool
    
    class Config:
        from_attributes = True



