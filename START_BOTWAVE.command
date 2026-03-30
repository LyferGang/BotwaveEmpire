#!/bin/bash
# Botwave Launcher for macOS/Linux
# Double-click to start all services

clear
echo "================================================================"
echo "                    BOTWAVE LAUNCHER"
echo "================================================================"
echo ""

# Get script directory
cd "$(dirname "$0")"

# Create data directory if needed
mkdir -p data

echo "================================================================"
echo "                    STARTING SERVICES"
echo "================================================================"
echo ""

# Start Plumbing Bot
echo "[1/2] Starting Telegram Bot..."
if [ -f "plumbing_telegram_bot.py" ]; then
    python3 plumbing_telegram_bot.py &
    echo "      Bot started (check plumbing_bot.log)"
else
    echo "      [SKIP] plumbing_telegram_bot.py not found"
fi

sleep 2

# Start Dashboard
echo "[2/2] Starting Dashboard..."
if [ -f "dashboard/web_app.py" ]; then
    python3 dashboard/web_app.py &
    echo "      Dashboard starting at http://localhost:5000"
else
    echo "      [SKIP] web_app.py not found"
fi

echo ""
echo "================================================================"
echo "                    SERVICES STARTED"
echo "================================================================"
echo ""
echo " Telegram Bot:  Running in background"
echo " Dashboard:     http://localhost:5000"
echo ""
echo " Press Enter to open dashboard in browser..."
echo "================================================================"
read

# Open dashboard
open http://localhost:5000 2>/dev/null || xdg-open http://localhost:5000 2>/dev/null

echo ""
echo "Services are running. Press Enter to stop."
read

# Kill services on exit
pkill -f "plumbing_telegram_bot.py"
pkill -f "web_app.py"

echo "Services stopped."