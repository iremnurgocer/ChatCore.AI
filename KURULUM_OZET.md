# Kurulum ve Başlatma - Özet

## Kullanım

### 1. İlk Kurulum
```batch
kurulum.bat
```

Bu script şunları yapar:
- Python kontrolü
- Virtual environment oluşturma
- Bağımlılıkları yükleme
- `.env` dosyası oluşturma
- PostgreSQL ve Redis'i Docker ile başlatma
- Database migration'larını çalıştırma
- Default kullanıcıları oluşturma

### 2. Servisleri Başlatma
```batch
baslat.bat
```

Bu script şunları yapar:
- PostgreSQL ve Redis kontrolü (yoksa başlatır)
- Backend'i başlatır (http://localhost:8000)
- Frontend'i başlatır (http://localhost:8501)

## Gereksinimler

1. **Python 3.8+**
   - İndir: https://www.python.org/downloads/
   - Kurulum sırasında "Add Python to PATH" seçeneğini işaretleyin

2. **Docker Desktop**
   - İndir: https://www.docker.com/products/docker-desktop
   - PostgreSQL ve Redis için gerekli

3. **API Key** (Gemini önerilir)
   - Al: https://makersuite.google.com/app/apikey
   - `backend\.env` dosyasına ekleyin

## Önemli Notlar

- İlk kurulum 5-10 dakika sürebilir
- API key eklemeden uygulama çalışmayacaktır
- Default kullanıcılar: admin/1234, user2/1234, user3/12345
- Production'da şifreleri mutlaka değiştirin!

## Sorun Giderme

### Docker Bulunamadı
- Docker Desktop'u indirin ve başlatın
- Windows'u yeniden başlatın gerekirse

### Port Zaten Kullanılıyor
- Port 8000 veya 8501 kullanılıyorsa, başka uygulamayı kapatın

### Migration Hatası
- Database'in hazır olması için 10 saniye bekleyin
- Manuel: `cd backend && alembic upgrade head`

### API Key Hatası
- `backend\.env` dosyasında `GEMINI_API_KEY` değerini kontrol edin
- API key'in geçerli olduğundan emin olun

