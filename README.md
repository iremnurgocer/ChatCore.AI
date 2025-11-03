# ChatCore.AI - Kurumsal AI Chat Sistemi

Profesyonel, güvenli ve entegrasyona hazır AI destekli kurumsal chat uygulaması. Bu sistem, şirket içi iletişim için AI desteği sağlar ve çalışanlar, projeler ve departmanlar hakkında soruları yanıtlar.

## İçindekiler

- [Proje Hakkında](#proje-hakkında)
- [Özellikler](#özellikler)
- [Mimari](#mimari)
- [Kurulum](#kurulum)
- [Yapılandırma](#yapılandırma)
- [Kullanım](#kullanım)
- [API Dokümantasyonu](#api-dokümantasyonu)
- [Entegrasyon Kılavuzu](#entegrasyon-kılavuzu)
- [Güvenlik Özellikleri](#güvenlik-özellikleri)
- [AI Sağlayıcıları](#ai-sağlayıcıları)
- [Sorun Giderme](#sorun-giderme)

## Proje Hakkında

ChatCore.AI, şirket içi bilgileri kullanarak soruları yanıtlayan, RAG (Retrieval-Augmented Generation) teknolojisi destekli bir AI chat sistemidir. Sistem, çalışanlar, projeler ve departmanlar hakkındaki soruları yanıtlayabilir ve kurumsal uygulamalara entegre edilebilir.

### Ana Amaçlar

- Şirket içi bilgilere dayalı AI destekli sohbet
- Çalışan, proje ve departman sorguları
- Çoklu AI sağlayıcı desteği (OpenAI, Azure, Gemini, Ollama)
- RESTful API yapısı
- Güvenli ve ölçeklenebilir mimari

## Özellikler

### Temel Özellikler

- **AI Sohbet**: Çoklu AI sağlayıcı desteği ile akıllı yanıtlar
- **RAG Desteği**: Şirket içi verilerle zenginleştirilmiş yanıtlar
- **Session Yönetimi**: Kullanıcı bazlı konuşma geçmişi
- **Intent Analizi**: Kullanıcı sorgularının otomatik analizi
- **Analytics**: API kullanım istatistikleri ve performans takibi

### Güvenlik Özellikleri

- **JWT Kimlik Doğrulama**: Token tabanlı güvenli erişim
- **Rate Limiting**: API isteklerinde hız sınırlaması
- **Input Validation**: XSS ve SQL injection koruması
- **Güvenlik Loglama**: Kategorize edilmiş güvenlik olayları
- **CORS Yapılandırması**: Cross-origin güvenliği

### Loglama ve İzleme

- **Kategorize Loglama**: Hata türlerine göre kategorize edilmiş loglar
- **Güvenlik Logları**: Rate limit, XSS, injection denemeleri
- **Performans İzleme**: Yanıt süreleri ve başarı oranları
- **Hata Takibi**: Detaylı hata logları ve analitik

## Mimari

### Proje Yapısı

```
ChatCore.AI/
├── backend/                 # FastAPI backend servisi
│   ├── main.py             # Ana API uygulaması
│   ├── ai_service.py       # AI sağlayıcı entegrasyonları
│   ├── auth.py             # JWT kimlik doğrulama
│   ├── data_loader.py      # Veri yükleme modülü
│   ├── session_manager.py  # Session yönetimi
│   ├── logger.py           # Loglama sistemi
│   ├── analytics.py        # İstatistik ve analitik
│   ├── security.py         # Güvenlik modülleri
│   ├── nlp_service.py      # Intent ve entity çıkarımı
│   ├── report_service.py  # PDF rapor oluşturma
│   ├── requirements.txt   # Python bağımlılıkları
│   └── data/              # JSON veri dosyaları
│       ├── employees.json
│       ├── departments.json
│       └── projects.json
├── frontend/               # Streamlit frontend
│   ├── app.py             # Ana Streamlit uygulaması
│   └── static/
│       └── styles.css     # CSS stilleri
├── kurulum.bat            # Windows kurulum scripti
├── baslat.bat             # Windows başlatma scripti
├── .gitignore             # Git ignore dosyası
└── README.md              # Bu dosya
```

### Teknoloji Stack

#### Backend

- FastAPI - Modern Python web framework
- LangChain - AI ve RAG desteği
- FAISS - Vektör veritabanı
- JWT - Token tabanlı kimlik doğrulama
- Pydantic - Veri doğrulama

#### Frontend

- Streamlit - Hızlı web arayüzü geliştirme

#### AI Sağlayıcılar

- OpenAI GPT-4/GPT-3.5
- Azure OpenAI
- Google Gemini (Ücretsiz katman mevcut)
- Ollama (Yerel, ücretsiz)
- Hugging Face

## Kurulum

### Gereksinimler

- Python 3.8 veya üzeri
- pip (Python paket yöneticisi)
- İsteğe bağlı: AI sağlayıcı API anahtarları (Gemini ücretsiz katman için önerilir)

### Hızlı Başlangıç

#### Otomatik Kurulum (Önerilen - Windows)

**İlk Kurulum:**

1. **`kurulum.bat`** dosyasına çift tıklayın
   - Python kontrolü yapar
   - Virtual environment oluşturur (yoksa)
   - Tüm bağımlılıkları yükler (backend + frontend)
   - `.env` dosyası oluşturur
   - Kurulum zaten yapılmışsa atlar, tekrar kurulum yapmaz

2. **API Key Ekleme:**
   - Script `.env` dosyası oluşturduktan sonra otomatik açılır
   - Eğer açılmadıysa `backend\.env` dosyasını manuel açın
   - `GEMINI_API_KEY=your-gemini-api-key-here` satırını bulun
   - API anahtarınızı ekleyin ve kaydedin (Ctrl+S)
   - API Key almak için: https://makersuite.google.com/app/apikey

3. **Servisleri Başlatma:**
   - **`baslat.bat`** dosyasına çift tıklayın
   - Backend ve Frontend otomatik başlar
   - Tarayıcıda: http://localhost:8501
   - Giriş: `admin` / `1234`

**Günlük Kullanım:**

İlk kurulumdan sonra sadece **`baslat.bat`** dosyasına çift tıklayın!

#### Manuel Kurulum

**1. Repository'yi klonlayın:**

```bash
git clone <repository-url>
cd ChatCore.AI
```

**2. Backend virtual environment oluşturun:**

```bash
cd backend
python -m venv venv
```

**3. Virtual environment'ı aktifleştirin:**

**Windows:**

```bash
venv\Scripts\activate
```

**Linux/Mac:**

```bash
source venv/bin/activate
```

**4. Bağımlılıkları yükleyin:**

```bash
pip install -r requirements.txt
```

**5. Environment değişkenlerini yapılandırın:**

`backend/.env` dosyası oluşturun:

```env
# AI Sağlayıcı (GEMINI, OPENAI, AZURE, OLLAMA, HUGGINGFACE, LOCAL)
AI_PROVIDER=GEMINI

# Google Gemini (Ücretsiz katman)
GEMINI_API_KEY=your_gemini_api_key_here

# OpenAI (Opsiyonel)
OPENAI_API_KEY=your_openai_key_here

# Azure OpenAI (Opsiyonel)
AZURE_OPENAI_API_KEY=your_azure_key_here
AZURE_OPENAI_ENDPOINT=your_endpoint_here
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini

# JWT Secret Key (Production'da değiştirin!)
SECRET_KEY=supersecret

# Şirket Adı
COMPANY_NAME=Company1

# CORS Origins (virgülle ayrılmış)
ALLOWED_ORIGINS=*
```

**6. Backend'i başlatın:**

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**7. Frontend'i başlatın (yeni terminal):**

```bash
cd frontend
streamlit run app.py
```

## Yapılandırma

### Environment Değişkenleri

`backend/.env` dosyasında yapılandırılabilir değişkenler:

| Değişken | Açıklama | Varsayılan |
|----------|----------|------------|
| `AI_PROVIDER` | AI sağlayıcı seçimi (GEMINI, OPENAI, AZURE, OLLAMA, HUGGINGFACE, LOCAL) | GEMINI |
| `GEMINI_API_KEY` | Google Gemini API anahtarı (Ücretsiz) | - |
| `OPENAI_API_KEY` | OpenAI API anahtarı (Ücretli) | - |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API anahtarı (Ücretli) | - |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint URL'i | - |
| `AZURE_OPENAI_DEPLOYMENT` | Azure OpenAI deployment adı | gpt-4o-mini |
| `OLLAMA_BASE_URL` | Ollama sunucu adresi (Yerel, Ücretsiz) | http://localhost:11434 |
| `OLLAMA_MODEL` | Ollama model adı | llama2 |
| `HUGGINGFACE_API_KEY` | Hugging Face API anahtarı (Ücretsiz) | - |
| `HUGGINGFACE_MODEL` | Hugging Face model adı | distilgpt2 |
| `SECRET_KEY` | JWT imzalama için gizli anahtar | supersecret |
| `COMPANY_NAME` | Şirket adı | Company1 |
| `BACKEND_URL` | Backend API URL'i | http://127.0.0.1:8000 |
| `ALLOWED_ORIGINS` | CORS izin verilen origin'ler | * |

### Veri Dosyaları

`backend/data/` dizinindeki JSON dosyalarını düzenleyerek şirket verilerinizi ekleyebilirsiniz:

- `employees.json` - Çalışan listesi
- `departments.json` - Departman bilgileri
- `projects.json` - Proje detayları

## Kullanım

### Web Arayüzü

1. Backend ve frontend servislerini başlatın
2. Tarayıcıda `http://localhost:8501` adresine gidin
3. Varsayılan kimlik bilgileriyle giriş yapın:
   - **Kullanıcı adı:** `admin`
   - **Şifre:** `1234`
4. Chat arayüzünde sorularınızı sorun

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

#### 3. RAG Sorgusu (Intent Analizi ile)

```bash
curl -X POST "http://localhost:8000/api/ask" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "Hangi projeler devam ediyor?"}'
```

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

#### Session Yönetimi

- `GET /api/sessions/{session_id}` - Session bilgilerini getir
- `DELETE /api/sessions/{session_id}` - Session'ı temizle

#### İstatistikler

- `GET /api/stats` - Analytics ve istatistikler
- `GET /api/status` - Sistem durumu

### API Dokümantasyonu

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Entegrasyon Kılavuzu

### Diğer Uygulamalara Entegrasyon

Bu API'yi kendi chat uygulamanıza entegre edebilirsiniz:

#### Python Örneği

```python
import requests

# Giriş yap
response = requests.post(
    "http://localhost:8000/api/login",
    json={"username": "admin", "password": "1234"}
)
token = response.json()["token"]

# Sorgu gönder
response = requests.post(
    "http://localhost:8000/api/chat",
    headers={"Authorization": f"Bearer {token}"},
    json={"prompt": "Merhaba, nasılsın?"}
)
answer = response.json()["response"]
print(answer)
```

#### JavaScript Örneği

```javascript
// Giriş yap
const loginResponse = await fetch('http://localhost:8000/api/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'admin', password: '1234' })
});
const { token } = await loginResponse.json();

// Sorgu gönder
const chatResponse = await fetch('http://localhost:8000/api/chat', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ prompt: 'Merhaba, nasılsın?' })
});
const { response } = await chatResponse.json();
console.log(response);
```

## Güvenlik Özellikleri

### Kimlik Doğrulama

- JWT token tabanlı kimlik doğrulama
- Token süresi: 2 saat
- Güvenli token imzalama (HS256)

### Rate Limiting

- Varsayılan: 60 istek/dakika
- Login endpoint'i: 10 istek/dakika
- IP ve kullanıcı bazlı takip

### Input Doğrulama

- XSS pattern tespiti ve engelleme
- SQL injection pattern tespiti
- Maksimum input uzunluğu: 5000 karakter
- HTML escape uygulanması

### Loglama

- Kategorize edilmiş hata logları (AUTH_ERROR, VALIDATION_ERROR, AI_ERROR, vb.)
- Güvenlik olayları loglaması (rate limit, XSS, injection denemeleri)
- Performans metrikleri
- Güvenlik logları ayrı dosyada (`logs/security.log`)

### Güvenlik Header'ları

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`

## AI Sağlayıcıları

### Google Gemini (Önerilen - Ücretsiz)

- Ücretsiz katman mevcut
- Yüksek kaliteli yanıtlar
- Hızlı yanıt süreleri

**Kurulum:**

1. [Google AI Studio](https://makersuite.google.com/app/apikey) adresinden API anahtarı alın
2. `.env` dosyasına `GEMINI_API_KEY` ekleyin
3. `AI_PROVIDER=GEMINI` ayarlayın

### OpenAI

- GPT-4 ve GPT-3.5 desteği
- RAG desteği ile FAISS entegrasyonu
- Yüksek kaliteli yanıtlar

**Kurulum:**

1. [OpenAI Platform](https://platform.openai.com/api-keys) adresinden API anahtarı alın
2. `.env` dosyasına `OPENAI_API_KEY` ekleyin
3. `AI_PROVIDER=OPENAI` ayarlayın

### Azure OpenAI

- Enterprise seviye güvenlik
- Azure üzerinden yönetim
- OpenAI modellerine erişim

**Kurulum:**

1. Azure OpenAI servis oluşturun
2. `.env` dosyasına Azure bilgilerini ekleyin
3. `AI_PROVIDER=AZURE` ayarlayın

### Ollama (Yerel, Ücretsiz)

- Tamamen ücretsiz
- Yerel çalışma (internet gerektirmez)
- Gizlilik odaklı

**Kurulum:**

1. [Ollama](https://ollama.ai) kurun
2. Model indirin: `ollama pull llama2`
3. `.env` dosyasında `AI_PROVIDER=OLLAMA` ayarlayın

## Sorun Giderme

### kurulum.bat Çalışmıyor veya Hata Veriyor

#### "Python bulunamadı" Hatası

**Sorun:** Script Python'u bulamıyor.

**Çözüm:**
1. Python'un kurulu olduğunu kontrol edin:
   ```bash
   python --version
   ```
2. Eğer hata veriyorsa:
   - [Python 3.8+](https://www.python.org/downloads/) indirip kurun
   - **ÖNEMLİ:** Kurulum sırasında "Add Python to PATH" seçeneğini işaretleyin
   - Windows'u yeniden başlatın
   - Tekrar `kurulum.bat` çalıştırın

#### "Virtual environment oluşturulamadı" Hatası

**Sorun:** Virtual environment oluşturma başarısız.

**Çözüm:**
1. `backend\venv` klasörünü silin (eğer varsa)
2. Python'u yönetici olarak çalıştırıp tekrar deneyin
3. Manuel olarak oluşturun:
   ```bash
   cd backend
   python -m venv venv
   ```
4. Tekrar `kurulum.bat` çalıştırın

#### "Bağımlılıklar yüklenemedi" Hatası

**Sorun:** `pip install -r requirements.txt` başarısız oluyor.

**Çözüm:**
1. İnternet bağlantınızı kontrol edin
2. Pip'i güncelleyin:
   ```bash
   python -m pip install --upgrade pip
   ```
3. Virtual environment'ı aktif edin:
   ```bash
   cd backend
   venv\Scripts\activate
   ```
4. Manuel yükleyin:
   ```bash
   pip install -r requirements.txt
   ```
5. Hata mesajlarını okuyun ve gerekirse sorunlu paketi tek tek yükleyin

#### "Permission denied" veya İzin Hatası

**Sorun:** Dosya yazma izni yok.

**Çözüm:**
1. Script'i sağ tıklayın → "Yönetici olarak çalıştır"
2. Antivirus yazılımının engelleyip engellemediğini kontrol edin
3. Proje klasörüne yazma izni verdiğinizden emin olun

### baslat.bat Çalışmıyor veya Hata Veriyor

#### "Virtual environment bulunamadı" Hatası

**Sorun:** `backend\venv` klasörü yok.

**Çözüm:**
1. Önce `kurulum.bat` dosyasını çalıştırın
2. Eğer hala hata veriyorsa:
   ```bash
   cd backend
   python -m venv venv
   cd ..
   kurulum.bat
   ```

#### "Bağımlılıklar yüklü değil" Hatası

**Sorun:** FastAPI veya diğer paketler eksik.

**Çözüm:**
1. `kurulum.bat` dosyasını tekrar çalıştırın
2. Veya manuel yükleyin:
   ```bash
   cd backend
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

#### "API Key henüz eklenmemiş" Hatası

**Sorun:** `.env` dosyasında API key yok.

**Çözüm:**
1. `backend\.env` dosyasını açın
2. `GEMINI_API_KEY=your-gemini-api-key-here` satırını bulun
3. `your-gemini-api-key-here` yerine API anahtarınızı yapıştırın
4. Dosyayı kaydedin (Ctrl+S)
5. Tekrar `baslat.bat` çalıştırın
6. API Key almak için: https://makersuite.google.com/app/apikey

#### "Port zaten kullanılıyor" Hatası

**Sorun:** 8000 veya 8501 portu başka bir uygulama tarafından kullanılıyor.

**Çözüm:**
1. Çalışan eski servisleri durdurun:
   - Açık olan Backend/Frontend pencerelerini kapatın
   - Görev Yöneticisi'nde `uvicorn.exe` ve `streamlit.exe` işlemlerini sonlandırın
2. Port'u kullanan uygulamayı bulun:
   ```bash
   netstat -ano | findstr :8000
   netstat -ano | findstr :8501
   ```
3. İşlemi sonlandırın veya farklı port kullanın

#### Backend Pencere Açılıp Hemen Kapanıyor

**Sorun:** Backend başlatılamıyor, hata var.

**Çözüm:**
1. Backend penceresini açık tutun, hata mesajını okuyun
2. Manuel başlatın ve hataları görün:
   ```bash
   cd backend
   venv\Scripts\activate
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
3. Hata mesajına göre düzeltme yapın (genelde import hatası veya modül eksikliği)

#### Frontend Pencere Açılıp Hemen Kapanıyor

**Sorun:** Streamlit başlatılamıyor.

**Çözüm:**
1. Frontend penceresini açık tutun, hata mesajını okuyun
2. Manuel başlatın:
   ```bash
   cd backend
   venv\Scripts\activate
   cd ..\frontend
   streamlit run app.py
   ```
3. Eğer "streamlit bulunamadı" hatası varsa:
   ```bash
   pip install streamlit
   ```

### Backend Başlamıyor (Manuel Kontrol)

- Python 3.8+ kurulu olduğundan emin olun: `python --version`
- Virtual environment'ın aktif olduğunu kontrol edin: `venv\Scripts\activate`
- Bağımlılıkların yüklü olduğunu doğrulayın: `pip list | findstr fastapi`
- Tüm modüllerin import edilebildiğini kontrol edin:
  ```bash
  cd backend
  python -c "from main import app; print('OK')"
  ```

### Frontend Backend'e Bağlanamıyor

- Backend'in çalıştığını kontrol edin: http://localhost:8000/api/status
- Tarayıcı konsolunda (F12) CORS hatası var mı kontrol edin
- `backend\.env` dosyasındaki `BACKEND_URL` değerini kontrol edin
- Firewall'ün 8000 ve 8501 portlarını engellemediğinden emin olun

### AI Yanıt Vermiyor

- AI sağlayıcı API anahtarının doğru olduğunu kontrol edin
- `.env` dosyasındaki `AI_PROVIDER` değerini kontrol edin (GEMINI, OPENAI, vb.)
- API anahtarının geçerli ve aktif olduğunu doğrulayın
- Backend log dosyalarını kontrol edin: `backend/logs/api.log`
- Backend konsolunda hata mesajları var mı bakın

### Tarayıcıda "Bağlantı Hatası" veya "ERR_CONNECTION_REFUSED"

**Sorun:** Frontend veya Backend servisleri çalışmıyor.

**Çözüm:**
1. Backend'in çalıştığını kontrol edin: http://localhost:8000/docs
2. Frontend'in çalıştığını kontrol edin: Komut satırında "Running on http://localhost:8501" mesajı görünüyor mu?
3. Her iki servisi de yeniden başlatın: `baslat.bat`
4. Antivirus veya firewall engelleyip engellemediğini kontrol edin

### Log Dosyaları

- Genel loglar: `backend/logs/api.log`
- Hata logları: `backend/logs/errors.log`
- Güvenlik logları: `backend/logs/security.log`

Log dosyaları bulunamıyorsa:
1. `backend/logs` klasörünün var olduğundan emin olun
2. Backend'i en az bir kez başlatın (log dosyaları otomatik oluşur)

### Rate Limit Hatası

- Rate limit aşıldı hatası alıyorsanız, `backend/security.py` dosyasındaki limitleri artırabilirsiniz
- Production'da Redis kullanarak rate limiting'i ölçeklendirebilirsiniz
- "Too many requests" hatası için birkaç dakika bekleyin

### Genel Sorun Giderme İpuçları

1. **Her şeyi sıfırdan başlatmak için:**
   - `backend\venv` klasörünü silin
   - `backend\.env` dosyasını kontrol edin (API key doğru mu?)
   - `kurulum.bat` çalıştırın
   - `baslat.bat` çalıştırın

2. **Bağımlılık sorunları için:**
   ```bash
   cd backend
   venv\Scripts\activate
   pip uninstall -r requirements.txt -y
   pip install -r requirements.txt
   ```

3. **Port sorunları için:**
   - Farklı portlar kullanın (örn: 8001, 8502)
   - `.env` dosyasında `BACKEND_URL=http://127.0.0.1:8001` olarak değiştirin

## Notlar

- **Production Kullanımı**: Production ortamında mutlaka `SECRET_KEY`'i değiştirin
- **Veritabanı**: Şu anda JSON dosyaları kullanılıyor, production için PostgreSQL/MongoDB önerilir
- **Rate Limiting**: Production'da Redis kullanarak rate limiting'i ölçeklendirin
- **Loglama**: Log dosyaları `backend/logs/` dizininde saklanır, düzenli olarak temizleyin
- **Güvenlik**: CORS ayarlarını production'da sadece gerekli origin'ler için yapılandırın

## Lisans

Bu proje demo amaçlıdır ve genel kullanım için hazırlanmıştır.

## Katkıda Bulunma

Sorularınız veya önerileriniz için issue açabilirsiniz.

---

**Not:** Bu sistem demo amaçlıdır ve production kullanımı için ek güvenlik ve optimizasyon önlemleri alınmalıdır.
