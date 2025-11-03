@echo off
chcp 65001 >nul
cls
echo ========================================
echo ChatCore.AI - Azure OpenAI Kurulum
echo ========================================
echo.

REM Proje dizinine git
cd /d "%~dp0"

REM Python kontrolu
echo [1/5] Python kontrol ediliyor...
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
echo [2/5] .env dosyasi kontrol ediliyor...
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

REM Azure bilgilerini al
echo [3/5] Azure OpenAI Bilgilerini Girin
echo.
echo NOT: Bu bilgileri Azure Portal'dan alabilirsiniz:
echo      https://portal.azure.com
echo.
echo Detayli bilgi icin KURULUM_AZURE.md dosyasina bakin.
echo.

set /p AZURE_KEY="Azure OpenAI API Key (KEY 1 veya KEY 2): "
set /p AZURE_ENDPOINT="Azure OpenAI Endpoint (ornek: https://your-resource.openai.azure.com): "
set /p AZURE_DEPLOYMENT="Deployment Adi (ornek: gpt-4o-mini): "

if "%AZURE_KEY%"=="" (
    echo.
    echo HATA: API Key bos olamaz!
    pause
    exit /b 1
)

if "%AZURE_ENDPOINT%"=="" (
    echo.
    echo HATA: Endpoint bos olamaz!
    pause
    exit /b 1
)

if "%AZURE_DEPLOYMENT%"=="" (
    set AZURE_DEPLOYMENT=gpt-4o-mini
    echo Varsayilan deployment kullaniliyor: gpt-4o-mini
)

echo.
echo [4/5] .env dosyasi guncelleniyor...

REM Endpoint'ten son / karakterini temizle
set AZURE_ENDPOINT=%AZURE_ENDPOINT:/=%
set AZURE_ENDPOINT=%AZURE_ENDPOINT: =%

REM AI_PROVIDER'i guncelle
powershell -Command "(Get-Content backend\.env) -replace 'AI_PROVIDER=.*', 'AI_PROVIDER=AZURE' | Set-Content backend\.env"

REM API Key'i guncelle
findstr /C:"AZURE_OPENAI_API_KEY" backend\.env >nul 2>&1
if %errorlevel% equ 0 (
    powershell -Command "(Get-Content backend\.env) -replace 'AZURE_OPENAI_API_KEY=.*', 'AZURE_OPENAI_API_KEY=%AZURE_KEY%' | Set-Content backend\.env"
) else (
    echo AZURE_OPENAI_API_KEY=%AZURE_KEY% >> backend\.env
)

REM Endpoint'i guncelle
findstr /C:"AZURE_OPENAI_ENDPOINT" backend\.env >nul 2>&1
if %errorlevel% equ 0 (
    powershell -Command "(Get-Content backend\.env) -replace 'AZURE_OPENAI_ENDPOINT=.*', 'AZURE_OPENAI_ENDPOINT=%AZURE_ENDPOINT%' | Set-Content backend\.env"
) else (
    echo AZURE_OPENAI_ENDPOINT=%AZURE_ENDPOINT% >> backend\.env
)

REM Deployment'i guncelle
findstr /C:"AZURE_OPENAI_DEPLOYMENT" backend\.env >nul 2>&1
if %errorlevel% equ 0 (
    powershell -Command "(Get-Content backend\.env) -replace 'AZURE_OPENAI_DEPLOYMENT=.*', 'AZURE_OPENAI_DEPLOYMENT=%AZURE_DEPLOYMENT%' | Set-Content backend\.env"
) else (
    echo AZURE_OPENAI_DEPLOYMENT=%AZURE_DEPLOYMENT% >> backend\.env
)

echo OK!
echo.

echo [5/5] Yapilandirma dogrulaniyor...
echo.
echo Yapilandirma Ozeti:
echo   - AI_PROVIDER: AZURE
echo   - AZURE_OPENAI_ENDPOINT: %AZURE_ENDPOINT%
echo   - AZURE_OPENAI_DEPLOYMENT: %AZURE_DEPLOYMENT%
echo   - API Key: **************** (gizli)
echo.

echo ========================================
echo Azure OpenAI Kurulumu Tamamlandi!
echo ========================================
echo.
echo NOT: Azure Portal'dan deployment'in aktif oldugundan emin olun.
echo      Detayli bilgi icin KURULUM_AZURE.md dosyasina bakin.
echo.
echo Simdi baslat.bat dosyasini calistirarak servisleri baslatabilirsiniz.
echo.
pause

