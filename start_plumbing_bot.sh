#!/bin/bash
# =============================================================================
# Jimenez Plumbing Telegram Bot - Startup Script
# =============================================================================

echo "========================================"
echo "  Jimenez Plumbing Telegram Bot"
echo "========================================"
echo ""

# Check if python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed!"
    echo "Please install Python 3.12 or later."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found!"
    echo "Creating from .env.example..."
    cp .env.example .env
    echo "Please edit .env and add your Telegram bot token!"
    exit 1
fi

# Check if required packages are installed
echo "Checking dependencies..."
python3 -c "import telegram" 2>/dev/null || {
    echo "Installing required packages..."
    pip install python-telegram-bot python-dotenv
}

# Create data directory if it doesn't exist
mkdir -p data

echo ""
echo "Starting Jimenez Plumbing Bot..."
echo ""
echo "To use this bot:"
echo "1. Message @BotFather on Telegram to create a bot"
echo "2. Copy the token to .env file (TG_PLUMBING_BOT_TOKEN)"
echo "3. Restart this script"
echo ""
echo "Press Ctrl+C to stop the bot"
echo ""

# Run the bot
python3 plumbing_telegram_bot.py