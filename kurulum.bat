@echo off
chcp 65001 >nul
cls
echo ========================================
echo ChatCore.AI - Otomatik Kurulum
echo ========================================
echo.

REM Proje dizinine git
cd /d "%~dp0"

REM Python kontrolu (hem python hem py komutlarini test et)
echo [1/6] Python kontrol ediliyor...
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

REM Python bulunamadi
echo.
echo ========================================
echo HATA: Python bulunamadi!
echo ========================================
echo.
echo Python 3.8 veya uzeri kurulu olmali.
echo.
echo Cozum Secenekleri:
echo.
echo SECENEK 1 - Manuel Kurulum (Onerilen):
echo 1. Python indirin: https://www.python.org/downloads/
echo 2. Kurulum sirasinda MUTLAKA "Add Python to PATH" secenegini isaretleyin
echo 3. Windows'u yeniden baslatin
echo 4. Tekrar kurulum.bat dosyasini calistirin
echo.
echo SECENEK 2 - Otomatik PATH Ekleme (Denenebilir):
echo Python kurulu ama PATH'te degil. PATH'e eklemek ister misiniz?
echo (Y) Evet, PATH'e ekle
echo (N) Hayir, manuel yapacagim
choice /C YN /N /M "Seciminiz: "
if errorlevel 2 goto :python_not_found_exit
if errorlevel 1 goto :try_add_python_path

:try_add_python_path
echo.
echo Python kurulum yolunu ariyorum...
REM Python'un muhtemel kurulum yerlerini kontrol et
set PYTHON_PATHS=^
"C:\Python3*\python.exe" ^
"C:\Program Files\Python3*\python.exe" ^
"C:\Program Files (x86)\Python3*\python.exe" ^
"%LOCALAPPDATA%\Programs\Python\Python3*\python.exe" ^
"%APPDATA%\Python\Python3*\python.exe"

for %%P in (%PYTHON_PATHS%) do (
    if exist %%P (
        echo Python bulundu: %%P
        REM Python dizinini PATH'e eklemek icin setx kullan
        for /f "tokens=*" %%D in ("%%~dpP") do (
            echo PATH'e ekleniyor...
            setx PATH "%PATH%;%%D;%%DScripts" >nul 2>&1
            if %errorlevel% equ 0 (
                echo OK! PATH'e eklendi. YENI bir komut istemi acin ve tekrar deneyin.
            ) else (
                echo UYARI: PATH'e eklenemedi. Yonetici olarak calistirin.
            )
        )
        goto :python_not_found_exit
    )
)

echo Python otomatik bulunamadi. Manuel kurulum yapmaniz gerekiyor.
goto :python_not_found_exit

:python_not_found_exit
echo.
echo Python kurulumu icin: https://www.python.org/downloads/
echo.
echo Herhangi bir tusa basiniz ve cikmak icin...
pause
exit /b 1

:python_found
echo OK! Python bulundu (%PYTHON_CMD%)
%PYTHON_CMD% --version
echo.

REM Virtual environment kontrolu ve olusturma
echo [2/6] Virtual Environment kontrolu...
if exist "backend\venv" (
    echo Virtual environment zaten mevcut, kurulum atlaniyor.
    echo Kurulumu sifirdan yapmak isterseniz backend\venv klasorunu silin.
) else (
    echo Virtual environment olusturuluyor...
    cd backend
    %PYTHON_CMD% -m venv venv
    if errorlevel 1 (
        echo HATA: Virtual environment olusturulamadi!
        pause
        exit /b 1
    )
    cd ..
    echo Virtual environment olusturuldu!
)
echo.

REM Virtual environment'i aktifleştir
call backend\venv\Scripts\activate.bat
if errorlevel 1 (
    echo HATA: Virtual environment aktiflestirilemedi!
    pause
    exit /b 1
)

REM Pip'i guncelle
echo [3/6] Pip guncelleniyor...
%PYTHON_CMD% -m pip install --upgrade pip --quiet --progress-bar off
if errorlevel 1 (
    echo UYARI: Pip guncellenemedi, devam ediliyor...
) else (
    echo OK!
)
echo.

REM Bagimliliklari kontrol et ve sadece eksikleri yukle
echo [4/6] Bagimliliklar kontrol ediliyor ve yukleniyor...
cd backend
echo.

