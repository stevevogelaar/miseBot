@echo off
setlocal

echo ==========================================
echo  miseBot - Your AI Sous-Chef
echo ==========================================
echo.

:: Check Python
python --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.11+.
    pause
    exit /b 1
)

:: Check virtual environment
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

:: Install deps
pip install -q -r requirements.txt

:: Launch
echo Starting miseBot...
streamlit run app.py

pause
