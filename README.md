# ChatCore.AI

Kurumsal veriler üzerinde çalışan, RAG (Retrieval-Augmented Generation) destekli yapay zekâ asistanı. Backend FastAPI, frontend Streamlit ile geliştirilmiştir ve şirket içi dokümanlarınızı güvenli biçimde indeksleyip ChatGPT benzeri bir arayüzle sunar.

---

## İçindekiler
- [Öz Bakış](#öz-bakış)
- [Temel Özellikler](#temel-özellikler)
- [Mimari Genel Bakış](#mimari-genel-bakış)
- [Hızlı Başlangıç (Otomatik Kurulum)](#hızlı-başlangıç-otomatik-kurulum)
- [Manuel Kurulum Adımları](#manuel-kurulum-adımları)
- [Konfigürasyon & Özelleştirme](#konfigürasyon--özelleştirme)
- [Başlatma ve Kullanım](#başlatma-ve-kullanım)
- [Bakım İşlemleri](#bakım-işlemleri)
- [Sorun Giderme](#sorun-giderme)
- [Geliştirme Notları](#geliştirme-notları)
- [Lisans](#lisans)

---

## Öz Bakış
ChatCore.AI, şirketlerin kendi veri kaynaklarına dayalı akıllı sohbet asistanları kurmasını sağlar. Proje; kalıcı sohbet geçmişi, departman bazlı veri yönetimi, rol bazlı güvenlik, çoklu yapay zekâ sağlayıcısı desteği ve RAG pipeline’ı ile uçtan uca bir çözüm sunar.

---

## Temel Özellikler
- **RAG Pipeline**: FAISS + BM25 hibrit arama, gerektiğinde cross-encoder yeniden sıralama.
- **Çoklu AI Sağlayıcısı**: Gemini (varsayılan), OpenAI, Azure OpenAI, Ollama, HuggingFace.
- **Kalıcı Sohbetler**: Oturumlar ve mesajlar PostgreSQL üzerinde saklanır, token yenileme desteği vardır.
- **Doküman Yönetimi**: PDF, DOCX, XLSX, TXT dosyalarını yükleyip indeksleyin.
- **Departman Bazlı Veri**: Enerji, Turizm, İnşaat, Üretim ve Altyapı departmanlarına ait örnek veri seti.
- **Saha Prosedürleri**: Güvenlik, operasyon, misafir deneyimi gibi örnek prosedürler sisteme dahil.
- **KPI & Proje Takibi**: Çeyreklik hedefler, kilometre taşları ve kalan süre bilgileri sunulur.
- **Otomatik Betikler**: Tek tuşla kurulum (Windows `kurulum.bat`) ve başlatma (`baslat.bat`).

---

## Mimari Genel Bakış
```
ChatCore.AI/
├── backend/           # FastAPI uygulaması
│   ├── api/           # REST API uçları (auth, chat, files, analytics ...)
│   ├── core/          # Config, DB, Redis, logging, security
│   ├── models/        # SQLModel veritabanı modelleri
│   ├── services/      # İş mantığı (AI, RAG, session, document ...)
│   ├── scripts/       # Yardımcı scriptler (seed, migrate, test ...)
│   ├── data/          # JSON veri setleri + vectorstore
│   └── main.py        # FastAPI giriş noktası
├── frontend/          # Streamlit arayüzü (app.py + bileşenler)
├── *.bat / *.sh       # Kurulum ve başlatma betikleri
└── docker-compose.yml # PostgreSQL, Redis servisleri
```

Backend PostgreSQL (kalıcı veri) ve Redis (cache) ile çalışır. RAG pipeline’ı LangChain + FAISS üzerinden yönetilir. Frontend; Streamlit chat bileşenleri, kalıcı session-state ve yönetim paneli içerir.

---

## Hızlı Başlangıç (Otomatik Kurulum)
### Windows
1. **Kurulum**: `kurulum.bat`
   - Python sanal ortamı kurar
   - Gerekli paketleri yükler
   - Örnek veritabanını hazırlar
2. **Başlatma**: `baslat.bat`
   - PostgreSQL/Redis Docker konteynerlerini çalıştırır (varsa)
   - Backend FastAPI uygulaması (8000)
   - Frontend Streamlit uygulaması (8501)

### Linux / macOS
1. `chmod +x install.sh start.sh`
2. `./install.sh`
3. `./start.sh`

> Not: Otomatik betikler Docker gereksinimlerini kontrol eder. Docker kullanmak istemezseniz “Manuel Kurulum” bölümüne geçin.

---

## Manuel Kurulum Adımları
### 1. Depoyu Klonlayın
```bash
git clone <repo-url>
cd ChatCore.AI
```

### 2. Sanal Ortam Oluşturun
```bash
python -m venv venv
# Windows
env\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Bağımlılıkları Yükleyin
```bash
pip install --upgrade pip
pip install -r backend/requirements-refactored.txt
```

### 4. Veritabanı & Cache Servisleri
- Docker ile:
  ```bash
  docker compose up -d postgres redis
  ```
- Manuel kurulum: PostgreSQL 15+, Redis 7+ servislerini yerelde çalıştırın.

### 5. Konfigürasyon Dosyaları
```bash
cd backend
cp .env.example .env
# .env dosyasını ihtiyaçlarınıza göre düzenleyin
```
Zorunlu alanlar: `DATABASE_URL`, `SECRET_KEY`, `AI_PROVIDER`, `GEMINI_API_KEY` (veya seçtiğiniz sağlayıcı anahtarı).

### 6. Veritabanı Migrasyonları ve Örnek Veri
```bash
alembic upgrade head
python scripts/seed_users.py
```
Opsiyonel: `python scripts/seed_data.py` ile geniş veri seti yüklenebilir.

### 7. Sunucuları Başlatın
- **Backend**: `uvicorn main:app --host 0.0.0.0 --port 8000`
- **Frontend**: `streamlit run app.py` (frontend klasörü içinde)

---

## Konfigürasyon & Özelleştirme
### Ortam Değişkenleri (`backend/.env`)
| Anahtar | Açıklama |
|--------|----------|
| `DATABASE_URL` | PostgreSQL bağlantı dizgesi (asyncpg) |
| `REDIS_HOST`, `REDIS_PORT` | Redis adresi |
| `SECRET_KEY` | JWT imzalama anahtarı |
| `AI_PROVIDER` | `GEMINI`, `OPENAI`, `AZURE`, `OLLAMA`, `HUGGINGFACE` |
| `GEMINI_API_KEY` | Gemini anahtarı (varsayılan sağlayıcı) |
| `OPENAI_API_KEY`, `AZURE_*` | Alternatif sağlayıcılar için anahtarlar |
| `COMPANY_NAME` | Prompta yansıtılan şirket adı |
| `ENVIRONMENT` | `development` / `production` |

### Veri Seti Özelleştirme
- **Çalışanlar**: `backend/data/employees.json`
- **Departmanlar & KPI’lar**: `backend/data/departments.json`
- **Projeler**: `backend/data/projects.json`
- **Prosedürler**: `backend/data/procedures.json`

Bu dosyaları güncelledikten sonra RAG indeksini yeniden inşa edin: 
```bash
python scripts/rag_rebuild.py  # varsa
# veya backend içinde
python -c "import asyncio; from services.rag_service import rag_service; asyncio.run(rag_service.initialize(force_rebuild=True))"
```

### AI Sağlayıcısı Seçimi
1. `AI_PROVIDER=GEMINI` (varsayılan) ve `GEMINI_API_KEY` ayarlayın.
2. Başka sağlayıcıya geçmek için ilgili anahtarları `.env` dosyasına ekleyin.
3. Streamlit arayüzü üzerinden de sağlanan seçeneklerle değişiklik yapılabilir (gerekirse).

---

## Başlatma ve Kullanım
### Otomatik Betikler
- `baslat.bat` (Windows) veya `start.sh` (Linux/Mac) iki terminal penceresi açarak backend/frontendi çalıştırır.

### Manuel Başlatma
1. Backend (FastAPI):
   ```bash
   cd backend
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```
2. Frontend (Streamlit):
   ```bash
   cd frontend
   streamlit run app.py
   ```

### Varsayılan Giriş Bilgileri
- Kullanıcı adı: `admin`
- Şifre: `1234`
> Güvenlik için üretimde mutlaka değiştirin.

### Arayüzde Yapabilecekleriniz
- **Yeni Sohbet**: Soldaki butonla yeni oturum başlatın (mesaj atana kadar kayıt oluşmaz).
- **Geçmiş Sohbetler**: İlk 10 kayıt listelenir; seçin, silin veya yenisini açın.
- **Örnek Sorular**: Enerji KPI’ları, Bodrum projeleri, prosedürlerle ilgili hazır sorular.
- **Prosedür Bildirimleri**: Backend’den gelen yeni prosedürler sağ sidebar’da listelenir.

---

## Bakım İşlemleri
- **RAG İndeksini Yenileme**: Veri JSON’larını güncelledikten sonra `rag_service.initialize(force_rebuild=True)` çağırın.
- **Sohbetleri Temizleme**: `python backend/scripts/clear_conversations.py`
- **Veritabanı Yedekleme**: PostgreSQL dump alın (`pg_dump`), `backend/data/` klasöründeki JSON ve `vectorstore/` klasörünü arşivleyin.
- **Loglar**: `backend/logs/` klasöründe API, hata ve güvenlik günlükleri tutulur.

---

## Sorun Giderme
| Belirti | Çözüm |
|---------|-------|
| `Database connection refused` | PostgreSQL servisinin çalıştığını ve `DATABASE_URL` değerinin doğru olduğunu kontrol edin. |
| `Redis unavailable` | `docker compose up -d redis` veya servis durumunu kontrol edin. |
| `ModuleNotFoundError` | Sanal ortamın aktif olduğundan ve `pip install -r backend/requirements-refactored.txt` çalıştırdığınızdan emin olun. |
| Streamlit sayfası boş / hatalı | `streamlit run app.py` komutunu doğru dizinde çalıştırdığınızdan emin olun; konsoldaki hataları kontrol edin. |
| RAG sonuç üretmiyor | JSON verilerini güncellediyseniz RAG indeksini yeniden inşa edin. |

---

## Geliştirme Notları
- Testler: `cd backend && pytest`
- Lint: `ruff check backend/`
- Tip kontrolü: `mypy backend/`
- Yeni DB migrasyonu: `alembic revision --autogenerate -m "desc"`

### Docker
```bash
docker compose up -d        # PostgreSQL + Redis
docker compose logs -f       # Anlık loglar
docker compose down          # Servisleri durdur
```

---

## Lisans
[Lisans metninizi buraya ekleyin.]

---

ChatCore.AI – Kurumsal RAG Destekli Yapay Zekâ Asistanı. FastAPI + Streamlit + PostgreSQL + Redis + FAISS. Tüm kurulum adımlarını tamamladıktan sonra `http://localhost:8501` üzerinden sisteme erişebilirsiniz. Sorularınız için örnek veri kümesi (çalışan listeleri, departman KPI’ları, projeler, prosedürler) hazır olarak gelir; ihtiyacınıza göre `backend/data/` dizinindeki JSON dosyalarını düzenleyerek kolayca özelleştirebilirsiniz.
