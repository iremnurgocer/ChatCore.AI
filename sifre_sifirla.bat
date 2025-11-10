@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ============================================================
echo Admin Sifre Sifirlama
echo ============================================================
echo.

cd /d "%~dp0"

REM Virtual environment kontrolu
if not exist "venv\Scripts\activate.bat" (
    echo HATA: Virtual environment bulunamadi!
    echo Lutfen once 'kurulum.bat' dosyasini calistirin.
    pause
    exit /b 1
)

REM Virtual environment'i aktiflestir
call venv\Scripts\activate.bat

REM Admin sifresini sifirla
echo Admin sifresi sifirlaniyor...
python backend\scripts\reset_admin_password.py

if errorlevel 1 (
    echo.
    echo HATA: Sifre sifirlama basarisiz!
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Sifre sifirlama tamamlandi!
echo ============================================================
echo.
echo Giris bilgileri:
echo   Kullanici Adi: admin
echo   Sifre: 1234
echo.
pause

