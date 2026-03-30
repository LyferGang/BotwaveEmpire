#!/usr/bin/env python3
"""
SCRYPT KEEPER STYLE - Full System Health Check
Validates all Botwave Empire components are operational
"""
import subprocess
import sys
import json
import time
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

def run_check(name, command, timeout=30):
    """Run a check command and return result."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=BASE_DIR
        )
        return {
            "name": name,
            "success": result.returncode == 0,
            "output": result.stdout[:500] if result.stdout else "",
            "error": result.stderr[:500] if result.stderr else ""
        }
    except subprocess.TimeoutExpired:
        return {"name": name, "success": False, "error": "Timeout"}
    except Exception as e:
        return {"name": name, "success": False, "error": str(e)}

def check_http(url, name, timeout=5):
    """Check HTTP endpoint."""
    try:
        req = urllib.request.Request(url, method='HEAD')
        req.add_header('User-Agent', 'Botwave-Health/1.0')
        response = urllib.request.urlopen(req, timeout=timeout)
        return {
            "name": name,
            "success": True,
            "status": response.status,
            "url": url
        }
    except urllib.error.HTTPError as e:
        return {
            "name": name,
            "success": e.code < 500,
            "status": e.code,
            "url": url
        }
    except Exception as e:
        return {"name": name, "success": False, "error": str(e), "url": url}

def check_mcp():
    """Check MCP server status."""
    return run_check("MCP Server", "python3 scripts/boot_mcp.py status")

def check_dashboard():
    """Check dashboard status."""
    return run_check("Dashboard", "python3 scripts/boot_dashboard.py status")

def check_docker():
    """Check Docker containers."""
    return run_check("Docker Containers", "python3 scripts/boot_docker.py status")

def check_tailscale():
    """Check Tailscale."""
    return run_check("Tailscale", "python3 scripts/boot_tailscale.py check")

def check_api():
    """Check API endpoints."""
    results = []

    # Dashboard
    results.append(check_http("http://localhost:5000", "Dashboard UI"))

    # Docker API (if running)
    results.append(check_http("http://localhost:8080/health", "Docker API"))

    return results

def check_filesystem():
    """Check required files/directories exist."""
    checks = []
    paths = [
        ("MCP Server", "mcp/botwave-mcp-server.py"),
        ("Dashboard", "dashboard/web_app.py"),
        ("Docker Compose", "docker-compose.yml"),
        ("Config Dir", "config"),
        ("Skills Dir", "skills"),
        ("Logs Dir", "logs"),
    ]

    for name, path in paths:
        full_path = BASE_DIR / path
        checks.append({
            "name": f"FS: {name}",
            "success": full_path.exists(),
            "path": str(full_path)
        })

    return checks

def run_stress_test():
    """Run a basic stress test."""
    results = []

    # Test 1: Parallel script execution
    start = time.time()
    procs = []
    for i in range(5):
        p = subprocess.Popen(
            [sys.executable, str(BASE_DIR / "scripts" / "boot_mcp.py"), "status"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        procs.append(p)

    for p in procs:
        p.wait()

    elapsed = time.time() - start
    results.append({
        "name": "Stress: Parallel Scripts",
        "success": elapsed < 10,
        "time": f"{elapsed:.2f}s"
    })

    return results

def main():
    print("=" * 60)
    print("BOTWAVE EMPIRE - FULL SYSTEM HEALTH CHECK")
    print("=" * 60)
    print()

    all_results = []

    # Run checks
    print("[1/6] Checking MCP Server...")
    all_results.append(check_mcp())

    print("[2/6] Checking Dashboard...")
    all_results.append(check_dashboard())

    print("[3/6] Checking Docker...")
    all_results.append(check_docker())

    print("[4/6] Checking Tailscale...")
    all_results.append(check_tailscale())

    print("[5/6] Checking Filesystem...")
    all_results.extend(check_filesystem())

    print("[6/6] Checking HTTP Endpoints...")
    all_results.extend(check_api())

    # Optional stress test
    if "--stress" in sys.argv:
        print("[7/6] Running Stress Test...")
        all_results.extend(run_stress_test())

    print()
    print("=" * 60)
    print("RESULTS")
    print("=" * 60)

    passed = sum(1 for r in all_results if r.get("success"))
    total = len(all_results)

    for result in all_results:
        status = "✅ PASS" if result.get("success") else "❌ FAIL"
        name = result.get("name", "Unknown")
        print(f"{status} - {name}")
        if not result.get("success") and result.get("error"):
            print(f"       Error: {result['error'][:60]}")

    print()
    print(f"Score: {passed}/{total} checks passed")

    if passed == total:
        print("🎉 All systems operational!")
        return 0
    elif passed >= total * 0.8:
        print("⚠️  Most systems operational, minor issues detected")
        return 0
    else:
        print("❌ Critical issues detected, system not fully operational")
        return 1

if __name__ == "__main__":
    sys.exit(main())
