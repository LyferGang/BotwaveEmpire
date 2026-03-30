#!/usr/bin/env python3
"""
SCRYPT KEEPER STYLE - MCP Server Bootstrap
Starts the Botwave MCP server with health checks
"""
import subprocess
import sys
import os
import time
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
MCP_SERVER = BASE_DIR / "mcp" / "botwave-mcp-server.py"
PID_FILE = BASE_DIR / ".mcp.pid"
LOG_FILE = BASE_DIR / "logs" / "mcp.log"

def check_mcp_running():
    """Check if MCP server is already running."""
    if PID_FILE.exists():
        pid = int(PID_FILE.read_text().strip())
        try:
            os.kill(pid, 0)
            return True
        except ProcessLookupError:
            PID_FILE.unlink()
    return False

def start_mcp():
    """Start the MCP server."""
    print("[MCP] Starting Botwave MCP server...")

    # Ensure log directory exists
    LOG_FILE.parent.mkdir(exist_ok=True)

    # Start MCP server in background
    with open(LOG_FILE, "w") as log:
        process = subprocess.Popen(
            [sys.executable, str(MCP_SERVER)],
            stdout=log,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            start_new_session=True
        )

    # Write PID file
    PID_FILE.write_text(str(process.pid))

    print(f"[MCP] Server started with PID {process.pid}")
    print(f"[MCP] Logs: {LOG_FILE}")

    return {"status": "started", "pid": process.pid}

def stop_mcp():
    """Stop the MCP server."""
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
    """Get MCP server status."""
    running = check_mcp_running()
    status = {
        "running": running,
        "server": "botwave-mcp",
        "timestamp": time.time()
    }

    if running:
        pid = int(PID_FILE.read_text().strip())
        status["pid"] = pid

    return status

def main():
    if len(sys.argv) < 2:
        print(json.dumps(get_status()))
        return

    command = sys.argv[1]

    if command == "start":
        if check_mcp_running():
            print(json.dumps({"status": "already_running"}))
        else:
            result = start_mcp()
            print(json.dumps(result))
    elif command == "stop":
        result = stop_mcp()
        print(json.dumps(result))
    elif command == "status":
        print(json.dumps(get_status()))
    elif command == "restart":
        stop_mcp()
        time.sleep(1)
        result = start_mcp()
        print(json.dumps(result))
    else:
        print(f"Unknown command: {command}")
        print("Usage: boot_mcp.py [start|stop|status|restart]")
        sys.exit(1)

if __name__ == "__main__":
    main()
