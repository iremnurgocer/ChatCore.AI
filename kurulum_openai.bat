@echo off
chcp 65001 >nul
cls
echo ========================================
echo ChatCore.AI - OpenAI Kurulum
echo ========================================
echo.

REM Proje dizinine git
cd /d "%~dp0"

REM Python kontrolu
echo [1/4] Python kontrol ediliyor...
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

echo.
echo HATA: Python bulunamadi!
echo Python 3.8 veya uzeri kurulu olmali.
echo.
pause
exit /b 1

:python_found
echo OK! Python bulundu
echo.

REM .env dosyasi kontrolu
echo [2/4] .env dosyasi kontrol ediliyor...
if not exist "backend\.env" (
    echo.
    echo UYARI: .env dosyasi bulunamadi!
    echo Once kurulum.bat dosyasini calistirin.
    echo.
    pause
    exit /b 1
)
echo OK! .env dosyasi mevcut
echo.

REM OpenAI bilgilerini al
echo [3/4] OpenAI API Key'ini Girin
echo.
echo NOT: API Key almak icin:
echo      1. https://platform.openai.com/api-keys adresine gidin
echo      2. "Create new secret key" butonuna tiklayin
echo      3. Key'i kopyalayin
echo.
echo Detayli bilgi icin KURULUM_OPENAI.md dosyasina bakin.
echo.

set /p OPENAI_KEY="OpenAI API Key (sk- ile baslayan): "

if "%OPENAI_KEY%"=="" (
    echo.
    echo HATA: API Key bos olamaz!
    pause
    exit /b 1
)

REM Model secimi
echo.
echo Model secimi (opsiyonel):
echo   1. gpt-4o-mini (Hizli, ekonomik - ONERILEN)
echo   2. gpt-4o (En iyi kalite)
echo   3. gpt-3.5-turbo (Cok ekonomik)
echo   4. Varsayilan (gpt-4o-mini)
set /p MODEL_CHOICE="Seciminiz (1-4, varsayilan: 4): "

if "%MODEL_CHOICE%"=="1" set OPENAI_MODEL=gpt-4o-mini
if "%MODEL_CHOICE%"=="2" set OPENAI_MODEL=gpt-4o
if "%MODEL_CHOICE%"=="3" set OPENAI_MODEL=gpt-3.5-turbo
if "%MODEL_CHOICE%"=="" set OPENAI_MODEL=gpt-4o-mini
if "%OPENAI_MODEL%"=="" set OPENAI_MODEL=gpt-4o-mini

echo.
echo [4/4] .env dosyasi guncelleniyor...

REM AI_PROVIDER'i guncelle
powershell -Command "(Get-Content backend\.env) -replace 'AI_PROVIDER=.*', 'AI_PROVIDER=OPENAI' | Set-Content backend\.env"

REM API Key'i guncelle
findstr /C:"OPENAI_API_KEY" backend\.env >nul 2>&1
if %errorlevel% equ 0 (
    powershell -Command "(Get-Content backend\.env) -replace 'OPENAI_API_KEY=.*', 'OPENAI_API_KEY=%OPENAI_KEY%' | Set-Content backend\.env"
) else (
    echo OPENAI_API_KEY=%OPENAI_KEY% >> backend\.env
)

REM Model'i ekle (opsiyonel)
findstr /C:"OPENAI_MODEL" backend\.env >nul 2>&1
if %errorlevel% equ 0 (
    powershell -Command "(Get-Content backend\.env) -replace 'OPENAI_MODEL=.*', 'OPENAI_MODEL=%OPENAI_MODEL%' | Set-Content backend\.env"
) else (
    echo OPENAI_MODEL=%OPENAI_MODEL% >> backend\.env
)

echo OK!
echo.

echo ========================================
echo OpenAI Kurulumu Tamamlandi!
echo ========================================
echo.
echo Yapilandirma:
echo   - AI_PROVIDER: OPENAI
echo   - OPENAI_MODEL: %OPENAI_MODEL%
echo   - API Key: **************** (gizli)
echo.
echo NOT: API Key'inizi guvenli tutun!
echo      Kullanim limitlerinizi kontrol edin: https://platform.openai.com/usage
echo.
echo Detayli bilgi icin KURULUM_OPENAI.md dosyasina bakin.
echo.
echo Simdi baslat.bat dosyasini calistirarak servisleri baslatabilirsiniz.
echo.
pause

