# -*- coding: utf-8 -*-
"""
Module: Session Service
Description: PostgreSQL-based session management with Redis caching for conversations and messages.
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func
import uuid

from core.database import get_async_session
from core.redis_client import get_redis
from services.cache_service import get_cache_service
from models.user_model import User
from models.conversation_model import Conversation
from models.message_model import Message, MessageRole
from models.session_model import Session as SessionModel

cache_service = get_cache_service()


class SessionService:
    """Session management service with PostgreSQL + Redis"""
    
    async def get_or_create_conversation(
        self,
        user_id: int,
        conversation_id: Optional[str] = None,
        title: Optional[str] = None,
        session: Optional[AsyncSession] = None
    ) -> Conversation:
        """Get or create conversation"""
        if session is None:
            async for db_session in get_async_session():
                return await self.get_or_create_conversation(user_id, conversation_id, title, db_session)
        
        if conversation_id:
            result = await session.execute(
                select(Conversation).where(
                    Conversation.conversation_id == conversation_id,
                    Conversation.user_id == user_id
                )
            )
            conv = result.scalars().first()
            if conv:
                # Conversation bulundu, aktifleştir (updated_at'i güncelleme - ChatGPT gibi)
                if not conv.is_active:
                    # Diğer conversation'ları deaktif et
                    other_convs_result = await session.execute(
                        select(Conversation).where(
                            Conversation.user_id == user_id,
                            Conversation.id != conv.id
                        )
                    )
                    for other_conv in other_convs_result.scalars().all():
                        other_conv.is_active = False

                    # Bu conversation'ı aktifleştir (updated_at'i güncelleme - sadece mesaj gönderildiğinde güncellenecek)
                    conv.is_active = True
                    await session.commit()
                return conv
        
        # Create new conversation
        new_conv_id = str(uuid.uuid4())[:8]
        conversation = Conversation(
            conversation_id=new_conv_id,
            user_id=user_id,
            title=title or "Yeni Sohbet",
            is_active=True,
            updated_at=datetime.utcnow()  # Yeni conversation için updated_at'i ayarla
        )
        session.add(conversation)
        await session.flush()
        
        # Deactivate other conversations
        other_convs_result = await session.execute(
            select(Conversation).where(
                Conversation.user_id == user_id,
                Conversation.id != conversation.id
            )
        )
        for conv in other_convs_result.scalars().all():
            conv.is_active = False
            # Diğer conversation'ları deaktif ederken updated_at'i güncelleme (sadece aktifleştirildiğinde güncelle)

        await session.commit()
        return conversation
    
    async def get_conversation_history(
        self,
        user_id: int,
        conversation_id: Optional[str] = None,
        limit: Optional[int] = None,
        session: Optional[AsyncSession] = None
    ) -> List[Dict]:
        """Get conversation history as LLM format"""
        if session is None:
            async for db_session in get_async_session():
                return await self.get_conversation_history(user_id, conversation_id, limit, db_session)
        
        # Get conversation
        if conversation_id:
            result = await session.execute(
                select(Conversation).where(
                    Conversation.conversation_id == conversation_id,
                    Conversation.user_id == user_id
                )
            )
            conv = result.scalars().first()
            if not conv:
                return []
            conv_db_id = conv.id
        else:
            # Get active conversation
            result = await session.execute(
                select(Conversation).where(
                    Conversation.user_id == user_id,
                    Conversation.is_active == True
                )
            )
            conv = result.scalars().first()
            if not conv:
                return []
            conv_db_id = conv.id
        
        # Get messages
        query = select(Message).where(
            Message.conversation_id == conv_db_id,
            Message.user_id == user_id
        ).order_by(Message.created_at)
        
        if limit:
            query = query.limit(limit)
        
        result = await session.execute(query)
        messages = result.scalars().all()
        
        return [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in messages
        ]
    
    async def add_message(
        self,
        user_id: int,
        conversation_id: str,
        role: str,
        content: str,
        used_documents: Optional[Dict] = None,
        token_count: Optional[int] = None,
        session: Optional[AsyncSession] = None
    ) -> Message:
        """Add message to conversation"""
        if session is None:
            async for db_session in get_async_session():
                return await self.add_message(
                    user_id, conversation_id, role, content,
                    used_documents, token_count, db_session
                )
        
        # Get conversation
        result = await session.execute(
            select(Conversation).where(
                Conversation.conversation_id == conversation_id,
                Conversation.user_id == user_id
            )
        )
        conv = result.scalars().first()
        if not conv:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        # Convert role string to enum if needed
        if isinstance(role, str):
            role_enum = MessageRole.USER if role == "user" else MessageRole.ASSISTANT
        else:
            role_enum = role
        
        # Create message
        message = Message(
            message_id=str(uuid.uuid4())[:12],
            user_id=user_id,
            conversation_id=conv.id,
            role=role_enum,
            content=content,
            used_documents=used_documents,
            token_count=token_count
        )
        session.add(message)
        
        # Update conversation
        conv.message_count += 1
        conv.updated_at = datetime.utcnow()
        
        # Auto-rename from first user message
        if conv.message_count == 1 and role_enum == MessageRole.USER:
            title = content[:50] + ("..." if len(content) > 50 else "")
            conv.title = title
        
        await session.commit()
        await session.refresh(message)
        
        return message
    
    async def get_user_conversations(
        self,
        user_id: int,
        session: Optional[AsyncSession] = None
    ) -> List[Conversation]:
        """Get all user conversations - active conversation first, then by updated_at desc"""
        if session is None:
            async for db_session in get_async_session():
                return await self.get_user_conversations(user_id, db_session)
        
        # Önce aktif conversation'ı bul, sonra diğerlerini updated_at'e göre sırala
        # Aktif conversation her zaman en üstte olmalı
        result = await session.execute(
            select(Conversation).where(
                Conversation.user_id == user_id
            ).order_by(
                Conversation.is_active.desc(),  # Aktif conversation önce (True > False)
                Conversation.updated_at.desc()  # Sonra updated_at'e göre
            )
        )
        return result.scalars().all()
    
    async def delete_conversation(
        self,
        user_id: int,
        conversation_id: str,
        session: Optional[AsyncSession] = None
    ) -> bool:
        """Delete conversation and all messages"""
        if session is None:
            async for db_session in get_async_session():
                return await self.delete_conversation(user_id, conversation_id, db_session)
        
        result = await session.execute(
            select(Conversation).where(
                Conversation.conversation_id == conversation_id,
                Conversation.user_id == user_id
            )
        )
        conv = result.scalars().first()
        if not conv:
            return False
        
        # Delete messages (CASCADE should handle this, but explicit for clarity)
        messages_result = await session.execute(
            select(Message).where(Message.conversation_id == conv.id)
        )
        for msg in messages_result.scalars().all():
            await session.delete(msg)
        
        await session.delete(conv)
        await session.commit()
        
        return True
    
    async def deactivate_all_conversations(
        self,
        user_id: int,
        session: Optional[AsyncSession] = None
    ) -> bool:
        """Deactivate all conversations for a user"""
        if session is None:
            async for db_session in get_async_session():
                return await self.deactivate_all_conversations(user_id, db_session)

        result = await session.execute(
            select(Conversation).where(
                Conversation.user_id == user_id,
                Conversation.is_active == True
            )
        )
        conversations = result.scalars().all()
        for conv in conversations:
            conv.is_active = False

        await session.commit()
        return True

    async def get_active_conversation_id(
        self,
        user_id: int,
        session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        """Get active conversation ID"""
        if session is None:
            async for db_session in get_async_session():
                return await self.get_active_conversation_id(user_id, db_session)
        
        result = await session.execute(
            select(Conversation).where(
                Conversation.user_id == user_id,
                Conversation.is_active == True
            )
        )
        conv = result.scalars().first()
        return conv.conversation_id if conv else None


# Global instance
session_service = SessionService()

