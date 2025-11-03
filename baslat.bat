@echo off
REM Script'in kapanmamasini saglamak icin
if "%1"=="" (
    start cmd /k "%~f0" keepopen
    exit /b
)

chcp 65001 >nul
cls

echo ========================================
echo ChatCore.AI - Servisleri Baslatma
echo ========================================
echo.

cd /d "%~dp0"

REM Python komutunu bul (python ve py test et)
set PYTHON_CMD=
echo Python komutu araniyor...

REM python komutunu test et
python --version >nul 2>&1
set PYTHON_TEST=%errorlevel%
if %PYTHON_TEST% equ 0 (
    set PYTHON_CMD=python
    echo Python bulundu: python
    goto :python_found
)

REM py komutunu test et
py --version >nul 2>&1
set PY_TEST=%errorlevel%
if %PY_TEST% equ 0 (
    set PYTHON_CMD=py
    echo Python bulundu: py
    goto :python_found
)

REM Python bulunamadi
echo.
echo ========================================
echo [HATA] Python bulunamadi!
echo ========================================
echo.
echo Hem "python" hem de "py" komutlari test edildi.
echo Python kurulu olmali ve PATH'te olmali.
echo.
echo Cozum:
echo 1. Python kurun: https://www.python.org/downloads/
echo 2. Kurulum sirasinda "Add Python to PATH" secenegini isaretleyin
echo 3. Windows'u yeniden baslatin
echo.
pause
exit /b 1

:python_found

REM .env dosyasi kontrolu
echo .env dosyasi kontrol ediliyor...
if not exist "backend\.env" (
    echo.
    echo [UYARI] .env dosyasi bulunamadi!
    echo.
    echo Once kurulum.bat dosyasini calistirin.
    echo.
    pause
    exit /b 1
)

REM Virtual environment kontrolu
if not exist "backend\venv\Scripts\activate.bat" (
    echo.
    echo [UYARI] Virtual environment bulunamadi!
    echo.
    echo Once kurulum.bat dosyasini calistirin.
    echo.
    pause
    exit /b 1
)

REM Backend'i baslat
echo [1/2] Backend baslatiliyor (Port 8000)...
start "ChatCore Backend" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate.bat && %PYTHON_CMD% -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

REM Backend'in baslamasi ve hazir olmasi icin bekle
echo Backend'in hazir olmasi bekleniyor...
echo NOT: Bu islem 5-10 saniye surebilir...
timeout /t 5 /nobreak >nul
echo.

REM Frontend'i baslat
echo [2/2] Frontend baslatiliyor (Port 8501)...
start "ChatCore Frontend" cmd /k "cd /d %~dp0 && call backend\venv\Scripts\activate.bat && cd frontend && %PYTHON_CMD% -m streamlit run app.py --server.headless true"

timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo Servisler Baslatildi!
echo ========================================
echo.
echo Iki pencere acildi:
echo   - Backend (Port 8000)
echo   - Frontend (Port 8501)
echo.
echo HATA DURUMUNDA:
echo   - Backend penceresindeki hata mesajlarini kontrol edin
echo   - Frontend penceresindeki hata mesajlarini kontrol edin
echo   - Hatalar kategorize sekilde backend\logs\ klasorunde loglanir:
echo     * errors.log - Tum hatalar (kategori bazli)
echo     * security.log - Guvenlik olaylari
echo     * api.log - Genel API loglari
echo.
echo Tarayicinizda: http://localhost:8501
echo API Docs: http://localhost:8000/docs
echo Giris: admin / 1234
echo.
echo Servisleri durdurmak icin acilan pencereleri kapatin.
echo.
pause
