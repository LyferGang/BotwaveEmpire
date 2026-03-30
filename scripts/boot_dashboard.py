#!/usr/bin/env python3
"""
SCRYPT KEEPER STYLE - Dashboard Bootstrap
Starts the Flask dashboard with SocketIO for real-time agent conversation
"""
import subprocess
import sys
import os
import time
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DASHBOARD_APP = BASE_DIR / "dashboard" / "web_app.py"
PID_FILE = BASE_DIR / ".dashboard.pid"
LOG_FILE = BASE_DIR / "logs" / "dashboard.log"
PORT = 5000

def check_dashboard_running():
    """Check if dashboard is already running."""
    if PID_FILE.exists():
        pid = int(PID_FILE.read_text().strip())
        try:
            os.kill(pid, 0)
            # Also verify it's responding
            import urllib.request
            try:
                urllib.request.urlopen(f"http://localhost:{PORT}/health", timeout=2)
                return True
            except:
                return False
        except ProcessLookupError:
            PID_FILE.unlink()
    return False

def start_dashboard():
    """Start the dashboard server."""
    print(f"[DASHBOARD] Starting Flask dashboard on port {PORT}...")

    # Ensure log directory exists
    LOG_FILE.parent.mkdir(exist_ok=True)

    # Set environment
    env = os.environ.copy()
    env["FLASK_APP"] = str(DASHBOARD_APP)
    env["FLASK_ENV"] = "production"

    # Start dashboard in background
    with open(LOG_FILE, "w") as log:
        process = subprocess.Popen(
            [sys.executable, str(DASHBOARD_APP)],
            stdout=log,
            stderr=subprocess.STDOUT,
            env=env,
            cwd=str(BASE_DIR),
            start_new_session=True
        )

    # Write PID file
    PID_FILE.write_text(str(process.pid))

    # Wait for it to start
    time.sleep(2)

    print(f"[DASHBOARD] Server started with PID {process.pid}")
    print(f"[DASHBOARD] URL: http://localhost:{PORT}")
    print(f"[DASHBOARD] Logs: {LOG_FILE}")

    return {
        "status": "started",
        "pid": process.pid,
        "url": f"http://localhost:{PORT}",
        "port": PORT
    }

def stop_dashboard():
    """Stop the dashboard server."""
    if PID_FILE.exists():
        pid = int(PID_FILE.read_text().strip())
        try:
            os.kill(pid, 15)
            PID_FILE.unlink()
            return {"status": "stopped", "pid": pid}
        except ProcessLookupError:
            PID_FILE.unlink()
    return {"status": "not_running"}

def get_status():
    """Get dashboard status."""
    running = check_dashboard_running()
    status = {
        "running": running,
        "service": "dashboard",
        "url": f"http://localhost:{PORT}",
        "port": PORT,
        "timestamp": time.time()
    }

    if running and PID_FILE.exists():
        pid = int(PID_FILE.read_text().strip())
        status["pid"] = pid

    return status

def get_recent_logs(lines=50):
    """Get recent dashboard logs."""
    if not LOG_FILE.exists():
        return []
    try:
        with open(LOG_FILE) as f:
            return f.readlines()[-lines:]
    except:
        return []

def main():
    if len(sys.argv) < 2:
        print(json.dumps(get_status()))
        return

    command = sys.argv[1]

    if command == "start":
        if check_dashboard_running():
            print(json.dumps({
                "status": "already_running",
                **get_status()
            }))
        else:
            result = start_dashboard()
            print(json.dumps(result))
    elif command == "stop":
        result = stop_dashboard()
        print(json.dumps(result))
    elif command == "status":
        print(json.dumps(get_status()))
    elif command == "logs":
        lines = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        print(json.dumps({"logs": get_recent_logs(lines)}))
    elif command == "restart":
        stop_dashboard()
        time.sleep(1)
        result = start_dashboard()
        print(json.dumps(result))
    else:
        print(f"Unknown command: {command}")
        print("Usage: boot_dashboard.py [start|stop|status|logs|restart]")
        sys.exit(1)

if __name__ == "__main__":
    main()
