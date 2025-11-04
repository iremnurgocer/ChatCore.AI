# -*- coding: utf-8 -*-
"""
Context Compression Modülü

Bu modül uzun context'leri optimize eder ve AI'nın token limitini
aşmadan maksimum bilgiyi göndermek için sıkıştırır.

Ne İşe Yarar:
- Uzun dokümanları özetleme ve sıkıştırma
- Token limit optimizasyonu
- Önemli bilgileri koruyarak gereksiz detayları çıkarma
- RAG context'lerini optimize etme

Kullanım:
- compress_context() - Context'i sıkıştır
- summarize_documents() - Dokümanları özetle
"""
from typing import List, Dict
from langchain_core.documents import Document

class ContextCompressor:
    """Context sıkıştırma ve optimizasyon"""
    
    MAX_CONTEXT_LENGTH = 3000  # Maksimum karakter sayısı
    TARGET_CONTEXT_LENGTH = 2000  # Hedef karakter sayısı
    
    @staticmethod
    def compress_context(documents: List[Document], query: str, max_length: int = None) -> str:
        """
        Context'i sıkıştır - en önemli bilgileri koru
        
        Args:
            documents: Document listesi
            query: Kullanıcı sorgusu
            max_length: Maksimum karakter sayısı
            
        Returns:
            Sıkıştırılmış context
        """
        if max_length is None:
            max_length = ContextCompressor.MAX_CONTEXT_LENGTH
        
        if not documents:
            return ""
        
        # Her document için relevance score hesapla
        scored_docs = []
        query_words = set(query.lower().split())
        
        for doc in documents:
            score = 0
            content_lower = doc.page_content.lower()
            
            # Exact match bonus
            if query.lower() in content_lower:
                score += 20
            
            # Word overlap
            content_words = set(content_lower.split())
            overlap = len(query_words & content_words)
            score += overlap * 5
            
            # Metadata bonus
            doc_type = doc.metadata.get("type", "")
            if doc_type in ["employees", "projects", "departments", "procedures"]:
                score += 10
            
            scored_docs.append((score, doc))
        
        # Score'a göre sırala
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        
        # En önemli document'lerden başlayarak context oluştur
        compressed_parts = []
        total_length = 0
        
        for score, doc in scored_docs:
            if total_length >= max_length:
                break
            
            # Document'i özetle
            content = doc.page_content
            remaining_length = max_length - total_length
            
            # İçeriği kısalt
            if len(content) > remaining_length:
                # İlk 70% ve son 30%'u al (önemli bilgiler genelde başta ve sonda)
                first_part = content[:int(remaining_length * 0.7)]
                last_part = content[-int(remaining_length * 0.3):] if remaining_length > 100 else ""
                content = first_part + ("..." if len(content) > remaining_length else "") + last_part
            
            compressed_parts.append(content[:remaining_length])
            total_length += len(content)
        
        return "\n\n".join(compressed_parts)
    
    @staticmethod
    def smart_chunk(documents: List[Document], target_chunks: int = 5) -> List[Document]:
        """
        Akıllı chunking - document'leri daha küçük parçalara böl
        
        Args:
            documents: Document listesi
            target_chunks: Hedef chunk sayısı
            
        Returns:
            Chunked documents
        """
        if not documents:
            return []
        
        if len(documents) <= target_chunks:
            return documents
        
        # En önemli document'leri koru, diğerlerini birleştir
        important_docs = documents[:target_chunks // 2]
        other_docs = documents[target_chunks // 2:]
        
        # Diğer document'leri birleştir
        if other_docs:
            combined_content = "\n\n".join([doc.page_content[:500] for doc in other_docs])
            combined_metadata = {"type": "combined", "source": "multiple"}
            combined_doc = Document(page_content=combined_content, metadata=combined_metadata)
            important_docs.append(combined_doc)
        
        return important_docs[:target_chunks]

