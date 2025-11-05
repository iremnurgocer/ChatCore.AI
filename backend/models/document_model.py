# -*- coding: utf-8 -*-
"""
Document Model - SQLModel definition for documents table

Stores company data and uploaded files (PDF, DOCX, XLSX) as JSONB.
"""
from datetime import datetime
from typing import Optional, Literal, TYPE_CHECKING
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime, Index, JSON as SAJSON, Enum as SAEnum, String, Integer
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB


class Document(SQLModel, table=True):
    """Document model for storing company data and uploaded files"""
    __tablename__ = "documents"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    doc_type: Literal["employee", "department", "project", "procedure", "file"] = Field(
        sa_column=Column(SAEnum("employee", "department", "project", "procedure", "file", name="doc_type_enum"))
    )
    body: dict = Field(sa_column=Column(JSONB))
    
    # File-specific fields (for doc_type="file")
    file_name: Optional[str] = Field(default=None, max_length=255)
    file_path: Optional[str] = Field(default=None, max_length=500)
    file_size: Optional[int] = Field(default=None)  # bytes
    file_type: Optional[str] = Field(default=None, max_length=50)  # pdf, docx, xlsx
    mime_type: Optional[str] = Field(default=None, max_length=100)
    uploaded_by: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    department: Optional[str] = Field(default=None, max_length=100, index=True)  # For per-dept indexes
    
    # Metadata
    title: Optional[str] = Field(default=None, max_length=500)
    summary: Optional[str] = Field(default=None)  # LLM-generated summary
    chunk_count: Optional[int] = Field(default=0)  # Number of chunks indexed
    
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_documents_doc_type", "doc_type"),
        Index("idx_documents_created_at", "created_at"),
        Index("idx_documents_body_gin", "body", postgresql_using="gin"),  # GIN index for JSONB queries
        Index("idx_documents_department", "department"),
        Index("idx_documents_uploaded_by", "uploaded_by"),
    )


class DocumentCreate(SQLModel):
    """Document creation model"""
    doc_type: Literal["employee", "department", "project", "procedure", "file"]
    body: dict
    file_name: Optional[str] = None
    department: Optional[str] = None
    title: Optional[str] = None


class DocumentRead(SQLModel):
    """Document read model"""
    id: int
    doc_type: Literal["employee", "department", "project", "procedure", "file"]
    body: dict
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    department: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


