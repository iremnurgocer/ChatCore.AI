"""
AI Servis Modeli - Çoklu sağlayıcı AI entegrasyonu RAG desteği ile
OpenAI, Azure OpenAI, Google Gemini, Ollama ve Hugging Face deste�i
"""
import os
import json
import requests
import time
from typing import Optional, List
from dotenv import load_dotenv
from pathlib import Path

# LangChain import'ları (modern API)
LANGCHAIN_AVAILABLE = False
try:
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain_core.documents import Document
    try:
        from langchain_community.embeddings import SentenceTransformerEmbeddings
    except ImportError:
        # Eski versiyonlar için alternatif import
        try:
            from langchain.embeddings import SentenceTransformerEmbeddings
        except ImportError:
            try:
                # LangChain 0.2+ için
                from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
            except ImportError:
                SentenceTransformerEmbeddings = None
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    LANGCHAIN_AVAILABLE = False
    print(f"Uyarı: LangChain kütüphaneleri mevcut değil veya uyumsuz versiyon: {e}")
    print("RAG özelliği devre dışı kalacak. LangChain paketlerini güncellemek için:")
    print("  pip install --upgrade langchain langchain-openai langchain-community langchain-core")

# Environment değişkenlerini yükle
load_dotenv()

# Environment Değişkenleri
AI_PROVIDER = os.getenv("AI_PROVIDER", "GEMINI").upper()  # Varsayılan: GEMINI (ücretsiz katman)

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Azure OpenAI
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")

# Google Gemini (ücretsiz katman mevcut)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Ollama (ücretsiz - Yerel)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

# Hugging Face
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HUGGINGFACE_MODEL = os.getenv("HUGGINGFACE_MODEL", "distilgpt2")

# Şirket adı environment'dan (varsayılan: Company1)
COMPANY_NAME = os.getenv("COMPANY_NAME", "Company1")

print(f"Aktif AI sağlayıcı: {AI_PROVIDER}")

# System Prompt Template
SYSTEM_PROMPT_TEMPLATE = """You are a professional digital assistant for {company_name}.

Your role:
- Provide accurate and helpful responses based on the company's internal information
- Answer in a clear, professional manner
- Only use information provided in the context
- Do not make assumptions about information not available
- Answer questions about employees, projects, and departments

If a user's question is not related to {company_name}'s internal information, politely explain that you can only assist with company-related matters."""

SYSTEM_PROMPT = SYSTEM_PROMPT_TEMPLATE.format(company_name=COMPANY_NAME)

# RAG Vector Store Cache
_vector_store_cache = None
_embeddings_cache = None
_data_cache_timestamp = None

def get_vector_store(force_reload: bool = False):
    """
    Get or create FAISS vector store with intelligent caching
    
    This function implements a caching mechanism to avoid recreating the vector
    store on every request. The cache is invalidated when data files are modified.
    
    Args:
        force_reload: If True, bypass cache and rebuild vector store
        
    Returns:
        Tuple of (vector_store, embeddings) or (None, None) if creation fails
    """
    global _vector_store_cache, _embeddings_cache, _data_cache_timestamp
    
    data_dir = Path(__file__).parent / "data"
    
    # Cache check
    if not force_reload and _vector_store_cache is not None:
        employees_path = data_dir / "employees.json"
        if employees_path.exists():
            current_mtime = employees_path.stat().st_mtime
            if _data_cache_timestamp == current_mtime:
                return _vector_store_cache, _embeddings_cache
    
    if not LANGCHAIN_AVAILABLE:
        return None, None
    
    try:
        # Embeddings model
        if OPENAI_API_KEY:
            embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        else:
            # Free alternative
            if SentenceTransformerEmbeddings is None:
                print("Uyarı: SentenceTransformerEmbeddings kullanılamıyor, embeddings oluşturulamadı")
                return None, None
            embeddings = SentenceTransformerEmbeddings(
                model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            )
        
        # Read and combine JSON data
        docs = []
        metadata = []
        
        for file_name in ["employees.json", "departments.json", "projects.json", "procedures.json"]:
            file_path = data_dir / file_name
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                # Create separate documents for each record
                if isinstance(data, list):
                    for item in data:
                        text = json.dumps(item, ensure_ascii=False)
                        docs.append(text)
                        metadata.append({"source": file_name, "type": file_name.replace(".json", "")})
                else:
                    text = json.dumps(data, ensure_ascii=False)
                    docs.append(text)
                    metadata.append({"source": file_name, "type": file_name.replace(".json", "")})
        
        if not docs:
            return None, None
        
        # Create FAISS vector database
        documents = [Document(page_content=doc, metadata=meta) for doc, meta in zip(docs, metadata)]
        vector_store = FAISS.from_documents(documents, embeddings)
        
        # Save to cache
        _vector_store_cache = vector_store
        _embeddings_cache = embeddings
        employees_path = data_dir / "employees.json"
        if employees_path.exists():
            _data_cache_timestamp = employees_path.stat().st_mtime

        print("Vector store cache güncellendi")
        return vector_store, embeddings
        
    except Exception as e:
        print(f"Uyarı: Vector store oluşturma hatası: {e}")
        return None, None

