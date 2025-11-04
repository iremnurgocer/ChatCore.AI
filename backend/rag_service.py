# -*- coding: utf-8 -*-
"""
Gelişmiş RAG (Retrieval-Augmented Generation) Servisi

Bu modül şirket verilerinize dayalı doğru yanıtlar üretmek için gelişmiş
RAG teknolojilerini kullanır. Multi-query, re-ranking, hybrid search ve
query expansion gibi özellikler içerir.

Ne İşe Yarar:
- Vector store'dan ilgili dokümanları bulma
- Multi-query ile birden fazla sorgu varyasyonu oluşturma
- Re-ranking ile en alakalı sonuçları seçme
- Hybrid search (dense + sparse search)
- Query expansion ile sorgu genişletme
- Context formatlama ve AI prompt'a hazırlama

Kullanım:
- get_rag_service() - RAG servis instance'ı al
- retrieve_context() - İlgili context'i getir
- format_context_for_ai() - Context'i AI prompt'una uygun formatla
"""
import json
import re
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import SentenceTransformerEmbeddings

# Global imports kontrolü
LANGCHAIN_AVAILABLE = False
try:
    from langchain_community.vectorstores import FAISS
    from langchain_core.documents import Document
    LANGCHAIN_AVAILABLE = True
except ImportError:
    pass

