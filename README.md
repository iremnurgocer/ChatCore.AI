# ChatCore.AI - Kurumsal AI Chat Sistemi

**Kurumsal AI Chat Sistemi** – Şirket içi bilgilere dayalı RAG teknolojisi destekli AI asistanı

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32.0+-red.svg)](https://streamlit.io)
[![AI](https://img.shields.io/badge/AI-RAG-orange.svg)](https://github.com/langchain-ai/langchain)

## Neden ChatCore.AI?

ChatCore.AI, şirket içi bilgilerinizi (çalışanlar, projeler, departmanlar, prosedürler) kullanarak soruları yanıtlayan profesyonel bir AI chat sistemidir. RAG (Retrieval-Augmented Generation) teknolojisi ile %100 doğru ve güncel yanıtlar sunar.

### Ana Avantajlar

- **Hızlı Kurulum**: 2 komut ile çalışır hale gelin (`kurulum.bat` → `baslat.bat`)
- **Çoklu AI Desteği**: Gemini, OpenAI, Azure, Ollama - hangisini isterseniz
- **Ücretsiz Kullanım**: Gemini ücretsiz katmanı veya tamamen yerel Ollama
- **Güvenli**: JWT authentication, input validation, rate limiting
- **RAG Teknolojisi**: Şirket verilerinize dayalı %100 doğru yanıtlar
- **Otomatik Fallback**: AI provider çalışmazsa otomatik yedek devreye girer
- **Kalıcı Oturum**: Sayfa yenileme sonrası sohbet geçmişiniz korunur
- **Ölçeklenebilir**: Küçük şirketlerden büyük şirketlere kadar

## Hızlı Kurulum

### Windows (Otomatik - Bat Dosyaları ile)

#### 1. Kurulum

Proje dizininde `kurulum.bat` dosyasına çift tıklayın veya komut satırından çalıştırın:

```batch
kurulum.bat
```

**Kurulum Scripti Ne Yapar?**
- Python kontrolü yapar (python veya py komutunu test eder)
- Virtual environment oluşturur (`backend\venv`)
- Pip'i günceller
- Tüm bağımlılıkları yükler (`requirements.txt`'den)
- Backend modüllerini test eder
- `.env` dosyası yoksa şablon oluşturur

**Kurulum Süresi:** İlk kurulum 2-5 dakika sürebilir (internet hızına bağlı).

#### 2. API Key Ekleme

Kurulum tamamlandıktan sonra:

1. `backend\.env` dosyasını açın (Notepad veya herhangi bir metin editörü ile)
2. `GEMINI_API_KEY=your-gemini-api-key-here` satırını bulun
3. `your-gemini-api-key-here` yerine kendi API anahtarınızı yapıştırın
4. Dosyayı kaydedin (Ctrl+S)

**API Key Nasıl Alınır?**
- https://makersuite.google.com/app/apikey adresine gidin
- Google hesabınızla giriş yapın
- "Create API Key" butonuna tıklayın
- Oluşturulan key'i kopyalayıp `.env` dosyasına yapıştırın

#### 3. Servisleri Başlatma

Proje dizininde `baslat.bat` dosyasına çift tıklayın veya komut satırından çalıştırın:

```batch
baslat.bat
```

**Başlatma Scripti Ne Yapar?**
- Python kontrolü yapar
- `.env` dosyasının varlığını kontrol eder
- Virtual environment'ın varlığını kontrol eder
- Backend'i yeni bir pencerede başlatır (Port 8000)
- 5 saniye bekler (backend'in hazır olması için)
- Frontend'i yeni bir pencerede başlatır (Port 8501)

**ÖNEMLİ:** Script çalıştığında iki yeni pencere açılacak:
- **"ChatCore Backend"** penceresi: Backend servisi (Port 8000)
- **"ChatCore Frontend"** penceresi: Frontend servisi (Port 8501)

**Başlatma Süresi:**
- Backend başlatma: 5-10 saniye
- Frontend başlatma: 3-5 saniye
- Toplam: ~10-15 saniye

**Hazır Olma Kontrolü:**
- Backend hazır olduğunda terminalde şu mesajı göreceksiniz:
  ```
  INFO:     Application startup complete.
  INFO:     Uvicorn running on http://0.0.0.0:8000
  ```
- Frontend hazır olduğunda tarayıcıda açılır veya şu adrese gidebilirsiniz:
  ```
  http://localhost:8501
  ```

**Giriş Bilgileri:**
- Kullanıcı adı: `admin`
- Şifre: `1234`

**Servisleri Durdurma:**
- Açılan "ChatCore Backend" ve "ChatCore Frontend" pencerelerini kapatın
- Veya pencerelerde Ctrl+C tuşlarına basın

### macOS / Linux (Otomatik - Shell Scriptleri ile)

#### 1. Kurulum

Terminal'de proje dizinine gidin ve şu komutları çalıştırın:

```bash
chmod +x kurulum.sh
./kurulum.sh
```

**Kurulum Scripti Ne Yapar?**
- Python kontrolü yapar (python3 veya python komutunu test eder)
- Virtual environment oluşturur (`backend/venv`)
- Pip'i günceller
- Tüm bağımlılıkları yükler (`requirements.txt`'den)
- Backend modüllerini test eder
- `.env` dosyası yoksa şablon oluşturur

**Kurulum Süresi:** İlk kurulum 2-5 dakika sürebilir (internet hızına bağlı).

#### 2. API Key Ekleme

Kurulum tamamlandıktan sonra:

1. `backend/.env` dosyasını düzenleyin:
   ```bash
   nano backend/.env
   # veya
   vim backend/.env
   ```
2. `GEMINI_API_KEY=your-gemini-api-key-here` satırını bulun
3. `your-gemini-api-key-here` yerine kendi API anahtarınızı yapıştırın
4. Dosyayı kaydedin (nano: Ctrl+X, Y, Enter | vim: Esc, :wq, Enter)

**API Key Nasıl Alınır?**
- https://makersuite.google.com/app/apikey adresine gidin
- Google hesabınızla giriş yapın
- "Create API Key" butonuna tıklayın
- Oluşturulan key'i kopyalayıp `.env` dosyasına yapıştırın

#### 3. Servisleri Başlatma

Terminal'de proje dizininde şu komutları çalıştırın:

```bash
chmod +x baslat.sh
./baslat.sh
```

**Başlatma Scripti Ne Yapar?**
- Python kontrolü yapar
- `.env` dosyasının varlığını kontrol eder
- Virtual environment'ın varlığını kontrol eder
- Backend'i yeni bir terminal penceresinde başlatır (Port 8000)
- 5 saniye bekler (backend'in hazır olması için)
- Frontend'i yeni bir terminal penceresinde başlatır (Port 8501)

**ÖNEMLİ:** Script çalıştığında iki yeni terminal penceresi açılacak:
- **Backend terminali**: Backend servisi (Port 8000)
- **Frontend terminali**: Frontend servisi (Port 8501)

**Başlatma Süresi:**
- Backend başlatma: 5-10 saniye
- Frontend başlatma: 3-5 saniye
- Toplam: ~10-15 saniye

**Hazır Olma Kontrolü:**
- Backend hazır olduğunda terminalde şu mesajı göreceksiniz:
  ```
  INFO:     Application startup complete.
  INFO:     Uvicorn running on http://0.0.0.0:8000
  ```
- Frontend hazır olduğunda tarayıcıda açılır veya şu adrese gidebilirsiniz:
  ```
  http://localhost:8501
  ```

**Giriş Bilgileri:**
- Kullanıcı adı: `admin`
- Şifre: `1234`

**Servisleri Durdurma:**
- Terminal pencerelerinde Ctrl+C tuşlarına basın
- Veya pencereleri kapatın

### Günlük Kullanım

İlk kurulumdan sonra her gün sadece:

**Windows:**
```batch
baslat.bat
```

**macOS/Linux:**
```bash
./baslat.sh
```

**Başlatma Sırası ve Bekleme Süreleri:**
1. Backend başlatılır → **5-10 saniye** bekleyin
2. Backend hazır olunca "Uvicorn running..." mesajını görürsünüz
3. Frontend otomatik başlatılır → **3-5 saniye** daha
4. Toplam başlatma süresi: **~10-15 saniye**

**Not:** İlk başlatmada biraz daha uzun sürebilir (Python modülleri yüklenirken). Sonraki başlatmalarda daha hızlı olur.

**Servisleri Durdurma:**
- Windows: Açılan pencereleri kapatın veya Ctrl+C
- macOS/Linux: Terminal pencerelerinde Ctrl+C veya pencereleri kapatın

## Manuel Kurulum

Script kullanmak istemiyorsanız veya sisteminizde script çalışmıyorsa, aşağıdaki adımları manuel olarak takip edebilirsiniz. Aslında scriptler de temelde bunları yapıyor, sadece adım adım kendiniz yapıyorsunuz.

### 1. Gereksinimler

- Python 3.8 veya üzeri
- pip (Python paket yöneticisi)
- AI Provider API Key (Gemini, OpenAI, Azure veya Ollama)

### 2. Repository'yi Klonlayın

```bash
git clone <repository-url>
cd ChatCore.AI
```

### 3. Backend Kurulumu

#### Virtual Environment Oluşturma

Backend için bir virtual environment oluşturmamız gerekiyor. Bu sayede sistem Python'unuzu kirletmeden projeye özel paketler yükleyebiliriz.

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

Virtual environment aktif olduğunda terminalde `(venv)` yazısını göreceksiniz. Bu işaret görünüyorsa doğru yoldasınız.

#### Bağımlılıkları Yükleme

Projede kullanılan tüm Python paketlerini yüklüyoruz. İlk kez yüklüyorsanız biraz zaman alabilir, normal.

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Bu işlem tamamlandığında FastAPI, Streamlit, LangChain ve diğer gerekli paketler yüklü olacak.

#### Environment Dosyası Oluşturma

`backend/.env` dosyası oluşturun veya mevcut dosyayı düzenleyin. Bu dosya tüm yapılandırmayı içerir:

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

**Önemli:** `GEMINI_API_KEY` değerini mutlaka kendi API anahtarınızla değiştirin. API anahtarı olmadan sistem çalışmaz.

#### Backend'i Başlatma

Backend'i başlatmak için uvicorn kullanıyoruz. Bu FastAPI uygulamalarını çalıştırmak için standart bir yöntem.

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**ÖNEMLİ:** Backend'in tamamen başlaması için 5-10 saniye bekleyin. Terminalde şu mesajları görmelisiniz:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [...]
INFO:     Started server process [...]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

"Application startup complete" mesajını gördüğünüzde backend hazır demektir. Bu mesajı görmeden frontend'i başlatmayın, bağlantı hatası alırsınız.

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

**Not:** Backend ve frontend'i aynı virtual environment'ı kullanabilirsiniz. İkisi de aynı Python paketlerini kullanıyor zaten.

### 5. Veri Dosyalarını Düzenleme

Kendi şirket verilerinizi eklemek için:

1. `backend/data/employees.json` - Çalışan listesi
2. `backend/data/departments.json` - Departman bilgileri
3. `backend/data/projects.json` - Proje detayları
4. `backend/data/procedures.json` - Şirket prosedürleri

Dosyaları açın, JSON formatında verilerinizi ekleyin. Format örnekleri için aşağıdaki "Yapılandırma" bölümüne bakabilirsiniz.

## Kullanım

### Web Arayüzü

1. Servisleri başlatın (`baslat.bat` veya `baslat.sh`)
2. Tarayıcıda `http://localhost:8501` adresine gidin
3. Giriş yapın: `admin` / `1234`
4. Sorularınızı sorun!

### Örnek Sorular

- "Enerji departmanında kimler çalışıyor?"
- "Hangi projeler devam ediyor?"
- "Ahmet Yılmaz'ın projeleri neler?"
- "Yeni prosedürler var mı?"
- "Turizm departmanının bütçesi nedir?"

### API Kullanımı

```bash
# Giriş yapma
curl -X POST "http://localhost:8000/api/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "1234"}'

# Chat sorgusu
curl -X POST "http://localhost:8000/api/chat" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Enerji departmanında kimler çalışıyor?"}'
```

**API Dokümantasyonu:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Yapılandırma

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
- Login: 20 istek/dakika
- Değiştirmek için: `backend/security.py` dosyasını düzenleyin

**JWT Token Süresi** (`backend/auth.py`):
- Varsayılan: 24 saat
- Değiştirmek için: `backend/auth.py` dosyasında `datetime.timedelta(hours=24)` satırını düzenleyin

**Session Timeout** (`backend/session_manager.py`):
- Varsayılan: 7200 saniye (2 saat)
- Değiştirmek için: `backend/session_manager.py` dosyasında `session_timeout` parametresini düzenleyin

### AI Sağlayıcı Seçimi

`backend/.env` dosyasında `AI_PROVIDER` değerini değiştirin:

```env
# Seçenekler: GEMINI, OPENAI, AZURE, OLLAMA
AI_PROVIDER=GEMINI

# Gemini (Ücretsiz - Önerilen)
GEMINI_API_KEY=your-gemini-api-key-here

# OpenAI (Ücretli)
OPENAI_API_KEY=your-openai-key-here

# Azure OpenAI (Ücretli)
AZURE_OPENAI_API_KEY=your-azure-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com

# Ollama (Yerel, Ücretsiz)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

## AI Sağlayıcıları

| Sağlayıcı | Fiyat | Kurulum | Önerilen |
|-----------|-------|---------|----------|
| **Gemini** | Ücretsiz | 5/5 | Başlangıç için |
| **Ollama** | Ücretsiz | 3/5 | Yerel kullanım |
| **OpenAI** | Ücretli | 5/5 | En iyi kalite |
| **Azure** | Ücretli | 4/5 | Kurumsal |

**Özel AI Sağlayıcı Kurulumu:**

Farklı bir AI sağlayıcı kullanmak istiyorsanız, özel kurulum scriptlerini kullanabilirsiniz:

**Windows:**
```batch
kurulum_openai.bat   # OpenAI için
kurulum_azure.bat    # Azure OpenAI için
kurulum_ollama.bat   # Ollama için
```

**macOS/Linux:**
```bash
chmod +x kurulum_openai.sh && ./kurulum_openai.sh   # OpenAI için
chmod +x kurulum_azure.sh && ./kurulum_azure.sh      # Azure OpenAI için
chmod +x kurulum_ollama.sh && ./kurulum_ollama.sh    # Ollama için
```

**Not:** Bu scriptler önce normal kurulumu (`kurulum.bat` veya `kurulum.sh`) yapmanızı bekler. Sadece `.env` dosyasındaki AI sağlayıcı ayarlarını değiştirirler.

### Gemini (Ücretsiz - Önerilen)

**Avantajlar:**
- Ücretsiz katman mevcut
- Azure/OpenAI benzeri bulut servisi
- Sadece API key gerekli, kurulum yok
- Yüksek kaliteli yanıtlar

**Kurulum:**
1. https://makersuite.google.com/app/apikey adresinden API key alın
2. `backend/.env` dosyasında `GEMINI_API_KEY` ekleyin
3. `AI_PROVIDER=GEMINI` ayarlayın

### OpenAI (Ücretli - En İyi Kalite)

**Avantajlar:**
- En gelişmiş AI modelleri
- Çok hızlı yanıt
- RAG desteği ile FAISS entegrasyonu

**Kurulum:**
```batch
# Windows
kurulum_openai.bat

# macOS/Linux
chmod +x kurulum_openai.sh
./kurulum_openai.sh
```

**Nasıl Çalışır?**
1. `.env` dosyasının varlığını kontrol eder
2. OpenAI API Key'inizi ister
3. Model seçimi yapmanızı sağlar (gpt-4o-mini, gpt-4o, gpt-3.5-turbo)
4. `.env` dosyasını otomatik olarak günceller

### Azure OpenAI (Ücretli - Kurumsal)

**Avantajlar:**
- Enterprise seviye güvenlik
- Azure üzerinden yönetim
- OpenAI modellerine erişim

**Kurulum:**
```batch
# Windows
kurulum_azure.bat

# macOS/Linux
chmod +x kurulum_azure.sh
./kurulum_azure.sh
```

**Nasıl Çalışır?**
1. `.env` dosyasının varlığını kontrol eder
2. Azure OpenAI API Key'inizi ister
3. Azure OpenAI Endpoint'inizi ister
4. Deployment adınızı ister (varsayılan: gpt-4o-mini)
5. `.env` dosyasını otomatik olarak günceller

### Ollama (Yerel - Ücretsiz)

**Avantajlar:**
- Tamamen ücretsiz, sınırsız
- Yerel çalışma (internet gerektirmez)
- Gizlilik odaklı

**Kurulum:**
```batch
# Windows
kurulum_ollama.bat

# macOS/Linux
chmod +x kurulum_ollama.sh
./kurulum_ollama.sh
```

**Nasıl Çalışır?**
1. Ollama'nın kurulu olduğunu kontrol eder
2. Model'in (llama3.2) indirilip indirilmediğini kontrol eder
3. Model yoksa otomatik olarak indirir (5-15 dakika sürebilir)
4. `.env` dosyasını otomatik olarak günceller

**ÖNEMLİ:** Ollama kurulumu için önce https://ollama.ai adresinden Ollama'yı indirip kurmanız gerekir.

## API Dokümantasyonu

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

## Sorun Giderme

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

**"Frontend başlamıyor" Hatası:**
- Backend'in çalıştığını kontrol edin: http://localhost:8000/api/status
- Streamlit'in yüklü olduğunu kontrol edin

**"Port zaten kullanılıyor" Hatası:**
- Çalışan eski servisleri durdurun
- Farklı port kullanın veya port'u kullanan uygulamayı bulun

**"AI yanıt vermiyor" Hatası:**
- API key'in doğru olduğunu kontrol edin
- `AI_PROVIDER` değerinin doğru olduğunu kontrol edin
- Backend loglarını kontrol edin

## Teknolojiler

- **Backend**: FastAPI, Uvicorn
- **Frontend**: Streamlit
- **AI**: LangChain, OpenAI, Google Gemini, Ollama
- **RAG**: FAISS, Sentence Transformers
- **Database**: TinyDB (session management)
- **Auth**: JWT (PyJWT)

## Notlar

- **Production Kullanımı**: Production'da mutlaka `SECRET_KEY`'i değiştirin
- **Veritabanı**: Şu anda JSON dosyaları kullanılıyor, production için PostgreSQL/MongoDB önerilir
- **Rate Limiting**: Production'da Redis kullanarak rate limiting'i ölçeklendirin

## Lisans

Bu proje demo amaçlıdır ve genel kullanım için hazırlanmıştır.

## Katkıda Bulunma

Sorularınız veya önerileriniz için issue açabilirsiniz.

---

**Son Güncelleme:** 11/2025
