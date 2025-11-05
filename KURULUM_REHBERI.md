# ChatCore.AI Kurulum ve Başlatma Rehberi

## Hızlı Başlangıç

### 1. Gereksinimler

- **Python 3.8+** (https://www.python.org/downloads/)
- **Docker Desktop** (PostgreSQL ve Redis için) (https://www.docker.com/products/docker-desktop)
- **Git** (opsiyonel, projeyi klonlamak için)

### 2. Kurulum Adımları

**Windows:**
1. `kurulum.bat` dosyasına çift tıklayın
2. Script otomatik olarak:
   - Python kontrolü yapar
   - Virtual environment oluşturur
   - Bağımlılıkları yükler
   - `.env` dosyası oluşturur
   - PostgreSQL ve Redis'i Docker ile başlatır
   - Database migration'larını çalıştırır
   - Default kullanıcıları oluşturur

**Not:** İlk kurulum 5-10 dakika sürebilir (paket indirme)

### 3. API Key Yapılandırması (Gerekli)

Kurulumdan sonra `backend\.env` dosyasını açın ve AI sağlayıcınızın API key'ini ekleyin:

**Gemini (Önerilen - Ücretsiz):**
```
GEMINI_API_KEY=your-api-key-here
```
API Key almak için: https://makersuite.google.com/app/apikey

**Diğer Seçenekler:**
- OpenAI: `OPENAI_API_KEY=...`
- Azure: `AZURE_OPENAI_API_KEY=...` ve `AZURE_OPENAI_ENDPOINT=...`
- Ollama: Yerel kurulum gerektirir

### 4. Uygulamayı Başlatma

**Windows:**
```
baslat.bat
```

Bu script:
- PostgreSQL ve Redis'in çalıştığını kontrol eder
- Backend'i başlatır (http://localhost:8000)
- Frontend'i başlatır (http://localhost:8501)

### 5. Giriş Yapma

Tarayıcıda http://localhost:8501 adresine gidin

**Default Kullanıcılar:**
- Username: `admin`, Password: `1234` (Admin)
- Username: `user2`, Password: `1234` (User)
- Username: `user3`, Password: `12345` (User)

**Güvenlik Notu:** Production'da mutlaka şifreleri değiştirin!

## Sorun Giderme

### Python Bulunamadı
- Python'u https://www.python.org/downloads/ adresinden indirin
- Kurulum sırasında "Add Python to PATH" seçeneğini işaretleyin
- Windows'u yeniden başlatın

### Docker Bulunamadı
- Docker Desktop'u https://www.docker.com/products/docker-desktop adresinden indirin
- Docker Desktop'u başlatın ve çalıştığından emin olun

### Database Bağlantı Hatası
- Docker Desktop'un çalıştığından emin olun
- `docker compose ps` komutuyla container'ların çalıştığını kontrol edin
- `docker compose up -d postgres redis` ile yeniden başlatın

### Port Zaten Kullanılıyor
- Port 8000 veya 8501 başka bir uygulama tarafından kullanılıyor olabilir
- O uygulamayı kapatın veya `.env` dosyasında portları değiştirin

### Migration Hatası
- Veritabanının hazır olduğundan emin olun (10 saniye bekleyin)
- Manuel olarak çalıştırın: `cd backend && alembic upgrade head`

### Bağımlılık Hataları
- Virtual environment'ın aktif olduğundan emin olun
- `pip install -r backend/requirements-refactored.txt` komutunu manuel çalıştırın

## Manuel Kurulum

Eğer script'ler çalışmıyorsa:

1. **Virtual Environment:**
   ```batch
   python -m venv venv
   venv\Scripts\activate.bat
   ```

2. **Bağımlılıklar:**
   ```batch
   pip install -r backend/requirements-refactored.txt
   ```

3. **Environment Dosyası:**
   ```batch
   copy backend\.env.example backend\.env
   ```

4. **Docker Servisleri:**
   ```batch
   docker compose up -d postgres redis
   ```

5. **Migration:**
   ```batch
   cd backend
   alembic upgrade head
   python scripts\seed_users.py
   ```

6. **Başlatma:**
   ```batch
   cd backend
   uvicorn main:app --reload
   ```
   (Yeni terminal)
   ```batch
   cd frontend
   streamlit run app.py
   ```

## Eksik Dosyalar

Eğer `.env.example` dosyası yoksa, `backend/.env` dosyasını manuel oluşturun:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/chatcore
REDIS_HOST=localhost
REDIS_PORT=6379
SECRET_KEY=CHANGE_THIS_IN_PRODUCTION
AI_PROVIDER=GEMINI
GEMINI_API_KEY=your-api-key-here
COMPANY_NAME=Company1
```

## İletişim ve Destek

Sorun yaşarsanız:
1. `backend/logs/` klasöründeki log dosyalarını kontrol edin
2. Backend ve Frontend pencerelerindeki hata mesajlarını inceleyin
3. Docker container loglarını kontrol edin: `docker compose logs`



