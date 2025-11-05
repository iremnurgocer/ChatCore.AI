# -*- coding: utf-8 -*-
"""
Module: RAG Service
Description: Persistent FAISS index with hybrid retrieval, Self-RAG, and per-department indexes.
"""
import json
import re
from typing import List, Dict, Optional, Tuple, Set
from pathlib import Path
import tiktoken

# LangChain imports
LANGCHAIN_AVAILABLE = False
try:
    from langchain_community.vectorstores import FAISS
    from langchain_core.documents import Document
    from langchain_openai import OpenAIEmbeddings
    from langchain_community.embeddings import SentenceTransformerEmbeddings
    LANGCHAIN_AVAILABLE = True
except ImportError:
    pass

# BM25 imports
try:
    from rank_bm25 import BM25Okapi
    BM25_AVAILABLE = True
except ImportError:
    BM25_AVAILABLE = False

# Cross-encoder re-ranking (optional)
try:
    from sentence_transformers import CrossEncoder
    CROSS_ENCODER_AVAILABLE = True
except ImportError:
    CROSS_ENCODER_AVAILABLE = False

from core.config import get_settings
from core.logger import APILogger

settings = get_settings()

# FAISS storage path
VECTORSTORE_DIR = Path(__file__).parent.parent / "data" / "vectorstore"
VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)
VECTORSTORE_PATH = VECTORSTORE_DIR / "faiss_index"


