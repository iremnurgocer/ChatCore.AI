@echo off
chcp 65001 >nul
cls
echo ========================================
echo ChatCore.AI - Servisleri Baslatma
echo ========================================
echo.

cd /d "%~dp0"

REM Python kontrolu
set PYTHON_CMD=
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    goto :python_found
)
py --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py
    goto :python_found
)

echo HATA: Python bulunamadi!
echo Once kurulum.bat dosyasini calistirin.
pause
exit /b 1

:python_found

REM .env dosyasi kontrolu
if not exist "backend\.env" (
    echo.
    echo HATA: .env dosyasi bulunamadi!
    echo Once kurulum.bat dosyasini calistirin.
    pause
    exit /b 1
)

REM Virtual environment kontrolu
if not exist "venv\Scripts\activate.bat" (
    echo.
    echo HATA: Virtual environment bulunamadi!
    echo Once kurulum.bat dosyasini calistirin.
    pause
    exit /b 1
)

REM Docker servislerini kontrol et ve baslat
echo Database servisleri kontrol ediliyor...
docker ps --filter "name=chatcore_postgres" --format "{{.Names}}" | findstr /C:"chatcore_postgres" >nul 2>&1
if errorlevel 1 (
    echo PostgreSQL ve Redis baslatiliyor...
    docker compose up -d postgres redis
    if errorlevel 1 (
        echo.
        echo HATA: Database servisleri baslatilamadi!
        echo Docker Desktop'un calistigindan emin olun.
        pause
        exit /b 1
    )
    echo Database servisleri baslatildi!
    echo Servislerin hazir olmasi bekleniyor...
    timeout /t 10 /nobreak >nul
) else (
    echo Database servisleri zaten calisiyor.
)
echo.

REM Backend'i baslat
echo [1/2] Backend baslatiliyor (Port 8000)...
start "ChatCore Backend" cmd /k "cd /d %~dp0backend && call ..\venv\Scripts\activate.bat && %PYTHON_CMD% -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

REM Backend'in baslamasi icin bekle
echo Backend'in hazir olmasi bekleniyor...
timeout /t 5 /nobreak >nul
echo.

REM Frontend'i baslat
echo [2/2] Frontend baslatiliyor (Port 8501)...
start "ChatCore Frontend" cmd /k "cd /d %~dp0 && call venv\Scripts\activate.bat && cd frontend && %PYTHON_CMD% -m streamlit run app.py --server.headless true"

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
echo Tarayicinizda: http://localhost:8501
echo API Docs: http://localhost:8000/docs
echo.
echo Default Giris:
echo   Username: admin
echo   Password: 1234
echo.
echo Servisleri durdurmak icin acilan pencereleri kapatin.
echo.
pause
