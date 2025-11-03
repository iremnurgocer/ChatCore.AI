#!/bin/bash

# ChatCore.AI - Otomatik Kurulum (Mac/Linux)
# Kullanım: chmod +x kurulum.sh && ./kurulum.sh

set -e  # Hata durumunda dur

clear
echo "========================================"
echo "ChatCore.AI - Otomatik Kurulum"
echo "========================================"
echo ""

# Proje dizinine git
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Python kontrolü
echo "[1/6] Python kontrol ediliyor..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
    echo "OK! Python bulundu ($PYTHON_CMD)"
    $PYTHON_CMD --version
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
    echo "OK! Python bulundu ($PYTHON_CMD)"
    $PYTHON_CMD --version
else
    echo ""
    echo "========================================"
    echo "HATA: Python bulunamadı!"
    echo "========================================"
    echo ""
    echo "Python 3.8 veya üzeri kurulu olmalı."
    echo ""
    echo "Çözüm Seçenekleri:"
    echo ""
    echo "Mac:"
    echo "  brew install python3"
    echo ""
    echo "Linux (Ubuntu/Debian):"
    echo "  sudo apt-get update && sudo apt-get install python3 python3-venv python3-pip"
    echo ""
    echo "Linux (Fedora/RHEL):"
    echo "  sudo dnf install python3 python3-venv python3-pip"
    echo ""
    echo "Python kurulumu için: https://www.python.org/downloads/"
    echo ""
    read -p "Devam etmek için Enter'a basın..."
    exit 1
fi
echo ""

# Virtual environment kontrolü ve oluşturma
echo "[2/6] Virtual Environment kontrolü..."
if [ -d "backend/venv" ]; then
    echo "Virtual environment zaten mevcut, kurulum atlanıyor."
    echo "Kurulumu sıfırdan yapmak isterseniz backend/venv klasörünü silin."
else
    echo "Virtual environment oluşturuluyor..."
    cd backend
    $PYTHON_CMD -m venv venv
    if [ $? -ne 0 ]; then
        echo "HATA: Virtual environment oluşturulamadı!"
        exit 1
    fi
    cd ..
    echo "Virtual environment oluşturuldu!"
fi
echo ""

# Virtual environment'i aktifleştir
source backend/venv/bin/activate
if [ $? -ne 0 ]; then
    echo "HATA: Virtual environment aktifleştirilemedi!"
    exit 1
fi

# Pip'i güncelle
echo "[3/6] Pip güncelleniyor..."
$PYTHON_CMD -m pip install --upgrade pip --quiet --progress-bar off
if [ $? -ne 0 ]; then
    echo "UYARI: Pip güncellenemedi, devam ediliyor..."
else
    echo "OK!"
fi
echo ""

# Bağımlılıkları kontrol et ve sadece eksikleri yükle
echo "[4/6] Bağımlılıklar kontrol ediliyor ve yükleniyor..."
cd backend
echo ""

# Temel paketleri kontrol et
echo "Bağımlılıklar kontrol ediliyor..."
$PYTHON_CMD -c "import fastapi, streamlit, langchain, openai" 2>/dev/null
if [ $? -ne 0 ]; then
    echo ""
    echo "Eksik bağımlılıklar bulundu, yükleniyor..."
    echo ""
    echo "NOT: Bu işlem 2-5 dakika sürebilir."
    echo "     Paketler sırasıyla indirilip kuruluyor..."
    echo ""
    echo "----------------------------------------"
    echo "[KURULUM BAŞLADI]"
    echo "----------------------------------------"
    echo ""
    echo "Paketler kurulurken her paket ve ilerleme görüntülenecek..."
    echo ""
    $PYTHON_CMD -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo ""
        echo "========================================"
        echo "HATA: Bağımlılıklar yüklenemedi!"
        echo "========================================"
        echo ""
        echo "Lütfen hataları kontrol edin."
        cd ..
        read -p "Devam etmek için Enter'a basın..."
        exit 1
    fi
    echo ""
    echo "----------------------------------------"
    echo "[KURULUM TAMAMLANDI]"
    echo "----------------------------------------"
