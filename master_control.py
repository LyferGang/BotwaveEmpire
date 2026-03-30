#!/usr/bin/env python3
"""
BOTWAVE MASTER CONTROL PANEL
Your personal command center for the dream team
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

# Colors for terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def clear():
    os.system('clear' if os.name != 'nt' else 'cls')

def print_header():
    clear()
    print(f"{Colors.HEADER}{'='*70}{Colors.END}")
    print(f"{Colors.HEADER}          BOTWAVE EMPIRE - MASTER CONTROL PANEL{Colors.END}")
    print(f"{Colors.HEADER}{'='*70}{Colors.END}")
    print(f"  {Colors.BLUE}Logged in: Al Gringo{Colors.END}")
    print(f"  {Colors.BLUE}Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
    print(f"{Colors.HEADER}{'='*70}{Colors.END}\n")

def check_service(name, command):
    """Check if a service is running."""
    try:
        result = subprocess.run(['pgrep', '-f', command], capture_output=True)
        return result.returncode == 0
    except:
        return False

def get_service_status():
    """Get status of all services."""
    services = {
        "Plumbing Bot": "plumbing_telegram_bot.py",
        "Dashboard": "web_app.py",
    }
    status = {}
    for name, cmd in services.items():
        status[name] = "RUNNING" if check_service(name, cmd) else "STOPPED"
    return status

def show_status():
    """Show system status."""
    print_header()
    print(f"{Colors.BOLD}SYSTEM STATUS{Colors.END}\n")

    status = get_service_status()
    for name, state in status.items():
        color = Colors.GREEN if state == "RUNNING" else Colors.RED
        print(f"  {name:.<30} {color}{state}{Colors.END}")

    print(f"\n{Colors.BOLD}QUICK STATS{Colors.END}\n")

    # Check database
    db_path = Path("data/plumbing_customers.db")
    if db_path.exists():
        import sqlite3
        try:
            conn = sqlite3.connect(db_path)
            customers = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
            quotes = conn.execute("SELECT COUNT(*) FROM quotes").fetchone()[0]
            appointments = conn.execute("SELECT COUNT(*) FROM appointments").fetchone()[0]
            conn.close()
            print(f"  Customers: {customers}")
            print(f"  Quotes: {quotes}")
            print(f"  Appointments: {appointments}")
        except:
            print(f"  Database: {Colors.YELLOW}Error reading{Colors.END}")
    else:
        print(f"  Database: {Colors.YELLOW}Not initialized{Colors.END}")

    print(f"\n{Colors.HEADER}{'='*70}{Colors.END}")

def start_plumbing_bot():
    """Start the plumbing bot."""
    print_header()
    print(f"{Colors.BOLD}STARTING PLUMBING BOT{Colors.END}\n")

    token = os.getenv("TG_PLUMBING_BOT_TOKEN")
    if not token or token == "your_bot_token_here":
        print(f"{Colors.RED}ERROR: TG_PLUMBING_BOT_TOKEN not set in .env{Colors.END}")
        print(f"\nGet token from @BotFather on Telegram")
        input("\nPress Enter to return...")
        return

    print(f"Token: {token[:20]}...")
    print(f"Starting bot...")

    subprocess.Popen(
        [sys.executable, "plumbing_telegram_bot.py"],
        stdout=open("plumbing_bot.log", "a"),
        stderr=subprocess.STDOUT,
        start_new_session=True
    )

    print(f"{Colors.GREEN}Bot started!{Colors.END}")
    print(f"Bot link: https://t.me/botwave_business_bot")
    time.sleep(2)
    input("\nPress Enter to return...")

def stop_plumbing_bot():
    """Stop the plumbing bot."""
    print_header()
    print(f"{Colors.BOLD}STOPPING PLUMBING BOT{Colors.END}\n")
    subprocess.run(['pkill', '-f', 'plumbing_telegram_bot.py'], capture_output=True)
    print(f"{Colors.GREEN}Bot stopped.{Colors.END}")
    time.sleep(1)
    input("\nPress Enter to return...")

def start_dashboard():
    """Start the web dashboard."""
    print_header()
    print(f"{Colors.BOLD}STARTING DASHBOARD{Colors.END}\n")

    print(f"Starting dashboard on http://localhost:5000...")
    subprocess.Popen(
        [sys.executable, "dashboard/web_app.py"],
        stdout=open("logs/dashboard.log", "a"),
        stderr=subprocess.STDOUT,
        start_new_session=True
    )

    print(f"{Colors.GREEN}Dashboard started!{Colors.END}")
    print(f"URL: http://localhost:5000")
    time.sleep(2)
    input("\nPress Enter to return...")

def stop_dashboard():
    """Stop the web dashboard."""
    print_header()
    print(f"{Colors.BOLD}STOPPING DASHBOARD{Colors.END}\n")
    subprocess.run(['pkill', '-f', 'web_app.py'], capture_output=True)
    print(f"{Colors.GREEN}Dashboard stopped.{Colors.END}")
    time.sleep(1)
    input("\nPress Enter to return...")

def view_logs():
    """View recent logs."""
    print_header()
    print(f"{Colors.BOLD}RECENT LOGS{Colors.END}\n")

    log_files = ["plumbing_bot.log", "logs/dashboard.log"]
    for log_file in log_files:
        path = Path(log_file)
        if path.exists():
            print(f"\n--- {log_file} (last 20 lines) ---")
            with open(path) as f:
                lines = f.readlines()[-20:]
                for line in lines:
                    print(line.rstrip())

    input("\nPress Enter to return...")

def open_telegram():
    """Open Telegram bot link."""
    print_header()
    print(f"{Colors.BOLD}TELEGRAM BOT{Colors.END}\n")
    print(f"Bot link: https://t.me/botwave_business_bot")
    print(f"\n{Colors.YELLOW}IMPORTANT: Make sure bot is public in BotFather:{Colors.END}")
    print(f"  1. Open @BotFather on Telegram")
    print(f"  2. Send: /mybots")
    print(f"  3. Select your bot")
    print(f"  4. Bot Settings -> Group Privacy -> DISABLE")
    print(f"  5. This allows bot to see all messages in groups")

    # Open in browser
    subprocess.run(['xdg-open', 'https://t.me/botwave_business_bot'],
                   capture_output=True)
    input("\nPress Enter to return...")

def show_menu():
    """Show main menu."""
    while True:
        print_header()

        status = get_service_status()

        print(f"{Colors.BOLD}QUICK ACTIONS{Colors.END}\n")
        print(f"  1. Start Plumbing Bot      [{status.get('Plumbing Bot', 'STOPPED')}]")
        print(f"  2. Stop Plumbing Bot")
        print(f"  3. Start Dashboard        [{status.get('Dashboard', 'STOPPED')}]")
        print(f"  4. Stop Dashboard")
        print(f"  5. View Logs")
        print(f"  6. Open Telegram Bot")
        print(f"  7. System Status")
        print(f"\n  0. Exit\n")
        print(f"{Colors.HEADER}{'='*70}{Colors.END}")

        choice = input(f"\n{Colors.BOLD}[Botwave]{Colors.END} Select: ").strip()

        if choice == "1":
            start_plumbing_bot()
        elif choice == "2":
            stop_plumbing_bot()
        elif choice == "3":
            start_dashboard()
        elif choice == "4":
            stop_dashboard()
        elif choice == "5":
            view_logs()
        elif choice == "6":
            open_telegram()
        elif choice == "7":
            show_status()
            input("\nPress Enter to return...")
        elif choice == "0":
            print(f"\n{Colors.GREEN}Goodbye!{Colors.END}")
            break

if __name__ == "__main__":
    # Load .env
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, val = line.strip().split('=', 1)
                    os.environ.setdefault(key, val)

    # Ensure directories exist
    Path("data").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)

    show_menu()