def ask_ai(prompt: str, conversation_history: Optional[List] = None, use_advanced_rag: bool = None, 
           use_cache: bool = True, use_fallback: bool = None) -> str:
    """
    AI sorguları için ana giriş noktası (Gelişmiş RAG, Cache ve Fallback desteği ile)

    İstekleri yapılandırmaya göre uygun AI sağlayıcıya yönlendirir.
    Çoklu sağlayıcı desteği: OpenAI, Azure, Gemini, Ollama, Hugging Face, Local.
    Tüm sağlayıcılar için gelişmiş RAG, cache ve fallback desteği.

    Args:
        prompt: Kullanıcı sorgusu veya mesajı
        conversation_history: Context için önceki mesajların opsiyonel listesi
        use_advanced_rag: Gelişmiş RAG kullan (hybrid search, re-ranking)
        use_cache: Response cache kullan
        use_fallback: Model fallback mekanizması kullan

    Returns:
        AI tarafından üretilmiş yanıt string olarak
    """
    if not prompt or not prompt.strip():
        return "Lütfen bir soru veya metin girin."
    
    # Performans yapılandırması (hızlı mod varsayılan)
    try:
        from performance_config import ADVANCED_RAG_ENABLED, FALLBACK_ENABLED
        if use_advanced_rag is None:
            use_advanced_rag = ADVANCED_RAG_ENABLED
        if use_fallback is None:
            use_fallback = FALLBACK_ENABLED
    except ImportError:
        # Varsayılan değerler (hızlı mod)
        if use_advanced_rag is None:
            use_advanced_rag = False
        if use_fallback is None:
            use_fallback = False
    
    start_time = time.time()

    # Cache kontrolü
    if use_cache:
        try:
            from ai_cache import get_ai_cache
            from ai_service import AI_PROVIDER
            
            cache = get_ai_cache()
            # Conversation context hash (son 2 mesaj)
            context_hash = ""
            if conversation_history:
                last_messages = conversation_history[-2:] if len(conversation_history) >= 2 else conversation_history
                context_str = "|".join([m.get('content', '')[:50] for m in last_messages if isinstance(m, dict)])
                import hashlib
                context_hash = hashlib.md5(context_str.encode()).hexdigest()
            
            cached_response = cache.get(prompt, AI_PROVIDER, context_hash)
            if cached_response:
                print(f"Cache hit - Yanıt cache'den döndü")
                return cached_response
        except Exception as e:
            print(f"Cache kontrolü hatası (devam ediliyor): {e}")

    try:
        response = None
        provider_used = AI_PROVIDER
        
        try:
            if AI_PROVIDER == "OPENAI":
                if not OPENAI_API_KEY:
                    raise Exception("OpenAI API key not found.")
                response = ask_openai_with_rag(prompt, conversation_history, use_advanced_rag)

            elif AI_PROVIDER == "AZURE":
                if not AZURE_OPENAI_API_KEY or not AZURE_OPENAI_ENDPOINT:
                    raise Exception("Azure API credentials missing.")
                response = ask_azure_with_rag(prompt, conversation_history, use_advanced_rag)
            
            elif AI_PROVIDER == "GEMINI":
                if not GEMINI_API_KEY:
                    raise Exception("Gemini API key not found.")
                response = ask_gemini_with_rag(prompt, conversation_history, use_advanced_rag)
            
            elif AI_PROVIDER == "OLLAMA":
                response = ask_ollama_with_rag(prompt, conversation_history, use_advanced_rag)

            elif AI_PROVIDER == "HUGGINGFACE":
                if not HUGGINGFACE_API_KEY:
                    raise Exception("Hugging Face API key missing.")
                response = ask_huggingface_with_rag(prompt, use_advanced_rag)

            elif AI_PROVIDER == "LOCAL":
                response = ask_local_with_rag(prompt, use_advanced_rag)

            else:
                response = f"Unknown AI_PROVIDER value: {AI_PROVIDER}"
        
        except Exception as e:
            print(f"Primary provider hatası ({AI_PROVIDER}): {e}")
            response = None
        
        # Fallback mekanizması
        if (not response or len(response.strip()) < 10 or response.startswith("Error") or 
            response.startswith("Hata")) and use_fallback:
            try:
                from ai_fallback import AIFallback
                fallback_response, fallback_provider = AIFallback.try_with_fallback(
                    prompt, conversation_history, AI_PROVIDER, str(e) if 'e' in locals() else ""
                )
                if fallback_response:
                    response = fallback_response
                    provider_used = fallback_provider
                    print(f"Fallback başarılı: {fallback_provider} kullanıldı")
            except Exception as fallback_error:
                print(f"Fallback hatası: {fallback_error}")
        
        # Cache'e kaydet
        if response and use_cache:
            try:
                from ai_cache import get_ai_cache
                cache = get_ai_cache()
                cache.set(prompt, provider_used, response, context_hash)
            except:
                pass
        
        return response if response else "Yanıt alınamadı. Lütfen tekrar deneyin."

    except Exception as e:
        print(f"AI servis hatası: {e}")
        return f"Hata: {str(e)}"
    finally:
        elapsed = time.time() - start_time
        print(f"Yanıt süresi: {elapsed:.2f}s")

