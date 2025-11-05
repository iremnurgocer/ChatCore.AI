# -*- coding: utf-8 -*-
"""
Module: Analytics API
Description: Health checks, statistics, and Prometheus metrics endpoints.
"""
import time
from datetime import datetime
from fastapi import APIRouter, Response, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func

from core.database import get_async_session
from core.redis_client import get_redis
from core.logger import APILogger, ErrorCategory
from models.user_model import User
from models.conversation_model import Conversation
from models.message_model import Message
from models.document_model import Document
from services.analytics_service import analytics_service
from api.auth_api import get_current_user

router = APIRouter(prefix="/api", tags=["analytics"])
v2_router = APIRouter(prefix="/api/v2", tags=["analytics"])

# Prometheus metrics (simple in-memory for now)
_metrics = {
    "requests_total": 0,
    "request_latency_histogram": [],
    "rag_retrieval_hit_ratio": 0.0,
    "cache_hits_total": 0
}


@router.get("/status")
async def health_check():
    """Health check endpoint"""
    status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "not configured",
        "redis": "not configured",
        "data_sources": {
            "employees": 0,
            "projects": 0,
            "departments": 0,
            "procedures": 0
        }
    }
    
    # Check database
    try:
        async for session in get_async_session():
            await session.execute(select(1))
            status["database"] = "connected"
            
            # Get document counts
            try:
                employee_result = await session.execute(
                    select(func.count(Document.id)).where(Document.doc_type == "employee")
                )
                status["data_sources"]["employees"] = employee_result.scalar() or 0
                
                project_result = await session.execute(
                    select(func.count(Document.id)).where(Document.doc_type == "project")
                )
                status["data_sources"]["projects"] = project_result.scalar() or 0
                
                dept_result = await session.execute(
                    select(func.count(Document.id)).where(Document.doc_type == "department")
                )
                status["data_sources"]["departments"] = dept_result.scalar() or 0
                
                proc_result = await session.execute(
                    select(func.count(Document.id)).where(Document.doc_type == "procedure")
                )
                status["data_sources"]["procedures"] = proc_result.scalar() or 0
            except Exception:
                pass  # If query fails, keep defaults
            
            # Session will be closed automatically after the async for loop
            return status
    except Exception:
        status["database"] = "disconnected"
    
    # Check Redis
    try:
        redis = await get_redis()
        await redis.ping()
        status["redis"] = "connected"
    except Exception:
        status["redis"] = "disconnected"
    
    # Overall status
    if status["database"] == "disconnected" or status["redis"] == "disconnected":
        status["status"] = "degraded"
    
    return status


@router.get("/stats")
async def get_stats(session: AsyncSession = Depends(get_async_session)):
    """Get basic statistics"""
    try:
        # User count
        user_result = await session.execute(select(func.count(User.id)))
        user_count = user_result.scalar() or 0
        
        # Active user count
        active_user_result = await session.execute(
            select(func.count(User.id)).where(User.is_active == True)
        )
        active_user_count = active_user_result.scalar() or 0
        
        # Conversation count
        conv_result = await session.execute(select(func.count(Conversation.id)))
        conv_count = conv_result.scalar() or 0
        
        # Message count
        msg_result = await session.execute(select(func.count(Message.id)))
        msg_count = msg_result.scalar() or 0
        
        return {
            "users": {
                "total": user_count,
                "active": active_user_count
            },
            "conversations": {
                "total": conv_count
            },
            "messages": {
                "total": msg_count
            },
            "metrics": {
                "requests_total": _metrics["requests_total"],
                "rag_hit_ratio": _metrics["rag_retrieval_hit_ratio"],
                "cache_hits": _metrics["cache_hits_total"]
            }
        }
    except Exception as e:
        APILogger.log_error(
            "/api/stats",
            e,
            None,
            ErrorCategory.DATABASE_ERROR
        )
        raise HTTPException(status_code=500, detail=f"Stats error: {str(e)}")


@router.get("/metrics")
async def prometheus_metrics():
    """Prometheus metrics endpoint"""
    metrics_lines = []
    
    # Request total
    metrics_lines.append(f"chatcore_requests_total {_metrics['requests_total']}")
    
    # Request latency histogram (simplified)
    if _metrics["request_latency_histogram"]:
        avg_latency = sum(_metrics["request_latency_histogram"]) / len(_metrics["request_latency_histogram"])
        metrics_lines.append(f"chatcore_request_latency_seconds {avg_latency}")
    
    # RAG hit ratio
    metrics_lines.append(f"chatcore_rag_retrieval_hit_ratio {_metrics['rag_retrieval_hit_ratio']}")
    
    # Cache hits
    metrics_lines.append(f"chatcore_cache_hits_total {_metrics['cache_hits_total']}")
    
    return Response(
        content="\n".join(metrics_lines) + "\n",
        media_type="text/plain"
    )


def record_request(latency_ms: float):
    """Record request metric"""
    _metrics["requests_total"] += 1
    _metrics["request_latency_histogram"].append(latency_ms / 1000)
    # Keep only last 1000 entries
    if len(_metrics["request_latency_histogram"]) > 1000:
        _metrics["request_latency_histogram"] = _metrics["request_latency_histogram"][-1000:]


def record_rag_hit(ratio: float):
    """Record RAG hit ratio"""
    _metrics["rag_retrieval_hit_ratio"] = ratio


def record_cache_hit():
    """Record cache hit"""
    _metrics["cache_hits_total"] += 1


# V2 Analytics endpoints
@v2_router.get("/analytics/stats")
async def get_analytics_stats(
    days: int = 7,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Get comprehensive analytics statistics (admin only)"""
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Usage by department
        usage_by_dept = await analytics_service.get_usage_by_department(days, session)
        
        # Top queries
        top_queries = await analytics_service.get_top_queries(limit=10, days=days, session=session)
        
        # Knowledge gaps
        knowledge_gaps = await analytics_service.get_knowledge_gaps(days, session)
        
        # Intent distribution
        intent_dist = await analytics_service.get_intent_distribution(days, session)
        
        # Document stats
        doc_stats = await analytics_service.get_document_stats(session)
        
        # User patterns
        user_patterns = await analytics_service.get_user_patterns(days=days, session=session)
        
        return {
            "period_days": days,
            "usage_by_department": usage_by_dept,
            "top_queries": top_queries,
            "knowledge_gaps": knowledge_gaps,
            "intent_distribution": intent_dist,
            "document_stats": doc_stats,
            "user_patterns": user_patterns,
            "metrics": {
                "requests_total": _metrics["requests_total"],
                "rag_hit_ratio": _metrics["rag_retrieval_hit_ratio"],
                "cache_hits": _metrics["cache_hits_total"]
            }
        }
    except Exception as e:
        APILogger.log_error(
            "/api/v2/analytics/stats",
            e,
            str(user.id),
            ErrorCategory.AI_ERROR
        )
        raise HTTPException(status_code=500, detail=f"Analytics error: {str(e)}")


@v2_router.get("/analytics/user")
async def get_user_analytics(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Get user-specific analytics"""
    try:
        patterns = await analytics_service.get_user_patterns(user.id, days=30, session=session)
        
        return {
            "user_id": user.id,
            "patterns": patterns
        }
    except Exception as e:
        APILogger.log_error(
            "/api/v2/analytics/user",
            e,
            str(user.id),
            ErrorCategory.AI_ERROR
        )
        raise HTTPException(status_code=500, detail=f"Analytics error: {str(e)}")

