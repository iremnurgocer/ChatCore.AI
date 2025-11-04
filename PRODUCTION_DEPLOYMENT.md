# ChatCore.AI - Production Deployment Rehberi

## Proje Durumu: Production'a Hazýr ?

Bu proje þirketlerin kendi prosedürlerini ve verilerini ekleyerek kullanabileceði þekilde tasarlanmýþtýr.

## Hýzlý Uyarlama Adýmlarý

### 1. Veri Dosyalarýný Özelleþtirme

`backend/data/` klasöründeki JSON dosyalarýný kendi þirket verilerinizle deðiþtirin:

#### `employees.json` - Çalýþan Listesi
```json
[
  {
    "id": 1,
    "name": "Ad Soyad",
    "department": "Departman Adý",
    "position": "Pozisyon",
    "email": "email@example.com",
    "phone": "+90 555 123 4567"
  }
]
```

#### `departments.json` - Departman Bilgileri
```json
[
  {
    "id": 1,
    "name": "Departman Adý",
    "director": "Yönetici Adý",
    "budget": 1000000,
    "location": "Lokasyon"
  }
]
```

#### `projects.json` - Proje Detaylarý
```json
[
  {
    "id": 1,
    "name": "Proje Adý",
    "status": "Devam Ediyor",
    "department": "Departman Adý",
    "manager": "Proje Yöneticisi",
    "budget": 500000,
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  }
]
```

#### `procedures.json` - Þirket Prosedürleri
```json
[
  {
    "id": 1,
    "code": "PROC-001",
    "title": "Prosedür Baþlýðý",
    "department": "Departman Adý",
    "category": "Kategori",
    "priority": "Yüksek",
    "content": "Prosedür detaylý açýklamasý...",
    "published_date": "2024-01-01",
    "updated_date": "2024-01-01"
  }
]
```

### 2. Environment Variables Yapýlandýrmasý

`backend/.env.example` dosyasýný kopyalayýp `backend/.env` olarak kaydedin ve deðerleri doldurun:

```env
# Þirket Bilgileri
COMPANY_NAME=Þirket Adýnýz
APP_NAME=Þirket AI Chat Sistemi

# AI Saðlayýcý Seçimi
# Seçenekler: GEMINI, OPENAI, AZURE, OLLAMA
AI_PROVIDER=GEMINI

# Google Gemini (Ücretsiz - Önerilen)
GEMINI_API_KEY=your-gemini-api-key-here

# OpenAI (Ücretli)
OPENAI_API_KEY=your-openai-key-here

# Azure OpenAI (Ücretli)
AZURE_OPENAI_API_KEY=your-azure-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini

# Ollama (Yerel, Ücretsiz)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Güvenlik (Production'da mutlaka deðiþtirin!)
SECRET_KEY=your-secret-key-change-in-production

# Backend URL (Production için)
BACKEND_URL=http://localhost:8000
ALLOWED_ORIGINS=http://localhost:8501,https://yourdomain.com

# Frontend URL (Production için)
FRONTEND_URL=http://localhost:8501
```

### 3. API Token ve Servis Yapýlandýrmasý

#### AI Servis Seçimi
1. Tercih ettiðiniz AI servisini seçin (Gemini önerilir - ücretsiz)
2. Ýlgili API key'i alýn
3. `backend/.env` dosyasýna ekleyin
4. `AI_PROVIDER` deðerini güncelleyin

#### API Key Alma Rehberleri
- **Gemini**: https://makersuite.google.com/app/apikey
- **OpenAI**: https://platform.openai.com/api-keys
- **Azure**: Azure Portal > Cognitive Services
- **Ollama**: https://ollama.ai (yerel kurulum)

### 4. Kullanýcý Yönetimi

Varsayýlan kullanýcýlar:
- `admin` / `1234`
- `user2` / `1234`
- `user3` / `12345`

**Yeni kullanýcý eklemek için:**
`backend/user_manager.py` dosyasýndaki `_initialize_default_users()` fonksiyonunu düzenleyin veya API üzerinden ekleyin.

### 5. Production Güvenlik Ayarlarý

#### Kritik Güvenlik Kontrolleri:
1. ? `SECRET_KEY` deðiþtirildi mi?
2. ? Þifreler güvenli mi? (varsayýlan þifreleri deðiþtirin)
3. ? CORS ayarlarý production için uygun mu?
4. ? Rate limiting aktif mi?
5. ? HTTPS kullanýlýyor mu?

## Developer Dokümantasyonu

### Proje Yapýsý

