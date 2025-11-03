"""
Prompt Optimizer - Few-shot examples ve gelişmiş prompt engineering
"""
from typing import List, Dict, Optional

class PromptOptimizer:
    """Prompt optimizasyonu ve few-shot examples"""
    
    # Few-shot examples - şirket verilerine göre örnekler
    FEW_SHOT_EXAMPLES = [
        {
            "input": "John Doe hangi projelerde çalışıyor?",
            "output": "John Doe şu projelerde çalışıyor:\n1. [Proje Adı] - [Durum]\n2. [Proje Adı] - [Durum]\n\nJohn Doe, [Departman] departmanında [Pozisyon] pozisyonunda görev almaktadır."
        },
        {
            "input": "Enerji departmanında kaç çalışan var?",
            "output": "Enerji departmanında toplam [X] çalışan bulunmaktadır. Departman direktörü [İsim]'dir ve departmanın 2024 bütçesi [Miktar] TL'dir."
        },
        {
            "input": "İstanbul'daki projelerin durumu nedir?",
            "output": "İstanbul'daki projeler:\n\n1. [Proje Adı]\n   - Durum: [Durum]\n   - Departman: [Departman]\n   - Yönetici: [İsim]\n   - Bütçe: [Miktar]\n\n2. [Proje Adı]\n   ..."
        },
        {
            "input": "Yeni prosedürler var mı?",
            "output": "Son zamanlarda yayınlanan prosedürler:\n\n1. [Prosedür Başlığı] (Kod: [Kod])\n   - Departman: [Departman]\n   - Yayın Tarihi: [Tarih]\n   - Öncelik: [Öncelik]\n\n2. [Prosedür Başlığı]\n   ..."
        }
    ]
    
    @staticmethod
    def enhance_prompt(prompt: str, intent: str = None, entities: Dict = None) -> str:
        """
        Prompt'u optimize et - few-shot examples ekle
        
        Args:
            prompt: Orijinal kullanıcı sorgusu
            intent: Tespit edilen intent
            entities: Çıkarılan entity'ler
            
        Returns:
            Optimize edilmiş prompt
        """
        # Intent'e göre few-shot example seç
        example = PromptOptimizer._select_example(intent, entities)
        
        if example:
            enhanced = f"""Aşağıda şirket bilgilerine göre soru-cevap örnekleri verilmiştir. Benzer şekilde cevap verin.

Örnek:
Soru: {example['input']}
Cevap: {example['output']}

Şimdi aşağıdaki soruya cevap verin:
Soru: {prompt}
Cevap:"""
            return enhanced
        
        return prompt
    
    @staticmethod
    def _select_example(intent: str, entities: Dict) -> Optional[Dict]:
        """
        Intent ve entity'lere göre uygun few-shot example seç
        
        Args:
            intent: Intent türü
            entities: Entity dictionary
            
        Returns:
            Seçilen example veya None
        """
        if not intent:
            return PromptOptimizer.FEW_SHOT_EXAMPLES[0]
        
        intent_lower = intent.lower()
        
        # Intent'e göre example seç
        if "employee" in intent_lower:
            return PromptOptimizer.FEW_SHOT_EXAMPLES[0]  # Employee query example
        
        elif "department" in intent_lower or "statistics" in intent_lower:
            return PromptOptimizer.FEW_SHOT_EXAMPLES[1]  # Department statistics example
        
        elif "project" in intent_lower or "location" in intent_lower:
            return PromptOptimizer.FEW_SHOT_EXAMPLES[2]  # Project location example
        
        elif "procedure" in intent_lower:
            return PromptOptimizer.FEW_SHOT_EXAMPLES[3]  # Procedure example
        
        # Varsayılan
        return PromptOptimizer.FEW_SHOT_EXAMPLES[0]
    
    @staticmethod
    def build_system_prompt(base_prompt: str, company_name: str = "Company1", 
                          include_examples: bool = True) -> str:
        """
        Gelişmiş system prompt oluştur
        
        Args:
            base_prompt: Temel system prompt
            company_name: Şirket adı
            include_examples: Few-shot examples ekle
            
        Returns:
            Gelişmiş system prompt
        """
        enhanced = f"""{base_prompt}

Yanıt Verme Kuralları:
1. Sadece verilen şirket bilgilerine göre cevap verin
2. Bilmediğiniz bilgiler için tahmin yapmayın
3. Sayısal verileri açıkça belirtin
4. Listeleri numaralandırarak sunun
5. Profesyonel ve net bir dil kullanın
6. Türkçe yanıt verin
"""
        
        if include_examples:
            enhanced += "\n\nYanıt Formatı Örnekleri:\n"
            for i, example in enumerate(PromptOptimizer.FEW_SHOT_EXAMPLES[:2], 1):
                enhanced += f"\nÖrnek {i}:\nSoru: {example['input']}\nCevap: {example['output']}\n"
        
        return enhanced