else
    echo ""
    echo "Tüm temel bağımlılıklar zaten yüklü!"
    echo "Uyumluluk kontrolü yapılıyor..."
    echo ""
    # Kritik paketleri güncelle (uyumsuzluk sorunları için)
    echo "----------------------------------------"
    echo "Kritik paketler güncelleniyor..."
    echo "----------------------------------------"
    echo ""
    echo "[1/3] Pydantic-core güncelleniyor (uyumluluk için kritik)..."
    $PYTHON_CMD -m pip install --upgrade "pydantic-core>=2.23.0"
    echo ""
    echo "[2/3] Pydantic güncelleniyor..."
    $PYTHON_CMD -m pip install --upgrade "pydantic>=2.9.0,<3.0.0"
    echo ""
    echo "[3/3] LangChain paketleri güncelleniyor..."
    $PYTHON_CMD -m pip install --upgrade "langchain>=0.2.0" "langchain-openai>=0.1.0" "langchain-community>=0.2.0" "langchain-core>=0.2.0"
    echo ""
    echo "----------------------------------------"
    echo "Eksik paketler kontrol ediliyor..."
    echo "----------------------------------------"
    echo ""
    $PYTHON_CMD -m pip install -r requirements.txt --upgrade-strategy only-if-needed
    if [ $? -ne 0 ]; then
        echo ""
        echo "UYARI: Bazı paketler güncellenemedi, ama devam ediliyor..."
    else
        echo ""
        echo "Bağımlılıklar güncellendi (sadece gerekenler)."
    fi
fi
echo ""
cd ..
echo ""

# Bağımlılık doğrulama
echo "[5/6] Bağımlılıklar doğrulanıyor..."
$PYTHON_CMD -c "import fastapi; import streamlit; import langchain; import openai; import tinydb; print('OK - Tüm ana bağımlılıklar yüklü!')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "UYARI: Bazı bağımlılıklar eksik olabilir."
    echo "Tekrar yüklemek için kurulum.sh dosyasını çalıştırın."
    echo ""
    echo "Eksik paketler kontrol ediliyor..."
    $PYTHON_CMD -c "import tinydb" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "TinyDB eksik, yükleniyor..."
        $PYTHON_CMD -m pip install "tinydb>=4.8.0" --quiet
    fi
else
    echo "Tüm ana bağımlılıklar doğrulandı ve hazır!"
fi
echo ""

# Backend modül kontrolü
echo "Backend modülleri test ediliyor..."
cd backend
$PYTHON_CMD -c "from dotenv import load_dotenv; load_dotenv(); from ai_service import ask_ai, AI_PROVIDER; print('OK - AI service yüklü')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "UYARI: AI service modülü test edilemedi, ama devam ediliyor..."
else
    echo "Backend modülleri hazır!"
fi
cd ..
echo ""

# .env dosyası kontrolü ve oluşturma
echo "[6/6] Yapılandırma dosyası kontrolü..."
if [ ! -f "backend/.env" ]; then
    echo ".env dosyası bulunamadı, kapsamlı şablon oluşturuluyor..."
    cat > backend/.env << 'EOF'
# ==========================================
# AI SAĞLAYICI AYARLARI
# ==========================================
# Hangi AI sağlayıcıyı kullanmak istiyorsunuz?
# Seçenekler: GEMINI, OLLAMA, OPENAI, AZURE, HUGGINGFACE, LOCAL
#
# TAVSİYE EDİLEN (Azure benzeri, ücretsiz):
# GEMINI: Bulut tabanlı, API key ile, ücretsiz katman, kurulum gerektirmez
#         Azure/OpenAI gibi çalışır ama ücretsiz!
#
# Diğer Seçenekler:
# OLLAMA: Yerel, tamamen ücretsiz ama model indirme gerekir (2-4GB)
# OPENAI: Ücretli, en iyi kalite
# AZURE: Ücretli, kurumsal çözüm
AI_PROVIDER=GEMINI

# ==========================================
# Google Gemini (AZURE BENZERİ - ÜCRETSİZ)
# ==========================================
# Azure/OpenAI gibi bulut tabanlı, API key ile çalışır
# TAM ÜCRETSİZ: Günlük sorgu limiti var ama normal kullanım için yeterli
# Kurulum gerektirmez, sadece API key yeterli
#
# Nasıl API Key Alınır:
# 1. https://makersuite.google.com/app/apikey adresine gidin
# 2. Google hesabınızla giriş yapın
# 3. "Create API Key" butonuna tıklayın
# 4. Oluşturulan key'i buraya yapıştırın
GEMINI_API_KEY=your-gemini-api-key-here

# ==========================================
# OpenAI (ÜCRETLİ - En iyi kalite)
# ==========================================
# Ücretli servis, en iyi AI kalitesi
# API Key almak için: https://platform.openai.com/api-keys
# Kredi kartı eklemeniz gerekir, kullanım başına ücret alınır
OPENAI_API_KEY=your-openai-api-key-here

