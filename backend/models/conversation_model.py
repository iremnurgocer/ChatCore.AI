# -*- coding: utf-8 -*-
"""
Module: Conversation Model
Description: SQLModel definition for conversations table with message relationships.
"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, String, Boolean, Index
from sqlalchemy.sql import func
import uuid

if TYPE_CHECKING:
    from models.user_model import User
    from models.message_model import Message


class ConversationBase(SQLModel):
    """Base conversation model"""
    title: str = Field(max_length=200)
    user_id: int = Field(foreign_key="users.id", index=True)


class Conversation(ConversationBase, table=True):
    """Conversation model"""
    __tablename__ = "conversations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: str = Field(
        unique=True,
        index=True,
        max_length=50,
        default_factory=lambda: str(uuid.uuid4())[:8]
    )
    is_active: bool = Field(default=False)
    message_count: int = Field(default=0)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )
    
    # Relationships
    user: "User" = Relationship(back_populates="conversations")
    messages: list["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_conversations_user_id", "user_id"),
        Index("idx_conversations_updated_at", "updated_at"),
        Index("idx_conversations_conversation_id", "conversation_id", unique=True),
    )


class ConversationCreate(SQLModel):
    """Conversation creation model"""
    title: str = Field(max_length=200)


class ConversationRead(ConversationBase):
    """Conversation read model"""
    id: int
    conversation_id: str
    is_active: bool
    message_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

