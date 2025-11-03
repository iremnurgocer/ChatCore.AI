#!/bin/bash

# ChatCore.AI - Ollama Kurulum (Mac/Linux)
# Kullanım: chmod +x kurulum_ollama.sh && ./kurulum_ollama.sh

clear

echo "========================================"
echo "ChatCore.AI - Ollama Kurulum"
echo "========================================"
echo ""

# Proje dizinine git
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Python kontrolü
echo "[1/4] Python kontrol ediliyor..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo ""
    echo "HATA: Python bulunamadı!"
    echo "Python 3.8 veya üzeri kurulu olmalı."
    echo ""
    read -p "Devam etmek için Enter'a basın..."
    exit 1
fi

echo "OK! Python bulundu"
$PYTHON_CMD --version
echo ""

# Ollama kontrolü
echo "[2/4] Ollama kontrol ediliyor..."
if ! command -v ollama &> /dev/null; then
    echo ""
    echo "========================================"
    echo "Ollama bulunamadı!"
    echo "========================================"
    echo ""
    echo "Ollama kurulumu gerekiyor."
    echo ""
    echo "Mac:"
    echo "  brew install ollama"
    echo ""
    echo "Linux:"
    echo "  curl -fsSL https://ollama.ai/install.sh | sh"
    echo ""
    echo "Veya: https://ollama.ai adresinden indirin"
    echo ""
    echo "NOT: Önce kurulum.sh dosyasını çalıştırmanız gerekiyor!"
    echo ""
    read -p "Devam etmek için Enter'a basın..."
    exit 1
fi

echo "OK! Ollama bulundu"
ollama --version
echo ""

# Model kontrolü
echo "[3/4] Model kontrol ediliyor..."
if ! ollama list | grep -q "llama3.2"; then
    echo ""
    echo "Model bulunamadı, indiriliyor..."
    echo "NOT: Bu işlem 5-15 dakika sürebilir (internet hızınıza bağlı)"
    echo ""
    ollama pull llama3.2
    if [ $? -ne 0 ]; then
        echo ""
        echo "HATA: Model indirilemedi!"
        echo "İnternet bağlantınızı kontrol edin."
        read -p "Devam etmek için Enter'a basın..."
        exit 1
    fi
    echo ""
    echo "Model başarıyla indirildi!"
else
    echo "OK! Model zaten mevcut"
fi
echo ""

# .env dosyası yapılandırma
echo "[4/4] .env dosyası yapılandırılıyor..."
if [ ! -f "backend/.env" ]; then
    echo ""
    echo "UYARI: .env dosyası bulunamadı!"
    echo "Önce kurulum.sh dosyasını çalıştırın."
    echo ""
    read -p "Devam etmek için Enter'a basın..."
    exit 1
fi

# Ollama ayarlarını güncelle
if ! grep -q "AI_PROVIDER=OLLAMA" backend/.env; then
    echo ""
    echo "AI_PROVIDER=OLLAMA olarak ayarlanıyor..."
    sed -i.bak 's/^AI_PROVIDER=.*/AI_PROVIDER=OLLAMA/' backend/.env
fi

if ! grep -q "OLLAMA_BASE_URL" backend/.env; then
    echo "OLLAMA_BASE_URL=http://localhost:11434 olarak ayarlanıyor..."
    echo "OLLAMA_BASE_URL=http://localhost:11434" >> backend/.env
fi

if ! grep -q "OLLAMA_MODEL" backend/.env; then
    echo "OLLAMA_MODEL=llama3.2 olarak ayarlanıyor..."
    echo "OLLAMA_MODEL=llama3.2" >> backend/.env
else
    sed -i.bak 's/^OLLAMA_MODEL=.*/OLLAMA_MODEL=llama3.2/' backend/.env
fi

# Backup dosyalarını temizle
rm -f backend/.env.bak 2>/dev/null

echo ""
echo "========================================"
echo "Ollama Kurulumu Tamamlandı!"
echo "========================================"
echo ""
echo "Yapılandırma:"
echo "  - AI_PROVIDER: OLLAMA"
echo "  - OLLAMA_BASE_URL: http://localhost:11434"
echo "  - OLLAMA_MODEL: llama3.2"
echo ""
echo "Detaylı bilgi için KURULUM_OLLAMA.md dosyasına bakın."
echo ""
echo "Şimdi baslat.sh dosyasını çalıştırarak servisleri başlatabilirsiniz."
echo ""
read -p "Devam etmek için Enter'a basın..."