def ask_openai_with_rag(prompt: str, conversation_history: Optional[List] = None, use_advanced_rag: bool = True) -> str:
    """
    OpenAI GPT with Advanced RAG (Retrieval-Augmented Generation)
    
    Uses advanced RAG service with hybrid search, multi-query, and re-ranking.
    Falls back to basic RAG or direct OpenAI call if needed.
    
    Args:
        prompt: User query
        conversation_history: Previous conversation messages
        use_advanced_rag: Use advanced RAG (hybrid search, re-ranking)
        
    Returns:
        AI response based on retrieved company data
    """
    try:
        vector_store, embeddings = get_vector_store()
        
        if vector_store is None:
            return ask_openai_direct(prompt, conversation_history)
        
        # RAG servisi kullan (optimize - hızlı mod)
        context = ""
        if use_advanced_rag:
            try:
                from rag_service import get_rag_service
                rag_service = get_rag_service(vector_store, embeddings)
                # Hızlı mod: k=3, hybrid=False (daha hızlı)
                context = rag_service.retrieve_context(prompt, k=3, use_hybrid=False)
            except ImportError:
                # Fallback to basic RAG
                use_advanced_rag = False
            except Exception as e:
                print(f"Gelişmiş RAG hatası (fallback): {e}")
                use_advanced_rag = False
        
        # Basit RAG fallback (optimize - daha az document)
        if not context or not use_advanced_rag:
            docs = vector_store.similarity_search(prompt, k=3)  # 5->3 (daha hızlı)
            if docs:
                context_parts = []
                for doc in docs:
                    try:
                        data = json.loads(doc.page_content)
                        doc_type = doc.metadata.get("type", "data")
                        if doc_type == "employees":
                            context_parts.append(f"Çalışan: {data.get('name', 'N/A')} - {data.get('department', 'N/A')}, {data.get('position', 'N/A')}")
                        elif doc_type == "projects":
                            context_parts.append(f"Proje: {data.get('name', 'N/A')} - {data.get('status', 'N/A')}, {data.get('department', 'N/A')}")
                        elif doc_type == "departments":
                            context_parts.append(f"Departman: {data.get('name', 'N/A')} - {data.get('director', 'N/A')}")
                        else:
                            context_parts.append(doc.page_content[:200])
                    except:
                        context_parts.append(doc.page_content[:200])
                context = "\n\n".join(context_parts)
        
        # LLM model
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.3,
            openai_api_key=OPENAI_API_KEY
        )
        
        # Conversation history için mesaj formatı
        messages = []
        
        # System prompt
        system_msg = f"""{SYSTEM_PROMPT}

Şirket Bilgileri (Sadece bu bilgilere göre cevap verin):
{context}""" if context else SYSTEM_PROMPT
        
        messages.append({"role": "system", "content": system_msg})
        
        # Conversation history
        if conversation_history:
            recent_history = conversation_history[-5:] if len(conversation_history) > 5 else conversation_history
            valid_history = [
                m for m in recent_history 
                if isinstance(m, dict) and "role" in m and "content" in m
            ]
            messages.extend(valid_history)
        
        # User query
        messages.append({"role": "user", "content": prompt})
        
        # LLM invoke
        response = llm.invoke(messages)
        return response.content.strip()
        
    except Exception as e:
        print(f"OpenAI RAG hatası: {e}")
        return ask_openai_direct(prompt, conversation_history)

