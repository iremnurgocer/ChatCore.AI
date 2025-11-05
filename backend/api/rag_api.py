# -*- coding: utf-8 -*-
"""
Module: RAG API
Description: RAG search endpoints for debugging retrieval and testing.
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session
from core.logger import APILogger, ErrorCategory
from api.auth_api import get_current_user
from models.user_model import User
from services.rag_service import rag_service

router = APIRouter(prefix="/api", tags=["rag"])


@router.get("/rag/search")
async def rag_search(
    query: str,
    k: int = 50,
    top_k: int = 5,
    use_hybrid: bool = True,
    use_rerank: bool = True,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    RAG search endpoint for debugging retrieval
    
    Returns:
        {
            "query": "...",
            "documents": [
                {
                    "doc_id": "...",
                    "title": "...",
                    "content": "...",
                    "score": 0.95,
                    "doc_type": "...",
                    "source": "..."
                }
            ],
            "used_documents": [...]
        }
    """
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter required")
    
    try:
        # Retrieve documents
        documents, used_documents = await rag_service.retrieve(
            query,
            k=k,
            top_k=top_k,
            use_hybrid=use_hybrid,
            use_rerank=use_rerank
        )
        
        # Format response
        result_docs = []
        for doc in documents:
            result_docs.append({
                "doc_id": doc.metadata.get("doc_id", "unknown"),
                "title": doc.metadata.get("name") or doc.metadata.get("project_name") or doc.metadata.get("title", "Untitled"),
                "content": doc.page_content[:500],  # Truncate for response
                "score": getattr(doc, "score", 0.0),
                "doc_type": doc.metadata.get("doc_type", "unknown"),
                "source": doc.metadata.get("source", "unknown")
            })
        
        return {
            "query": query,
            "documents": result_docs,
            "used_documents": used_documents,
            "total_found": len(documents)
        }
    
    except Exception as e:
        APILogger.log_error(
            "/api/rag/search",
            e,
            str(user.id),
            ErrorCategory.AI_ERROR
        )
        raise HTTPException(status_code=500, detail=f"RAG search error: {str(e)}")

