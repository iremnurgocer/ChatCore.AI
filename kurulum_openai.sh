#!/bin/bash

# ChatCore.AI - OpenAI Kurulum (Mac/Linux)
# Kullanım: chmod +x kurulum_openai.sh && ./kurulum_openai.sh

clear

echo "========================================"
echo "ChatCore.AI - OpenAI Kurulum"
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
echo ""

# .env dosyası kontrolü
echo "[2/4] .env dosyası kontrol ediliyor..."
if [ ! -f "backend/.env" ]; then
    echo ""
    echo "UYARI: .env dosyası bulunamadı!"
    echo "Önce kurulum.sh dosyasını çalıştırın."
    echo ""
    read -p "Devam etmek için Enter'a basın..."
    exit 1
fi

echo "OK! .env dosyası mevcut"
echo ""

# OpenAI bilgilerini al
echo "[3/4] OpenAI API Key'ini Girin"
echo ""
echo "NOT: API Key almak için:"
echo "     1. https://platform.openai.com/api-keys adresine gidin"
echo "     2. 'Create new secret key' butonuna tıklayın"
echo "     3. Key'i kopyalayın"
echo ""
echo "Detaylı bilgi için KURULUM_OPENAI.md dosyasına bakın."
echo ""

read -p "OpenAI API Key (sk- ile başlayan): " OPENAI_KEY

if [ -z "$OPENAI_KEY" ]; then
    echo ""
    echo "HATA: API Key boş olamaz!"
    read -p "Devam etmek için Enter'a basın..."
    exit 1
fi

# Model seçimi
echo ""
echo "Model seçimi (opsiyonel):"
echo "  1. gpt-4o-mini (Hızlı, ekonomik - ÖNERİLEN)"
echo "  2. gpt-4o (En iyi kalite)"
echo "  3. gpt-3.5-turbo (Çok ekonomik)"
echo "  4. Varsayılan (gpt-4o-mini)"
read -p "Seçiminiz (1-4, varsayılan: 4): " MODEL_CHOICE

case $MODEL_CHOICE in
    1)
        OPENAI_MODEL="gpt-4o-mini"
        ;;
    2)
        OPENAI_MODEL="gpt-4o"
        ;;
    3)
        OPENAI_MODEL="gpt-3.5-turbo"
        ;;
    *)
        OPENAI_MODEL="gpt-4o-mini"
        ;;
esac

echo ""
echo "[4/4] .env dosyası güncelleniyor..."

# Backup oluştur
cp backend/.env backend/.env.bak

# AI_PROVIDER'i güncelle
sed -i.bak 's/^AI_PROVIDER=.*/AI_PROVIDER=OPENAI/' backend/.env

# API Key'i güncelle
if grep -q "^OPENAI_API_KEY" backend/.env; then
    sed -i.bak "s|^OPENAI_API_KEY=.*|OPENAI_API_KEY=$OPENAI_KEY|" backend/.env
else
    echo "OPENAI_API_KEY=$OPENAI_KEY" >> backend/.env
fi

# Model'i ekle (opsiyonel)
if grep -q "^OPENAI_MODEL" backend/.env; then
    sed -i.bak "s/^OPENAI_MODEL=.*/OPENAI_MODEL=$OPENAI_MODEL/" backend/.env
else
    echo "OPENAI_MODEL=$OPENAI_MODEL" >> backend/.env
fi

# Backup dosyasını temizle
rm -f backend/.env.bak 2>/dev/null

echo "OK!"
echo ""

echo "========================================"
echo "OpenAI Kurulumu Tamamlandı!"
echo "========================================"
echo ""
echo "Yapılandırma:"
echo "  - AI_PROVIDER: OPENAI"
echo "  - OPENAI_MODEL: $OPENAI_MODEL"
echo "  - API Key: **************** (gizli)"
echo ""
echo "NOT: API Key'inizi güvenli tutun!"
echo "     Kullanım limitlerinizi kontrol edin: https://platform.openai.com/usage"
echo ""
echo "Detaylı bilgi için KURULUM_OPENAI.md dosyasına bakın."
echo ""
echo "Şimdi baslat.sh dosyasını çalıştırarak servisleri başlatabilirsiniz."
echo ""
read -p "Devam etmek için Enter'a basın..."