def ask_openai_langchain(prompt: str, conversation_history: Optional[List] = None) -> str:
    """
    OpenAI GPT with RAG (Retrieval-Augmented Generation)
    
    Uses FAISS vector database to retrieve relevant company data before generating response.
    Falls back to direct OpenAI call if vector store is unavailable.
    
    Args:
        prompt: User query
        conversation_history: Previous conversation messages
        
    Returns:
        AI response based on retrieved company data
    """
    try:
        vector_store, embeddings = get_vector_store()
        
        if vector_store is None:
            return ask_openai_direct(prompt, conversation_history)
        
        # LLM model
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.3,
            openai_api_key=OPENAI_API_KEY
        )
        
        # Context retrieval (optimize - hızlı)
        docs = vector_store.similarity_search(prompt, k=3)  # Zaten optimize edilmiş
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Prompt template
        prompt_template = f"""{SYSTEM_PROMPT}

Company Information:
{context}

Question: {prompt}

Answer (based only on provided information, professional and clear):"""
        
        response = llm.invoke(prompt_template)
        return response.content.strip()

    except Exception as e:
        print(f"LangChain/OpenAI hatas�: {e}")
        return ask_openai_direct(prompt, conversation_history)

def ask_openai_direct(prompt: str, conversation_history: Optional[List] = None) -> str:
    """
    Direct OpenAI API call without RAG
    
    Used as fallback when vector store is unavailable or for simpler queries.
    Includes conversation history for context-aware responses.
    
    Args:
        prompt: User query
        conversation_history: Previous messages (last 5 used)
        
    Returns:
        OpenAI generated response
    """
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        if conversation_history:
            recent_history = conversation_history[-5:] if len(conversation_history) > 5 else conversation_history
            valid_history = [
                m for m in recent_history 
                if isinstance(m, dict) and "role" in m and "content" in m
            ]
            messages.extend(valid_history)
        
        messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.3,
            max_tokens=500
        )
        
        if not response.choices or len(response.choices) == 0:
            return "OpenAI returned no response"
        
        return response.choices[0].message.content.strip() if response.choices[0].message.content else ""
    except Exception as e:
        return f"OpenAI response error: {e}"

def ask_azure_with_rag(prompt: str, conversation_history: Optional[List] = None, use_advanced_rag: bool = True) -> str:
    """
    Azure OpenAI with Advanced RAG
    
    Args:
        prompt: User query
        conversation_history: Previous conversation messages
        use_advanced_rag: Use advanced RAG
        
    Returns:
        Azure OpenAI generated response with company context
    """
    try:
        from openai import AzureOpenAI
        
        # RAG context al
        context = ""
        try:
            vector_store, embeddings = get_vector_store()
            if vector_store:
                if use_advanced_rag:
                    try:
                        from rag_service import get_rag_service
                        rag_service = get_rag_service(vector_store, embeddings)
                        context = rag_service.retrieve_context(prompt, k=5, use_hybrid=True)
                    except:
                        # Basic RAG fallback
                        docs = vector_store.similarity_search(prompt, k=3)
                        if docs:
                            from rag_service import AdvancedRAGService
                            rag_temp = AdvancedRAGService(vector_store, embeddings)
                            context = rag_temp.format_context_for_ai(docs, prompt)
                else:
                    docs = vector_store.similarity_search(prompt, k=5)
                    if docs:
                        from rag_service import AdvancedRAGService
                        rag_temp = AdvancedRAGService(vector_store, embeddings)
                        context = rag_temp.format_context_for_ai(docs, prompt)
        except Exception as e:
            print(f"RAG context alınamadı (devam ediliyor): {e}")
        
        client = AzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            api_version="2024-02-15-preview",
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
        
        system_msg = SYSTEM_PROMPT
        if context:
            system_msg = f"""{SYSTEM_PROMPT}

Şirket Bilgileri (Sadece bu bilgilere göre cevap verin):
{context}"""
        
        messages = [{"role": "system", "content": system_msg}]
        if conversation_history:
            recent_history = conversation_history[-5:] if len(conversation_history) > 5 else conversation_history
            valid_history = [
                m for m in recent_history 
                if isinstance(m, dict) and "role" in m and "content" in m
            ]
            messages.extend(valid_history)
        messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=messages,
            temperature=0.5,
            max_tokens=600
        )

        if not response.choices or len(response.choices) == 0:
            return "Azure OpenAI returned no response"
        
        return response.choices[0].message.content.strip() if response.choices[0].message.content else ""

    except Exception as e:
        print(f"Azure OpenAI hatası: {e}")
        return f"Azure response error: {e}"