```
ChatCore.AI/
??? backend/                    # FastAPI Backend
?   ??? main.py               # Ana API uygulamasý ve endpoint'ler
?   ??? auth.py               # JWT authentication ve login/logout
?   ??? ai_service.py         # AI saðlayýcý entegrasyonlarý (OpenAI, Gemini, Azure, Ollama)
?   ??? data_loader.py        # JSON veri dosyalarýný yükleme
?   ??? session_manager.py    # Kullanýcý session ve conversation yönetimi
?   ??? rag_service.py        # RAG (Retrieval-Augmented Generation) servisi
?   ??? security.py           # Güvenlik validasyonlarý ve rate limiting
?   ??? user_manager.py       # Kullanýcý yönetimi (TinyDB)
?   ??? ai_cache.py           # AI yanýt cache sistemi
?   ??? analytics.py          # Kullaným analitikleri
?   ??? logger.py             # Loglama sistemi
?   ??? data/                 # Þirket veri dosyalarý (JSON)
?   ?   ??? employees.json    # Çalýþan listesi
?   ?   ??? departments.json  # Departman bilgileri
?   ?   ??? projects.json     # Proje detaylarý
?   ?   ??? procedures.json   # Þirket prosedürleri
?   ?   ??? sessions.json     # Kullanýcý session ve conversation verileri (TinyDB)
?   ??? .env                  # Environment variables (oluþturulmalý)
?
??? frontend/                  # Streamlit Frontend
?   ??? app.py                # Ana web arayüzü
?   ??? static/
?       ??? styles.css        # CSS stil dosyasý
?
??? README.md                  # Ana dokümantasyon
??? KURULUM_REHBERI.md        # Kurulum rehberi
??? GELISTIRME_OZELLIKLERI.md # Geliþtirilebilecek özellikler
??? kurulum.bat/sh            # Otomatik kurulum scripti
??? baslat.bat/sh             # Servis baþlatma scripti
```

### API Endpoint'leri

#### Authentication
- `POST /api/login` - Kullanýcý giriþi
- `POST /api/logout` - Kullanýcý çýkýþý

#### Chat
- `POST /api/chat` - AI sohbet mesajý gönderme
- `GET /api/conversations` - Kullanýcýnýn conversation listesi
- `POST /api/conversations/new` - Yeni conversation oluþturma
- `POST /api/conversations/{id}/switch` - Conversation deðiþtirme

#### Veri Endpoint'leri
- `GET /api/employees` - Çalýþan listesi
- `GET /api/departments` - Departman listesi
- `GET /api/projects` - Proje listesi
- `GET /api/procedures/new` - Yeni prosedürler

#### Sistem
- `GET /api/status` - Backend durumu
- `GET /docs` - Swagger API dokümantasyonu

### Veri Dosyasý Þemalarý

#### employees.json
```json
[
  {
    "id": 1,
    "name": "Ad Soyad",
    "department": "Departman",
    "position": "Pozisyon",
    "email": "email@example.com",
    "phone": "+90 555 123 4567"
  }
]
```

#### departments.json
```json
[
  {
    "id": 1,
    "name": "Departman Adý",
    "director": "Yönetici Adý",
    "budget": 1000000,
    "location": "Lokasyon",
    "employee_count": 10
  }
]
```

#### projects.json
```json
[
  {
    "id": 1,
    "name": "Proje Adý",
    "status": "Devam Ediyor",
    "department": "Departman",
    "manager": "Proje Yöneticisi",
    "budget": 500000,
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "description": "Proje açýklamasý"
  }
]
```

#### procedures.json
```json
[
  {
    "id": 1,
    "code": "PROC-001",
    "title": "Prosedür Baþlýðý",
    "department": "Departman",
    "category": "Kategori",
    "priority": "Yüksek",
    "content": "Detaylý prosedür açýklamasý...",
    "published_date": "2024-01-01",
    "updated_date": "2024-01-01"
  }
]
```

### Kod Yapýsý ve Özelleþtirme

#### Veri Ekleme/Düzenleme
1. `backend/data/` klasöründeki JSON dosyalarýný düzenleyin
2. RAG sistemi otomatik olarak yeni verileri indeksler
3. Cache otomatik olarak güncellenir

#### AI Servis Deðiþtirme
1. `backend/.env` dosyasýnda `AI_PROVIDER` deðerini deðiþtirin
2. Ýlgili API key'leri ekleyin
3. Backend'i yeniden baþlatýn

#### Yeni Endpoint Ekleme
`backend/main.py` dosyasýna yeni endpoint ekleyin:
```python
@app.get("/api/custom-endpoint")
def custom_endpoint(user_id: str = Depends(get_current_user)):
    """Yeni endpoint açýklamasý"""
    # Kod buraya
    return {"success": True}
```

#### Frontend Özelleþtirme
`frontend/app.py` dosyasýný düzenleyerek:
- Þirket adýný deðiþtirebilirsiniz
- Renkler ve stilleri özelleþtirebilirsiniz
- Yeni özellikler ekleyebilirsiniz

