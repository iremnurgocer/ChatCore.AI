# -*- coding: utf-8 -*-
"""
Module: Search API
Description: Semantic and keyword search endpoints for documents and conversations.
"""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, or_, func

from core.database import get_async_session
from core.logger import APILogger, ErrorCategory
from api.auth_api import get_current_user
from models.user_model import User
from models.document_model import Document
from models.message_model import Message
from models.conversation_model import Conversation
from services.rag_service import rag_service
from services.memory_service import memory_service

router = APIRouter(prefix="/api/v2", tags=["search"])


@router.get("/search")
async def search(
    query: str = Query(..., description="Search query"),
    search_type: str = Query("semantic", description="semantic, keyword, or hybrid"),
    doc_type: Optional[str] = Query(None, description="Filter by document type"),
    department: Optional[str] = Query(None, description="Filter by department"),
    limit: int = Query(10, ge=1, le=50, description="Number of results"),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Search documents and conversations
    
    Supports:
    - semantic: Vector similarity search (FAISS)
    - keyword: Text matching in database
    - hybrid: Both semantic and keyword
    """
    if not query or len(query.strip()) < 2:
        raise HTTPException(status_code=400, detail="Query too short (minimum 2 characters)")
    
    try:
        results = {
            "query": query,
            "search_type": search_type,
            "documents": [],
            "conversations": []
        }
        
        # Semantic search (FAISS)
        if search_type in ["semantic", "hybrid"]:
            docs, used_docs = await rag_service.retrieve(
                query,
                k=limit * 2,
                top_k=limit,
                use_hybrid=True,
                use_rerank=True
            )
            
            # Filter by doc_type and department if provided
            filtered_docs = []
            for doc, used_doc in zip(docs, used_docs):
                metadata = doc.metadata
                
                # Apply filters
                if doc_type and metadata.get("doc_type") != doc_type:
                    continue
                if department and metadata.get("department") != department:
                    continue
                
                # Get document from database if document_id exists
                if metadata.get("document_id"):
                    doc_result = await session.execute(
                        select(Document).where(Document.id == metadata["document_id"])
                    )
                    db_doc = doc_result.scalars().first()
                    
                    if db_doc:
                        # Check permissions
                        if not user.is_admin and db_doc.uploaded_by != user.id:
                            continue
                        
                        filtered_docs.append({
                            "id": db_doc.id,
                            "title": db_doc.title or db_doc.file_name or "Untitled",
                            "doc_type": db_doc.doc_type,
                            "department": db_doc.department,
                            "snippet": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                            "score": used_doc.get("score", 0),
                            "source": "semantic",
                            "created_at": db_doc.created_at.isoformat()
                        })
            
            results["documents"] = filtered_docs[:limit]
        
        # Keyword search (database)
        if search_type in ["keyword", "hybrid"]:
            # Search in documents
            keyword_query = select(Document).where(
                or_(
                    Document.title.ilike(f"%{query}%"),
                    Document.file_name.ilike(f"%{query}%"),
                    func.jsonb_path_exists(Document.body, f'$.text', f'%{query}%')
                )
            )
            
            if doc_type:
                keyword_query = keyword_query.where(Document.doc_type == doc_type)
            if department:
                keyword_query = keyword_query.where(Document.department == department)
            
            # Permission check
            if not user.is_admin:
                keyword_query = keyword_query.where(
                    or_(
                        Document.uploaded_by == user.id,
                        Document.uploaded_by.is_(None)  # System documents
                    )
                )
            
            keyword_query = keyword_query.order_by(Document.created_at.desc()).limit(limit)
            
            doc_result = await session.execute(keyword_query)
            keyword_docs = doc_result.scalars().all()
            
            # Add keyword results (avoid duplicates)
            existing_ids = {doc["id"] for doc in results["documents"]}
            for doc in keyword_docs:
                if doc.id not in existing_ids:
                    results["documents"].append({
                        "id": doc.id,
                        "title": doc.title or doc.file_name or "Untitled",
                        "doc_type": doc.doc_type,
                        "department": doc.department,
                        "snippet": doc.body.get("text", "")[:200] + "..." if doc.body.get("text") else "",
                        "score": 0.5,  # Lower score for keyword matches
                        "source": "keyword",
                        "created_at": doc.created_at.isoformat()
                    })
        
        # Search conversations (keyword only for now)
        if search_type in ["keyword", "hybrid"]:
            # Get user's conversations
            conv_query = select(Conversation).where(
                Conversation.user_id == user.id,
                or_(
                    Conversation.title.ilike(f"%{query}%"),
                    Conversation.conversation_id.ilike(f"%{query}%")
                )
            ).order_by(Conversation.updated_at.desc()).limit(limit)
            
            conv_result = await session.execute(conv_query)
            conversations = conv_result.scalars().all()
            
            # Get conversation summaries
            for conv in conversations:
                summary = await memory_service.get_summary(conv.conversation_id)
                
                results["conversations"].append({
                    "id": conv.conversation_id,
                    "title": conv.title,
                    "summary": summary,
                    "message_count": conv.message_count,
                    "updated_at": conv.updated_at.isoformat()
                })
        
        # Sort documents by score
        results["documents"].sort(key=lambda x: x["score"], reverse=True)
        results["documents"] = results["documents"][:limit]
        
        return {
            "query": query,
            "total_documents": len(results["documents"]),
            "total_conversations": len(results["conversations"]),
            "results": results
        }
    
    except Exception as e:
        APILogger.log_error(
            "/api/v2/search",
            e,
            str(user.id),
            ErrorCategory.AI_ERROR
        )
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/search/suggestions")
async def search_suggestions(
    query: str = Query(..., min_length=2),
    limit: int = Query(5, ge=1, le=10),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Get search query suggestions (autocomplete)"""
    try:
        # Simple autocomplete from document titles
        suggestions_query = select(Document).where(
            or_(
                Document.title.ilike(f"{query}%"),
                Document.file_name.ilike(f"{query}%")
            )
        ).limit(limit)
        
        if not user.is_admin:
            suggestions_query = suggestions_query.where(
                or_(
                    Document.uploaded_by == user.id,
                    Document.uploaded_by.is_(None)
                )
            )
        
        result = await session.execute(suggestions_query)
        suggestions = []
        
        seen = set()
        for doc in result.scalars().all():
            text = doc.title or doc.file_name or ""
            if text and text not in seen:
                suggestions.append(text)
                seen.add(text)
                if len(suggestions) >= limit:
                    break
        
        return {"suggestions": suggestions}
    
    except Exception as e:
        APILogger.log_error(
            "/api/v2/search/suggestions",
            e,
            str(user.id),
            ErrorCategory.AI_ERROR
        )
        return {"suggestions": []}

