@echo off
REM ChatCore.AI Startup Script for Windows
REM Starts both backend and frontend services

echo ========================================
echo ChatCore.AI Startup
echo ========================================
echo.

REM Check if virtual environment exists
if not exist venv (
    echo ERROR: Virtual environment not found
    echo Please run install.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if .env exists
if not exist backend\.env (
    echo ERROR: backend\.env not found
    echo Please run install.bat first or create backend\.env manually
    pause
    exit /b 1
)

REM Check if PostgreSQL and Redis are running
echo Checking database services...
docker ps --filter "name=chatcore_postgres" --format "{{.Names}}" | findstr /C:"chatcore_postgres" >nul 2>&1
if errorlevel 1 (
    echo PostgreSQL container not running, starting...
    docker compose up -d postgres redis
    if errorlevel 1 (
        echo ERROR: Failed to start database services
        echo Please ensure Docker is running and try again
        pause
        exit /b 1
    )
    echo Waiting for database services to be ready...
    timeout /t 10 /nobreak >nul
) else (
    echo Database services are running
)

echo.
echo Starting backend and frontend...
echo.
echo Backend will be available at: http://localhost:8000
echo Frontend will be available at: http://localhost:8501
echo API Docs: http://localhost:8000/docs
echo.
echo Default login: admin / 1234
echo.
echo Press Ctrl+C to stop all services
echo.

REM Start backend in background
start "ChatCore Backend" cmd /k "cd backend && call ..\venv\Scripts\activate.bat && uvicorn main:app --reload --host 0.0.0.0 --port 8000"

REM Wait a bit for backend to start
timeout /t 5 /nobreak >nul

REM Start frontend
echo Starting frontend...
cd frontend
call ..\venv\Scripts\activate.bat
streamlit run app.py

REM If frontend exits, kill backend
taskkill /FI "WINDOWTITLE eq ChatCore Backend*" /T /F >nul 2>&1

pause