## Production Deployment Checklist

### Güvenlik
- [ ] `SECRET_KEY` deðiþtirildi (güçlü bir key kullanýn)
- [ ] Varsayýlan kullanýcý þifreleri deðiþtirildi
- [ ] CORS ayarlarý production domain'leri için yapýlandýrýldý
- [ ] HTTPS kullanýlýyor
- [ ] Rate limiting aktif
- [ ] Firewall kurallarý yapýlandýrýldý

### Veritabaný (Opsiyonel)
- [ ] Production için PostgreSQL/MongoDB geçiþi yapýldý (þu an TinyDB kullanýlýyor)
- [ ] Veritabaný yedekleme stratejisi belirlendi

### Performans
- [ ] Cache sistemi aktif
- [ ] RAG sistemi optimize edildi
- [ ] Rate limiting deðerleri ayarlandý
- [ ] Loglama seviyesi production için ayarlandý

### Monitoring
- [ ] Log dosyalarý izleniyor (`backend/logs/`)
- [ ] Analytics aktif
- [ ] Hata bildirimleri yapýlandýrýldý

## Özelleþtirme Örnekleri

### Örnek 1: Kendi Prosedürlerinizi Ekleme
```bash
# 1. backend/data/procedures.json dosyasýný açýn
# 2. Kendi prosedürlerinizi JSON formatýnda ekleyin
# 3. Backend'i yeniden baþlatýn
# 4. AI otomatik olarak yeni prosedürleri öðrenir
```

### Örnek 2: AI Servis Deðiþtirme
```bash
# 1. backend/.env dosyasýný açýn
# 2. AI_PROVIDER=OPENAI olarak deðiþtirin
# 3. OPENAI_API_KEY=your-key ekleyin
# 4. Backend'i yeniden baþlatýn
```

### Örnek 3: Þirket Adýný Deðiþtirme
```bash
# backend/.env dosyasýnda:
COMPANY_NAME=Þirket Adýnýz

# frontend/app.py dosyasýnda:
COMPANY_NAME = os.getenv("COMPANY_NAME", "Þirket Adýnýz")
```

## Sorun Giderme

### Veri Dosyalarý Yüklenmiyor
- JSON formatýný kontrol edin
- Dosya encoding'inin UTF-8 olduðundan emin olun
- `backend/data/` klasöründe dosyalarýn olduðunu kontrol edin

### AI Yanýt Vermiyor
- API key'in doðru olduðunu kontrol edin
- `AI_PROVIDER` deðerinin doðru olduðunu kontrol edin
- Internet baðlantýsýný kontrol edin
- Backend loglarýný kontrol edin: `backend/logs/errors.log`

### RAG Sistemi Çalýþmýyor
- LangChain kütüphanelerinin yüklü olduðunu kontrol edin
- `pip install langchain langchain-openai langchain-community` komutunu çalýþtýrýn
- Vector store cache'ini temizleyin (otomatik yenilenir)

## Production Ýyileþtirme Önerileri

### Kýsa Vadeli (Kolay)
1. ? .env.example dosyasý eklendi
2. ? Production deployment rehberi hazýrlandý
3. ? Veri þema dokümantasyonu eklendi

### Orta Vadeli (Önerilen)
1. PostgreSQL/MongoDB geçiþi (TinyDB yerine)
2. Redis cache sistemi (daha hýzlý)
3. Docker containerization
4. CI/CD pipeline kurulumu

### Uzun Vadeli (Ýleri Seviye)
1. Kubernetes deployment
2. Load balancing
3. Monitoring ve alerting (Prometheus, Grafana)
4. Automated testing

## Sonuç

**Proje Durumu: ? Production'a Hazýr**

- ? Kod yapýsý anlaþýlýr ve dokümante edilmiþ
- ? Veri dosyalarý kolayca özelleþtirilebilir
- ? AI servis seçimi basit (environment variable)
- ? Güvenlik önlemleri mevcut
- ? Ölçeklenebilir yapý

**Developer'lar için:**
- Kod Türkçe yorumlarla açýklanmýþ
- Modüler yapý (her modül ayrý dosyada)
- API dokümantasyonu mevcut (Swagger)
- Veri þemalarý dokümante edilmiþ

**Þirketler için:**
- Kendi verilerinizi JSON dosyalarýna ekleyin
- AI servisini seçin (Gemini önerilir - ücretsiz)
- API key'i ekleyin
- Çalýþtýrýn!

Bu proje þirketlerin kendi prosedürlerini, çalýþanlarýný ve projelerini ekleyerek hýzlýca kullanabileceði þekilde tasarlanmýþtýr.

