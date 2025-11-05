@echo off
REM ChatCore.AI Installation Script for Windows
REM Creates virtual environment and installs dependencies

echo ========================================
echo ChatCore.AI Installation
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/4] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists, skipping...
) else (
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
)

echo.
echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo [3/4] Upgrading pip...
python -m pip install --upgrade pip

echo.
echo [4/4] Installing dependencies...
pip install -r backend\requirements-refactored.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [5/5] Setting up environment file...
if not exist backend\.env (
    if exist backend\.env.example (
        copy backend\.env.example backend\.env
        echo Created backend\.env from .env.example
        echo Please edit backend\.env with your configuration
    ) else (
        echo Warning: .env.example not found, creating basic .env...
        (
            echo DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/chatcore
            echo REDIS_HOST=localhost
            echo REDIS_PORT=6379
            echo SECRET_KEY=CHANGE_THIS_IN_PRODUCTION
            echo AI_PROVIDER=GEMINI
            echo GEMINI_API_KEY=your_gemini_api_key_here
        ) > backend\.env
    )
) else (
    echo backend\.env already exists, skipping...
)

echo.
echo [6/8] Checking Docker installation...
docker --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: Docker not found or not running
    echo PostgreSQL and Redis will not be started automatically
    echo Please install Docker Desktop from https://www.docker.com/products/docker-desktop
    echo Or manually start PostgreSQL and Redis
    set DOCKER_AVAILABLE=0
) else (
    echo Docker found, proceeding with database setup...
    set DOCKER_AVAILABLE=1
)

echo.
echo [7/8] Starting PostgreSQL and Redis...
if "%DOCKER_AVAILABLE%"=="1" (
    docker compose up -d postgres redis
    if errorlevel 1 (
        echo WARNING: Failed to start Docker containers
        echo Please start PostgreSQL and Redis manually
    ) else (
        echo Waiting for PostgreSQL and Redis to be ready...
        timeout /t 10 /nobreak >nul
        echo Database services started
    )
) else (
    echo Skipping Docker setup (Docker not available)
    echo Please ensure PostgreSQL and Redis are running before starting the application
)

echo.
echo [8/8] Setting up database...
call venv\Scripts\activate.bat
cd backend

REM Wait for database to be ready
echo Waiting for database connection...
timeout /t 5 /nobreak >nul

REM Run migrations
echo Running database migrations...
alembic upgrade head
if errorlevel 1 (
    echo WARNING: Migration failed, database may not be ready yet
    echo You can retry migrations manually: cd backend ^&^& alembic upgrade head
) else (
    echo Database migrations completed
)

REM Seed users
echo Seeding default users...
python scripts\seed_users.py
if errorlevel 1 (
    echo WARNING: User seeding failed
    echo You can retry manually: python backend\scripts\seed_users.py
) else (
    echo Default users created (admin/1234, user2/1234, user3/12345)
)

cd ..

echo.
echo ========================================
echo Installation completed successfully!
echo ========================================
echo.
echo IMPORTANT: Configure your AI provider API key
echo 1. Edit backend\.env
echo 2. Set GEMINI_API_KEY or your preferred provider key
echo 3. Save the file
echo.
echo Default users:
echo - admin / 1234 (Admin)
echo - user2 / 1234 (User)
echo - user3 / 12345 (User)
echo.
echo Next step: Run start.bat to start the application
echo.
pause

