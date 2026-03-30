@echo off
title Botwave - Starting Services
color 0A
cls

echo ================================================================
echo                    BOTWAVE LAUNCHER
echo ================================================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.10+
    pause
    exit /b 1
)

echo [OK] Python found
echo.

:: Change to script directory
cd /d "%~dp0"

:: Create data directory if needed
if not exist "data" mkdir data

echo ================================================================
echo                    STARTING SERVICES
echo ================================================================
echo.

:: Start Plumbing Bot (if token is set)
echo [1/2] Starting Telegram Bot...
if exist "plumbing_telegram_bot.py" (
    start "Botwave - Telegram Bot" /min python plumbing_telegram_bot.py
    echo       Bot started (check plumbing_bot.log for output)
) else (
    echo       [SKIP] plumbing_telegram_bot.py not found
)

:: Wait a moment
timeout /t 2 /nobreak >nul

:: Start Dashboard
echo [2/2] Starting Dashboard...
if exist "dashboard\web_app.py" (
    start "Botwave - Dashboard" python dashboard\web_app.py
    echo       Dashboard starting at http://localhost:5000
) else (
    echo       [SKIP] web_app.py not found
)

echo.
echo ================================================================
echo                    SERVICES STARTED
echo ================================================================
echo.
echo  Telegram Bot:  Running in background (minimized)
echo  Dashboard:     http://localhost:5000
echo.
echo  [Press any key to open dashboard in browser]
echo ================================================================
pause >nul

:: Open dashboard in browser
start http://localhost:5000

echo.
echo Services are running. Close this window to stop.
echo.
pause