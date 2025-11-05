# -*- coding: utf-8 -*-
"""
Module: Message Model
Description: SQLModel definition for messages table with RAG metadata support.
"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, Text, Integer, JSON, Index, Enum as SAEnum
from sqlalchemy.sql import func
import uuid
import enum

if TYPE_CHECKING:
    from models.user_model import User
    from models.conversation_model import Conversation


class MessageRole(str, enum.Enum):
    """Message role enum"""
    USER = "user"
    ASSISTANT = "assistant"


class MessageBase(SQLModel):
    """Base message model"""
    role: MessageRole = Field(sa_column=Column(SAEnum(MessageRole, name="message_role_enum")))
    content: str = Field(sa_column=Column(Text))
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)


class Message(MessageBase, table=True):
    """Message model"""
    __tablename__ = "messages"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    message_id: str = Field(
        unique=True,
        index=True,
        max_length=50,
        default_factory=lambda: str(uuid.uuid4())[:12]
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    
    # RAG metadata
    used_documents: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    token_count: Optional[int] = Field(default=None)
    
    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")
    user: "User" = Relationship(back_populates="messages")
    
    # Indexes
    __table_args__ = (
        Index("idx_messages_conversation_id", "conversation_id"),
        Index("idx_messages_created_at", "created_at"),
        Index("idx_messages_user_id", "user_id"),
        Index("idx_messages_message_id", "message_id", unique=True),
    )


class MessageCreate(SQLModel):
    """Message creation model"""
    role: MessageRole
    content: str


class MessageRead(MessageBase):
    """Message read model"""
    id: int
    message_id: str
    created_at: datetime
    used_documents: Optional[dict] = None
    token_count: Optional[int] = None
    
    class Config:
        from_attributes = True

