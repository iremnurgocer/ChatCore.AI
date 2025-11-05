#!/bin/bash
# ChatCore.AI Installation Script for Linux/Mac
# Creates virtual environment and installs dependencies

set -e

echo "========================================"
echo "ChatCore.AI Installation"
echo "========================================"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ first"
    exit 1
fi

echo "[1/4] Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists, skipping..."
else
    python3 -m venv venv
    echo "Virtual environment created successfully."
fi

echo ""
echo "[2/4] Activating virtual environment..."
source venv/bin/activate

echo ""
echo "[3/4] Upgrading pip..."
pip install --upgrade pip

echo ""
echo "[4/4] Installing dependencies..."
pip install -r backend/requirements-refactored.txt

echo ""
echo "[5/5] Setting up environment file..."
if [ ! -f "backend/.env" ]; then
    if [ -f "backend/.env.example" ]; then
        cp backend/.env.example backend/.env
        echo "Created backend/.env from .env.example"
        echo "Please edit backend/.env with your configuration"
    else
        echo "Warning: .env.example not found, creating basic .env..."
        cat > backend/.env << EOF
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/chatcore
REDIS_HOST=localhost
REDIS_PORT=6379
SECRET_KEY=CHANGE_THIS_IN_PRODUCTION
AI_PROVIDER=GEMINI
GEMINI_API_KEY=your_gemini_api_key_here
EOF
    fi
else
    echo "backend/.env already exists, skipping..."
fi

echo ""
echo "========================================"
echo "Installation completed successfully!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Edit backend/.env with your configuration"
echo "2. Start PostgreSQL and Redis: docker compose up -d"
echo "3. Run database migrations: cd backend && alembic upgrade head"
echo "4. Seed users: python backend/scripts/seed_users.py"
echo "5. Run ./start.sh to start the application"
echo ""