def ask_azure(prompt: str, conversation_history: Optional[List] = None) -> str:
    """Backward compatibility wrapper"""
    return ask_azure_with_rag(prompt, conversation_history, use_advanced_rag=True)

def ask_gemini_with_rag(prompt: str, conversation_history: Optional[List] = None, use_advanced_rag: bool = True) -> str:
    """
    Google Gemini API with Advanced RAG
    
    Args:
        prompt: User query
        conversation_history: Previous messages for context
        use_advanced_rag: Use advanced RAG (hybrid search, re-ranking)
        
    Returns:
        Gemini generated response with company data context
    """
    try:
        if not GEMINI_API_KEY or GEMINI_API_KEY == "your-gemini-api-key-here":
            return "Gemini API key bulunamadı. Lütfen backend/.env dosyasında GEMINI_API_KEY'i ayarlayın."
        
        # Gelişmiş RAG context al
        company_context = ""
        try:
            vector_store, embeddings = get_vector_store()
            if vector_store is not None:
                if use_advanced_rag:
                    try:
                        from rag_service import get_rag_service
                        rag_service = get_rag_service(vector_store, embeddings)
                        company_context = rag_service.retrieve_context(prompt, k=3, use_hybrid=False)
                    except Exception as e:
                        print(f"Gelişmiş RAG hatası (fallback): {e}")
                        # Basic RAG fallback
                        docs = vector_store.similarity_search(prompt, k=3)
                        if docs:
                            from rag_service import AdvancedRAGService
                            rag_temp = AdvancedRAGService(vector_store, embeddings)
                            company_context = rag_temp.format_context_for_ai(docs, prompt)
                else:
                    docs = vector_store.similarity_search(prompt, k=5)
                    if docs:
                        from rag_service import AdvancedRAGService
                        rag_temp = AdvancedRAGService(vector_store, embeddings)
                        company_context = rag_temp.format_context_for_ai(docs, prompt)
        except Exception as e:
            print(f"RAG context alınamadı (devam ediliyor): {e}")
        
        # REST API kullan (Postman örneğine göre - daha güvenilir)
        # URL formatı: https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={API_KEY}
        # Body formatı: {"contents": [{"role": "user", "parts": [{"text": "..."}]}]}
        
        # Güncel modelleri sırayla dene (Postman örneğinde gemini-2.0-flash çalıştı)
        models_to_try = [
            "gemini-2.0-flash",      # Postman'de çalışan model
            "gemini-2.5-flash",      # En güncel
            "gemini-2.5-pro",        # Pro versiyonu
            "gemini-1.5-flash",      # Önceki versiyon
            "gemini-1.5-pro",        # Önceki pro
            "gemini-pro",            # Eski versiyon
        ]
        
        # Build contents array (Postman formatına göre)
        contents = []
        
        # System prompt ve company context'i user mesajına ekle
        if company_context:
            user_text = f"""{SYSTEM_PROMPT}

Şirket Verileri (Sadece bu bilgilere göre cevap verin):
{company_context}

Soru: {prompt}

Yanıt (sadece yukarıdaki şirket verilerine göre, açık ve profesyonel):"""
        else:
            # Context yoksa sadece system prompt
            user_text = f"{SYSTEM_PROMPT}\n\nSoru: {prompt}"
        
        # Conversation history ekle
        if conversation_history:
            recent_history = conversation_history[-3:] if len(conversation_history) > 3 else conversation_history
            history_parts = []
            for m in recent_history:
                if isinstance(m, dict):
                    role = m.get('role', 'user')
                    content = m.get('content', '')
                    # Gemini için role mapping: 'assistant' -> 'model', 'user' -> 'user'
                    if role == 'assistant':
                        role = 'model'
                    elif role != 'user':
                        role = 'user'
                    
                    # Her mesajı contents array'ine ekle
                    contents.append({
                        "role": role,
                        "parts": [{"text": content}]
                    })
        
        # Son kullanıcı mesajını ekle
        contents.append({
            "role": "user",
            "parts": [{"text": user_text}]
        })
        
        # Payload (Postman formatına göre)
        payload = {
            "contents": contents
        }
        
        # Her modeli dene
        last_error = None
        for model_name in models_to_try:
            try:
                # URL (Postman formatına göre)
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
                
                # POST request (Postman formatına göre) - Timeout kısaltıldı (timeout sorunu için)
                response = requests.post(url, json=payload, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Response formatı (Postman formatına göre)
                    # {"candidates": [{"content": {"parts": [{"text": "..."}]}}]}
                    if "candidates" in data and len(data["candidates"]) > 0:
                        candidate = data["candidates"][0]
                        if "content" in candidate and "parts" in candidate["content"]:
                            parts = candidate["content"]["parts"]
                            if len(parts) > 0 and "text" in parts[0]:
                                return parts[0]["text"].strip()
                    
                    # Yanıt yapısı beklenen formatta değil
                    last_error = f"{model_name}: Yanıt formatı beklenmeyen formatta"
                    continue
                
                # 200 değilse hata kontrolü
                error_text = response.text if hasattr(response, 'text') else str(response.status_code)
                last_error = f"{model_name}: {response.status_code} - {error_text[:150]}"
                
                # API key hatası - hemen döndür
                if response.status_code == 401 or "API key" in error_text:
                    return "Gemini API key geçersiz veya eksik. Lütfen backend/.env dosyasında GEMINI_API_KEY'i kontrol edin."
                
                # Quota/limit hatası - hemen döndür
                if response.status_code == 429 or "quota" in error_text.lower() or "limit" in error_text.lower():
                    return "Gemini API limiti doldu. Ücretsiz ve sınırsız kullanım için Ollama'yı deneyin (AI_PROVIDER=OLLAMA)."
                
                # Model bulunamadı - bir sonraki modeli dene
                if response.status_code == 404 or "not found" in error_text.lower():
                    continue
                
                # Diğer hatalar - bir sonraki modeli dene
                continue
                    
            except requests.exceptions.RequestException as e:
                error_msg = str(e)
                last_error = f"{model_name}: {error_msg[:150]}"
                
                # Bağlantı hatası - sonraki modeli dene
                if "Connection" in error_msg or "timeout" in error_msg.lower():
                    continue
                
                # Diğer hatalar - sonraki modeli dene
                continue
            except Exception as e:
                error_msg = str(e)
                last_error = f"{model_name}: {error_msg[:150]}"
                continue
        
        # Hiçbiri çalışmadıysa detaylı hata döndür
        if last_error:
            if "404" in last_error or "not found" in last_error.lower():
                return f"Gemini model bulunamadı: {last_error[:200]}\n\nÇözüm: Ollama kullanın (tamamen ücretsiz, yerel): AI_PROVIDER=OLLAMA"
            return f"Gemini API hatası: {last_error[:200]}\n\nÇözüm: Ollama kullanın (tamamen ücretsiz, yerel): AI_PROVIDER=OLLAMA"
        
        return "Gemini API: Hiçbir model çalışmadı. Lütfen backend/.env dosyasında GEMINI_API_KEY'i kontrol edin.\n\nÇözüm: Ollama kullanın (tamamen ücretsiz, yerel): AI_PROVIDER=OLLAMA"

    except Exception as e:
        error_msg = str(e)
        print(f"Gemini hatası: {error_msg}")
        
        # Bağlantı hatası
        if "Connection" in error_msg or "timeout" in error_msg.lower():
            return "Gemini API'ye bağlanılamadı. İnternet bağlantınızı kontrol edin veya Ollama kullanın (yerel, ücretsiz)."
        
        return f"Gemini hatası: {error_msg[:200]}\n\nÇözüm: Ollama kullanın (tamamen ücretsiz, yerel): AI_PROVIDER=OLLAMA"

def ask_gemini(prompt: str, conversation_history: Optional[List] = None) -> str:
    """Backward compatibility wrapper"""
    return ask_gemini_with_rag(prompt, conversation_history, use_advanced_rag=True)

def ask_ollama_with_rag(prompt: str, conversation_history: Optional[List] = None, use_advanced_rag: bool = True) -> str:
    """
    Ollama local model with Advanced RAG (free, runs offline)
    
    Requires Ollama server to be running locally. Ideal for privacy-sensitive deployments.
    
    Args:
        prompt: User query
        conversation_history: Previous conversation messages
        use_advanced_rag: Use advanced RAG
        
    Returns:
        Ollama model generated response with company context
    """
    try:
        # RAG context al
        company_context = ""
        try:
            vector_store, embeddings = get_vector_store()
            if vector_store:
                if use_advanced_rag:
                    try:
                        from rag_service import get_rag_service
                        rag_service = get_rag_service(vector_store, embeddings)
                        company_context = rag_service.retrieve_context(prompt, k=3, use_hybrid=False)
                    except:
                        docs = vector_store.similarity_search(prompt, k=3)
                        if docs:
                            from rag_service import AdvancedRAGService
                            rag_temp = AdvancedRAGService(vector_store, embeddings)
                            company_context = rag_temp.format_context_for_ai(docs, prompt)
                else:
                    docs = vector_store.similarity_search(prompt, k=5)
                    if docs:
                        from rag_service import AdvancedRAGService
                        rag_temp = AdvancedRAGService(vector_store, embeddings)
                        company_context = rag_temp.format_context_for_ai(docs, prompt)
        except Exception as e:
            print(f"RAG context alınamadı (devam ediliyor): {e}")
        
        url = f"{OLLAMA_BASE_URL}/api/generate"
        
        # Context ile prompt hazırla
        if company_context:
            full_prompt = f"""{SYSTEM_PROMPT}

Şirket Bilgileri (Sadece bu bilgilere göre cevap verin):
{company_context}

Soru: {prompt}

Yanıt (sadece yukarıdaki şirket verilerine göre):"""
        else:
            full_prompt = f"{SYSTEM_PROMPT}\n\nSoru: {prompt}"
        
        if conversation_history:
            recent_history = conversation_history[-3:] if len(conversation_history) > 3 else conversation_history
            history_text = "\n".join([
                f"{m.get('role', 'user' if m.get('role') == 'user' else 'assistant')}: {m.get('content', '')}" 
                for m in recent_history 
                if isinstance(m, dict)
            ])
            if history_text:
                full_prompt = f"{full_prompt}\n\nÖnceki Konuşma:\n{history_text}"
        
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": full_prompt,
            "stream": False
        }
        
        response = requests.post(url, json=payload, timeout=60)  # 120->60 (daha hızlı yanıt)
        
        if response.status_code != 200:
            error_msg = response.text if hasattr(response, 'text') else "Unknown error"
            return f"Ollama hatası: Ollama sunucusunun çalıştığından emin olun.\n\nKurulum:\n1. https://ollama.ai adresinden Ollama'yı indirin\n2. Model indirin: ollama pull {OLLAMA_MODEL}\n3. Ollama'yı başlatın: ollama serve\n\nDetaylar için KURULUM_OLLAMA.md dosyasına bakın."
        
        data = response.json()
        response_text = data.get("response", "Response not available").strip()
        
        if not response_text or response_text == "Response not available":
            return "Ollama yanıt üretemedi. Model indirildiğinden emin olun (ollama pull " + OLLAMA_MODEL + ")"
        
        return response_text
        
    except requests.exceptions.ConnectionError:
        return f"Ollama'ya bağlanılamadı. Ollama sunucusunun çalıştığından emin olun ({OLLAMA_BASE_URL}).\n\nKurulum:\n1. https://ollama.ai adresinden Ollama'yı indirin\n2. PowerShell'de: ollama pull {OLLAMA_MODEL}\n3. Ollama'yı başlatın: ollama serve\n\nDetaylar: KURULUM_OLLAMA.md"
    except Exception as e:
        print(f"Ollama hatası: {e}")
        return f"Ollama hatası: {str(e)}\n\nOllama kurulumu için KURULUM_OLLAMA.md dosyasına bakın."

