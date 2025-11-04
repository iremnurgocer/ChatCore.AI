"""
Performans Yapılandırma Dosyası
Hızlı yanıt için optimize edilmiş ayarlar
"""

# RAG Ayarları (Performans için)
RAG_K_DOCUMENTS = 3  # Document sayısı (5'ten 3'e düşürüldü - %40 daha hızlı)
RAG_USE_HYBRID = False  # Hybrid search (False = daha hızlı)
RAG_USE_RE_RANKING = False  # Re-ranking (False = daha hızlı)
RAG_MAX_QUERY_EXPANSIONS = 2  # Query expansion sayısı (5'ten 2'ye)

# Cache Ayarları
CACHE_ENABLED = True
CACHE_TTL_HOURS = 24
CACHE_MAX_SIZE = 1000  # Maksimum cache entry sayısı

# AI Provider Timeout'ları (saniye)
TIMEOUT_GEMINI = 15
TIMEOUT_OPENAI = 30
TIMEOUT_AZURE = 30
TIMEOUT_OLLAMA = 60  # Ollama daha yavaş olabilir
TIMEOUT_HUGGINGFACE = 20

# Fallback Ayarları (performans için)
FALLBACK_ENABLED = False  # Fallback kapalı (daha hızlı, ama daha az güvenilir)
FALLBACK_ONLY_ON_ERROR = True  # Sadece hata durumunda fallback

# Advanced RAG Ayarları
ADVANCED_RAG_ENABLED = False  # Varsayılan olarak kapalı (basit RAG daha hızlı)

def get_rag_config():
    """RAG yapılandırması"""
    return {
        "k": RAG_K_DOCUMENTS,
        "use_hybrid": RAG_USE_HYBRID,
        "use_re_ranking": RAG_USE_RE_RANKING,
        "max_expansions": RAG_MAX_QUERY_EXPANSIONS
    }

def get_timeout(provider: str) -> int:
    """Provider'a göre timeout değeri"""
    timeouts = {
        "GEMINI": TIMEOUT_GEMINI,
        "OPENAI": TIMEOUT_OPENAI,
        "AZURE": TIMEOUT_AZURE,
        "OLLAMA": TIMEOUT_OLLAMA,
        "HUGGINGFACE": TIMEOUT_HUGGINGFACE
    }
    return timeouts.get(provider.upper(), 30)


