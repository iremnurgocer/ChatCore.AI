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

def ask_ai(prompt: str, conversation_history: Optional[List] = None) -> str:
    """
    AI sorguları için ana giriş noktası

    İstekleri yapılandırmaya göre uygun AI sağlayıcıya yönlendirir.
    Çoklu sağlayıcı desteği: OpenAI, Azure, Gemini, Ollama, Hugging Face, Local.

    Args:
        prompt: Kullanıcı sorgusu veya mesajı
        conversation_history: Context için önceki mesajların opsiyonel listesi

    Returns:
        AI tarafından üretilmiş yanıt string olarak
    """
    if not prompt or not prompt.strip():
        return "Lütfen bir soru veya metin girin."
    
    start_time = time.time()

    try:
        if AI_PROVIDER == "OPENAI":
            if not OPENAI_API_KEY:
                return "OpenAI API key not found."
            return ask_openai_langchain(prompt, conversation_history)

        elif AI_PROVIDER == "AZURE":
            if not AZURE_OPENAI_API_KEY or not AZURE_OPENAI_ENDPOINT:
                return "Azure API credentials missing."
            return ask_azure(prompt, conversation_history)
        
        elif AI_PROVIDER == "GEMINI":
            if not GEMINI_API_KEY:
                return "Gemini API key not found. Please set GEMINI_API_KEY environment variable."
            return ask_gemini(prompt, conversation_history)
        
        elif AI_PROVIDER == "OLLAMA":
            return ask_ollama(prompt, conversation_history)

        elif AI_PROVIDER == "HUGGINGFACE":
            if not HUGGINGFACE_API_KEY:
                return "Hugging Face API key missing."
            return ask_huggingface(prompt)

        elif AI_PROVIDER == "LOCAL":
            return ask_local(prompt)

        else:
            return f"Unknown AI_PROVIDER value: {AI_PROVIDER}"

    except Exception as e:
        print(f"AI servis hatası: {e}")
        return f"Hata: {str(e)}"
    finally:
        elapsed = time.time() - start_time
        print(f"Yanıt süresi: {elapsed:.2f}s")

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
        
        # Context retrieval
        docs = vector_store.similarity_search(prompt, k=3)
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

def ask_azure(prompt: str, conversation_history: Optional[List] = None) -> str:
    """
    Azure OpenAI service integration
    
    Args:
        prompt: User query
        conversation_history: Previous conversation messages
        
    Returns:
        Azure OpenAI generated response
    """
    try:
        from openai import AzureOpenAI
        
        client = AzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            api_version="2024-02-15-preview",
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
        
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
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=messages,
            temperature=0.5,
            max_tokens=400
        )

        if not response.choices or len(response.choices) == 0:
            return "Azure OpenAI returned no response"
        
        return response.choices[0].message.content.strip() if response.choices[0].message.content else ""

    except Exception as e:
        print(f"Azure OpenAI hatası: {e}")
        return f"Azure response error: {e}"

def ask_gemini(prompt: str, conversation_history: Optional[List] = None) -> str:
    """
    Google Gemini API integration (free tier available)
    RAG (Retrieval-Augmented Generation) desteği ile - şirket verilerini kullanır.
    
    Args:
        prompt: User query
        conversation_history: Previous messages for context (last 3 used)
        
    Returns:
        Gemini generated response with company data context
    """
    try:
        if not GEMINI_API_KEY or GEMINI_API_KEY == "your-gemini-api-key-here":
            return "Gemini API key bulunamadı. Lütfen backend/.env dosyasında GEMINI_API_KEY'i ayarlayın."
        
        # RAG: Vector store'dan şirket verilerini çek
        company_context = ""
        try:
            vector_store, embeddings = get_vector_store()
            if vector_store is not None:
                # Benzer dökümanları bul (en fazla 5)
                docs = vector_store.similarity_search(prompt, k=5)
                if docs:
                    # JSON formatındaki verileri okuyucu için düzenle
                    context_parts = []
                    for doc in docs:
                        try:
                            # JSON'ı parse et ve okunabilir formata çevir
                            import json
                            data = json.loads(doc.page_content)
                            doc_type = doc.metadata.get("type", "data")
                            
                            # Tipine göre formatla
                            if doc_type == "employees":
                                context_parts.append(
                                    f"Çalışan: {data.get('name', 'N/A')} - "
                                    f"Departman: {data.get('department', 'N/A')}, "
                                    f"Pozisyon: {data.get('position', 'N/A')}, "
                                    f"Lokasyon: {data.get('location', 'N/A')}, "
                                    f"Projeler: {', '.join(data.get('projects', []))}"
                                )
                            elif doc_type == "projects":
                                context_parts.append(
                                    f"Proje: {data.get('name', 'N/A')} - "
                                    f"Durum: {data.get('status', 'N/A')}, "
                                    f"Departman: {data.get('department', 'N/A')}, "
                                    f"Yönetici: {data.get('project_manager', 'N/A')}, "
                                    f"Lokasyon: {data.get('location', 'N/A')}, "
                                    f"Bütçe: {data.get('budget', 'N/A')}"
                                )
                            elif doc_type == "departments":
                                context_parts.append(
                                    f"Departman: {data.get('name', 'N/A')} - "
                                    f"Direktör: {data.get('director', 'N/A')}, "
                                    f"Çalışan Sayısı: {data.get('employee_count', 'N/A')}, "
                                    f"Bütçe: {data.get('budget_2024', 'N/A')}, "
                                    f"Lokasyon: {data.get('location', 'N/A')}"
                                )
                            else:
                                # Genel format
                                context_parts.append(doc.page_content)
                        except Exception:
                            # JSON parse edilemezse ham içeriği kullan
                            context_parts.append(doc.page_content[:200])
                    
                    if context_parts:
                        company_context = "\n\n".join(context_parts)
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

