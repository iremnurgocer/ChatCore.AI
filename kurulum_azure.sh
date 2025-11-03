#!/bin/bash

# ChatCore.AI - Azure OpenAI Kurulum (Mac/Linux)
# Kullanım: chmod +x kurulum_azure.sh && ./kurulum_azure.sh

clear

echo "========================================"
echo "ChatCore.AI - Azure OpenAI Kurulum"
echo "========================================"
echo ""

# Proje dizinine git
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Python kontrolü
echo "[1/5] Python kontrol ediliyor..."
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
echo "[2/5] .env dosyası kontrol ediliyor..."
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

# Azure bilgilerini al
echo "[3/5] Azure OpenAI Bilgilerini Girin"
echo ""
echo "NOT: Bu bilgileri Azure Portal'dan alabilirsiniz:"
echo "     https://portal.azure.com"
echo ""
echo "Detaylı bilgi için KURULUM_AZURE.md dosyasına bakın."
echo ""

read -p "Azure OpenAI API Key (KEY 1 veya KEY 2): " AZURE_KEY
read -p "Azure OpenAI Endpoint (örn: https://your-resource.openai.azure.com): " AZURE_ENDPOINT
read -p "Deployment Adı (örn: gpt-4o-mini, varsayılan: gpt-4o-mini): " AZURE_DEPLOYMENT

if [ -z "$AZURE_KEY" ]; then
    echo ""
    echo "HATA: API Key boş olamaz!"
    read -p "Devam etmek için Enter'a basın..."
    exit 1
fi

if [ -z "$AZURE_ENDPOINT" ]; then
    echo ""
    echo "HATA: Endpoint boş olamaz!"
    read -p "Devam etmek için Enter'a basın..."
    exit 1
fi

if [ -z "$AZURE_DEPLOYMENT" ]; then
    AZURE_DEPLOYMENT="gpt-4o-mini"
    echo "Varsayılan deployment kullanılıyor: gpt-4o-mini"
fi

# Endpoint'ten son / karakterini temizle
AZURE_ENDPOINT=$(echo "$AZURE_ENDPOINT" | sed 's|/$||' | tr -d ' ')

echo ""
echo "[4/5] .env dosyası güncelleniyor..."

# Backup oluştur
cp backend/.env backend/.env.bak

# AI_PROVIDER'i güncelle
sed -i.bak 's/^AI_PROVIDER=.*/AI_PROVIDER=AZURE/' backend/.env

# API Key'i güncelle
if grep -q "^AZURE_OPENAI_API_KEY" backend/.env; then
    sed -i.bak "s|^AZURE_OPENAI_API_KEY=.*|AZURE_OPENAI_API_KEY=$AZURE_KEY|" backend/.env
else
    echo "AZURE_OPENAI_API_KEY=$AZURE_KEY" >> backend/.env
fi

# Endpoint'i güncelle
if grep -q "^AZURE_OPENAI_ENDPOINT" backend/.env; then
    sed -i.bak "s|^AZURE_OPENAI_ENDPOINT=.*|AZURE_OPENAI_ENDPOINT=$AZURE_ENDPOINT|" backend/.env
else
    echo "AZURE_OPENAI_ENDPOINT=$AZURE_ENDPOINT" >> backend/.env
fi

# Deployment'i güncelle
if grep -q "^AZURE_OPENAI_DEPLOYMENT" backend/.env; then
    sed -i.bak "s/^AZURE_OPENAI_DEPLOYMENT=.*/AZURE_OPENAI_DEPLOYMENT=$AZURE_DEPLOYMENT/" backend/.env
else
    echo "AZURE_OPENAI_DEPLOYMENT=$AZURE_DEPLOYMENT" >> backend/.env
fi

# Backup dosyasını temizle
rm -f backend/.env.bak 2>/dev/null

echo "OK!"
echo ""

echo "[5/5] Yapılandırma doğrulanıyor..."
echo ""
echo "Yapılandırma Özeti:"
echo "  - AI_PROVIDER: AZURE"
echo "  - AZURE_OPENAI_ENDPOINT: $AZURE_ENDPOINT"
echo "  - AZURE_OPENAI_DEPLOYMENT: $AZURE_DEPLOYMENT"
echo "  - API Key: **************** (gizli)"
echo ""

echo "========================================"
echo "Azure OpenAI Kurulumu Tamamlandı!"
echo "========================================"
echo ""
echo "NOT: Azure Portal'dan deployment'in aktif olduğundan emin olun."
echo "     Detaylı bilgi için KURULUM_AZURE.md dosyasına bakın."
echo ""
echo "Şimdi baslat.sh dosyasını çalıştırarak servisleri başlatabilirsiniz."
echo ""
read -p "Devam etmek için Enter'a basın..."