REM Temel paketleri kontrol et
echo Bagimliliklar kontrol ediliyor...
%PYTHON_CMD% -c "import fastapi, streamlit, langchain, openai" 2>nul
if errorlevel 1 (
    echo.
    echo Eksik bagimliliklar bulundu, yukleniyor...
    echo.
    echo NOT: Bu islem 2-5 dakika surebilir.
    echo      Paketler sirasiyla indirilip kuruluyor...
    echo.
    echo ----------------------------------------
    echo [KURULUM BASLADI]
    echo ----------------------------------------
    echo.
    echo Paketler kurulurken her paket ve ilerleme goruntulenecek...
    echo.
    %PYTHON_CMD% -m pip install -r requirements.txt --no-warn-script-location
    if errorlevel 1 (
        echo.
        echo ========================================
        echo HATA: Bagimliliklar yuklenemedi!
        echo ========================================
        echo.
        echo Lutfen hatalari kontrol edin.
        cd ..
        pause
        exit /b 1
    )
    echo.
    echo ----------------------------------------
    echo [KURULUM TAMAMLANDI]
    echo ----------------------------------------
) else (
    echo.
    echo Tum temel bagimliliklar zaten yuklu!
    echo Uyumluluk kontrolu yapiliyor...
    echo.
    REM Kritik paketleri guncelle (uyumsuzluk sorunlari icin)
    echo ----------------------------------------
    echo Kritik paketler guncelleniyor...
    echo ----------------------------------------
    echo.
    echo [1/3] Pydantic-core guncelleniyor (uyumluluk icin kritik)...
    %PYTHON_CMD% -m pip install --upgrade "pydantic-core>=2.23.0" --no-warn-script-location
    echo.
    echo [2/3] Pydantic guncelleniyor...
    %PYTHON_CMD% -m pip install --upgrade "pydantic>=2.9.0,<3.0.0" --no-warn-script-location
    echo.
    echo [3/3] LangChain paketleri guncelleniyor...
    %PYTHON_CMD% -m pip install --upgrade "langchain>=0.2.0" "langchain-openai>=0.1.0" "langchain-community>=0.2.0" "langchain-core>=0.2.0" --no-warn-script-location
    echo.
    echo ----------------------------------------
    echo Eksik paketler kontrol ediliyor...
    echo ----------------------------------------
    echo.
    %PYTHON_CMD% -m pip install -r requirements.txt --upgrade-strategy only-if-needed --no-warn-script-location
    if errorlevel 1 (
        echo.
        echo UYARI: Bazı paketler guncellenemedi, ama devam ediliyor...
    ) else (
        echo.
        echo Bagimliliklar guncellendi (sadece gerekenler).
    )
)
echo.
cd ..
echo.

REM Bagimlilik dogrulama
echo [5/6] Bagimliliklar dogrulanıyor...
%PYTHON_CMD% -c "import fastapi; import streamlit; import langchain; import openai; import tinydb; print('OK - Tüm ana bagimliliklar yuklu!')" 2>nul
if errorlevel 1 (
    echo UYARI: Bazı bagimliliklar eksik olabilir.
    echo Tekrar yuklemek icin kurulum.bat dosyasini calistirin.
    echo.
    echo Eksik paketleri kontrol ediliyor...
    %PYTHON_CMD% -c "import tinydb" 2>nul
    if errorlevel 1 (
        echo TinyDB eksik, yukleniyor...
        %PYTHON_CMD% -m pip install "tinydb>=4.8.0" --quiet --no-warn-script-location
    )
) else (
    echo Tüm ana bagimliliklar dogrulandi ve hazir!
)
echo.

REM Backend modül kontrolü
echo Backend modülleri test ediliyor...
cd backend
%PYTHON_CMD% -c "from dotenv import load_dotenv; load_dotenv(); from ai_service import ask_ai, AI_PROVIDER; print('OK - AI service yuklu')" 2>nul
if errorlevel 1 (
    echo UYARI: AI service modulu test edilemedi, ama devam ediliyor...
) else (
    echo Backend modülleri hazir!
)
cd ..
echo.