class AdvancedRAGService:
    """Gelişmiş RAG servisi - multi-query, re-ranking, hybrid search"""
    
    def __init__(self, vector_store=None, embeddings=None):
        self.vector_store = vector_store
        self.embeddings = embeddings
        
    def expand_query(self, query: str, max_expansions: int = 2) -> List[str]:
        """
        Query expansion - sorguyu genişletir ve alternatif sorgular üretir
        
        Args:
            query: Orijinal sorgu
            max_expansions: Maksimum expansion sayısı (performans için)
            
        Returns:
            Genişletilmiş sorgu listesi
        """
        expanded = [query]  # Orijinal sorgu her zaman dahil
        
        # Türkçe soru kelimeleri eşleştirme
        question_expansions = {
            "kim": ["hangi kişi", "hangisi", "kimler", "hangi çalışan"],
            "ne": ["nedir", "neler", "hangi", "hangisi"],
            "nasıl": ["ne şekilde", "hangi yöntemle", "nasıl yapılır"],
            "nerede": ["hangi konumda", "nereye", "hangi şehirde"],
            "hangi": ["hangisi", "nedir", "ne"],
            "kaç": ["ne kadar", "hangi miktar", "toplam"],
        }
        
        query_lower = query.lower()
        for key, alternatives in question_expansions.items():
            if key in query_lower:
                for alt in alternatives:
                    expanded_query = query_lower.replace(key, alt)
                    if expanded_query != query_lower:
                        expanded.append(expanded_query)
        
        # Entity-based expansion (departman, proje, lokasyon)
        # Bu bilgiler verilerden çekilebilir ama şimdilik pattern-based
        entity_keywords = {
            "departman": ["bölüm", "şube", "birim"],
            "proje": ["çalışma", "iş", "geliştirme"],
            "çalışan": ["personel", "görevli", "kişi"],
        }
        
        for key, alternatives in entity_keywords.items():
            if key in query_lower:
                for alt in alternatives:
                    expanded_query = query_lower.replace(key, alt)
                    if expanded_query != query_lower:
                        expanded.append(expanded_query)
        
        # Maksimum sorgu sayısı (performans için azaltıldı)
        return expanded[:max_expansions + 1]  # +1 çünkü orijinal sorgu dahil
    
    def multi_query_retrieval(self, query: str, k: int = 3) -> List[Document]:
        """
        Multi-query retrieval - birden fazla sorgu ile arama yapar (optimize edilmiş)
        
        Args:
            query: Orijinal sorgu
            k: Her sorgu için döndürülecek document sayısı (azaltıldı: 5->3)
            
        Returns:
            Unique ve ranked documents
        """
        if not self.vector_store:
            return []
        
        # Query expansion (maksimum 2 expansion - performans için)
        expanded_queries = self.expand_query(query, max_expansions=2)
        
        # Her sorgu için arama yap
        all_docs = []
        seen_content = set()
        
        for exp_query in expanded_queries:
            try:
                docs = self.vector_store.similarity_search(exp_query, k=k)
                for doc in docs:
                    # Duplicate kontrolü
                    content_hash = hash(doc.page_content)
                    if content_hash not in seen_content:
                        seen_content.add(content_hash)
                        all_docs.append(doc)
            except Exception:
                continue
        
        return all_docs
    
    def re_rank_documents(self, query: str, documents: List[Document], top_k: int = 5) -> List[Document]:
        """
        Document re-ranking - relevance scoring ile sıralama
        
        Args:
            query: Orijinal sorgu
            documents: Sıralanacak documents
            top_k: En üstte döndürülecek document sayısı
            
        Returns:
            Re-ranked documents
        """
        if not documents:
            return []
        
        query_lower = query.lower()
        scored_docs = []
        
        for doc in documents:
            score = 0
            content_lower = doc.page_content.lower()
            
            # Exact match bonus
            if query_lower in content_lower:
                score += 10
            
            # Word overlap
            query_words = set(query_lower.split())
            content_words = set(content_lower.split())
            overlap = len(query_words & content_words)
            score += overlap * 2
            
            # Metadata bonus
            doc_type = doc.metadata.get("type", "")
            type_keywords = {
                "employees": ["kim", "çalışan", "personel", "görevli"],
                "departments": ["departman", "bölüm", "şube"],
                "projects": ["proje", "iş", "çalışma"],
                "procedures": ["prosedür", "kural", "politika"],
            }
            
            for type_name, keywords in type_keywords.items():
                if doc_type == type_name:
                    if any(kw in query_lower for kw in keywords):
                        score += 5
            
            # JSON field matching
            try:
                data = json.loads(doc.page_content)
                # Query'deki kelimeler JSON değerlerinde var mı?
                query_words_str = " ".join(query_words)
                data_str = json.dumps(data, ensure_ascii=False).lower()
                if query_words_str in data_str or any(word in data_str for word in query_words if len(word) > 3):
                    score += 3
            except:
                pass
            
            scored_docs.append((score, doc))
        
        # Score'a göre sırala
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        
        # Top k documents
        return [doc for score, doc in scored_docs[:top_k]]
    
    def hybrid_search(self, query: str, k: int = 3) -> List[Document]:
        """
        Hybrid search - semantic search + keyword matching (optimize edilmiş)
        
        Args:
            query: Arama sorgusu
            k: Döndürülecek document sayısı (azaltıldı: 5->3)
            
        Returns:
            Hybrid search sonuçları
        """
        if not self.vector_store:
            return []
        
        # 1. Semantic search (vector similarity) - daha az document
        semantic_docs = self.multi_query_retrieval(query, k=k)
        
        # 2. Keyword matching
        keyword_docs = []
        query_words = set(query.lower().split())
        
        # Keyword matching (optimize - daha az document kontrol et)
        try:
            # FAISS'ten documents'ları almak için similarity_search_with_score kullan (azaltıldı)
            all_semantic = self.vector_store.similarity_search_with_score(query, k=k*2)  # k*3 -> k*2
            
            # Keyword match score ekle
            for doc, sim_score in all_semantic:
                content_lower = doc.page_content.lower()
                keyword_matches = sum(1 for word in query_words if word in content_lower and len(word) > 2)
                
                # Combined score (semantic + keyword)
                combined_score = float(sim_score) + (keyword_matches * 0.1)
                keyword_docs.append((combined_score, doc))
            
            # Re-rank
            keyword_docs.sort(key=lambda x: x[0])
            keyword_docs = [doc for score, doc in keyword_docs[:k]]
        except:
            keyword_docs = semantic_docs[:k]
        
        # Combine ve deduplicate
        all_results = []
        seen = set()
        
        for doc in semantic_docs:
            content_hash = hash(doc.page_content)
            if content_hash not in seen:
                seen.add(content_hash)
                all_results.append(doc)
        
        for doc in keyword_docs:
            content_hash = hash(doc.page_content)
            if content_hash not in seen:
                seen.add(content_hash)
                all_results.append(doc)
        
        # Final re-ranking
        return self.re_rank_documents(query, all_results, top_k=k)
    
    def format_context_for_ai(self, documents: List[Document], query: str) -> str:
        """
        Documents'ları AI için okunabilir formata çevirir
        
        Args:
            documents: Formatlanacak documents
            query: Orijinal sorgu (formatlama için context)
            
        Returns:
            Formatlanmış context string
        """
        if not documents:
            return ""
        
        context_parts = []
        query_lower = query.lower()
        
        for i, doc in enumerate(documents, 1):
            try:
                data = json.loads(doc.page_content)
                doc_type = doc.metadata.get("type", "data")
                
                # Tipine göre formatla
                if doc_type == "employees":
                    formatted = f"[Çalışan #{i}] İsim: {data.get('name', 'N/A')}"
                    if data.get('department'):
                        formatted += f" | Departman: {data.get('department')}"
                    if data.get('position'):
                        formatted += f" | Pozisyon: {data.get('position')}"
                    if data.get('location'):
                        formatted += f" | Lokasyon: {data.get('location')}"
                    if data.get('projects'):
                        formatted += f" | Projeler: {', '.join(data.get('projects', []))}"
                    context_parts.append(formatted)
                    
                elif doc_type == "departments":
                    formatted = f"[Departman #{i}] İsim: {data.get('name', 'N/A')}"
                    if data.get('director'):
                        formatted += f" | Direktör: {data.get('director')}"
                    if data.get('employee_count'):
                        formatted += f" | Çalışan Sayısı: {data.get('employee_count')}"
                    if data.get('budget_2024'):
                        formatted += f" | Bütçe 2024: {data.get('budget_2024')} TL"
                    if data.get('location'):
                        formatted += f" | Lokasyon: {data.get('location')}"
                    context_parts.append(formatted)
                    
                elif doc_type == "projects":
                    formatted = f"[Proje #{i}] İsim: {data.get('name', 'N/A')}"
                    if data.get('status'):
                        formatted += f" | Durum: {data.get('status')}"
                    if data.get('department'):
                        formatted += f" | Departman: {data.get('department')}"
                    if data.get('project_manager'):
                        formatted += f" | Proje Yöneticisi: {data.get('project_manager')}"
                    if data.get('location'):
                        formatted += f" | Lokasyon: {data.get('location')}"
                    if data.get('budget'):
                        formatted += f" | Bütçe: {data.get('budget')}"
                    context_parts.append(formatted)
                    
                elif doc_type == "procedures":
                    formatted = f"[Prosedür #{i}] Başlık: {data.get('title', 'N/A')}"
                    if data.get('code'):
                        formatted += f" | Kod: {data.get('code')}"
                    if data.get('department'):
                        formatted += f" | Departman: {data.get('department')}"
                    if data.get('published_date'):
                        formatted += f" | Yayın Tarihi: {data.get('published_date')[:10]}"
                    if data.get('priority'):
                        formatted += f" | Öncelik: {data.get('priority')}"
                    if data.get('content'):
                        # Content kısa özet
                        content = data.get('content', '')[:150]
                        formatted += f" | İçerik: {content}..."
                    context_parts.append(formatted)
                    
                else:
                    # Genel format
                    formatted = json.dumps(data, ensure_ascii=False, indent=2)
                    context_parts.append(f"[Veri #{i}]\n{formatted}")
                    
            except Exception:
                # JSON parse edilemezse ham içeriği kullan
                content = doc.page_content[:200]
                context_parts.append(f"[Veri #{i}] {content}...")
        
        return "\n\n".join(context_parts)
    
    def retrieve_context(self, query: str, k: int = 3, use_hybrid: bool = False) -> str:
        """
        Ana retrieval fonksiyonu - optimize edilmiş (hızlı yanıt için)
        
        Args:
            query: Arama sorgusu
            k: Döndürülecek document sayısı (azaltıldı: 5->3)
            use_hybrid: Hybrid search kullan (False = daha hızlı)
            
        Returns:
            Formatlanmış context string
        """
        if not self.vector_store:
            return ""
        
        # Basit semantic search (hybrid çok yavaş)
        if use_hybrid:
            documents = self.hybrid_search(query, k=k)
        else:
            # Direkt similarity search (en hızlı)
            documents = self.vector_store.similarity_search(query, k=k)
            # Re-ranking (opsiyonel - daha yavaş ama daha iyi sonuç)
            # documents = self.re_rank_documents(query, documents, top_k=k)
        
        # Formatla
        return self.format_context_for_ai(documents, query)

# Global RAG service instance
_rag_service = None

def get_rag_service(vector_store=None, embeddings=None):
    """RAG service singleton"""
    global _rag_service
    if _rag_service is None or vector_store is not None:
        _rag_service = AdvancedRAGService(vector_store, embeddings)
    return _rag_service

