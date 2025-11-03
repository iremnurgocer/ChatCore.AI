# ChatCore.AI - Kurumsal AI Chat Sistemi

**Şirket içi bilgilere dayalı AI destekli sohbet platformu. Çalışanlar, projeler, departmanlar ve prosedürler hakkında anlık ve doğru yanıtlar.**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32.0+-red.svg)](https://streamlit.io)
[![AI](https://img.shields.io/badge/AI-Enabled-orange.svg)](https://github.com/langchain-ai/langchain)

## Neden ChatCore.AI?

**Kurumsal verilerinizi AI ile güçlendirin!** ChatCore.AI, şirket içi bilgilere 7/24 erişim sağlayan, RAG (Retrieval-Augmented Generation) teknolojisi destekli profesyonel bir chat sistemidir. Çalışanlar, projeler, departmanlar ve prosedürler hakkında anlık ve doğru yanıtlar alın.

### Ana Avantajlar

- **Hızlı Kurulum**: 2 komut ile çalışır hale gelin (`kurulum.bat` → `baslat.bat`)
- **Çoklu AI Desteği**: Gemini, OpenAI, Azure, Ollama - hangisini isterseniz
- **Ücretsiz Kullanım**: Gemini ücretsiz katmanı veya tamamen yerel Ollama
- **Güvenli**: JWT authentication, input validation, rate limiting
- **RAG Teknolojisi**: Şirket verilerinize dayalı %100 doğru yanıtlar
- **Otomatik Fallback**: AI provider çalışmazsa otomatik yedek devreye girer
- **Kalıcı Oturum**: Sayfa yenileme sonrası sohbet geçmişiniz korunur
- **Ölçeklenebilir**: Küçük şirketlerden büyük holdinglere kadar

### ✨ Ne Kadar Hızlı?

| İşlem | Süre |
|-------|------|
| Kurulum | ~2 dakika |
| İlk Chat | <3 saniye |
| Cache'den Yanıt | <100ms |
| Sayfa Yükleme | <1 saniye |

## 📋 İçindekiler

- [Proje Hakkında](#proje-hakkında)
- [Özellikler](#özellikler)
- [Proje Yapısı ve Dosyalar](#proje-yapısı-ve-dosyalar)
- [Hızlı Kurulum](#hızlı-kurulum)
- [Manuel Kurulum](#manuel-kurulum)
- [Yapılandırma](#yapılandırma)
- [Kullanım](#kullanım)
- [AI Sağlayıcıları](#ai-sağlayıcıları)
- [API Dokümantasyonu](#api-dokümantasyonu)
- [Sorun Giderme](#sorun-giderme)

## 🎯 Proje Hakkında

ChatCore.AI, şirket içi bilgileri kullanarak soruları yanıtlayan, **RAG (Retrieval-Augmented Generation)** teknolojisi destekli bir AI chat sistemidir. Sistem, çalışanlar, projeler, departmanlar ve prosedürler hakkındaki soruları yanıtlayabilir ve kurumsal uygulamalara entegre edilebilir.

### 🎯 Neden Bu Projeyi Yapmalısınız?

**Önce Sorun:**
- Çalışanlar şirket bilgilerine erişemiyor
- HR departmanı her soruyu tekrar cevaplıyor
- Proje durumları hakkında güncel bilgi yok
- Yeni prosedürleri kimse okumuyor
- Bilgi aramak çok zaman alıyor

**Sonra Çözüm:**
- ✅ 7/24 çalışan AI asistan
- ✅ Anında doğru yanıtlar
- ✅ Güncel prosedür bildirimleri
- ✅ Sohbet geçmişi saklama
- ✅ Çoklu AI provider desteği

### ✨ Temel Özellikler

- 🧠 **RAG Teknolojisi**: Şirket verilerinize dayalı %100 doğru yanıtlar
- 🔐 **Güvenlik**: JWT authentication, input validation, rate limiting
- 💾 **Session Management**: TinyDB ile kalıcı oturum ve sohbet geçmişi
- 📢 **Prosedür Takibi**: Yeni prosedür bildirimleri ve görüntülenme takibi
- 🔄 **Otomatik Fallback**: AI provider çalışmazsa otomatik yedek
- ⚡ **Cache Sistemi**: Çok hızlı tekrarlayan yanıtlar
- 🎯 **Multi-Query**: Gelişmiş arama algoritmaları
- 📊 **Analytics**: Kullanım istatistikleri ve loglar
- 🌍 **API First**: RESTful yapı, kolay entegrasyon
- 🏢 **Ölçeklenebilir**: Küçük şirketlerden büyük holdinglere

### Teknoloji Stack

Bu proje modern, ölçeklenebilir ve esnek bir teknoloji stack'i kullanmaktadır. Her teknoloji özellikle performans, güvenlik ve geliştirme kolaylığı için seçilmiştir.

#### 🖥️ Backend Framework

**FastAPI (v0.109.0)**
- **Neden Tercih Edildi:**
  - Yüksek performans (Node.js ve Go ile karşılaştırılabilir)
  - Otomatik API dokümantasyonu (Swagger UI, ReDoc)
  - Python type hints ile güçlü tip kontrolü
  - Async/await desteği ile modern asenkron programlama
  - Kolay entegrasyon ve genişletilebilirlik
- **Nasıl Genişletilir:**
  - WebSocket desteği eklenebilir (real-time chat için)
  - Celery ile background job processing eklenebilir
  - FastAPI-Plugins ile ek özellikler eklenebilir
- **Nasıl Daraltılır:**
  - Flask'e geçiş yapılabilir (daha hafif, ancak özellikler azalır)
  - Minimal FastAPI kullanımı (sadece temel endpoint'ler)

**Uvicorn (v0.27.0)**
- **Neden Tercih Edildi:**
  - FastAPI için önerilen ASGI server
  - Yüksek performans ve düşük gecikme
  - Hot reload desteği (development için)
  - Production-ready (workers, SSL desteği)
- **Nasıl Genişletilir:**
  - Gunicorn + Uvicorn workers (production scaling)
  - Nginx reverse proxy eklenebilir
- **Nasıl Daraltılır:**
  - Tek worker mode (development için yeterli)

#### 🤖 AI & Machine Learning

**LangChain (v0.2.0+)**
- **Neden Tercih Edildi:**
  - RAG (Retrieval-Augmented Generation) için en iyi framework
  - Çoklu AI sağlayıcı desteği (OpenAI, Azure, Ollama, vb.)
  - Vector store entegrasyonu (FAISS, Pinecone, ChromaDB)
  - Prompt engineering araçları
  - Document loaders ve text splitters
  - Zengin ekosistem ve aktif topluluk
- **Nasıl Genişletilir:**
  - LangGraph ile multi-agent sistemleri
  - LangSmith ile monitoring ve tracing
  - Özel chains ve tools eklenebilir
  - Memory management iyileştirilebilir
- **Nasıl Daraltılır:**
  - LangChain olmadan direkt AI API çağrıları (daha az özellik)
  - Minimal LangChain kullanımı (sadece vector store)

**FAISS (Facebook AI Similarity Search)**
- **Neden Tercih Edildi:**
  - Facebook tarafından geliştirilen yüksek performanslı vector database
  - Milyonlarca vektör için hızlı similarity search
  - CPU ve GPU desteği
  - Memory-efficient
  - RAG sistemleri için industry standard
- **Nasıl Genişletilir:**
  - FAISS-GPU kullanılabilir (daha hızlı)
  - Pinecone, Weaviate, Qdrant gibi cloud vector DB'lere geçilebilir
  - ChromaDB ile persistent storage eklenebilir
- **Nasıl Daraltılır:**
  - Basit cosine similarity (küçük veri setleri için)
  - In-memory dictionary tabanlı arama

**Sentence Transformers**
- **Neden Tercih Edildi:**
  - Ücretsiz embedding modeli (OpenAI embeddings'e alternatif)
  - Çok dilli model desteği (Türkçe dahil)
  - Yerel çalışma (privacy-first)
  - Kolay model değiştirme
- **Nasıl Genişletilir:**
  - Daha büyük modeller (paraphrase-multilingual-mpnet-base-v2)
  - Fine-tuning ile özelleştirilmiş modeller
  - Domain-specific embeddings
- **Nasıl Daraltılır:**
  - OpenAI embeddings'e geçilebilir (daha küçük kod, ücretli)
  - Basit TF-IDF embeddings

#### 💾 Veritabanı & Storage

**TinyDB (v4.8.0+)**
- **Neden Tercih Edildi:**
  - Hafif ve kolay kullanım (yalnızca Python)
  - JSON tabanlı, kurulum gerektirmez
  - Session ve chat history için yeterli
  - Hızlı development ve testing
  - Dosya tabanlı, backup kolaylığı
- **Nasıl Genişletilir:**
  - PostgreSQL veya MongoDB'ye geçilebilir (production için)
  - Redis cache layer eklenebilir
  - Elasticsearch ile arama özelliği
  - S3/MinIO ile object storage
- **Nasıl Daraltılır:**
  - In-memory dictionary (session için, restart'ta kaybolur)
  - SQLite (daha hafif, SQL desteği)

**JSON Files (Data Storage)**
- **Neden Tercih Edildi:**
  - Kolay edit ve version control (Git ile)
  - Hiçbir veritabanı kurulumu gerektirmez
  - İnsan tarafından okunabilir format
  - Hızlı development
- **Nasıl Genişletilir:**
  - PostgreSQL/MySQL'e migrate edilebilir
  - CSV import/export eklenebilir
  - Excel entegrasyonu
  - API'den veri çekme (real-time data)
- **Nasıl Daraltılır:**
  - Hard-coded Python dictionaries (çok küçük veriler için)

#### 🔐 Güvenlik & Authentication

**PyJWT (v2.8.0)**
- **Neden Tercih Edildi:**
  - JWT (JSON Web Token) standard implementasyonu
  - Stateless authentication (scalable)
  - Token expiration ve refresh desteği
  - Industry standard güvenlik
- **Nasıl Genişletilir:**
  - OAuth2 entegrasyonu (Google, Microsoft, GitHub)
  - Refresh token mekanizması
  - Multi-factor authentication (MFA)
  - SSO (Single Sign-On) desteği
- **Nasıl Daraltılır:**
  - Session-based auth (Flask-Session)
  - Basic HTTP authentication

**Python-JOSE**
- **Neden Tercih Edildi:**
  - JWT + JWE (JSON Web Encryption) desteği
  - Cryptographic operations
  - Token validation ve verification
- **Nasıl Genişletilir:**
  - RSA key pairs ile token signing
  - Certificate-based authentication
- **Nasıl Daraltılır:**
  - Sadece PyJWT kullanılabilir

**Rate Limiting (Custom Implementation)**
- **Neden Tercih Edildi:**
  - In-memory, kurulum gerektirmez
  - Basit ve anlaşılır
  - Development için yeterli
- **Nasıl Genişletilir:**
  - Redis-based rate limiting (distributed)
  - Advanced rate limiting algorithms (Token Bucket, Sliding Window)
  - IP-based, user-based limitler
  - Rate limiting per endpoint
- **Nasıl Daraltılır:**
  - Rate limiting kaldırılabilir (internal use için)

#### 🌐 HTTP & API

**Requests (v2.31.0)**
- **Neden Tercih Edildi:**
  - Python'da en yaygın HTTP library
  - Kolay kullanım ve geniş destek
  - SSL/TLS desteği
  - Session management
- **Nasıl Genişletilir:**
  - httpx (async HTTP client) eklenebilir
  - Connection pooling
  - Retry mechanisms
- **Nasıl Daraltılır:**
  - urllib (Python built-in, daha az özellik)

**Pydantic (v2.9.0+)**
- **Neden Tercih Edildi:**
  - FastAPI ile native entegrasyon
  - Otomatik veri doğrulama
  - Type safety
  - JSON serialization/deserialization
  - Performance (Rust ile yazılmış core)
- **Nasıl Genişletilir:**
  - Pydantic Settings (environment yönetimi)
  - Custom validators
  - Async validation
- **Nasıl Daraltılır:**
  - Dataclasses (daha basit, daha az özellik)

#### 🎨 Frontend

**Streamlit (v1.32.0+)**
- **Neden Tercih Edildi:**
  - Hızlı prototype ve development
  - Python-only (backend geliştiriciler için kolay)
  - Built-in widgets ve components
  - Otomatik state management
  - Hot reload
  - Deploy kolaylığı (Streamlit Cloud)
- **Nasıl Genişletilir:**
  - React/Vue.js frontend eklenebilir (daha özelleştirilebilir)
  - Streamlit Components ile custom widgets
  - Multi-page apps (Streamlit pages)
  - Custom CSS/JavaScript injection
- **Nasıl Daraltılır:**
  - Minimal Streamlit UI (sadece chat interface)
  - REST API only (frontend yok)

#### 🔧 Utilities

**Python-dotenv (v1.0.0)**
- **Neden Tercih Edildi:**
  - Environment variable yönetimi
  - .env dosyası desteği
  - Production/development ayarları
- **Nasıl Genişletilir:**
  - Pydantic Settings ile birleştirilebilir
  - Kubernetes ConfigMaps/Secrets
  - HashiCorp Vault entegrasyonu
- **Nasıl Daraltılır:**
  - Direkt os.getenv() kullanımı

**python-multipart**
- **Neden Tercih Edildi:**
  - FastAPI file upload için gerekli
  - Form data processing
- **Nasıl Genişletilir:**
  - File validation ve processing
  - Image processing (Pillow)
- **Nasıl Daraltılır:**
  - File upload özelliği kaldırılabilir

#### 🤖 AI Sağlayıcılar

**Google Gemini**
- **Neden Tercih Edildi:**
  - Ücretsiz katman mevcut
  - Azure/OpenAI benzeri kalite
  - Kolay entegrasyon (sadece API key)
  - Türkçe dil desteği
  - REST API (stabil)
- **Nasıl Genişletilir:**
  - Gemini Pro modelleri (daha güçlü)
  - Multimodal input (resim, video)
  - Function calling
- **Nasıl Daraltılır:**
  - Gemini kullanımı kaldırılabilir (diğer sağlayıcılar var)

**OpenAI**
- **Neden Tercih Edildi:**
  - En gelişmiş modeller (GPT-4, GPT-3.5)
  - En hızlı yanıt süreleri
  - En iyi RAG entegrasyonu
  - Industry leader
- **Nasıl Genişletilir:**
  - GPT-4 Turbo kullanımı
  - Fine-tuning
  - Assistants API
  - Vision models
- **Nasıl Daraltılır:**
  - GPT-3.5-only (daha ucuz)
  - OpenAI kaldırılabilir

**Azure OpenAI**
- **Neden Tercih Edildi:**
  - Enterprise-grade güvenlik
  - Azure entegrasyonu
  - SLA garantisi
  - Compliance (HIPAA, SOC2)
- **Nasıl Genişletilir:**
  - Private endpoints
  - Custom models
  - Azure Cognitive Services entegrasyonu
- **Nasıl Daraltılır:**
  - Azure kaldırılabilir (standalone OpenAI kullanılabilir)

**Ollama**
- **Neden Tercih Edildi:**
  - Tamamen ücretsiz
  - Yerel çalışma (privacy)
  - Internet gerektirmez
  - Sınırsız kullanım
- **Nasıl Genişletilir:**
  - Daha büyük modeller (Llama 2, Mistral)
  - GPU acceleration
  - Custom model fine-tuning
- **Nasıl Daraltılır:**
  - Ollama kurulumu kaldırılabilir (cloud-only)

#### 📊 Gelişmiş Özellikler (Yeni Eklenen)

**RAG Service (Custom)**
- **Neden Eklendi:**
  - Hybrid search (semantic + keyword)
  - Multi-query retrieval
  - Query expansion
  - Re-ranking algoritması
- **Nasıl Genişletilir:**
  - BM25 keyword search eklenebilir
  - Cross-encoder re-ranking
  - Query classification
  - Context compression (uzun context'ler için)

**AI Cache System**
- **Neden Eklendi:**
  - Benzer sorgular için hızlı yanıt
  - API cost azaltma
  - Performance iyileştirme
- **Nasıl Genişletilir:**
  - Redis cache eklenebilir (distributed)
  - Cache invalidation strategies
  - Cache warming
- **Nasıl Daraltılır:**
  - Cache devre dışı bırakılabilir

**Model Fallback System**
- **Neden Eklendi:**
  - Yüksek availability (%99+)
  - Otomatik failover
  - Kullanıcı deneyimi korunur
- **Nasıl Genişletilir:**
  - Health check mekanizması
  - Load balancing
  - Cost-based provider selection
- **Nasıl Daraltılır:**
  - Tek provider kullanımı

**Prompt Optimizer**
- **Neden Eklendi:**
  - Few-shot examples
  - Intent-based prompt selection
  - Daha iyi AI yanıtları
- **Nasıl Genişletilir:**
  - Dynamic few-shot selection
  - A/B testing
  - Prompt templates library
- **Nasıl Daraltılır:**
  - Basit prompt templates

#### 🔄 Genel Genişletme/Daraltma Stratejileri

**Genişletme Önerileri:**
1. **Microservices Mimari**: Her servis ayrı container olarak çalışabilir
2. **Message Queue**: RabbitMQ/Kafka ile async processing
3. **Monitoring**: Prometheus + Grafana
4. **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
5. **Database**: PostgreSQL + Redis cache layer
6. **CI/CD**: GitHub Actions, GitLab CI
7. **Containerization**: Docker + Kubernetes
8. **API Gateway**: Kong, Traefik

**Daraltma Önerileri:**
1. **Minimal AI**: Sadece bir AI provider
2. **No RAG**: Direkt AI çağrıları (daha basit kod)
3. **File-based Storage**: Veritabanı yok, sadece JSON
4. **Single Server**: Microservices yerine monolith
5. **No Cache**: Cache sistemini kaldır
6. **Minimal Security**: Sadece JWT, rate limiting yok

#### 📦 Teknoloji Versiyonları

```
Python: 3.8+
FastAPI: 0.109.0
Uvicorn: 0.27.0
LangChain: 0.2.0+
FAISS: 1.8.0+
Sentence-Transformers: 2.2.2+
TinyDB: 4.8.0+
Streamlit: 1.32.0+
Pydantic: 2.9.0+
PyJWT: 2.8.0
```

## ✨ Özellikler

### Temel Özellikler

- **AI Sohbet**: Çoklu AI sağlayıcı desteği ile akıllı yanıtlar
- **RAG Desteği**: Şirket içi verilerle zenginleştirilmiş yanıtlar
- **Kalıcı Session Yönetimi**: Kullanıcı bazlı konuşma geçmişi (TinyDB ile kalıcı)
- **Prosedür Takip**: Yeni prosedür bildirimleri ve görüntüleme takibi
- **Intent Analizi**: Kullanıcı sorgularının otomatik analizi
- **Analytics**: API kullanım istatistikleri ve performans takibi

### Güvenlik Özellikleri

- **JWT Kimlik Doğrulama**: Token tabanlı güvenli erişim
- **Rate Limiting**: API isteklerinde hız sınırlaması
- **Input Validation**: XSS ve SQL injection koruması
- **Güvenlik Loglama**: Kategorize edilmiş güvenlik olayları
- **CORS Yapılandırması**: Cross-origin güvenliği

## 📁 Proje Yapısı ve Dosyalar

```
ChatCore.AI/
├── backend/                      # FastAPI backend servisi
│   ├── main.py                   # Ana API uygulaması ve endpoint'ler
│   ├── ai_service.py             # AI sağlayıcı entegrasyonları (Gemini, OpenAI, Azure, Ollama)
│   ├── auth.py                   # JWT kimlik doğrulama modülü
│   ├── data_loader.py            # JSON veri dosyalarını yükleme modülü
│   ├── session_manager.py        # TinyDB ile kalıcı session ve chat geçmişi yönetimi
│   ├── logger.py                 # Kategorize edilmiş loglama sistemi
│   ├── analytics.py              # API istatistikleri ve analitik
│   ├── security.py               # Güvenlik modülleri (rate limiting, input validation)
│   ├── nlp_service.py            # Intent ve entity çıkarımı
│   ├── report_service.py         # PDF rapor oluşturma (opsiyonel)
│   ├── requirements.txt          # Python bağımlılıkları
│   ├── .env                      # Yapılandırma dosyası (API key'ler burada)
│   ├── data/                     # Şirket veri dosyaları
│   │   ├── employees.json        # Çalışan listesi
│   │   ├── departments.json     # Departman bilgileri
│   │   ├── projects.json         # Proje detayları
│   │   ├── procedures.json       # Şirket prosedürleri
│   │   └── sessions.json         # TinyDB session veritabanı (otomatik oluşur)
│   └── logs/                     # Log dosyaları (otomatik oluşur)
│       ├── api.log               # Genel API logları
│       ├── errors.log             # Hata logları
│       └── security.log           # Güvenlik olayları
│
├── frontend/                      # Streamlit frontend
│   ├── app.py                    # Ana Streamlit uygulaması
│   └── static/
│       └── styles.css            # CSS stilleri
│
├── kurulum.bat                    # Windows otomatik kurulum scripti
├── kurulum.sh                     # macOS/Linux otomatik kurulum scripti
├── baslat.bat                     # Windows servis başlatma scripti
├── baslat.sh                      # macOS/Linux servis başlatma scripti
│
├── kurulum_ollama.bat             # Ollama için özel kurulum (Windows)
├── kurulum_ollama.sh              # Ollama için özel kurulum (macOS/Linux)
├── kurulum_openai.bat             # OpenAI için özel kurulum (Windows)
├── kurulum_openai.sh              # OpenAI için özel kurulum (macOS/Linux)
├── kurulum_azure.bat              # Azure için özel kurulum (Windows)
├── kurulum_azure.sh               # Azure için özel kurulum (macOS/Linux)
│
├── KURULUM_REHBERI.md             # AI sağlayıcı seçimi rehberi
├── KURULUM_OLLAMA.md              # Ollama detaylı kurulum rehberi
├── KURULUM_OPENAI.md              # OpenAI detaylı kurulum rehberi
├── KURULUM_AZURE.md               # Azure OpenAI detaylı kurulum rehberi
│
└── README.md                      # Bu dosya
```

### Dosya Açıklamaları

#### Backend Dosyaları

**`main.py`**
- FastAPI uygulaması ana giriş noktası
- Tüm API endpoint'lerinin tanımlandığı dosya
- CORS, middleware ve hata yönetimi
- **Değiştirilecekler:** Endpoint eklemek/çıkarmak, CORS ayarları

**`ai_service.py`**
- AI sağlayıcı entegrasyonları (Gemini, OpenAI, Azure, Ollama)
- RAG (Retrieval-Augmented Generation) implementasyonu
- Şirket verilerini AI'ya sağlama mantığı
- **Değiştirilecekler:** AI model seçimi, RAG parametreleri, prompt şablonları

**`auth.py`**
- JWT token oluşturma ve doğrulama
- Login endpoint'i
- **Değiştirilecekler:** Kullanıcı doğrulama mantığı, token süresi (şu an 2 saat)

**`session_manager.py`**
- TinyDB ile kalıcı session yönetimi
- Chat geçmişi saklama
- Prosedür görüntüleme takibi
- **Değiştirilecekler:** Session timeout (şu an 7200 saniye), max history (şu an 100 mesaj)

**`data_loader.py`**
- JSON veri dosyalarını yükleme
- Veri formatı doğrulama
- **Değiştirilecekler:** Yeni veri dosyası eklemek için buraya ekleyin

**`security.py`**
- Rate limiting (60 istek/dakika)
- Input validation (XSS, SQL injection koruması)
- **Değiştirilecekler:** Rate limit değerleri, validation kuralları

**`logger.py`**
- Kategorize edilmiş loglama sistemi
- **Değiştirilecekler:** Log formatı, log dosyası konumları

**`requirements.txt`**
- Python paket bağımlılıkları
- **Değiştirilecekler:** Yeni paket eklemek için buraya ekleyin

**`backend/.env`**
- Tüm yapılandırma ayarları
- API key'ler burada saklanır
- **Değiştirilecekler:** Tüm ayarlar burada

#### Frontend Dosyaları

**`frontend/app.py`**
- Streamlit web arayüzü
- Kullanıcı girişi, chat arayüzü, prosedür bildirimleri
- **Değiştirilecekler:** UI tasarımı, yeni özellikler

#### Veri Dosyaları

**`backend/data/employees.json`**
- Çalışan listesi
- **Değiştirilecekler:** Kendi çalışan verilerinizi buraya ekleyin

**`backend/data/departments.json`**
- Departman bilgileri
- **Değiştirilecekler:** Kendi departman verilerinizi buraya ekleyin

**`backend/data/projects.json`**
- Proje detayları
- **Değiştirilecekler:** Kendi proje verilerinizi buraya ekleyin

**`backend/data/procedures.json`**
- Şirket prosedürleri
- **Değiştirilecekler:** Yeni prosedürler ekleyin, mevcutları güncelleyin

## 🚀 Hızlı Kurulum

### Otomatik Kurulum (Önerilen)

#### Windows

1. **İlk Kurulum:**
   ```batch
   kurulum.bat
   ```
   Bu script:
   - ✅ Python kontrolü yapar
   - ✅ Virtual environment oluşturur
   - ✅ Tüm bağımlılıkları yükler
   - ✅ `.env` dosyası oluşturur (API key boş, siz ekleyeceksiniz)
   - ✅ Her şeyi hazırlar

2. **API Key Ekleme:**
   - Script bittikten sonra `backend\.env` dosyasını açın
   - `GEMINI_API_KEY=your-gemini-api-key-here` satırını bulun
   - `your-gemini-api-key-here` yerine API anahtarınızı yapıştırın
   - Dosyayı kaydedin
   - API Key almak için: https://makersuite.google.com/app/apikey

3. **Servisleri Başlatma:**
   ```batch
   baslat.bat
   ```
   - Backend ve Frontend otomatik başlar
   - ⚠️ **ÖNEMLİ:** Backend'in tamamen hazır olması için 5-10 saniye bekleyin
   - Backend hazır olduğunda terminalde "Uvicorn running on http://0.0.0.0:8000" mesajını göreceksiniz
   - Frontend otomatik olarak backend hazır olduktan sonra başlatılır
   - Tarayıcıda: http://localhost:8501
   - Giriş: `admin` / `1234`

#### macOS / Linux

1. **İlk Kurulum:**
   ```bash
   chmod +x kurulum.sh
   ./kurulum.sh
   ```

2. **API Key Ekleme:**
   - `backend/.env` dosyasını açın
   - `GEMINI_API_KEY=your-gemini-api-key-here` satırını düzenleyin

3. **Servisleri Başlatma:**
   ```bash
   chmod +x baslat.sh
   ./baslat.sh
   ```
   - ⚠️ **ÖNEMLİ:** Backend'in tamamen hazır olması için 5-10 saniye bekleyin
   - Backend hazır olduğunda terminalde "Uvicorn running on http://0.0.0.0:8000" mesajını göreceksiniz
   - Frontend otomatik olarak backend hazır olduktan sonra başlatılır

### Günlük Kullanım

İlk kurulumdan sonra sadece:
```batch
baslat.bat    # Windows
# veya
./baslat.sh   # macOS/Linux
```

**Başlatma Sırası ve Bekleme Süreleri:**
1. Backend başlatılır → **5-10 saniye** bekleyin
2. Backend hazır olunca "Uvicorn running..." mesajını görürsünüz
3. Frontend otomatik başlatılır → **3-5 saniye** daha
4. Toplam başlatma süresi: **~10-15 saniye**

⚠️ **Not:** İlk başlatmada biraz daha uzun sürebilir (Python modülleri yüklenirken). Sonraki başlatmalarda daha hızlı olur.

## 📖 Manuel Kurulum

Script kullanmak istemiyorsanız, aşağıdaki adımları manuel olarak takip edebilirsiniz.

### 1. Gereksinimler

- Python 3.8 veya üzeri
- pip (Python paket yöneticisi)
- Git (projeyi klonlamak için)

### 2. Repository'yi Klonlayın

```bash
git clone <repository-url>
cd ChatCore.AI
```

### 3. Backend Kurulumu

#### Virtual Environment Oluşturma

**Windows:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

#### Bağımlılıkları Yükleme

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Environment Dosyası Oluşturma

`backend/.env` dosyası oluşturun:

```env
# AI Sağlayıcı (GEMINI, OPENAI, AZURE, OLLAMA, HUGGINGFACE)
AI_PROVIDER=GEMINI

# Google Gemini (Ücretsiz katman - Önerilen)
GEMINI_API_KEY=your-gemini-api-key-here

# OpenAI (Opsiyonel - Ücretli)
OPENAI_API_KEY=your-openai-key-here

# Azure OpenAI (Opsiyonel - Ücretli)
AZURE_OPENAI_API_KEY=your-azure-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini

# Ollama (Opsiyonel - Yerel, Ücretsiz)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# JWT Secret Key (Production'da değiştirin!)
SECRET_KEY=supersecret

# Şirket Adı
COMPANY_NAME=Company1

# Backend URL
BACKEND_URL=http://127.0.0.1:8000

# CORS Origins
ALLOWED_ORIGINS=*
```

#### Backend'i Başlatma

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

⚠️ **ÖNEMLİ:** Backend'in tamamen başlaması için 5-10 saniye bekleyin. Terminalde şu mesajları görmelisiniz:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [...]
INFO:     Started server process [...]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

Backend hazır olduktan sonra frontend'i başlatın.

### 4. Frontend Kurulumu

**ÖNEMLİ:** Backend'in tamamen başlamış ve hazır olduğundan emin olun. Backend terminalinde "Application startup complete" mesajını gördükten sonra frontend'i başlatın.

**Yeni bir terminal penceresi açın:**

```bash
cd frontend
# Backend'deki venv'i kullan (veya kendi venv'inizi oluşturun)
# Windows: ..\backend\venv\Scripts\activate
# macOS/Linux: source ../backend/venv/bin/activate
streamlit run app.py
```

**Frontend başlatma süresi:**
- Frontend başlaması genellikle 3-5 saniye sürer
- Backend'e bağlanmak için ek 2-3 saniye gerekebilir
- Toplam: İlk başlatma için yaklaşık 10-15 saniye bekleyin

Frontend: http://localhost:8501

### 5. Veri Dosyalarını Düzenleme

Kendi şirket verilerinizi eklemek için:

1. `backend/data/employees.json` - Çalışan listesi
2. `backend/data/departments.json` - Departman bilgileri
3. `backend/data/projects.json` - Proje detayları
4. `backend/data/procedures.json` - Şirket prosedürleri

Dosyaları açın, JSON formatında verilerinizi ekleyin.

## ⚙️ Yapılandırma

### Environment Değişkenleri

`backend/.env` dosyasında yapılandırılabilir değişkenler:

| Değişken | Açıklama | Varsayılan | Nerede Değiştirilir |
|----------|----------|------------|-------------------|
| `AI_PROVIDER` | AI sağlayıcı seçimi (GEMINI, OPENAI, AZURE, OLLAMA) | GEMINI | `backend/.env` |
| `GEMINI_API_KEY` | Google Gemini API anahtarı | - | `backend/.env` |
| `OPENAI_API_KEY` | OpenAI API anahtarı | - | `backend/.env` |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API anahtarı | - | `backend/.env` |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint URL'i | - | `backend/.env` |
| `AZURE_OPENAI_DEPLOYMENT` | Azure OpenAI deployment adı | gpt-4o-mini | `backend/.env` |
| `OLLAMA_BASE_URL` | Ollama sunucu adresi | http://localhost:11434 | `backend/.env` |
| `OLLAMA_MODEL` | Ollama model adı | llama3.2 | `backend/.env` |
| `SECRET_KEY` | JWT imzalama için gizli anahtar | supersecret | `backend/.env` |
| `COMPANY_NAME` | Şirket adı | Company1 | `backend/.env` |
| `BACKEND_URL` | Backend API URL'i | http://127.0.0.1:8000 | `backend/.env`, `frontend/app.py` |
| `ALLOWED_ORIGINS` | CORS izin verilen origin'ler | * | `backend/.env` |

### Veri Dosyaları Yapılandırması

**Çalışan Ekleme** (`backend/data/employees.json`):
```json
[
  {
    "id": 1,
    "name": "Ahmet Yılmaz",
    "department": "Technology",
    "role": "Senior Developer",
    "email": "ahmet@company.com"
  }
]
```

**Departman Ekleme** (`backend/data/departments.json`):
```json
[
  {
    "id": 1,
    "name": "Technology",
    "code": "TECH",
    "director": "Ahmet Yılmaz",
    "budget_2024": "50000000"
  }
]
```

**Proje Ekleme** (`backend/data/projects.json`):
```json
[
  {
    "id": 1,
    "name": "Yeni Sistem Geliştirme",
    "department": "Technology",
    "status": "Active",
    "budget": "1000000"
  }
]
```

**Prosedür Ekleme** (`backend/data/procedures.json`):
```json
[
  {
    "id": 1,
    "title": "Yeni Prosedür",
    "code": "HR-2024-001",
    "department": "Genel",
    "published_date": "2024-01-15T10:00:00",
    "status": "Aktif",
    "content": "Prosedür içeriği..."
  }
]
```

### Güvenlik Ayarları

**Rate Limiting** (`backend/security.py`):
- Varsayılan: 60 istek/dakika
- Login: 10 istek/dakika
- Değiştirmek için: `backend/security.py` dosyasını düzenleyin

**JWT Token Süresi** (`backend/auth.py`):
- Varsayılan: 2 saat
- Değiştirmek için: `backend/auth.py` dosyasında `datetime.timedelta(hours=2)` satırını düzenleyin

**Session Timeout** (`backend/session_manager.py`):
- Varsayılan: 7200 saniye (2 saat)
- Değiştirmek için: `backend/session_manager.py` dosyasında `session_timeout` parametresini düzenleyin

## 🎮 Kullanım

### Web Arayüzü

1. Backend ve frontend servislerini başlatın
2. Tarayıcıda `http://localhost:8501` adresine gidin
3. Varsayılan kimlik bilgileriyle giriş yapın:
   - **Kullanıcı adı:** `admin`
   - **Şifre:** `1234`
4. Chat arayüzünde sorularınızı sorun

### Örnek Sorular

- "Enerji departmanında kimler çalışıyor?"
- "Hangi projeler devam ediyor?"
- "Ahmet Yılmaz'ın projeleri neler?"
- "Yeni prosedürler var mı?"
- "Turizm departmanının bütçesi nedir?"

### API Kullanımı

#### 1. Giriş Yapma

```bash
curl -X POST "http://localhost:8000/api/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "1234"}'
```

Yanıt:
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "expires_in": 7200
}
```

#### 2. Chat Sorgusu

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Enerji departmanında kimler çalışıyor?"}'
```

#### 3. Prosedürler

```bash
# Yeni prosedürleri getir
curl -X GET "http://localhost:8000/api/procedures/new" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Tüm prosedürleri getir
curl -X GET "http://localhost:8000/api/procedures" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🤖 AI Sağlayıcıları

### Google Gemini (Önerilen - Ücretsiz)

✅ **Avantajlar:**
- Ücretsiz katman mevcut
- Azure/OpenAI benzeri bulut servisi
- Sadece API key gerekli, kurulum yok
- Yüksek kaliteli yanıtlar

📝 **Kurulum:**
1. https://makersuite.google.com/app/apikey adresinden API key alın
2. `backend/.env` dosyasında `GEMINI_API_KEY` ekleyin
3. `AI_PROVIDER=GEMINI` ayarlayın

**Detaylı Rehber:** `KURULUM_REHBERI.md`

### OpenAI (Ücretli - En İyi Kalite)

✅ **Avantajlar:**
- En gelişmiş AI modelleri
- Çok hızlı yanıt
- RAG desteği ile FAISS entegrasyonu

📝 **Kurulum:**
```batch
# Windows
kurulum_openai.bat

# macOS/Linux
./kurulum_openai.sh
```

**Detaylı Rehber:** `KURULUM_OPENAI.md`

### Azure OpenAI (Ücretli - Kurumsal)

✅ **Avantajlar:**
- Enterprise seviye güvenlik
- Azure üzerinden yönetim
- OpenAI modellerine erişim

📝 **Kurulum:**
```batch
# Windows
kurulum_azure.bat

# macOS/Linux
./kurulum_azure.sh
```

**Detaylı Rehber:** `KURULUM_AZURE.md`

### Ollama (Yerel - Ücretsiz)

✅ **Avantajlar:**
- Tamamen ücretsiz, sınırsız
- Yerel çalışma (internet gerektirmez)
- Gizlilik odaklı

📝 **Kurulum:**
```batch
# Windows
kurulum_ollama.bat

# macOS/Linux
./kurulum_ollama.sh
```

**Detaylı Rehber:** `KURULUM_OLLAMA.md`

## 📚 API Dokümantasyonu

### Endpoint'ler

#### Kimlik Doğrulama
- `POST /api/login` - Kullanıcı girişi, JWT token döndürür

#### Chat Endpoint'leri
- `POST /api/chat` - AI sohbet endpoint'i
- `POST /api/ask` - RAG pipeline ile intent analizli sorgu

#### Veri Endpoint'leri
- `GET /api/employees` - Çalışan listesi
- `GET /api/departments` - Departman listesi
- `GET /api/projects` - Proje listesi
- `GET /api/procedures` - Tüm prosedürler
- `GET /api/procedures/new` - Yeni prosedürler (görüntülenmemiş)

#### Session Yönetimi
- `GET /api/sessions/{session_id}` - Session bilgilerini getir
- `DELETE /api/sessions/{session_id}` - Session'ı temizle

#### İstatistikler
- `GET /api/stats` - Analytics ve istatistikler
- `GET /api/status` - Sistem durumu

### API Dokümantasyonu

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 Sorun Giderme

### Kurulum Sorunları

**"Python bulunamadı" Hatası:**
- Python 3.8+ kurulu olduğundan emin olun
- PATH'e eklendiğini kontrol edin: `python --version`
- Kurulum sırasında "Add Python to PATH" seçeneğini işaretleyin

**"Virtual environment oluşturulamadı" Hatası:**
- `backend\venv` klasörünü silin ve tekrar deneyin
- Script'i yönetici olarak çalıştırın

**"Bağımlılıklar yüklenemedi" Hatası:**
- İnternet bağlantınızı kontrol edin
- Pip'i güncelleyin: `python -m pip install --upgrade pip`
- Virtual environment'ı aktif edin ve tekrar deneyin

### Çalıştırma Sorunları

**"Backend başlamıyor" Hatası:**
- `backend/.env` dosyasının var olduğundan emin olun
- API key'in doğru olduğunu kontrol edin
- Backend loglarını kontrol edin: `backend/logs/errors.log`
- Manuel başlatın ve hata mesajını okuyun:
  ```bash
  cd backend
  venv\Scripts\activate
  python -m uvicorn main:app --reload
  ```

**"Frontend başlamıyor" Hatası:**
- Streamlit'in yüklü olduğunu kontrol edin: `pip list | findstr streamlit`
- Backend'in çalıştığını kontrol edin: http://localhost:8000/api/status
- Manuel başlatın:
  ```bash
  cd frontend
  streamlit run app.py
  ```

**"Port zaten kullanılıyor" Hatası:**
- Çalışan eski servisleri durdurun
- Farklı port kullanın veya port'u kullanan uygulamayı bulun:
  ```bash
  netstat -ano | findstr :8000
  netstat -ano | findstr :8501
  ```

**"AI yanıt vermiyor" Hatası:**
- API key'in doğru olduğunu kontrol edin
- `AI_PROVIDER` değerinin doğru olduğunu kontrol edin
- Backend loglarını kontrol edin: `backend/logs/api.log`

### Veri Sorunları

**"Veri bulunamadı" Hatası:**
- `backend/data/` dizinindeki JSON dosyalarının var olduğundan emin olun
- JSON formatının doğru olduğunu kontrol edin
- Dosya kodlamasının UTF-8 olduğundan emin olun

## 📝 Notlar

- **Production Kullanımı**: Production ortamında mutlaka `SECRET_KEY`'i değiştirin
- **Veritabanı**: Şu anda JSON dosyaları (veri) ve TinyDB (session) kullanılıyor, production için PostgreSQL/MongoDB önerilir
- **Rate Limiting**: Production'da Redis kullanarak rate limiting'i ölçeklendirin
- **Loglama**: Log dosyaları `backend/logs/` dizininde saklanır, düzenli olarak temizleyin
- **Güvenlik**: CORS ayarlarını production'da sadece gerekli origin'ler için yapılandırın

## 📄 Lisans

Bu proje demo amaçlıdır ve genel kullanım için hazırlanmıştır.

## 🤝 Katkıda Bulunma

Sorularınız veya önerileriniz için issue açabilirsiniz.

---

**Son Güncelleme:** 2024

**Not:** Bu sistem demo amaçlıdır ve production kullanımı için ek güvenlik ve optimizasyon önlemleri alınmalıdır.
