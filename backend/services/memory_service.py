# -*- coding: utf-8 -*-
"""
Module: Memory Service
Description: Conversation summarization and vector-based memory storage with Redis caching.
"""
from typing import Optional, List, Dict
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from core.database import get_async_session
from core.redis_client import get_redis
from core.logger import APILogger, ErrorCategory
from models.conversation_model import Conversation
from models.message_model import Message
from services.summary_service import summary_service
from services.rag_service import rag_service

# LangChain imports
try:
    from langchain_core.documents import Document as LangChainDocument
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


class MemoryService:
    """Service for conversation memory and summarization"""
    
    async def summarize_and_store(
        self,
        conversation_id: str,
        user_id: int,
        session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        """
        Summarize conversation and store summary
        
        Returns:
            Summary text
        """
        if session is None:
            async for db_session in get_async_session():
                return await self.summarize_and_store(conversation_id, user_id, db_session)
        
        try:
            # Get conversation
            result = await session.execute(
                select(Conversation).where(
                    Conversation.conversation_id == conversation_id,
                    Conversation.user_id == user_id
                )
            )
            conv = result.scalars().first()
            
            if not conv:
                return None
            
            # Get messages
            result = await session.execute(
                select(Message).where(
                    Message.conversation_id == conv.id,
                    Message.user_id == user_id
                ).order_by(Message.created_at)
            )
            messages = result.scalars().all()
            
            if not messages:
                return None
            
            # Convert to dict format
            message_dicts = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
            
            # Generate summary
            summary = await summary_service.summarize_conversation(message_dicts)
            
            # Store summary in Redis (for quick access)
            redis = await get_redis()
            summary_key = f"conv:summary:{conversation_id}"
            await redis.setex(summary_key, 86400 * 7, summary)  # 7 days TTL
            
            # Store summary in conversation metadata (if we add a summary field)
            # For now, we'll store it in Redis only
            
            # Create vector memory (optional - store summary as searchable document)
            if LANGCHAIN_AVAILABLE:
                await self._store_vector_memory(conversation_id, summary, user_id)
            
            return summary
        
        except Exception as e:
            APILogger.log_error(
                "/memory/summarize",
                e,
                str(user_id),
                ErrorCategory.AI_ERROR,
                conversation_id=conversation_id
            )
            return None
    
    async def get_summary(
        self,
        conversation_id: str
    ) -> Optional[str]:
        """Get conversation summary from cache"""
        try:
            redis = await get_redis()
            summary_key = f"conv:summary:{conversation_id}"
            summary = await redis.get(summary_key)
            return summary.decode() if summary else None
        except Exception:
            return None
    
    async def _store_vector_memory(
        self,
        conversation_id: str,
        summary: str,
        user_id: int
    ):
        """Store conversation summary as searchable vector memory"""
        if not LANGCHAIN_AVAILABLE:
            return
        
        try:
            # Create document from summary
            doc = LangChainDocument(
                page_content=summary,
                metadata={
                    "conversation_id": conversation_id,
                    "user_id": user_id,
                    "doc_type": "conversation_summary",
                    "created_at": datetime.utcnow().isoformat()
                }
            )
            
            # Add to FAISS index (with low priority - use separate memory index if needed)
            # For now, we'll skip this to avoid polluting main index
            # await rag_service.add_documents([doc], document_id=None)
        
        except Exception as e:
            APILogger.log_error(
                "/memory/store_vector",
                e,
                str(user_id),
                ErrorCategory.AI_ERROR,
                conversation_id=conversation_id
            )
    
    async def search_memory(
        self,
        query: str,
        user_id: int,
        limit: int = 5
    ) -> List[Dict]:
        """
        Search conversation summaries/memories
        
        Returns:
            List of relevant conversation summaries
        """
        # For now, return empty - would require separate memory index
        # In future, could search Redis keys or dedicated memory FAISS index
        return []


# Global instance
memory_service = MemoryService()

