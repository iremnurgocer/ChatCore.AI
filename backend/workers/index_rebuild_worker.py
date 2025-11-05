# -*- coding: utf-8 -*-
"""
Module: Index Rebuild Worker
Description: Celery worker for background FAISS index rebuild operations.
"""
import os
from celery import Celery
from pathlib import Path

# Celery configuration
celery_app = Celery(
    "chatcore",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(name="rebuild_faiss_index")
def rebuild_faiss_index(department: str = None):
    """
    Rebuild FAISS index (can be called asynchronously)
    
    Args:
        department: Optional department name for per-dept index
    
    Returns:
        Success status
    """
    try:
        # Import here to avoid circular imports
        import asyncio
        from services.rag_service import rag_service
        
        # Run async function
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            rag_service.initialize(force_rebuild=True)
        )
        
        return {
            "success": result,
            "department": department,
            "message": "Index rebuilt successfully" if result else "Index rebuild failed"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "department": department
        }


@celery_app.task(name="index_document")
def index_document(document_id: int, department: str = None):
    """
    Index a single document in FAISS
    
    Args:
        document_id: Document ID from database
        department: Optional department name
    
    Returns:
        Success status
    """
    try:
        import asyncio
        from services.rag_service import rag_service
        from services.document_service import document_service
        from langchain_core.documents import Document as LangChainDocument
        
        # Get document from database
        from core.database import get_sync_session
        from models.document_model import Document
        from sqlmodel import select
        
        session = next(get_sync_session())
        result = session.exec(select(Document).where(Document.id == document_id))
        doc = result.first()
        
        if not doc:
            return {"success": False, "error": "Document not found"}
        
        # Get chunks from document body
        chunks_text = doc.body.get("chunks", [])
        
        if not chunks_text:
            return {"success": False, "error": "No chunks found"}
        
        # Create LangChain documents
        chunks = [
            LangChainDocument(page_content=chunk, metadata={"document_id": document_id})
            for chunk in chunks_text
        ]
        
        # Index in FAISS
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            rag_service.add_documents(chunks, document_id=document_id, department=department)
        )
        
        return {
            "success": result,
            "document_id": document_id,
            "chunks": len(chunks)
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "document_id": document_id
        }


if __name__ == "__main__":
    celery_app.start()

