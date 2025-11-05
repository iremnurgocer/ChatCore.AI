@echo off
setlocal enabledelayedexpansion
cls
echo ========================================
echo Database Kurulum Scripti
echo ========================================
echo.

REM Proje dizinine git
cd /d "%~dp0"

REM Docker kontrolu
echo [1/4] Docker kontrolu...
docker --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo HATA: Docker bulunamadi!
    echo.
    echo Lutfen Docker Desktop'i kurun:
    echo https://www.docker.com/products/docker-desktop
    echo.
    echo Docker Desktop'i kurduktan sonra:
    echo 1. Docker Desktop'i baslatin
    echo 2. Bu script'i tekrar calistirin
    echo.
    pause
    exit /b 1
)
echo OK! Docker bulundu
docker --version
echo.

REM .env dosyasi kontrolu ve olusturma
echo [2/4] .env dosyasi kontrolu...
if not exist "backend\.env" (
    echo .env dosyasi olusturuluyor...
    (
        echo DATABASE_URL=postgresql://postgres:postgres@localhost:5432/chatcore
        echo REDIS_HOST=localhost
        echo REDIS_PORT=6379
        echo SECRET_KEY=CHANGE_THIS_IN_PRODUCTION
        echo AI_PROVIDER=GEMINI
        echo GEMINI_API_KEY=your-gemini-api-key-here
        echo COMPANY_NAME=Company1
        echo ALLOWED_ORIGINS=http://localhost:8501,http://127.0.0.1:8501
    ) > backend\.env
    echo OK! .env dosyasi olusturuldu!
) else (
    echo .env dosyasi zaten mevcut.
)
echo.

REM Docker servislerini baslat
echo [3/4] PostgreSQL ve Redis baslatiliyor...
echo Docker Desktop'in calistigindan emin olun!
echo.
docker compose up -d postgres redis
if errorlevel 1 (
    echo.
    echo HATA: Docker servisleri baslatilamadi!
    echo.
    echo Kontrol edin:
    echo 1. Docker Desktop calisiyor mu?
    echo 2. Port 5432 ve 6379 bos mu?
    echo.
    pause
    exit /b 1
)
echo OK! Docker servisleri baslatildi!
echo Servislerin hazir olmasi bekleniyor...
timeout /t 15 /nobreak >nul
echo.

REM Database migration
echo [4/4] Database migration calistiriliyor...
cd backend
if exist "..\venv\Scripts\activate.bat" (
    call ..\venv\Scripts\activate.bat
)

echo Migration'lar calistiriliyor...
alembic upgrade head
if errorlevel 1 (
    echo.
    echo HATA: Migration basarisiz!
    echo Database hazir olmayabilir.
    echo 10 saniye bekleyip tekrar deneyin veya manuel calistirin:
    echo   cd backend ^&^& alembic upgrade head
    cd ..
    pause
    exit /b 1
)
echo OK! Migration'lar tamamlandi!
echo.

echo Default kullanicilar olusturuluyor...
python scripts\seed_users.py
if errorlevel 1 (
    echo UYARI: Kullanici olusturulamadi!
    echo Manuel olarak calistirin: python backend\scripts\seed_users.py
) else (
    echo OK! Default kullanicilar olusturuldu!
)
cd ..
echo.

echo ========================================
echo DATABASE KURULUMU TAMAMLANDI!
echo ========================================
echo.
echo Database servisleri calisiyor:
echo - PostgreSQL: localhost:5432
echo - Redis: localhost:6379
echo.
echo Default kullanicilar:
echo - admin / 1234 (Admin)
echo - user2 / 1234 (User)
echo - user3 / 12345 (User)
echo.
echo ONEMLI: Backend'i yeniden baslatin!
echo.
pause

