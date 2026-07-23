@echo off
title miseBot Launcher
color 0B

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

:: Use this file's directory as project root
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

:: Ensure log dir
if not exist "%PROJECT_ROOT%logs" mkdir "%PROJECT_ROOT%logs"
set LOG_FILE=%PROJECT_ROOT%logs\misebot-start.log

:: Kill any stale miseBot / streamlit on port 8503
echo Flushing stale miseBot / Streamlit processes...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8503') do (
    taskkill /F /PID %%a > nul 2>&1
)
timeout /t 2 /nobreak > nul

:: Activate venv
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat

:: Install deps
echo Installing / checking dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo ERROR: pip install failed. Check %LOG_FILE%
    pause
    exit /b 1
)

:: Launch info
cls
echo.
echo ********************************************
echo   DO NOT CLOSE THIS WINDOW
echo   It is running the miseBot server.
echo   Close the browser tab first, then press
echo   Ctrl+C here and confirm Y to stop.
echo ********************************************
echo.
echo miseBot is starting on:
echo   http://localhost:8503
echo   http://192.168.68.111:8503  (local network)
echo.
echo Ctrl+click one of the URLs above to open.
echo.

:: Run headless so browser does not auto-open
echo Starting... (see %LOG_FILE% for details)
streamlit run app.py --server.port 8503 --server.address 0.0.0.0 --server.headless true --server.runOnSave false >> "%LOG_FILE%" 2>&1

if errorlevel 1 (
    echo.
    echo ERROR: Streamlit failed to start. Code: %errorlevel%
    echo See log: %LOG_FILE%
    type "%LOG_FILE%"
    echo.
    pause
)
