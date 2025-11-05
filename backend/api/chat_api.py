# -*- coding: utf-8 -*-
"""
Module: Chat API
Description: Chat endpoints for conversation management, message persistence, and RAG integration.
"""
import time
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session
from core.logger import APILogger, ErrorCategory
from core.security import default_rate_limiter, SecurityValidator
from api.auth_api import get_current_user
from models.user_model import User
from models.conversation_model import Conversation
from services.session_service import session_service
from services.ai_service import AIService
from services.rag_service import rag_service

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat")
async def chat(
    request: Request,
    chat_data: dict,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Send chat message - generates AI response with RAG
    
    Request body:
        {
            "prompt": "...",
            "conversation_id": "..." (optional)
        }
    
    Returns:
        {
            "response": "...",
            "conversation_id": "...",
            "used_documents": [...],
            "token_count": 123,
            "latency_ms": 456.7
        }
    """
    prompt = chat_data.get("prompt", "").strip()
    conversation_id = chat_data.get("conversation_id")
    
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")
    
    # Rate limiting
    ip_address = request.client.host if request.client else "unknown"
    identifier = f"{ip_address}:{user.id}"
    is_allowed, remaining = await default_rate_limiter.is_allowed(identifier, "/api/chat")
    
    if not is_allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={"X-RateLimit-Remaining": "0"}
        )
    
    # Input validation
    prompt = SecurityValidator.sanitize_input(prompt, str(user.id), ip_address)
    
    start_time = time.time()
    
    try:
        # Get or create conversation
        conversation = await session_service.get_or_create_conversation(
            user.id,
            conversation_id,
            session=session
        )
        
        # Get conversation history
        history = await session_service.get_conversation_history(
            user.id,
            conversation.conversation_id,
            limit=10,
            session=session
        )
        
        # RAG retrieval
        rag_docs, used_documents = await rag_service.retrieve(
            prompt,
            k=50,
            top_k=5,
            use_hybrid=True,
            use_rerank=True
        )
        
        # Format context
        context = rag_service.format_context(rag_docs, max_tokens=2000)
        
        # Generate AI response
        async with AIService() as ai:
            response_text, ai_metadata = await ai.generate(
                prompt=prompt,
                conversation_history=history,
                context=context,
                user_id=str(user.id)
            )
        
        latency_ms = (time.time() - start_time) * 1000
        
        # Store user message
        user_message = await session_service.add_message(
            user.id,
            conversation.conversation_id,
            role="user",
            content=prompt,
            session=session
        )
        
        # Store assistant message with metadata
        assistant_message = await session_service.add_message(
            user.id,
            conversation.conversation_id,
            role="assistant",
            content=response_text,
            used_documents={"documents": used_documents},
            token_count=ai_metadata.get("token_count"),
            session=session
        )
        
        # Log chat query
        APILogger.log_chat_query(
            str(user.id),
            prompt,
            response_text,
            latency_ms / 1000,
            conversation.conversation_id
        )
        
        return {
            "response": response_text,
            "conversation_id": conversation.conversation_id,
            "used_documents": used_documents,
            "token_count": ai_metadata.get("token_count"),
            "latency_ms": round(latency_ms, 2)
        }
    
    except Exception as e:
        APILogger.log_error(
            "/api/chat",
            e,
            str(user.id),
            ErrorCategory.AI_ERROR
        )
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@router.get("/conversations")
async def get_conversations(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Get all user conversations sorted by updated_at desc"""
    conversations = await session_service.get_user_conversations(user.id, session=session)
    
    # Get active conversation ID
    active_conversation_id = await session_service.get_active_conversation_id(user.id, session=session)
    
    return {
        "conversations": [
            {
                "id": conv.conversation_id,
                "conversation_id": conv.conversation_id,  # Backward compatibility
                "title": conv.title,
                "message_count": conv.message_count,
                "is_active": conv.is_active,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat()
            }
            for conv in conversations
        ],
        "active_conversation_id": active_conversation_id
    }


@router.post("/conversations/new")
async def create_conversation(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Create new conversation"""
    conversation = await session_service.get_or_create_conversation(
        user.id,
        None,
        title="Yeni Sohbet",
        session=session
    )
    
    return {
        "conversation_id": conversation.conversation_id,
        "id": conversation.conversation_id,  # Backward compatibility
        "title": conversation.title,
        "message_count": conversation.message_count,
        "created_at": conversation.created_at.isoformat()
    }


@router.post("/conversations/{conversation_id}/switch")
async def switch_conversation(
    conversation_id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Switch active conversation"""
    conversation = await session_service.get_or_create_conversation(
        user.id,
        conversation_id,
        session=session
    )
    
    return {
        "id": conversation.conversation_id,
        "title": conversation.title,
        "message_count": conversation.message_count,
        "is_active": conversation.is_active
    }


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Delete conversation"""
    success = await session_service.delete_conversation(
        user.id,
        conversation_id,
        session=session
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {"success": True}


@router.get("/conversation/{conversation_id}/restore")
async def restore_conversation(
    conversation_id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Restore conversation history"""
    history = await session_service.get_conversation_history(
        user.id,
        conversation_id,
        session=session
    )
    
    return {
        "conversation_id": conversation_id,
        "messages": history
    }

