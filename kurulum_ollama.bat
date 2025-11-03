@echo off
chcp 65001 >nul
cls
echo ========================================
echo ChatCore.AI - Ollama Kurulum
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
%PYTHON_CMD% --version
echo.

REM Ollama kontrolu
echo [2/4] Ollama kontrol ediliyor...
ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo Ollama bulunamadi!
    echo ========================================
    echo.
    echo Ollama kurulumu gerekiyor.
    echo.
    echo 1. https://ollama.ai adresine gidin
    echo 2. "Download for Windows" butonuna tiklayin
    echo 3. Indirilen dosyayi kurun
    echo 4. Bu script'i tekrar calistirin
    echo.
    echo NOT: Kurulum.bat dosyasini ONCE calistirmaniz gerekiyor!
    echo.
    pause
    exit /b 1
)
echo OK! Ollama bulundu
ollama --version
echo.

REM Model kontrolu
echo [3/4] Model kontrol ediliyor...
ollama list | findstr "llama3.2" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo Model bulunamadi, indiriliyor...
    echo NOT: Bu islem 5-15 dakika surebilir (internet hiziniza bagli)
    echo.
    ollama pull llama3.2
    if %errorlevel% neq 0 (
        echo.
        echo HATA: Model indirilemedi!
        echo Internet baglantinizi kontrol edin.
        pause
        exit /b 1
    )
    echo.
    echo Model basariyla indirildi!
) else (
    echo OK! Model zaten mevcut
)
echo.

REM .env dosyasi yapilandirma
echo [4/4] .env dosyasi yapilandiriliyor...
if not exist "backend\.env" (
    echo .env dosyasi bulunamadi, kurulum.bat dosyasini calistirin!
    pause
    exit /b 1
)

REM Ollama ayarlarini guncelle
findstr /C:"AI_PROVIDER=OLLAMA" backend\.env >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo AI_PROVIDER=OLLAMA olarak ayarlaniyor...
    powershell -Command "(Get-Content backend\.env) -replace 'AI_PROVIDER=.*', 'AI_PROVIDER=OLLAMA' | Set-Content backend\.env"
)

findstr /C:"OLLAMA_BASE_URL" backend\.env >nul 2>&1
if %errorlevel% neq 0 (
    echo OLLAMA_BASE_URL=http://localhost:11434 olarak ayarlaniyor...
    echo OLLAMA_BASE_URL=http://localhost:11434 >> backend\.env
)

findstr /C:"OLLAMA_MODEL" backend\.env >nul 2>&1
if %errorlevel% neq 0 (
    echo OLLAMA_MODEL=llama3.2 olarak ayarlaniyor...
    echo OLLAMA_MODEL=llama3.2 >> backend\.env
) else (
    REM Model degerini guncelle
    powershell -Command "(Get-Content backend\.env) -replace 'OLLAMA_MODEL=.*', 'OLLAMA_MODEL=llama3.2' | Set-Content backend\.env"
)

echo.
echo ========================================
echo Ollama Kurulumu Tamamlandi!
echo ========================================
echo.
echo Yapilandirma:
echo   - AI_PROVIDER: OLLAMA
echo   - OLLAMA_BASE_URL: http://localhost:11434
echo   - OLLAMA_MODEL: llama3.2
echo.
echo Detayli bilgi icin KURULUM_OLLAMA.md dosyasina bakin.
echo.
echo Simdi baslat.bat dosyasini calistirarak servisleri baslatabilirsiniz.
echo.
pause

