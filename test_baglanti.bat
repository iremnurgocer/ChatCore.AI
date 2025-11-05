@echo off
chcp 65001 >nul
cls
echo ============================================================
echo ChatCore.AI - Baglanti Test Scripti
echo ============================================================
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
pause
exit /b 1

:python_found

REM Virtual environment kontrolu
if not exist "venv\Scripts\activate.bat" (
    echo HATA: Virtual environment bulunamadi!
    echo Once kurulum.bat dosyasini calistirin.
    pause
    exit /b 1
)

REM Docker servislerini kontrol et
echo.
echo [1/4] Docker servisleri kontrol ediliyor...
docker ps --filter "name=chatcore_postgres" --format "{{.Names}}" | findstr /C:"chatcore_postgres" >nul 2>&1
if errorlevel 1 (
    echo [WARN] PostgreSQL container calismiyor. Baslatiliyor...
    docker compose up -d postgres redis
    if errorlevel 1 (
        echo.
        echo HATA: Database servisleri baslatilamadi!
        echo Docker Desktop'un calistigindan emin olun.
        pause
        exit /b 1
    )
    echo Servislerin hazir olmasi bekleniyor...
    timeout /t 10 /nobreak >nul
) else (
    echo [OK] PostgreSQL ve Redis container'lari calisiyor
)

REM Database baglantisini test et
echo.
echo [2/4] Database baglantisi test ediliyor...
call venv\Scripts\activate.bat
cd backend
%PYTHON_CMD% scripts\test_db.py
if errorlevel 1 (
    echo.
    echo [WARN] Database testi basarisiz oldu. Database'i kontrol edin.
    cd ..
    pause
    exit /b 1
)
cd ..

REM Backend'in calistigini kontrol et
echo.
echo [3/4] Backend servisinin calistigini kontrol ediliyor...
%PYTHON_CMD% backend\scripts\test_connection.py >nul 2>&1
if errorlevel 1 (
    echo [WARN] Backend servisi calisiyor gibi gorunmuyor.
    echo Backend'i baslatmak icin: baslat.bat
) else (
    echo [OK] Backend servisi calisiyor (http://localhost:8000)
)

echo.
echo ============================================================
echo Test Tamamlandi
echo ============================================================
echo.
echo Notlar:
echo - Database baglantisi: scripts\test_db.py ile test edildi
echo - Backend servisi: http://localhost:8000
echo - Frontend: http://localhost:8501 (Streamlit)
echo.
pause

