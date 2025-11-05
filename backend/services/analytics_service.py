# -*- coding: utf-8 -*-
"""
Module: Analytics Service
Description: Usage analytics aggregation including department stats, knowledge gaps, and intent distribution.
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func, and_, or_

from core.database import get_async_session
from core.redis_client import get_redis
from models.user_model import User
from models.conversation_model import Conversation
from models.message_model import Message, MessageRole
from models.document_model import Document


class AnalyticsService:
    """Service for analytics and statistics"""
    
    async def get_usage_by_department(
        self,
        days: int = 30,
        session: Optional[AsyncSession] = None
    ) -> Dict[str, int]:
        """Get usage statistics by department"""
        if session is None:
            async for db_session in get_async_session():
                return await self.get_usage_by_department(days, db_session)
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get conversations by department (from user's department or document department)
        result = await session.execute(
            select(
                Document.department,
                func.count(Conversation.id).label("count")
            ).join(
                User, User.id == Conversation.user_id
            ).join(
                Document, Document.department.isnot(None)
            ).where(
                Conversation.created_at >= cutoff_date
            ).group_by(Document.department)
        )
        
        usage = {}
        for row in result:
            dept, count = row.department, row.count
            if dept:
                usage[dept] = count
        
        return usage
    
    async def get_top_queries(
        self,
        limit: int = 10,
        days: int = 7,
        session: Optional[AsyncSession] = None
    ) -> List[Dict]:
        """Get top queries by frequency"""
        if session is None:
            async for db_session in get_async_session():
                return await self.get_top_queries(limit, days, db_session)
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get user messages (queries)
        result = await session.execute(
            select(
                Message.content,
                func.count(Message.id).label("count")
            ).where(
                and_(
                    Message.role == MessageRole.USER,
                    Message.created_at >= cutoff_date
                )
            ).group_by(Message.content).order_by(func.count(Message.id).desc()).limit(limit)
        )
        
        queries = []
        for row in result:
            content, count = row.content, row.count
            queries.append({
                "query": content[:100] + "..." if len(content) > 100 else content,
                "count": count
            })
        
        return queries
    
    async def get_knowledge_gaps(
        self,
        days: int = 7,
        session: Optional[AsyncSession] = None
    ) -> List[Dict]:
        """Identify knowledge gaps (queries with no document hits)"""
        if session is None:
            async for db_session in get_async_session():
                return await self.get_knowledge_gaps(days, db_session)
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get messages with no used_documents or empty used_documents
        result = await session.execute(
            select(Message).where(
                and_(
                    Message.role == MessageRole.USER,
                    Message.created_at >= cutoff_date,
                    or_(
                        Message.used_documents.is_(None),
                        func.jsonb_path_exists(Message.used_documents, '$.documents', '[]')
                    )
                )
            ).limit(20)
        )
        
        gaps = []
        for msg in result.scalars().all():
            gaps.append({
                "query": msg.content[:100] + "..." if len(msg.content) > 100 else msg.content,
                "conversation_id": msg.conversation_id,
                "created_at": msg.created_at.isoformat()
            })
        
        return gaps
    
    async def get_user_patterns(
        self,
        user_id: Optional[int] = None,
        days: int = 30,
        session: Optional[AsyncSession] = None
    ) -> Dict:
        """Get user usage patterns"""
        if session is None:
            async for db_session in get_async_session():
                return await self.get_user_patterns(user_id, days, db_session)
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        query = select(
            func.count(Conversation.id).label("conversations"),
            func.count(Message.id).label("messages"),
            func.avg(func.length(Message.content)).label("avg_message_length")
        ).join(
            Message, Message.conversation_id == Conversation.id
        ).where(
            Conversation.created_at >= cutoff_date
        )
        
        if user_id:
            query = query.where(Conversation.user_id == user_id)
        
        result = await session.execute(query)
        row = result.first()
        
        if row:
            return {
                "conversations": row.conversations or 0,
                "messages": row.messages or 0,
                "avg_message_length": round(row.avg_message_length or 0, 2)
            }
        return {
            "conversations": 0,
            "messages": 0,
            "avg_message_length": 0
        }
    
    async def get_intent_distribution(
        self,
        days: int = 7,
        session: Optional[AsyncSession] = None
    ) -> Dict[str, int]:
        """Get intent distribution (simplified - based on keywords)"""
        if session is None:
            async for db_session in get_async_session():
                return await self.get_intent_distribution(days, db_session)
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Simple keyword-based intent detection
        intents = {
            "question": 0,
            "request": 0,
            "information": 0,
            "other": 0
        }
        
        result = await session.execute(
            select(Message.content).where(
                and_(
                    Message.role == MessageRole.USER,
                    Message.created_at >= cutoff_date
                )
            )
        )
        
        for row in result:
            content = row.content
            content_lower = content.lower()
            if "?" in content or "nasıl" in content_lower or "nedir" in content_lower:
                intents["question"] += 1
            elif "istiyorum" in content_lower or "yap" in content_lower or "göster" in content_lower:
                intents["request"] += 1
            elif "bilgi" in content_lower or "hakkında" in content_lower:
                intents["information"] += 1
            else:
                intents["other"] += 1
        
        return intents
    
    async def get_document_stats(
        self,
        session: Optional[AsyncSession] = None
    ) -> Dict:
        """Get document statistics"""
        if session is None:
            async for db_session in get_async_session():
                return await self.get_document_stats(db_session)
        
        # Total documents
        total_result = await session.execute(select(func.count(Document.id)))
        total = total_result.scalar() or 0
        
        # By type
        type_result = await session.execute(
            select(
                Document.doc_type,
                func.count(Document.id).label("count")
            ).group_by(Document.doc_type)
        )
        
        by_type = {}
        for row in type_result:
            doc_type, count = row.doc_type, row.count
            by_type[doc_type] = count
        
        # By department
        dept_result = await session.execute(
            select(
                Document.department,
                func.count(Document.id).label("count")
            ).where(
                Document.department.isnot(None)
            ).group_by(Document.department)
        )
        
        by_department = {}
        for row in dept_result:
            dept, count = row.department, row.count
            if dept:
                by_department[dept] = count
        
        return {
            "total": total,
            "by_type": by_type,
            "by_department": by_department
        }


# Global instance
analytics_service = AnalyticsService()

