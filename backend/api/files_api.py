# -*- coding: utf-8 -*-
"""
Module: Files API
Description: Async endpoints for document upload, parsing, and FAISS indexing.
"""
import os
from pathlib import Path
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from core.database import get_async_session
from core.logger import APILogger, ErrorCategory
from core.security import default_rate_limiter, SecurityValidator
from api.auth_api import get_current_user
from models.user_model import User
from models.document_model import Document, DocumentRead
from services.document_service import document_service
from services.rag_service import rag_service

router = APIRouter(prefix="/api/v2", tags=["files"])


@router.post("/files/upload")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    department: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Upload and index a document (PDF, DOCX, XLSX, TXT)
    
    Request:
        - file: File to upload
        - department: Optional department name (for per-dept indexes)
        - title: Optional document title
    
    Returns:
        {
            "document_id": 123,
            "file_name": "...",
            "file_size": 45678,
            "chunks_indexed": 10,
            "status": "indexed"
        }
    """
    # Rate limiting
    ip_address = request.client.host if request.client else "unknown"
    identifier = f"{ip_address}:{user.id}"
    is_allowed, remaining = await default_rate_limiter.is_allowed(identifier, "/api/v2/files/upload")
    
    if not is_allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={"X-RateLimit-Remaining": "0"}
        )
    
    try:
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Validate file
        is_valid, error_msg = document_service.validate_file(file.filename, file_size)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Determine file type
        ext = Path(file.filename).suffix.lower()
        file_type_map = {
            ".pdf": "pdf",
            ".docx": "docx",
            ".xlsx": "xlsx",
            ".txt": "txt"
        }
        file_type = file_type_map.get(ext, "unknown")
        
        if file_type == "unknown":
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Save file
        file_path = document_service.save_uploaded_file(
            file_content,
            file.filename,
            user.id
        )
        
        # Parse file
        text_content, parse_metadata = await document_service.parse_file(file_path, file_type)
        
        if not text_content.strip():
            raise HTTPException(status_code=400, detail="File appears to be empty or unreadable")
        
        # Chunk text
        chunks = document_service.chunk_text(text_content)
        chunk_count = len(chunks)
        
        # Create document record
        doc_body = {
            "text": text_content,
            "chunks": [chunk.page_content for chunk in chunks],
            "parse_metadata": parse_metadata,
            "file_hash": document_service.get_file_hash(file_path)
        }
        
        doc_title = title or file.filename.rsplit(".", 1)[0]
        
        document = Document(
            doc_type="file",
            body=doc_body,
            file_name=file.filename,
            file_path=str(file_path),
            file_size=file_size,
            file_type=file_type,
            mime_type=file.content_type,
            uploaded_by=user.id,
            department=department,
            title=doc_title,
            chunk_count=chunk_count
        )
        
        session.add(document)
        await session.flush()
        
        # Index chunks in FAISS (async, non-blocking)
        try:
            await rag_service.add_documents(chunks, document_id=document.id, department=department)
        except Exception as e:
            APILogger.log_error(
                "/api/v2/files/upload",
                e,
                str(user.id),
                ErrorCategory.AI_ERROR,
                document_id=document.id
            )
            # Don't fail upload if indexing fails - can retry later
        
        await session.commit()
        await session.refresh(document)
        
        APILogger.log_request(
            "/api/v2/files/upload",
            "POST",
            str(user.id),
            None,
            200,
            file_name=file.filename,
            file_size=file_size,
            chunks=chunk_count
        )
        
        return {
            "document_id": document.id,
            "file_name": file.filename,
            "file_size": file_size,
            "chunks_indexed": chunk_count,
            "status": "indexed",
            "department": department
        }
    
    except HTTPException:
        raise
    except Exception as e:
        APILogger.log_error(
            "/api/v2/files/upload",
            e,
            str(user.id),
            ErrorCategory.AI_ERROR
        )
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/files", response_model=List[DocumentRead])
async def list_files(
    department: Optional[str] = None,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """List uploaded files (filtered by department if provided)"""
    query = select(Document).where(Document.doc_type == "file")
    
    # Filter by department if provided
    if department:
        query = query.where(Document.department == department)
    
    # Filter by user (non-admin users only see their own files)
    if not user.is_admin:
        query = query.where(Document.uploaded_by == user.id)
    
    query = query.order_by(Document.created_at.desc())
    
    result = await session.execute(query)
    documents = result.scalars().all()
    
    return documents


@router.get("/files/{document_id}", response_model=DocumentRead)
async def get_file(
    document_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Get file metadata"""
    result = await session.execute(
        select(Document).where(
            Document.id == document_id,
            Document.doc_type == "file"
        )
    )
    document = result.scalars().first()
    
    if not document:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Check permissions
    if not user.is_admin and document.uploaded_by != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return document


@router.delete("/files/{document_id}")
async def delete_file(
    document_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Delete uploaded file"""
    result = await session.execute(
        select(Document).where(
            Document.id == document_id,
            Document.doc_type == "file"
        )
    )
    document = result.scalars().first()
    
    if not document:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Check permissions
    if not user.is_admin and document.uploaded_by != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Delete file from disk
    if document.file_path:
        try:
            file_path = Path(document.file_path)
            if file_path.exists():
                file_path.unlink()
        except Exception as e:
            APILogger.log_error(
                "/api/v2/files/delete",
                e,
                str(user.id),
                ErrorCategory.AI_ERROR,
                document_id=document_id
            )
    
    # Remove from FAISS index (async)
    try:
        await rag_service.remove_document(document_id)
    except Exception as e:
        APILogger.log_error(
            "/api/v2/files/delete",
            e,
            str(user.id),
            ErrorCategory.AI_ERROR,
            document_id=document_id
        )
    
    # Delete from database
    await session.delete(document)
    await session.commit()
    
    return {"success": True, "message": "File deleted"}


@router.post("/files/{document_id}/reindex")
async def reindex_file(
    document_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Re-index a document in FAISS"""
    result = await session.execute(
        select(Document).where(
            Document.id == document_id,
            Document.doc_type == "file"
        )
    )
    document = result.scalars().first()
    
    if not document:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Check permissions
    if not user.is_admin and document.uploaded_by != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Get chunks from document body
        chunks_text = document.body.get("chunks", [])
        
        if not chunks_text:
            raise HTTPException(status_code=400, detail="No chunks found in document")
        
        # Create LangChain documents
        from langchain_core.documents import Document as LangChainDocument
        chunks = [
            LangChainDocument(page_content=chunk, metadata={"document_id": document_id})
            for chunk in chunks_text
        ]
        
        # Re-index
        await rag_service.add_documents(
            chunks,
            document_id=document_id,
            department=document.department
        )
        
        return {"success": True, "message": "Document re-indexed", "chunks": len(chunks)}
    
    except Exception as e:
        APILogger.log_error(
            "/api/v2/files/reindex",
            e,
            str(user.id),
            ErrorCategory.AI_ERROR,
            document_id=document_id
        )
        raise HTTPException(status_code=500, detail=f"Re-indexing failed: {str(e)}")

