#!/bin/bash

# ChatCore.AI - Servisleri Başlatma (Mac/Linux)
# Kullanım: chmod +x baslat.sh && ./baslat.sh

clear

echo "========================================"
echo "ChatCore.AI - Servisleri Başlatma"
echo "========================================"
echo ""

# Proje dizinine git
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Python komutunu bul (python3 ve python test et)
PYTHON_CMD=""
echo "Python komutu aranıyor..."

# python3 komutunu test et
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
    echo "Python bulundu: python3"
# py komutunu test et (bazı sistemlerde python yerine)
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
    echo "Python bulundu: python"
fi

# Python bulunamadı
if [ -z "$PYTHON_CMD" ]; then
    echo ""
    echo "========================================"
    echo "[HATA] Python bulunamadı!"
    echo "========================================"
    echo ""
    echo "Hem 'python3' hem de 'python' komutları test edildi."
    echo "Python kurulu olmalı ve PATH'te olmalı."
    echo ""
    echo "Çözüm:"
    echo "Mac: brew install python3"
    echo "Linux: sudo apt-get install python3 python3-venv"
    echo "Veya: https://www.python.org/downloads/"
    echo ""
    read -p "Devam etmek için Enter'a basın..."
    exit 1
fi

# .env dosyası kontrolü
if [ ! -f "backend/.env" ]; then
    echo ""
    echo "[UYARI] .env dosyası bulunamadı!"
    echo ""
    echo "Önce kurulum.sh dosyasını çalıştırın."
    echo ""
    read -p "Devam etmek için Enter'a basın..."
    exit 1
fi

# Virtual environment kontrolü
if [ ! -d "backend/venv" ]; then
    echo ""
    echo "[UYARI] Virtual environment bulunamadı!"
    echo ""
    echo "Önce kurulum.sh dosyasını çalıştırın."
    echo ""
    read -p "Devam etmek için Enter'a basın..."
    exit 1
fi

# Backend'i başlat
echo "[1/2] Backend başlatılıyor (Port 8000)..."
cd backend
source venv/bin/activate

# Yeni terminal penceresi aç (macOS ve Linux için farklı)
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    osascript -e "tell application \"Terminal\" to do script \"cd '$SCRIPT_DIR/backend' && source venv/bin/activate && $PYTHON_CMD -m uvicorn main:app --reload --host 0.0.0.0 --port 8000\""
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux - gnome-terminal, xterm, veya başka terminal
    if command -v gnome-terminal &> /dev/null; then
        gnome-terminal -- bash -c "cd '$SCRIPT_DIR/backend' && source venv/bin/activate && $PYTHON_CMD -m uvicorn main:app --reload --host 0.0.0.0 --port 8000; exec bash"
    elif command -v xterm &> /dev/null; then
        xterm -e bash -c "cd '$SCRIPT_DIR/backend' && source venv/bin/activate && $PYTHON_CMD -m uvicorn main:app --reload --host 0.0.0.0 --port 8000; exec bash" &
    elif command -v konsole &> /dev/null; then
        konsole -e bash -c "cd '$SCRIPT_DIR/backend' && source venv/bin/activate && $PYTHON_CMD -m uvicorn main:app --reload --host 0.0.0.0 --port 8000; exec bash" &
    else
        # Terminal bulunamadı, arka planda çalıştır
        nohup $PYTHON_CMD -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
        echo "Backend arka planda başlatıldı (log: backend.log)"
    fi
else
    # Diğer Unix sistemler için arka planda çalıştır
    nohup $PYTHON_CMD -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
    echo "Backend arka planda başlatıldı (log: backend.log)"
fi

cd ..

# Backend'in başlaması ve hazır olması için bekle
echo "Backend'in hazır olması bekleniyor..."
echo "NOT: Bu işlem 5-10 saniye sürebilir..."
sleep 5
echo ""

# Frontend'i başlat
echo "[2/2] Frontend başlatılıyor (Port 8501)..."
cd "$SCRIPT_DIR"

# Frontend için yeni terminal
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    osascript -e "tell application \"Terminal\" to do script \"cd '$SCRIPT_DIR' && source backend/venv/bin/activate && cd frontend && $PYTHON_CMD -m streamlit run app.py --server.headless true\""
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    if command -v gnome-terminal &> /dev/null; then
        gnome-terminal -- bash -c "cd '$SCRIPT_DIR' && source backend/venv/bin/activate && cd frontend && $PYTHON_CMD -m streamlit run app.py --server.headless true; exec bash"
    elif command -v xterm &> /dev/null; then
        xterm -e bash -c "cd '$SCRIPT_DIR' && source backend/venv/bin/activate && cd frontend && $PYTHON_CMD -m streamlit run app.py --server.headless true; exec bash" &
    elif command -v konsole &> /dev/null; then
        konsole -e bash -c "cd '$SCRIPT_DIR' && source backend/venv/bin/activate && cd frontend && $PYTHON_CMD -m streamlit run app.py --server.headless true; exec bash" &
    else
        # Terminal bulunamadı, arka planda çalıştır
        nohup bash -c "cd '$SCRIPT_DIR' && source backend/venv/bin/activate && cd frontend && $PYTHON_CMD -m streamlit run app.py --server.headless true" > frontend.log 2>&1 &
        echo "Frontend arka planda başlatıldı (log: frontend.log)"
    fi
else
    # Diğer Unix sistemler için arka planda çalıştır
    nohup bash -c "cd '$SCRIPT_DIR' && source backend/venv/bin/activate && cd frontend && $PYTHON_CMD -m streamlit run app.py --server.headless true" > frontend.log 2>&1 &
    echo "Frontend arka planda başlatıldı (log: frontend.log)"
fi

sleep 2

echo ""
echo "========================================"
echo "Servisler Başlatıldı!"
echo "========================================"
echo ""
echo "İki terminal penceresi açıldı (veya arka planda çalışıyor):"
echo "  - Backend (Port 8000)"
echo "  - Frontend (Port 8501)"
echo ""
echo "HATA DURUMUNDA:"
echo "  - Backend terminalindeki hata mesajlarını kontrol edin"
echo "  - Frontend terminalindeki hata mesajlarını kontrol edin"
echo "  - Hatalar kategorize şekilde backend/logs/ klasöründe loglanır:"
echo "    * errors.log - Tüm hatalar (kategori bazlı)"
echo "    * security.log - Güvenlik olayları"
echo "    * api.log - Genel API logları"
echo ""
echo "Tarayıcınızda: http://localhost:8501"
echo "API Docs: http://localhost:8000/docs"
echo "Giriş: admin / 1234"
echo ""
echo "Servisleri durdurmak için terminal pencerelerini kapatın"
echo "veya Ctrl+C ile durdurun."
echo ""
read -p "Devam etmek için Enter'a basın..."

