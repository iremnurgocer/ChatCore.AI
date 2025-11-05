@echo off
chcp 65001 >nul
cls
echo ============================================================
echo ChatCore.AI - Veri Yukleme Scripti
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

REM Database baglantisini test et
echo.
echo [1/2] Database baglantisi test ediliyor...
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

REM Baslangic verilerini yukle
echo.
echo [2/2] Baslangic verileri yukleniyor...
call venv\Scripts\activate.bat
cd backend
%PYTHON_CMD% scripts\seed_data.py
cd ..

echo.
echo ============================================================
echo Tamamlandi
echo ============================================================
echo.
echo Notlar:
echo - Kullanici verileri: scripts\seed_users.py ile yuklendi
echo - Baslangic verileri: scripts\seed_data.py ile yuklendi
echo - Backend'i yeniden baslatmaniz gerekebilir
echo.
pause

