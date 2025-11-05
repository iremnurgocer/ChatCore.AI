# -*- coding: utf-8 -*-
"""
Models __init__ - Aggregates all models for Alembic metadata

This module imports all models so Alembic can discover them.
"""
from sqlmodel import SQLModel

# Import all models to register them with SQLModel metadata
from models.user_model import User
from models.conversation_model import Conversation
from models.message_model import Message
from models.refresh_token_model import RefreshToken
from models.session_model import Session
from models.document_model import Document

# Export metadata for Alembic
__all__ = [
    "User",
    "Conversation",
    "Message",
    "RefreshToken",
    "Session",
    "Document",
    "SQLModel",
]

# SQLModel metadata - used by Alembic
metadata = SQLModel.metadata