def ask_ollama(prompt: str, conversation_history: Optional[List] = None) -> str:
    """Backward compatibility wrapper"""
    return ask_ollama_with_rag(prompt, conversation_history, use_advanced_rag=True)

def ask_huggingface_with_rag(prompt: str, use_advanced_rag: bool = True) -> str:
    """
    Hugging Face Inference API with Advanced RAG
    
    Args:
        prompt: User query
        use_advanced_rag: Use advanced RAG
        
    Returns:
        Hugging Face model generated response with company context
    """
    try:
        # RAG context al
        company_context = ""
        try:
            vector_store, embeddings = get_vector_store()
            if vector_store:
                if use_advanced_rag:
                    try:
                        from rag_service import get_rag_service
                        rag_service = get_rag_service(vector_store, embeddings)
                        company_context = rag_service.retrieve_context(prompt, k=3, use_hybrid=False)
                    except:
                        docs = vector_store.similarity_search(prompt, k=3)
                        if docs:
                            from rag_service import AdvancedRAGService
                            rag_temp = AdvancedRAGService(vector_store, embeddings)
                            company_context = rag_temp.format_context_for_ai(docs, prompt)
                else:
                    docs = vector_store.similarity_search(prompt, k=5)
                    if docs:
                        from rag_service import AdvancedRAGService
                        rag_temp = AdvancedRAGService(vector_store, embeddings)
                        company_context = rag_temp.format_context_for_ai(docs, prompt)
        except Exception as e:
            print(f"RAG context alınamadı (devam ediliyor): {e}")
        
        url = f"https://api-inference.huggingface.co/models/{HUGGINGFACE_MODEL}"
        headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
        
        if company_context:
            full_prompt = f"""{SYSTEM_PROMPT}

Şirket Bilgileri:
{company_context}

Soru: {prompt}"""
        else:
            full_prompt = f"{SYSTEM_PROMPT}\n\nSoru: {prompt}"
        
        payload = {"inputs": full_prompt}

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code != 200:
            return f"Hugging Face API error: {response.status_code}"

        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            return data[0].get("generated_text", "").strip()
        elif isinstance(data, dict):
            return data.get("generated_text", "").strip()
        else:
            return str(data) if data else "Hugging Face returned empty response"
    except Exception as e:
        print(f"HuggingFace hatası: {e}")
        return f"Hugging Face response error: {e}"

