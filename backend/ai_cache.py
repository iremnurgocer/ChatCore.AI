"""
AI Response Caching Sistemi
Benzer sorgular için hızlı yanıt döndürür
"""
import hashlib
import json
import time
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime, timedelta

class AICache:
    """AI yanıt cache sistemi - benzer sorgular için hızlı dönüş"""
    
    def __init__(self, cache_dir: Path = None, ttl_hours: int = 24):
        """
        Args:
            cache_dir: Cache dosyalarının saklanacağı dizin
            ttl_hours: Cache'in geçerlilik süresi (saat)
        """
        if cache_dir is None:
            cache_dir = Path(__file__).parent / "data" / ".cache"
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
        self.cache_file = self.cache_dir / "ai_responses.json"
        self._cache: Dict[str, Dict] = {}
        self._load_cache()
    
    def _load_cache(self):
        """Cache dosyasını yükle"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self._cache = json.load(f)
                # Expired entries'i temizle
                self._cleanup_expired()
            except Exception as e:
                print(f"Cache yüklenemedi: {e}")
                self._cache = {}
        else:
            self._cache = {}
    
    def _save_cache(self):
        """Cache'i dosyaya kaydet"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self._cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Cache kaydedilemedi: {e}")
    
    def _generate_key(self, prompt: str, provider: str, conversation_context: str = "") -> str:
        """
        Cache key oluştur
        
        Args:
            prompt: Kullanıcı sorgusu
            provider: AI sağlayıcı adı
            conversation_context: Conversation history hash
            
        Returns:
            Cache key (hash)
        """
        # Prompt'u normalize et (küçük harf, boşlukları temizle)
        normalized_prompt = prompt.lower().strip()
        # Çok benzer sorguları yakalamak için ilk 100 karakteri al
        if len(normalized_prompt) > 100:
            normalized_prompt = normalized_prompt[:100]
        
        key_string = f"{provider}:{normalized_prompt}:{conversation_context}"
        return hashlib.md5(key_string.encode('utf-8')).hexdigest()
    
    def _cleanup_expired(self):
        """Süresi dolmuş cache entry'lerini temizle"""
        now = datetime.now()
        expired_keys = []
        
        for key, entry in self._cache.items():
            try:
                cached_time = datetime.fromisoformat(entry.get('timestamp', ''))
                if now - cached_time > self.ttl:
                    expired_keys.append(key)
            except:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            self._save_cache()
    
    def get(self, prompt: str, provider: str, conversation_context: str = "") -> Optional[str]:
        """
        Cache'den yanıt al
        
        Args:
            prompt: Kullanıcı sorgusu
            provider: AI sağlayıcı
            conversation_context: Conversation history hash
            
        Returns:
            Cached yanıt veya None
        """
        key = self._generate_key(prompt, provider, conversation_context)
        
        if key in self._cache:
            entry = self._cache[key]
            try:
                cached_time = datetime.fromisoformat(entry['timestamp'])
                if datetime.now() - cached_time < self.ttl:
                    # Cache hit - usage counter'ı artır
                    entry['usage_count'] = entry.get('usage_count', 0) + 1
                    self._save_cache()
                    return entry['response']
                else:
                    # Expired
                    del self._cache[key]
                    self._save_cache()
            except:
                del self._cache[key]
        
        return None
    
    def set(self, prompt: str, provider: str, response: str, conversation_context: str = ""):
        """
        Cache'e yanıt kaydet
        
        Args:
            prompt: Kullanıcı sorgusu
            provider: AI sağlayıcı
            response: AI yanıtı
            conversation_context: Conversation history hash
        """
        key = self._generate_key(prompt, provider, conversation_context)
        
        self._cache[key] = {
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'provider': provider,
            'prompt_preview': prompt[:50],
            'usage_count': 0
        }
        
        # Cache boyutunu kontrol et (max 1000 entry)
        if len(self._cache) > 1000:
            # En az kullanılan entry'leri sil
            sorted_entries = sorted(
                self._cache.items(),
                key=lambda x: (x[1].get('usage_count', 0), x[1].get('timestamp', ''))
            )
            # En eski %20'yi sil
            remove_count = len(sorted_entries) // 5
            for key_to_remove, _ in sorted_entries[:remove_count]:
                del self._cache[key_to_remove]
        
        self._save_cache()
    
    def get_stats(self) -> Dict[str, Any]:
        """Cache istatistikleri"""
        self._cleanup_expired()
        return {
            'total_entries': len(self._cache),
            'cache_size_kb': self.cache_file.stat().st_size / 1024 if self.cache_file.exists() else 0,
            'ttl_hours': self.ttl.total_seconds() / 3600
        }
    
    def clear(self):
        """Cache'i temizle"""
        self._cache = {}
        if self.cache_file.exists():
            self.cache_file.unlink()

# Global cache instance
_ai_cache = None

def get_ai_cache() -> AICache:
    """Global cache instance"""
    global _ai_cache
    if _ai_cache is None:
        _ai_cache = AICache()
    return _ai_cache

