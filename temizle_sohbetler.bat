@echo off
chcp 65001 >nul
echo ========================================
echo ChatCore.AI - Sohbet Geçmişini Temizle
echo ========================================
echo.

cd /d "%~dp0"

if not exist "backend\venv\Scripts\activate.bat" (
    echo HATA: Virtual environment bulunamadi!
    echo Lutfen once 'kurulum.bat' dosyasini calistirin.
    pause
    exit /b 1
)

echo Virtual environment aktiflestiriliyor...
call backend\venv\Scripts\activate.bat

if errorlevel 1 (
    echo HATA: Virtual environment aktiflestirilemedi!
    pause
    exit /b 1
)

echo.
echo Veritabani baglantisi kontrol ediliyor...
python backend\scripts\clear_conversations.py

if errorlevel 1 (
    echo.
    echo HATA: Temizleme basarisiz!
    pause
    exit /b 1
)

echo.
echo Tamamlandi!
pause

