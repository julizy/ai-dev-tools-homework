@echo off
REM Online Coding Interview Platform - Startup Script (Windows)

echo.
echo ================================
echo Online Coding Interview Platform
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python 3.8 or higher.
    exit /b 1
)

cd backend

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt >nul 2>&1

if errorlevel 0 (
    echo [OK] Dependencies installed
) else (
    echo [WARNING] Some dependencies may not have installed correctly
)

REM Start the Flask server
echo.
echo [OK] Starting Flask server...
echo ================================
echo Server running at: http://localhost:5000
echo ================================
echo.
python app.py
