# -*- coding: utf-8 -*-
"""
Gelişmiş NLP Servisi - AI Tabanlı Intent Classification ve Entity Extraction

Bu modül gelişmiş NLP teknikleri kullanarak kullanıcı sorgularını analiz eder.
AI tabanlı intent classification ve entity extraction yapar.

Ne İşe Yarar:
- AI tabanlı intent classification
- Entity extraction (isim, departman, proje vb.)
- Query understanding ve semantic analysis
- Gelişmiş NLP işlemleri

Kullanım:
- analyze_query() - Sorguyu gelişmiş NLP ile analiz et
- classify_intent() - Intent'i AI ile sınıflandır
- extract_entities() - Entity'leri çıkar
"""
import re
import json
from typing import Dict, List, Optional
from pathlib import Path

class AdvancedNLPService:
    """Gelişmiş NLP işlemleri - AI destekli intent ve entity extraction"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent / "data"
        self._entity_cache = None
    
    def load_entity_data(self):
        """Entity'leri veri dosyalarından yükle"""
        if self._entity_cache:
            return self._entity_cache
        
        entities = {
            "departments": [],
            "employees": [],
            "projects": [],
            "locations": []
        }
        
        try:
            # Departments
            dept_path = self.data_dir / "departments.json"
            if dept_path.exists():
                with open(dept_path, "r", encoding="utf-8") as f:
                    depts = json.load(f)
                    if isinstance(depts, list):
                        entities["departments"] = [
                            dept.get("name", "").lower() for dept in depts
                        ] + [
                            dept.get("code", "").lower() for dept in depts if dept.get("code")
                        ]
            
            # Employees
            emp_path = self.data_dir / "employees.json"
            if emp_path.exists():
                with open(emp_path, "r", encoding="utf-8") as f:
                    emps = json.load(f)
                    if isinstance(emps, list):
                        entities["employees"] = [
                            emp.get("name", "").lower() for emp in emps
                        ]
            
            # Projects
            proj_path = self.data_dir / "projects.json"
            if proj_path.exists():
                with open(proj_path, "r", encoding="utf-8") as f:
                    projs = json.load(f)
                    if isinstance(projs, list):
                        entities["projects"] = [
                            proj.get("name", "").lower() for proj in projs
                        ]
            
            # Locations (projects ve departments'den çek)
            all_locations = set()
            if dept_path.exists():
                with open(dept_path, "r", encoding="utf-8") as f:
                    depts = json.load(f)
                    if isinstance(depts, list):
                        for dept in depts:
                            if dept.get("location"):
                                all_locations.add(dept.get("location").lower())
            if proj_path.exists():
                with open(proj_path, "r", encoding="utf-8") as f:
                    projs = json.load(f)
                    if isinstance(projs, list):
                        for proj in projs:
                            if proj.get("location"):
                                all_locations.add(proj.get("location").lower())
            
            entities["locations"] = list(all_locations)
            
        except Exception:
            pass
        
        self._entity_cache = entities
        return entities
    
    def extract_entities_advanced(self, query: str) -> Dict[str, List[str]]:
        """
        Gelişmiş entity extraction - veri dosyalarından entity'leri çıkarır
        
        Args:
            query: Kullanıcı sorgusu
            
        Returns:
            Entity dictionary (names, departments, projects, locations)
        """
        entities = {
            "names": [],
            "departments": [],
            "projects": [],
            "locations": []
        }
        
        query_lower = query.lower()
        entity_data = self.load_entity_data()
        
        # Departments
        for dept in entity_data.get("departments", []):
            if dept and dept in query_lower:
                entities["departments"].append(dept)
        
        # Employees
        for emp in entity_data.get("employees", []):
            if emp and emp in query_lower:
                entities["names"].append(emp)
        
        # Projects
        for proj in entity_data.get("projects", []):
            if proj and proj in query_lower:
                entities["projects"].append(proj)
        
        # Locations
        for loc in entity_data.get("locations", []):
            if loc and loc in query_lower:
                entities["locations"].append(loc)
        
        # Pattern-based extraction (fallback)
        # Büyük harfle başlayan kelimeler (potansiyel isimler)
        words = query.split()
        for word in words:
            if word and word[0].isupper() and len(word) > 2:
                # Yaygın isimler veya veri dosyasında var mı kontrol et
                if word.lower() in entity_data.get("employees", []):
                    if word not in entities["names"]:
                        entities["names"].append(word)
        
        return entities
    
    def classify_intent_advanced(self, query: str, entities: Dict) -> str:
        """
        Gelişmiş intent classification - pattern ve entity bazlı
        
        Args:
            query: Kullanıcı sorgusu
            entities: Çıkarılan entity'ler
            
        Returns:
            Intent string
        """
        query_lower = query.lower()
        
        # Prosedür sorguları
        procedure_keywords = ["prosedür", "kural", "politika", "düzenleme", "yeni prosedür", "prosedürler"]
        if any(kw in query_lower for kw in procedure_keywords):
            return "procedure_query"
        
        # Employee sorguları
        if entities.get("names") or any(kw in query_lower for kw in ["kim", "çalışan", "personel", "görevli", "hangi kişi"]):
            return "employee_query"
        
        # Department sorguları
        if entities.get("departments") or any(kw in query_lower for kw in ["departman", "bölüm", "şube", "birim"]):
            return "department_query"
        
        # Project sorguları
        if entities.get("projects") or any(kw in query_lower for kw in ["proje", "iş", "çalışma", "geliştirme"]):
            return "project_query"
        
        # Budget/Financial sorguları
        if any(kw in query_lower for kw in ["bütçe", "maliyet", "harcama", "fiyat", "ücret", "para"]):
            return "financial_query"
        
        # Location sorguları
        if entities.get("locations") or any(kw in query_lower for kw in ["nerede", "hangi şehir", "hangi lokasyon", "konum"]):
            return "location_query"
        
        # Count/Statistics sorguları
        if any(kw in query_lower for kw in ["kaç", "sayı", "toplam", "adet", "miktar"]):
            return "statistics_query"
        
        # Search/List sorguları
        if any(kw in query_lower for kw in ["listele", "göster", "bul", "ara", "list"]):
            return "search_query"
        
        # General chat
        if any(kw in query_lower for kw in ["merhaba", "selam", "nasılsın", "teşekkür", "sağol", "iyi günler"]):
            return "general_chat"
        
        # Varsayılan
        return "general_query"
    
    def analyze_sentiment(self, query: str) -> Dict:
        """
        Sentiment analysis - kullanıcı sorgusunun duygusal tonunu analiz eder
        
        Args:
            query: Kullanıcı sorgusu
            
        Returns:
            Sentiment analiz sonucu
        """
        query_lower = query.lower()
        
        # Pozitif kelimeler
        positive_words = ["teşekkür", "sağol", "harika", "güzel", "mükemmel", "iyi", "yardımcı", "başarılı"]
        # Negatif kelimeler
        negative_words = ["kötü", "kötüleşti", "hata", "yanlış", "çalışmıyor", "sorun", "problem", "neden", "neden"]
        # Soru kelimeleri
        question_words = ["neden", "nasıl", "nedir", "kim", "ne", "hangi", "nerede", "ne zaman"]
        
        positive_count = sum(1 for word in positive_words if word in query_lower)
        negative_count = sum(1 for word in negative_words if word in query_lower)
        is_question = any(word in query_lower for word in question_words)
        
        # Sentiment score hesapla
        if positive_count > negative_count:
            sentiment = "positive"
            score = 0.6 + (positive_count * 0.1)
        elif negative_count > positive_count:
            sentiment = "negative"
            score = 0.3 - (negative_count * 0.1)
        else:
            sentiment = "neutral"
            score = 0.5
        
        score = max(0.0, min(1.0, score))
        
        return {
            "sentiment": sentiment,
            "score": round(score, 2),
            "is_question": is_question,
            "positive_keywords": positive_count,
            "negative_keywords": negative_count
        }
    
    def analyze_query_advanced(self, query: str) -> Dict:
        """
        Gelişmiş sorgu analizi - intent + entity + confidence + sentiment
        
        Args:
            query: Kullanıcı sorgusu
            
        Returns:
            Detaylı analiz sonucu
        """
        # Entity extraction
        entities = self.extract_entities_advanced(query)
        
        # Intent classification
        intent = self.classify_intent_advanced(query, entities)
        
        # Sentiment analysis
        sentiment = self.analyze_sentiment(query)
        
        # Confidence hesaplama (basit)
        confidence = 0.5  # Base confidence
        
        # Entity varsa confidence artar
        if any(entities.values()):
            confidence += 0.2
        
        # Intent pattern match varsa confidence artar
        if intent != "general_query":
            confidence += 0.2
        
        # Query uzunluğu (daha uzun sorgular genelde daha spesifik)
        if len(query.split()) > 5:
            confidence += 0.1
        
        # Sentiment pozitifse confidence artar
        if sentiment["sentiment"] == "positive":
            confidence += 0.05
        
        confidence = min(confidence, 1.0)
        
        return {
            "intent": intent,
            "entities": entities,
            "confidence": round(confidence, 2),
            "sentiment": sentiment,
            "original_query": query,
            "query_length": len(query),
            "word_count": len(query.split())
        }
    
    def generate_search_query(self, query: str, intent: str, entities: Dict) -> List[str]:
        """
        Intent ve entity'ye göre optimize edilmiş arama sorguları üretir
        
        Args:
            query: Orijinal sorgu
            intent: Tespit edilen intent
            entities: Çıkarılan entity'ler
            
        Returns:
            Optimize edilmiş arama sorguları listesi
        """
        optimized_queries = [query]
        
        # Entity-based query generation
        if entities.get("names"):
            for name in entities["names"]:
                optimized_queries.append(f"{name} çalışan bilgisi projeler")
                optimized_queries.append(f"{name} departman pozisyon")
        
        if entities.get("departments"):
            for dept in entities["departments"]:
                optimized_queries.append(f"{dept} departman çalışanlar bütçe")
                optimized_queries.append(f"{dept} departman projeler")
        
        if entities.get("projects"):
            for proj in entities["projects"]:
                optimized_queries.append(f"{proj} proje durum bütçe yönetici")
        
        if entities.get("locations"):
            for loc in entities["locations"]:
                optimized_queries.append(f"{loc} lokasyon proje çalışan")
        
        # Intent-based query generation
        if intent == "financial_query":
            optimized_queries.append("bütçe maliyet harcama finans")
            optimized_queries.append("departman bütçe 2024")
        
        if intent == "statistics_query":
            optimized_queries.append("çalışan sayısı proje sayısı toplam")
        
        # Maksimum 5 sorgu
        return optimized_queries[:5]

