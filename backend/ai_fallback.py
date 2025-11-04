# -*- coding: utf-8 -*-
"""
AI Model Fallback Mekanizması

Bu modül bir AI model başarısız olursa otomatik olarak diğer bir modele
geçiş yapar. Böylece sistem kesintisiz çalışmaya devam eder.

Ne İşe Yarar:
- AI provider başarısızlığında otomatik yedek devreye girme
- Çoklu AI provider desteği
- Hata yönetimi ve recovery
- Kesintisiz servis sağlama

Kullanım:
- Bir AI provider çalışmazsa otomatik olarak diğerine geçer
- Yapılandırma: backend/.env dosyasında AI_PROVIDER sırası
"""
import os
from typing import Optional, List, Tuple
from dotenv import load_dotenv

load_dotenv()

class AIFallback:
    """AI sağlayıcı fallback sistemi"""
    
    # Fallback sırası (öncelik sırasına göre)
    FALLBACK_ORDER = [
        "GEMINI",      # 1. öncelik (ücretsiz katman)
        "OPENAI",      # 2. öncelik
        "AZURE",       # 3. öncelik
        "OLLAMA",      # 4. öncelik (yerel, ücretsiz)
        "HUGGINGFACE", # 5. öncelik
        "LOCAL"        # 6. öncelik (son çare)
    ]
    
    @staticmethod
    def get_fallback_providers(current_provider: str) -> List[str]:
        """
        Fallback sağlayıcı listesi oluştur
        
        Args:
            current_provider: Şu anki AI sağlayıcı
            
        Returns:
            Fallback sağlayıcı listesi (mevcut + alternatifler)
        """
        current_upper = current_provider.upper()
        
        # Mevcut sağlayıcıyı listeden çıkar ve başa ekle
        fallback_list = [current_upper]
        for provider in AIFallback.FALLBACK_ORDER:
            if provider != current_upper:
                fallback_list.append(provider)
        
        # Sadece API key'i olan sağlayıcıları filtrele
        available_providers = []
        for provider in fallback_list:
            if AIFallback._is_provider_available(provider):
                available_providers.append(provider)
        
        return available_providers
    
    @staticmethod
    def _is_provider_available(provider: str) -> bool:
        """Sağlayıcının kullanılabilir olup olmadığını kontrol et"""
        provider_upper = provider.upper()
        
        if provider_upper == "GEMINI":
            return bool(os.getenv("GEMINI_API_KEY")) and os.getenv("GEMINI_API_KEY") != "your-gemini-api-key-here"
        
        elif provider_upper == "OPENAI":
            return bool(os.getenv("OPENAI_API_KEY"))
        
        elif provider_upper == "AZURE":
            return bool(os.getenv("AZURE_OPENAI_API_KEY")) and bool(os.getenv("AZURE_OPENAI_ENDPOINT"))
        
        elif provider_upper == "OLLAMA":
            # Ollama her zaman mevcut (yerel)
            return True
        
        elif provider_upper == "HUGGINGFACE":
            return bool(os.getenv("HUGGINGFACE_API_KEY"))
        
        elif provider_upper == "LOCAL":
            # Local her zaman mevcut (transformers kütüphanesi gerekli)
            try:
                import transformers
                return True
            except:
                return False
        
        return False
    
    @staticmethod
    def try_with_fallback(prompt: str, conversation_history: Optional[List] = None, 
                         current_provider: str = None, error_message: str = "") -> Tuple[Optional[str], str]:
        """
        Fallback mekanizması ile AI yanıtı dene
        
        Args:
            prompt: Kullanıcı sorgusu
            conversation_history: Conversation history
            current_provider: Şu anki sağlayıcı
            error_message: Hata mesajı (debug için)
            
        Returns:
            (yanıt, kullanılan_sağlayıcı) veya (None, hata_mesajı)
        """
        from ai_service import ask_ai, AI_PROVIDER
        
        if current_provider is None:
            current_provider = AI_PROVIDER
        
        fallback_providers = AIFallback.get_fallback_providers(current_provider)
        
        last_error = None
        for provider in fallback_providers:
            try:
                # Geçici olarak provider'ı değiştir
                original_provider = os.getenv("AI_PROVIDER")
                os.environ["AI_PROVIDER"] = provider
                
                # AI yanıtını al
                response = ask_ai(prompt, conversation_history)
                
                # Provider'ı geri al
                if original_provider:
                    os.environ["AI_PROVIDER"] = original_provider
                
                # Başarılı yanıt kontrolü
                if response and len(response.strip()) > 10 and not response.startswith("Error") and not response.startswith("Hata"):
                    return response, provider
                
                # Başarısız yanıt
                last_error = f"{provider}: Invalid response"
                
            except Exception as e:
                last_error = f"{provider}: {str(e)}"
                continue
            finally:
                # Provider'ı geri al
                if original_provider:
                    os.environ["AI_PROVIDER"] = original_provider
        
        return None, f"Tüm sağlayıcılar denendi, hiçbiri çalışmadı. Son hata: {last_error}"