class RAGService:
    """Advanced RAG service with persistent FAISS and hybrid retrieval"""
    
    def __init__(self):
        self.vector_store: Optional[FAISS] = None
        self.embeddings = None
        self.bm25_index: Optional[BM25Okapi] = None
        self.documents: List[Document] = []
        self.cross_encoder = None
        self._initialized = False
        
        # Per-department indexes
        self.department_indexes: Dict[str, FAISS] = {}
        self.department_documents: Dict[str, List[Document]] = {}
    
    async def initialize(self, force_rebuild: bool = False) -> bool:
        """Initialize RAG service - load or build FAISS index"""
        if self._initialized and not force_rebuild:
            return True
        
        try:
            # Try to load existing FAISS index
            if not force_rebuild and VECTORSTORE_PATH.exists():
                await self._load_faiss_index()
                self._initialized = True
                APILogger.log_request(
                    "/rag/init",
                    "GET",
                    None,
                    None,
                    200,
                    log_message="FAISS index loaded from disk"
                )
                return True
            
            # Build new index
            await self._build_faiss_index()
            self._initialized = True
            APILogger.log_request(
                "/rag/init",
                "GET",
                None,
                None,
                200,
                log_message="FAISS index built and saved"
            )
            return True
        
        except Exception as e:
            APILogger.log_error(
                "/rag/init",
                e,
                None,
                ErrorCategory.AI_ERROR
            )
            return False
    
    async def _load_faiss_index(self):
        """Load FAISS index from disk"""
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("LangChain not available")
        
        # Load embeddings
        if settings.OPENAI_API_KEY:
            self.embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
        else:
            self.embeddings = SentenceTransformerEmbeddings(
                model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            )
        
        # Load FAISS
        self.vector_store = FAISS.load_local(
            str(VECTORSTORE_PATH),
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        
        # Load documents metadata
        metadata_path = VECTORSTORE_PATH.parent / "documents.json"
        if metadata_path.exists():
            with open(metadata_path, "r", encoding="utf-8") as f:
                docs_data = json.load(f)
                self.documents = [
                    Document(page_content=d["content"], metadata=d["metadata"])
                    for d in docs_data
                ]
        
        # Build BM25 index
        if BM25_AVAILABLE and self.documents:
            corpus = [doc.page_content.lower().split() for doc in self.documents]
            self.bm25_index = BM25Okapi(corpus)
        
        # Initialize cross-encoder (optional)
        if CROSS_ENCODER_AVAILABLE:
            try:
                self.cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
            except Exception:
                pass
    
    async def _build_faiss_index(self):
        """Build FAISS index from JSON data files"""
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("LangChain not available")
        
        # Load embeddings
        if settings.OPENAI_API_KEY:
            self.embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
        else:
            self.embeddings = SentenceTransformerEmbeddings(
                model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            )
        
        # Load documents from JSON files
        data_dir = Path(__file__).parent.parent / "data"
        self.documents = []
        
        for file_name in ["employees.json", "departments.json", "projects.json", "procedures.json"]:
            file_path = data_dir / file_name
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                doc_type = file_name.replace(".json", "")
                
                if isinstance(data, list):
                    for item in data:
                        text = self._format_document_text(item, doc_type)
                        metadata = {
                            "doc_type": doc_type,
                            "doc_id": item.get("id") or item.get("name") or str(hash(str(item))),
                            "source": file_name
                        }
                        # Add type-specific metadata
                        if doc_type == "employees":
                            metadata["name"] = item.get("name", "")
                            metadata["department"] = item.get("department", "")
                        elif doc_type == "projects":
                            metadata["project_name"] = item.get("name", "")
                        
                        self.documents.append(Document(page_content=text, metadata=metadata))
        
        if not self.documents:
            raise ValueError("No documents found to index")
        
        # Build FAISS index
        self.vector_store = FAISS.from_documents(self.documents, self.embeddings)
        
        # Save FAISS index
        self.vector_store.save_local(str(VECTORSTORE_PATH))
        
        # Save documents metadata
        docs_data = [
            {
                "content": doc.page_content,
                "metadata": doc.metadata
            }
            for doc in self.documents
        ]
        metadata_path = VECTORSTORE_PATH.parent / "documents.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(docs_data, f, ensure_ascii=False, indent=2)
        
        # Build BM25 index
        if BM25_AVAILABLE:
            corpus = [doc.page_content.lower().split() for doc in self.documents]
            self.bm25_index = BM25Okapi(corpus)
        
        # Initialize cross-encoder (optional)
        if CROSS_ENCODER_AVAILABLE:
            try:
                self.cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
            except Exception:
                pass
    
    def _format_document_text(self, item: Dict, doc_type: str) -> str:
        """Format document item as text"""
        if doc_type == "employees":
            return f"Çalışan: {item.get('name', '')} - Departman: {item.get('department', '')} - Pozisyon: {item.get('position', '')} - Email: {item.get('email', '')}"
        elif doc_type == "departments":
            return f"Departman: {item.get('name', '')} - Açıklama: {item.get('description', '')}"
        elif doc_type == "projects":
            return f"Proje: {item.get('name', '')} - Durum: {item.get('status', '')} - Açıklama: {item.get('description', '')}"
        elif doc_type == "procedures":
            return f"Prosedür: {item.get('title', '')} - Açıklama: {item.get('description', '')} - Adımlar: {item.get('steps', '')}"
        else:
            return json.dumps(item, ensure_ascii=False)
    
    async def retrieve(
        self,
        query: str,
        k: int = 50,
        top_k: int = 5,
        use_hybrid: bool = True,
        use_rerank: bool = True
    ) -> Tuple[List[Document], List[Dict]]:
        """
        Retrieve relevant documents with hybrid search and re-ranking
        
        Returns:
            (documents, used_documents_metadata)
            used_documents_metadata: List of dicts with doc_id, title, chunk_id, score
        """
        if not self._initialized:
            await self.initialize()
        
        if not self.vector_store:
            return [], []
        
        # Hybrid retrieval: FAISS dense + BM25 sparse
        if use_hybrid and BM25_AVAILABLE and self.bm25_index:
            dense_docs, sparse_docs = await self._hybrid_retrieval(query, k)
            # Merge and deduplicate
            all_docs = self._merge_documents(dense_docs, sparse_docs)
        else:
            # Dense only
            all_docs = self.vector_store.similarity_search(query, k=k)
        
        # Re-ranking
        if use_rerank and len(all_docs) > top_k:
            if CROSS_ENCODER_AVAILABLE and self.cross_encoder:
                all_docs = self._rerank_with_cross_encoder(query, all_docs, top_k)
            else:
                all_docs = self._rerank_simple(query, all_docs, top_k)
        else:
            all_docs = all_docs[:top_k]
        
        # Build used_documents metadata
        used_documents = []
        for idx, doc in enumerate(all_docs):
            metadata = doc.metadata
            used_documents.append({
                "doc_id": metadata.get("doc_id", f"doc_{idx}"),
                "title": metadata.get("name") or metadata.get("project_name") or metadata.get("title", f"Document {idx+1}"),
                "chunk_id": idx,
                "score": metadata.get("score", 1.0 - (idx * 0.1)),
                "doc_type": metadata.get("doc_type", "unknown"),
                "source": metadata.get("source", "unknown")
            })
        
        return all_docs, used_documents
    
    async def _hybrid_retrieval(self, query: str, k: int) -> Tuple[List[Document], List[Document]]:
        """Hybrid retrieval: FAISS dense + BM25 sparse"""
        # Dense retrieval (FAISS)
        dense_docs = self.vector_store.similarity_search(query, k=k)
        
        # Sparse retrieval (BM25)
        query_tokens = query.lower().split()
        if self.bm25_index:
            bm25_scores = self.bm25_index.get_scores(query_tokens)
            # Get top k BM25 results
            top_indices = sorted(
                range(len(bm25_scores)),
                key=lambda i: bm25_scores[i],
                reverse=True
            )[:k]
            sparse_docs = [self.documents[i] for i in top_indices if i < len(self.documents)]
        else:
            sparse_docs = []
        
        return dense_docs, sparse_docs
    
    def _merge_documents(self, dense_docs: List[Document], sparse_docs: List[Document]) -> List[Document]:
        """Merge and deduplicate documents from dense and sparse retrieval"""
        seen_content = set()
        merged = []
        
        # Weighted merge: dense (0.7) + sparse (0.3)
        for doc in dense_docs:
            content_hash = hash(doc.page_content)
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                doc.metadata["score"] = 0.7  # Dense score weight
                merged.append(doc)
        
        for doc in sparse_docs:
            content_hash = hash(doc.page_content)
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                doc.metadata["score"] = 0.3  # Sparse score weight
                merged.append(doc)
            else:
                # Update score if already exists
                for existing in merged:
                    if hash(existing.page_content) == content_hash:
                        existing.metadata["score"] = max(existing.metadata.get("score", 0), 0.3)
        
        return merged
    
    def _rerank_with_cross_encoder(self, query: str, documents: List[Document], top_k: int) -> List[Document]:
        """Re-rank using cross-encoder"""
        if not self.cross_encoder:
            return self._rerank_simple(query, documents, top_k)
        
        # Prepare pairs for cross-encoder
        pairs = [[query, doc.page_content] for doc in documents]
        
        # Get scores
        scores = self.cross_encoder.predict(pairs)
        
        # Sort by score
        scored_docs = list(zip(documents, scores))
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        # Update document scores
        reranked = []
        for doc, score in scored_docs[:top_k]:
            doc.metadata["score"] = float(score)
            reranked.append(doc)
        
        return reranked
    
    def _rerank_simple(self, query: str, documents: List[Document], top_k: int) -> List[Document]:
        """Simple re-ranking based on keyword matching"""
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        scored_docs = []
        for doc in documents:
            content_lower = doc.page_content.lower()
            content_words = set(content_lower.split())
            
            # Calculate overlap score
            overlap = len(query_words & content_words)
            score = overlap / len(query_words) if query_words else 0
            
            # Boost score if query appears in content
            if query_lower in content_lower:
                score += 0.5
            
            scored_docs.append((doc, score))
        
        # Sort by score
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        # Update document scores
        reranked = []
        for doc, score in scored_docs[:top_k]:
            doc.metadata["score"] = score
            reranked.append(doc)
        
        return reranked
    
    def format_context(
        self,
        documents: List[Document],
        max_tokens: int = 2000,
        model: str = "gpt-3.5-turbo"
    ) -> str:
        """Format documents as context with token limit"""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        
        context_parts = []
        current_tokens = 0
        
        for doc in documents:
            doc_text = f"[{doc.metadata.get('doc_type', 'document')}] {doc.page_content}"
            doc_tokens = len(encoding.encode(doc_text))
            
            if current_tokens + doc_tokens > max_tokens:
                break
            
            context_parts.append(doc_text)
            current_tokens += doc_tokens
        
        return "\n\n".join(context_parts)
    
    async def add_documents(
        self,
        documents: List[Document],
        document_id: Optional[int] = None,
        department: Optional[str] = None
    ) -> bool:
        """
        Add documents to FAISS index dynamically
        
        Args:
            documents: List of LangChain Document objects
            document_id: Optional document ID from database
            department: Optional department name for per-dept index
        """
        if not self._initialized:
            await self.initialize()
        
        if not self.vector_store or not self.embeddings:
            return False
        
        try:
            # Add metadata to documents
            for doc in documents:
                if document_id:
                    doc.metadata["document_id"] = document_id
                if department:
                    doc.metadata["department"] = department
                doc.metadata["doc_type"] = "file"
            
            # Add to main index
            self.vector_store.add_documents(documents)
            self.documents.extend(documents)
            
            # Update BM25 index
            if BM25_AVAILABLE:
                new_corpus = [doc.page_content.lower().split() for doc in documents]
                if self.bm25_index:
                    # Rebuild BM25 index with new documents
                    corpus = [doc.page_content.lower().split() for doc in self.documents]
                    self.bm25_index = BM25Okapi(corpus)
                else:
                    self.bm25_index = BM25Okapi(new_corpus)
            
            # Add to department-specific index if provided
            if department:
                if department not in self.department_indexes:
                    # Create new department index
                    dept_index = FAISS.from_documents(documents, self.embeddings)
                    self.department_indexes[department] = dept_index
                    self.department_documents[department] = documents.copy()
                else:
                    # Add to existing department index
                    self.department_indexes[department].add_documents(documents)
                    self.department_documents[department].extend(documents)
            
            # Save updated index
            self.vector_store.save_local(str(VECTORSTORE_PATH))
            
            return True
        
        except Exception as e:
            APILogger.log_error(
                "/rag/add_documents",
                e,
                None,
                ErrorCategory.AI_ERROR,
                document_id=document_id,
                department=department
            )
            return False
    
    async def remove_document(self, document_id: int) -> bool:
        """
        Remove document from FAISS index
        
        Note: FAISS doesn't support deletion directly, so we rebuild the index
        """
        if not self._initialized:
            return False
        
        try:
            # Filter out documents with matching document_id
            original_count = len(self.documents)
            self.documents = [
                doc for doc in self.documents
                if doc.metadata.get("document_id") != document_id
            ]
            
            if len(self.documents) == original_count:
                # No documents removed
                return False
            
            # Rebuild FAISS index
            if self.documents:
                self.vector_store = FAISS.from_documents(self.documents, self.embeddings)
            else:
                # Empty index
                self.vector_store = None
            
            # Rebuild BM25 index
            if BM25_AVAILABLE and self.documents:
                corpus = [doc.page_content.lower().split() for doc in self.documents]
                self.bm25_index = BM25Okapi(corpus)
            else:
                self.bm25_index = None
            
            # Save updated index
            if self.vector_store:
                self.vector_store.save_local(str(VECTORSTORE_PATH))
            
            return True
        
        except Exception as e:
            APILogger.log_error(
                "/rag/remove_document",
                e,
                None,
                ErrorCategory.AI_ERROR,
                document_id=document_id
            )
            return False
    
    async def retrieve_with_self_rag(
        self,
        query: str,
        k: int = 50,
        top_k: int = 5,
        confidence_threshold: float = 0.5,
        department: Optional[str] = None
    ) -> Tuple[List[Document], List[Dict], bool]:
        """
        Self-RAG: If no confident documents found, expand query and retry
        
        Returns:
            (documents, used_documents_metadata, expanded)
        """
        # Initial retrieval
        docs, used_docs = await self.retrieve(
            query,
            k=k,
            top_k=top_k,
            use_hybrid=True,
            use_rerank=True
        )
        
        # Check confidence (based on top score)
        if used_docs and used_docs[0].get("score", 0) >= confidence_threshold:
            return docs, used_docs, False
        
        # Low confidence - expand query
        expanded_query = self._expand_query_for_retry(query)
        
        # Retry with expanded query
        expanded_docs, expanded_used_docs = await self.retrieve(
            expanded_query,
            k=k * 2,  # Get more candidates
            top_k=top_k,
            use_hybrid=True,
            use_rerank=True
        )
        
        # Use expanded results if better
        if expanded_used_docs and expanded_used_docs[0].get("score", 0) > used_docs[0].get("score", 0):
            return expanded_docs, expanded_used_docs, True
        
        return docs, used_docs, False
    
    def _expand_query_for_retry(self, query: str) -> str:
        """Expand query for Self-RAG retry"""
        # Add synonyms and related terms
        expansions = [
            query,
            f"{query} detaylı bilgi",
            f"{query} açıklama",
            f"{query} örnek",
            f"{query} nasıl"
        ]
        
        # Combine expansions
        return " ".join(expansions[:3])  # Use first 3 expansions
    
    async def retrieve_by_department(
        self,
        query: str,
        department: str,
        k: int = 20,
        top_k: int = 5
    ) -> Tuple[List[Document], List[Dict]]:
        """
        Retrieve documents from department-specific index
        
        Returns:
            (documents, used_documents_metadata)
        """
        if department not in self.department_indexes:
            # Fallback to main index
            return await self.retrieve(query, k=k, top_k=top_k)
        
        dept_index = self.department_indexes[department]
        dept_docs = self.department_documents.get(department, [])
        
        # Retrieve from department index
        docs = dept_index.similarity_search(query, k=k)
        
        # Re-rank
        if len(docs) > top_k:
            docs = self._rerank_simple(query, docs, top_k)
        else:
            docs = docs[:top_k]
        
        # Build used_documents metadata
        used_documents = []
        for idx, doc in enumerate(docs):
            metadata = doc.metadata
            used_documents.append({
                "doc_id": metadata.get("document_id", f"doc_{idx}"),
                "title": metadata.get("title", f"Document {idx+1}"),
                "chunk_id": idx,
                "score": metadata.get("score", 1.0 - (idx * 0.1)),
                "doc_type": metadata.get("doc_type", "file"),
                "department": department,
                "source": "department_index"
            })
        
        return docs, used_documents


# Global instance
rag_service = RAGService()