def ask_ollama(prompt: str, conversation_history: Optional[List] = None) -> str:
    """
    Ollama local model integration (free, runs offline)
    
    Requires Ollama server to be running locally. Ideal for privacy-sensitive deployments.
    
    Args:
        prompt: User query
        conversation_history: Not currently used for Ollama
        
    Returns:
        Ollama model generated response
    """
    try:
        url = f"{OLLAMA_BASE_URL}/api/generate"
        
        full_prompt = f"{SYSTEM_PROMPT}\n\nUser Question: {prompt}"
        
        if conversation_history:
            recent_history = conversation_history[-3:] if len(conversation_history) > 3 else conversation_history
            history_text = "\n".join([
                f"{m.get('role', 'user' if m.get('role') == 'user' else 'assistant')}: {m.get('content', '')}" 
                for m in recent_history 
                if isinstance(m, dict)
            ])
            if history_text:
                full_prompt = f"{full_prompt}\n\nPrevious Conversation:\n{history_text}"
        
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": full_prompt,
            "stream": False
        }
        
        response = requests.post(url, json=payload, timeout=120)  # Ollama yavaş olabilir
        
        if response.status_code != 200:
            error_msg = response.text if hasattr(response, 'text') else "Unknown error"
            return f"Ollama hatası: Ollama sunucusunun çalıştığından emin olun.\n\nKurulum:\n1. https://ollama.ai adresinden Ollama'yı indirin\n2. Model indirin: ollama pull {OLLAMA_MODEL}\n3. Ollama'yı başlatın: ollama serve\n\nDetaylar için OLLAMA_KURULUM.md dosyasına bakın."
        
        data = response.json()
        response_text = data.get("response", "Response not available").strip()
        
        if not response_text or response_text == "Response not available":
            return "Ollama yanıt üretemedi. Model indirildiğinden emin olun (ollama pull " + OLLAMA_MODEL + ")"
        
        return response_text
        
    except requests.exceptions.ConnectionError:
        return f"Ollama'ya bağlanılamadı. Ollama sunucusunun çalıştığından emin olun ({OLLAMA_BASE_URL}).\n\nKurulum:\n1. https://ollama.ai adresinden Ollama'yı indirin\n2. PowerShell'de: ollama pull {OLLAMA_MODEL}\n3. Ollama'yı başlatın: ollama serve\n\nDetaylar: OLLAMA_KURULUM.md"
    except Exception as e:
        print(f"Ollama hatası: {e}")
        return f"Ollama hatası: {str(e)}\n\nOllama kurulumu için OLLAMA_KURULUM.md dosyasına bakın."

def ask_huggingface(prompt: str) -> str:
    """
    Hugging Face Inference API integration
    
    Args:
        prompt: User query
        
    Returns:
        Hugging Face model generated response
    """
    try:
        url = f"https://api-inference.huggingface.co/models/{HUGGINGFACE_MODEL}"
        headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
        payload = {"inputs": f"{SYSTEM_PROMPT}\n\nQuestion: {prompt}"}

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

def ask_local(prompt: str) -> str:
    """
    Local transformer model using Hugging Face transformers library
    
    Runs completely offline. Requires model to be downloaded first.
    May be slow on CPU-only systems.
    
    Args:
        prompt: User query
        
    Returns:
        Locally generated response
    """
    try:
        from transformers import pipeline
        generator = pipeline("text-generation", model="dbmdz/bert-base-turkish-cased")
        output = generator(
            f"{SYSTEM_PROMPT}\n\nQuestion: {prompt}",
            max_length=150,
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