def ask_huggingface(prompt: str) -> str:
    """Backward compatibility wrapper"""
    return ask_huggingface_with_rag(prompt, use_advanced_rag=True)

def ask_local_with_rag(prompt: str, use_advanced_rag: bool = True) -> str:
    """
    Local transformer model with Advanced RAG
    
    Runs completely offline. Requires model to be downloaded first.
    May be slow on CPU-only systems.
    
    Args:
        prompt: User query
        use_advanced_rag: Use advanced RAG
        
    Returns:
        Locally generated response with company context
    """
    try:
        # RAG context al
        company_context = ""
        try:
            vector_store, embeddings = get_vector_store()
            if vector_store:
                if use_advanced_rag:
                    try:
                        from rag_service import get_rag_service
                        rag_service = get_rag_service(vector_store, embeddings)
                        company_context = rag_service.retrieve_context(prompt, k=3, use_hybrid=False)
                    except:
                        docs = vector_store.similarity_search(prompt, k=3)
                        if docs:
                            from rag_service import AdvancedRAGService
                            rag_temp = AdvancedRAGService(vector_store, embeddings)
                            company_context = rag_temp.format_context_for_ai(docs, prompt)
                else:
                    docs = vector_store.similarity_search(prompt, k=5)
                    if docs:
                        from rag_service import AdvancedRAGService
                        rag_temp = AdvancedRAGService(vector_store, embeddings)
                        company_context = rag_temp.format_context_for_ai(docs, prompt)
        except Exception as e:
            print(f"RAG context alınamadı (devam ediliyor): {e}")
        
        from transformers import pipeline
        generator = pipeline("text-generation", model="dbmdz/bert-base-turkish-cased")
        
        if company_context:
            full_prompt = f"""{SYSTEM_PROMPT}

Şirket Bilgileri:
{company_context}

Soru: {prompt}"""
        else:
            full_prompt = f"{SYSTEM_PROMPT}\n\nSoru: {prompt}"
        
        output = generator(
            full_prompt,
            max_length=200,
            num_return_sequences=1
        )
        
        if not output or len(output) == 0:
            return "Local model could not generate response"
        
        text = output[0].get("generated_text", "")
        if not text:
            return "Local model returned empty response"
            
        if prompt in text:
            parts = text.split(prompt)
            if len(parts) > 1:
                text = parts[-1]
        
        return text.strip()
    except Exception as e:
        print(f"Yerel model hatası: {e}")
        return "Local model could not be run. Internet connection or API key required."

def ask_local(prompt: str) -> str:
    """Backward compatibility wrapper"""
    return ask_local_with_rag(prompt, use_advanced_rag=True)