# ==========================================
# Azure OpenAI (ÜCRETLİ - Kurumsal)
# ==========================================
# Microsoft Azure bulut servisi
# Kurumsal çözümler için uygun, enterprise özellikler
# Azure Portal'dan API key ve endpoint alın
AZURE_OPENAI_API_KEY=your-azure-openai-key-here
AZURE_OPENAI_ENDPOINT=your-azure-endpoint-here
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini

# ==========================================
# Ollama (ÜCRETSİZ - Yerel, Azure benzeri değil)
# ==========================================
# YEREL ÇALIŞIR: Bulut değil, bilgisayarınızda çalışır
# Tamamen ücretsiz, sorgu limiti YOK
# Avantajlar: Ücretsiz, sınırsız, gizlilik, internet gerektirmez
# Dezavantajlar: Model indirme gerekir (2-4GB), bilgisayar gücüne bağlı
# NOT: Azure/OpenAI gibi değil - yerel kurulum gerektirir
# Kurulum: https://ollama.ai adresinden indirin
# Model indirme: Terminal'de "ollama pull llama3.2" komutu
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# ==========================================
# Hugging Face (ÜCRETSİZ)
# ==========================================
# API Key almak için: https://huggingface.co/settings/tokens
HUGGINGFACE_API_KEY=your-huggingface-key-here
HUGGINGFACE_MODEL=distilgpt2

# ==========================================
# Genel Ayarlar
# ==========================================
SECRET_KEY=supersecret
COMPANY_NAME=Company1
BACKEND_URL=http://127.0.0.1:8000
ALLOWED_ORIGINS=*
EOF
    echo ".env dosyası oluşturuldu!"
    echo ""
    echo "NOT: backend/.env dosyasını düzenleyerek AI sağlayıcı seçin:"
    echo ""
    echo "TAVSİYE EDİLEN (Azure benzeri, ücretsiz):"
    echo "  - GEMINI: Bulut tabanlı, API key ile, Azure/OpenAI gibi çalışır"
    echo "            Ücretsiz katman mevcut, sadece Google hesabı + API key gerekir"
    echo "            Kurulum gerektirmez, hemen kullanmaya başlayabilirsiniz"
    echo ""
    echo "DİĞER ÜCRETSİZ:"
    echo "  - OLLAMA: Yerel çalışır, model indirme gerekir (Azure benzeri değil)"
    echo ""
    echo "ÜCRETLİ:"
    echo "  - OPENAI: En iyi kalite, Azure benzeri bulut servisi"
    echo "  - AZURE: Microsoft Azure bulut servisi, kurumsal çözüm"
    echo ""
    echo "Gemini API Key almak için: https://makersuite.google.com/app/apikey"
    echo ""
else
    echo ".env dosyası zaten mevcut."
    echo "İsterseniz backend/.env dosyasını düzenleyerek AI sağlayıcı değiştirebilirsiniz."
fi

echo ""
echo "========================================"
echo "KURULUM TAMAMLANDI!"
echo "========================================"
echo ""
echo "ÖNEMLİ ADIMLAR:"
echo ""
echo "1. API KEY EKLEME (Gerekli):"
echo "   - backend/.env dosyasını açın"
echo "   - GEMINI_API_KEY=your-gemini-api-key-here satırını bulun"
echo "   - your-gemini-api-key-here yerine API anahtarınızı yapıştırın"
echo "   - Dosyayı kaydedin"
echo ""
echo "   API Key almak için:"
echo "   https://makersuite.google.com/app/apikey"
echo ""
echo "2. SERVISLERI BAŞLATMA:"
echo "   - ./baslat.sh komutunu çalıştırın"
echo "   - Backend ve Frontend otomatik başlar"
echo "   - Tarayıcınızda: http://localhost:8501"
echo "   - Giriş: admin / 1234"
echo ""
echo "NOT: Eğer farklı bir AI sağlayıcı kullanmak istiyorsanız:"
echo "     - ./kurulum_openai.sh (OpenAI için)"
echo "     - ./kurulum_azure.sh (Azure OpenAI için)"
echo "     - ./kurulum_ollama.sh (Ollama için)"
echo ""
echo "Detaylı bilgi için README.md dosyasına bakın."
echo ""
read -p "Devam etmek için Enter'a basın..."

