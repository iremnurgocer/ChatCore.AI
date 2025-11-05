# -*- coding: utf-8 -*-
"""
Module: User Model
Description: SQLModel definition for users table with authentication and preferences.
"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, String, Boolean, Index
from sqlalchemy.sql import func

if TYPE_CHECKING:
    from models.conversation_model import Conversation
    from models.refresh_token_model import RefreshToken
    from models.session_model import Session
    from models.message_model import Message


class UserBase(SQLModel):
    """Base user model"""
    username: str = Field(unique=True, index=True, max_length=50)
    email: Optional[str] = Field(default=None, max_length=255)
    is_active: bool = Field(default=True)
    is_admin: bool = Field(default=False)


class User(UserBase, table=True):
    """User model"""
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    password_hash: str = Field(max_length=255)
    salt: str = Field(max_length=64)
    mfa_secret: Optional[str] = Field(default=None, max_length=32)  # TOTP secret
    mfa_enabled: bool = Field(default=False)
    
    # User preferences
    theme: Optional[str] = Field(default="light", max_length=20)  # light, dark
    persona: Optional[str] = Field(default="default", max_length=50)  # default, finance, it, hr, legal
    language: Optional[str] = Field(default="tr", max_length=10)  # tr, en
    
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )
    
    # Relationships
    conversations: list["Conversation"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    refresh_tokens: list["RefreshToken"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    sessions: list["Session"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    messages: list["Message"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_users_username", "username", unique=True),
    )


class UserCreate(UserBase):
    """User creation model"""
    password: str


class UserRead(UserBase):
    """User read model"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
