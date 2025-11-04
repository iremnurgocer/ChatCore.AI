# ChatCore.AI

**Kurumsal AI Chat Sistemi** - Şirket içi bilgilere dayalı RAG teknolojisi destekli AI asistanı

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32.0+-red.svg)](https://streamlit.io)
[![AI](https://img.shields.io/badge/AI-RAG-orange.svg)](https://github.com/langchain-ai/langchain)

## Hakkında

ChatCore.AI, şirket içi bilgilerinizi (çalışanlar, projeler, departmanlar, prosedürler) kullanarak soruları yanıtlayan profesyonel bir AI chat sistemidir. RAG (Retrieval-Augmented Generation) teknolojisi ile %100 doğru ve güncel yanıtlar sunar.

### Özellikler

- **Çoklu AI Desteği**: Gemini (ücretsiz), OpenAI, Azure, Ollama
- **RAG Teknolojisi**: Şirket verilerinize dayalı doğru yanıtlar
- **Kalıcı Oturum**: Sohbet geçmişi korunur
- **Güvenlik**: JWT authentication, rate limiting, input validation
- **Analytics**: Kullanım istatistikleri ve loglama
- **Otomatik Fallback**: AI provider çalışmazsa yedek devreye girer

## Hızlı Kurulum

### Windows

1. **Kurulum:**
   ```batch
   kurulum.bat
   ```

2. **API Key Ekleme:**
   - `backend\.env` dosyasını açın
   - `GEMINI_API_KEY=your-gemini-api-key-here` satırını bulun
   - API anahtarınızı yapıştırın
   - API Key almak için: https://makersuite.google.com/app/apikey

3. **Servisleri Başlatma:**
   ```batch
   baslat.bat
   ```
   - Tarayıcıda: http://localhost:8501
   - Giriş: `admin` / `1234`

### macOS / Linux

1. **Kurulum:**
   ```bash
   chmod +x kurulum.sh
   ./kurulum.sh
   ```

2. **API Key Ekleme:**
   - `backend/.env` dosyasını düzenleyin
   - `GEMINI_API_KEY` değerini güncelleyin

3. **Servisleri Başlatma:**
   ```bash
   chmod +x baslat.sh
   ./baslat.sh
   ```

## Gereksinimler

- Python 3.8 veya üzeri
- pip (Python paket yöneticisi)
- AI Provider API Key (Gemini, OpenAI, Azure veya Ollama)

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

### Veri Dosyaları

Kendi şirket verilerinizi eklemek için `backend/data/` klasöründeki JSON dosyalarını düzenleyin:

- `employees.json` - Çalışan listesi
- `departments.json` - Departman bilgileri
- `projects.json` - Proje detayları
- `procedures.json` - Şirket prosedürleri

## AI Sağlayıcıları

| Sağlayıcı | Fiyat | Kurulum | Önerilen |
|-----------|-------|---------|----------|
| **Gemini** | Ücretsiz | 5/5 | Başlangıç için |
| **Ollama** | Ücretsiz | 3/5 | Yerel kullanım |
| **OpenAI** | Ücretli | 5/5 | En iyi kalite |
| **Azure** | Ücretli | 4/5 | Kurumsal |

Detaylı kurulum rehberleri için:
- [KURULUM_REHBERI.md](KURULUM_REHBERI.md) - Genel rehber
- [KURULUM_OLLAMA.md](KURULUM_OLLAMA.md) - Ollama kurulumu
- [KURULUM_OPENAI.md](KURULUM_OPENAI.md) - OpenAI kurulumu
- [KURULUM_AZURE.md](KURULUM_AZURE.md) - Azure kurulumu

## Proje Yapısı

```
ChatCore.AI/
├── backend/              # FastAPI backend
│   ├── main.py          # Ana API uygulaması
│   ├── ai_service.py    # AI sağlayıcı entegrasyonları
│   ├── data/            # Şirket veri dosyaları (JSON)
│   └── .env            # Yapılandırma dosyası
├── frontend/            # Streamlit frontend
│   └── app.py          # Web arayüzü
├── kurulum.bat/sh       # Otomatik kurulum
└── baslat.bat/sh        # Servis başlatma
```

## Sorun Giderme

### Backend başlamıyor
- `backend/.env` dosyasının var olduğundan emin olun
- API key'in doğru olduğunu kontrol edin
- Backend loglarını kontrol edin: `backend/logs/errors.log`

### Frontend başlamıyor
- Backend'in çalıştığını kontrol edin: http://localhost:8000/api/status
- Streamlit'in yüklü olduğunu kontrol edin

### Port zaten kullanılıyor
- Çalışan eski servisleri durdurun
- Farklı port kullanın veya port'u kullanan uygulamayı bulun

### AI yanıt vermiyor
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

**Son Güncelleme:** 2024