REM .env dosyasi kontrolu ve olusturma
echo [6/6] Yapilandirma dosyasi kontrolu...
if not exist "backend\.env" (
    echo .env dosyasi bulunamadi, kapsamli sabbon olusturuluyor...
    (
        echo # ==========================================
        echo # AI SAGLAYICI AYARLARI
        echo # ==========================================
        echo # Hangi AI saglayiciyi kullanmak istiyorsunuz?
        echo # Secenekler: GEMINI, OLLAMA, OPENAI, AZURE, HUGGINGFACE, LOCAL
        echo #.
        echo # TAVSIYE EDILEN ^(Azure benzeri, ucretsiz^):
        echo # GEMINI: Bulut tabanli, API key ile, ucretsiz katman, kurulum gerektirmez
        echo #         Azure/OpenAI gibi calisir ama ucretsiz!
        echo #.
        echo # Diger Secenekler:
        echo # OLLAMA: Yerel, tamamen ucretsiz ama model indirme gerekir ^(2-4GB^)
        echo # OPENAI: Ucretli, en iyi kalite
        echo # AZURE: Ucretli, kurumsal cozum
        echo AI_PROVIDER=GEMINI
        echo.
        echo # ==========================================
        echo # Google Gemini ^(AZURE BENZERI - UCRETSIZ^)
        echo # ==========================================
        echo # Azure/OpenAI gibi bulut tabanli, API key ile calisir
        echo # TAM UCRETSIZ: Gunluk sorgu limiti var ama normal kullanim icin yeterli
        echo # Kurulum gerektirmez, sadece API key yeterli
        echo #.
        echo # Nasil API Key Alinir:
        echo # 1. https://makersuite.google.com/app/apikey adresine gidin
        echo # 2. Google hesabinizla giris yapin
        echo # 3. "Create API Key" butonuna tiklayin
        echo # 4. Olusturulan key'i buraya yapistirin
        echo GEMINI_API_KEY=your-gemini-api-key-here
        echo.
        echo # ==========================================
        echo # OpenAI ^(UCRETLI - En iyi kalite^)
        echo # ==========================================
        echo # Ucretli servis, en iyi AI kalitesi
        echo # API Key almak icin: https://platform.openai.com/api-keys
        echo # Kredi karti eklemeniz gerekir, kullanim basina ucret alinir
        echo OPENAI_API_KEY=your-openai-api-key-here
        echo.
        echo # ==========================================
        echo # Azure OpenAI ^(UCRETLI - Kurumsal^)
        echo # ==========================================
        echo # Microsoft Azure bulut servisi
        echo # Kurumsal cozumler icin uygun, enterprise ozellikler
        echo # Azure Portal'dan API key ve endpoint alin
        echo AZURE_OPENAI_API_KEY=your-azure-openai-key-here
        echo AZURE_OPENAI_ENDPOINT=your-azure-endpoint-here
        echo AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
        echo.
        echo # ==========================================
        echo # Ollama ^(UCRETSIZ - Yerel, Azure benzeri degil^)
        echo # ==========================================
        echo # YEREL CALISIR: Bulut degil, bilgisayarinizda calisir
        echo # Tamamen ucretsiz, sorgu limiti YOK
        echo # Avantajlar: Ucretsiz, sinirsiz, gizlilik, internet gerektirmez
        echo # Dezavantajlar: Model indirme gerekir ^(2-4GB^), bilgisayar gucune bagli
        echo # NOT: Azure/OpenAI gibi degil - yerel kurulum gerektirir
        echo # Kurulum: https://ollama.ai adresinden indirin
        echo # Model indirme: PowerShell'de "ollama pull llama3.2" komutu
        echo OLLAMA_BASE_URL=http://localhost:11434
        echo OLLAMA_MODEL=llama3.2
        echo.
        echo # ==========================================
        echo # Hugging Face ^(UCRETSIZ^)
        echo # ==========================================
        echo # API Key almak icin: https://huggingface.co/settings/tokens
        echo HUGGINGFACE_API_KEY=your-huggingface-key-here
        echo HUGGINGFACE_MODEL=distilgpt2
        echo.
        echo # ==========================================
        echo # Genel Ayarlar
        echo # ==========================================
        echo SECRET_KEY=supersecret
        echo COMPANY_NAME=Company1
        echo BACKEND_URL=http://127.0.0.1:8000
        echo ALLOWED_ORIGINS=*
    ) > backend\.env
    echo .env dosyasi olusturuldu!
    echo.
    echo NOT: backend\.env dosyasini duzenleyerek AI saglayici secin:
    echo.
    echo TAVSIYE EDILEN ^(Azure benzeri, ucretsiz^):
    echo   - GEMINI: Bulut tabanli, API key ile, Azure/OpenAI gibi calisir
    echo            Ucretsiz katman mevcut, sadece Google hesabi + API key gerekir
    echo            Kurulum gerektirmez, hemen kullanmaya baslayabilirsiniz
    echo.
    echo DIGER UCRETSIZ:
    echo   - OLLAMA: Yerel calisir, model indirme gerekir ^(Azure benzeri degil^)
    echo.
    echo UCRETLI:
    echo   - OPENAI: En iyi kalite, Azure benzeri bulut servisi
    echo   - AZURE: Microsoft Azure bulut servisi, kurumsal cozum
    echo.
    echo Gemini API Key almak icin: https://makersuite.google.com/app/apikey
    echo.
) else (
    echo .env dosyasi zaten mevcut.
    echo Isterseniz backend\.env dosyasini duzenleyerek AI saglayici degistirebilirsiniz.
)

echo.
echo ========================================
echo KURULUM TAMAMLANDI!
echo ========================================
echo.
echo ONEMLI ADIMLAR:
echo.
echo 1. API KEY EKLEME (Gerekli):
echo    - backend\.env dosyasini acin
echo    - GEMINI_API_KEY=your-gemini-api-key-here satirini bulun
echo    - your-gemini-api-key-here yerine API anahtarinizi yapistirin
echo    - Dosyayi kaydedin (Ctrl+S)
echo.
echo    API Key almak icin:
echo    https://makersuite.google.com/app/apikey
echo.
echo 2. SERVISLERI BASLATMA:
echo    - baslat.bat dosyasina cift tiklayin
echo    - Backend ve Frontend otomatik baslar
echo    - Tarayicinizda: http://localhost:8501
echo    - Giris: admin / 1234
echo.
echo NOT: Eger farkli bir AI saglayici kullanmak istiyorsaniz:
echo      - kurulum_openai.bat (OpenAI icin)
echo      - kurulum_azure.bat (Azure OpenAI icin)
echo      - kurulum_ollama.bat (Ollama icin)
echo.
echo Detayli bilgi icin README.md dosyasina bakin.
echo.
pause

