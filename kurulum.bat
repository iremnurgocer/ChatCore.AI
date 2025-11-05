@echo off
setlocal enabledelayedexpansion
cls
echo ========================================
echo ChatCore.AI - Otomatik Kurulum
echo ========================================
echo.

REM Proje dizinine git
cd /d "%~dp0"

REM Python kontrolu
echo [1/7] Python kontrol ediliyor...
set PYTHON_CMD=
python --version >nul 2>&1
if !errorlevel! equ 0 (
    set PYTHON_CMD=python
    goto :python_found
)
py --version >nul 2>&1
if !errorlevel! equ 0 (
    set PYTHON_CMD=py
    goto :python_found
)

echo.
echo ========================================
echo HATA: Python bulunamadi!
echo ========================================
echo.
echo Python 3.8+ kurulu olmali.
echo Indir: https://www.python.org/downloads/
echo Kurulum sirasinda "Add Python to PATH" secenegini isaretleyin
echo.
pause
exit /b 1

:python_found
echo OK! Python bulundu
!PYTHON_CMD! --version
echo.

REM Virtual environment kontrolu ve olusturma
echo [2/7] Virtual Environment kontrolu...
if exist "venv\Scripts\activate.bat" (
    echo Virtual environment zaten mevcut.
    goto :venv_ready
)
echo Virtual environment olusturuluyor...
!PYTHON_CMD! -m venv venv
if errorlevel 1 (
    echo HATA: Virtual environment olusturulamadi!
    pause
    exit /b 1
)
echo Virtual environment olusturuldu!
:venv_ready
echo.

REM Virtual environment'i aktifleştir
echo [3/7] Virtual environment aktiflestiriliyor...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    if errorlevel 1 (
        echo HATA: Virtual environment aktiflestirilemedi!
        pause
        exit /b 1
    )
    echo Virtual environment aktiflestirildi!
) else (
    echo UYARI: activate.bat dosyasi bulunamadi!
    echo Virtual environment tam olusturulmamis olabilir.
    echo Tekrar olusturuluyor...
    !PYTHON_CMD! -m venv venv
    if errorlevel 1 (
        echo HATA: Virtual environment olusturulamadi!
        pause
        exit /b 1
    )
    call venv\Scripts\activate.bat
    if errorlevel 1 (
        echo HATA: Virtual environment aktiflestirilemedi!
        pause
        exit /b 1
    )
)
echo.

REM Pip'i guncelle
echo [4/7] Pip guncelleniyor...
!PYTHON_CMD! -m pip install --upgrade pip --quiet
echo OK!
echo.

REM Bagimliliklari yukle
echo [5/7] Bagimliliklar yukleniyor...
echo NOT: Bu islem 3-5 dakika surebilir...
echo.
cd backend
!PYTHON_CMD! -m pip install -r requirements-refactored.txt
if errorlevel 1 (
    echo.
    echo HATA: Bagimliliklar yuklenemedi!
    cd ..
    pause
    exit /b 1
)
cd ..
echo.
echo Bagimliliklar yuklendi!
echo.

REM .env dosyasi kontrolu ve olusturma
echo [6/7] Yapilandirma dosyasi kontrolu...
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
    echo .env dosyasi olusturuldu!
    goto :env_ready
)
echo .env dosyasi zaten mevcut.
:env_ready
echo.

REM Docker kontrolu
echo [7/7] Docker kontrolu...
docker --version >nul 2>&1
if errorlevel 1 (
    echo UYARI: Docker bulunamadi!
    echo PostgreSQL ve Redis manuel baslatilmalidir.
    echo Docker Desktop indir: https://www.docker.com/products/docker-desktop
    set DOCKER_AVAILABLE=0
    goto :docker_check_done
)
echo Docker bulundu!
set DOCKER_AVAILABLE=1
:docker_check_done
echo.

REM Docker servislerini baslat
echo Database servisleri baslatiliyor...
if "%DOCKER_AVAILABLE%"=="1" (
    echo PostgreSQL ve Redis baslatiliyor...
    docker compose up -d postgres redis
    if errorlevel 1 (
        echo UYARI: Docker servisleri baslatilamadi!
        echo Docker Desktop'un calistigindan emin olun.
        goto :docker_done
    )
    echo Database servisleri baslatildi!
    echo Servislerin hazir olmasi bekleniyor...
    timeout /t 10 /nobreak >nul
    goto :docker_done
)
echo Docker yok, servisler atlaniyor.
echo PostgreSQL ve Redis'i manuel baslatmalisiniz.
:docker_done
echo.

REM Database migration ve seed
echo Database hazirlaniyor...
cd backend
if exist "..\venv\Scripts\activate.bat" (
    call ..\venv\Scripts\activate.bat
)

echo Migration'lar calistiriliyor...
alembic upgrade head
if errorlevel 1 (
    echo UYARI: Migration basarisiz! Database hazir olmayabilir.
    echo 10 saniye bekleyip tekrar deneyin veya manuel calistirin:
    echo   cd backend ^&^& alembic upgrade head
    goto :migration_done
)
echo Migration'lar tamamlandi!
:migration_done
echo.

echo Default kullanicilar olusturuluyor...
python scripts\seed_users.py
if errorlevel 1 (
    echo UYARI: Kullanici olusturulamadi!
    echo Manuel olarak calistirin: python backend\scripts\seed_users.py
    goto :seed_done
)
echo Default kullanicilar olusturuldu!
:seed_done
cd ..
echo.

echo ========================================
echo KURULUM TAMAMLANDI!
echo ========================================
echo.
echo ONEMLI ADIMLAR:
echo.
echo 1. API KEY EKLEME (Gerekli):
echo    - backend\.env dosyasini acin
echo    - GEMINI_API_KEY=your-gemini-api-key-here satirini bulun
echo    - your-gemini-api-key-here yerine API anahtarinizi yapistirin
echo    - Dosyayi kaydedin
echo.
echo    API Key almak icin: https://makersuite.google.com/app/apikey
echo.
echo 2. SERVISLERI BASLATMA:
echo    - baslat.bat dosyasina cift tiklayin
echo    - Backend ve Frontend otomatik baslar
echo    - Tarayicinizda: http://localhost:8501
echo    - Giris: admin / 1234
echo.
echo Default kullanicilar:
echo - admin / 1234 (Admin)
echo - user2 / 1234 (User)
echo - user3 / 12345 (User)
echo.
pause
