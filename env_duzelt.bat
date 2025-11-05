@echo off
setlocal enabledelayedexpansion
cls
echo ========================================
echo .env Dosyasi Duzenleme
echo ========================================
echo.

REM Proje dizinine git
cd /d "%~dp0"

REM .env dosyasi kontrolu
if not exist "backend\.env" (
    echo HATA: backend\.env dosyasi bulunamadi!
    echo database_kur.bat script'ini calistirin.
    pause
    exit /b 1
)

echo Mevcut .env dosyasi bulundu.
echo DATABASE_URL formatini duzeltiyoruz...
echo.

REM .env dosyasini oku ve duzenle
set "tempfile=%TEMP%\env_temp_%RANDOM%.txt"
(
    for /f "usebackq tokens=*" %%a in ("backend\.env") do (
        set "line=%%a"
        setlocal enabledelayedexpansion
        set "line=!line:postgresql+asyncpg://=postgresql://!"
        echo !line!
        endlocal
    )
) > "%tempfile%"

REM Gecici dosyayi .env'e kopyala
move /y "%tempfile%" "backend\.env" >nul

echo OK! .env dosyasi duzenlendi!
echo.
echo Simdi migration'i tekrar calistirin:
echo   cd backend
echo   alembic upgrade head
echo.
pause

