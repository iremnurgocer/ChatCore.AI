# -*- coding: utf-8 -*-
"""
Intent ve Entity Çıkarım Modülü

Bu modül kullanıcı sorgularını analiz eder ve anlam çıkarır.
Intent (niyet) ve entity (varlık) çıkarımı yaparak daha doğru
yanıtlar üretilmesini sağlar.

Ne İşe Yarar:
- Kullanıcı sorgularını analiz etme
- Intent (niyet) çıkarımı
- Entity (varlık) çıkarımı
- Gelişmiş NLP servisi ile entegrasyon

Kullanım:
- IntentClassifier.analyze_query() - Sorguyu analiz et
- extract_intent() - Intent çıkar
- extract_entities() - Entity'leri çıkar
"""
import re
from typing import Dict, List, Optional, Tuple

class IntentClassifier:
    """Sorgu intent'ini sınıflandırır (Gelişmiş NLP servisi ile entegre)"""
    
    INTENT_PATTERNS = {
        "employee_query": [
            r"kim.*çalışıyor",
            r"kim.*var",
            r"kimi.*bul",
            r"hangi.*çalışan",
            r".*personel",
            r".*görevli"
        ],
        "department_query": [
            r"hangi.*departman",
            r".*departman.*kim",
            r"departman.*liste",
            r"bölüm.*hakkında"
        ],
        "project_query": [
            r"hangi.*proje",
            r"proje.*durum",
            r"proje.*hakkında",
            r".*proje.*bilgi"
        ],
        "general_chat": [
            r"merhaba",
            r"selam",
            r"nasılsın",
            r"teşekkür",
            r"sağol"
        ],
        "search": [
            r"ara",
            r"bul",
            r"listele",
            r"göster"
        ]
    }
    
    @staticmethod
    def classify_intent(query: str) -> str:
        """Sorgu intent'ini belirler"""
        query_lower = query.lower()
        
        for intent, patterns in IntentClassifier.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return intent

        return "general_query"  # Varsayılan

    @staticmethod
    def extract_entities(query: str) -> Dict[str, List[str]]:
        """Sorgudan entity'leri çıkarır"""
        entities = {
            "names": [],
            "departments": [],
            "projects": [],
            "locations": []
        }
        
        # Departman isimleri
        departments = ["enerji", "turizm", "inşaat", "sanayi", "altyapı"]
        query_lower = query.lower()
        for dept in departments:
            if dept in query_lower:
                entities["departments"].append(dept)
        
        # Konum isimleri
        locations = ["istanbul", "ankara", "antalya", "bursa", "bodrum", "çanakkale", "izmir"]
        for loc in locations:
            if loc in query_lower:
                entities["locations"].append(loc)
        
        # Proje anahtar kelimeleri
        project_keywords = ["proje", "santral", "çiftlik", "resort", "köprü", "tünel"]
        for keyword in project_keywords:
            if keyword in query_lower:
                entities["projects"].append(keyword)

        # İsim çıkarımı (basit pattern)
        # Büyük harfle başlayan kelimeler (isim formatı)
        words = query.split()
        for word in words:
            if word and word[0].isupper() and len(word) > 2:
                # Yaygın isimler
                common_names = ["ahmet", "mehmet", "ayşe", "zeynep", "can", "burak", "elif", "selin"]
                if word.lower() not in ["ic", "holding", "a.ş"] and word.lower() in common_names:
                    entities["names"].append(word)
        
        return entities
    
    @staticmethod
    def analyze_query(query: str, use_advanced: bool = True) -> Dict:
        """
        Tam sorgu analizi
        
        Args:
            query: Kullanıcı sorgusu
            use_advanced: Gelişmiş NLP servisi kullan (True) veya basit (False)
        
        Returns:
            Analiz sonucu
        """
        # Gelişmiş NLP servisi varsa kullan
        if use_advanced:
            try:
                from nlp_service_advanced import AdvancedNLPService
                nlp_service = AdvancedNLPService()
                return nlp_service.analyze_query_advanced(query)
            except ImportError:
                # Fallback to basic
                pass
            except Exception:
                # Fallback to basic
                pass
        
        # Basit analiz (fallback)
        intent = IntentClassifier.classify_intent(query)
        entities = IntentClassifier.extract_entities(query)
        
        return {
            "intent": intent,
            "entities": entities,
            "original_query": query,
            "confidence": 0.5
        }
