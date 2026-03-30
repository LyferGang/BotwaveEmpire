#!/usr/bin/env python3
"""
SCRYPT KEEPER STYLE - Docker Infrastructure Bootstrap
Manages Docker containers for Botwave Empire
"""
import subprocess
import sys
import json
import time
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
COMPOSE_FILE = BASE_DIR / "docker-compose.yml"

def run_docker_command(cmd, capture=True):
    """Run a docker command and return result."""
    try:
        if capture:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "code": result.returncode
            }
        else:
            subprocess.run(cmd, check=True, timeout=300)
            return {"success": True}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def check_docker_daemon():
    """Check if Docker daemon is running."""
    result = run_docker_command(["docker", "info"])
    return result["success"]

def get_container_status():
    """Get status of all Botwave containers."""
    result = run_docker_command([
        "docker", "ps", "-a",
        "--filter", "name=botwave",
        "--format", "json"
    ])

    if not result["success"]:
        return {"error": "Failed to get container status"}

    containers = []
    for line in result["stdout"].strip().split("\n"):
        if line:
            try:
                containers.append(json.loads(line))
            except:
                pass

    return {
        "containers": containers,
        "count": len(containers),
        "running": sum(1 for c in containers if c.get("State") == "running")
    }

def build_images():
    """Build all Docker images."""
    print("[DOCKER] Building images...")
    return run_docker_command([
        "docker", "compose", "-f", str(COMPOSE_FILE), "build"
    ])

def start_infrastructure():
    """Start API and base services."""
    print("[DOCKER] Starting API service...")
    return run_docker_command([
        "docker", "compose", "-f", str(COMPOSE_FILE), "up", "-d", "api"
    ])

def start_agents():
    """Start agent containers."""
    print("[DOCKER] Starting agent containers...")
    return run_docker_command([
        "docker", "compose", "-f", str(COMPOSE_FILE),
        "--profile", "agents", "up", "-d"
    ])

def stop_all():
    """Stop all containers."""
    print("[DOCKER] Stopping all containers...")
    return run_docker_command([
        "docker", "compose", "-f", str(COMPOSE_FILE), "down"
    ])

def get_logs(service=None):
    """Get logs from containers."""
    cmd = ["docker", "compose", "-f", str(COMPOSE_FILE), "logs", "--tail", "100"]
    if service:
        cmd.append(service)
    return run_docker_command(cmd)

def main():
    if len(sys.argv) < 2:
        # Default: show status
        if not check_docker_daemon():
            print(json.dumps({"error": "Docker daemon not running"}))
            return

        status = get_container_status()
        print(json.dumps(status, indent=2))
        return

    command = sys.argv[1]

    if command == "check":
        daemon_ok = check_docker_daemon()
        print(json.dumps({
            "daemon_running": daemon_ok,
            "timestamp": time.time()
        }))
    elif command == "status":
        print(json.dumps(get_container_status(), indent=2))
    elif command == "build":
        print(json.dumps(build_images(), indent=2))
    elif command == "start":
        if not check_docker_daemon():
            print(json.dumps({"error": "Docker daemon not running"}))
            return
        result = start_infrastructure()
        print(json.dumps(result, indent=2))
    elif command == "start-agents":
        result = start_agents()
        print(json.dumps(result, indent=2))
    elif command == "stop":
        print(json.dumps(stop_all(), indent=2))
    elif command == "logs":
        service = sys.argv[2] if len(sys.argv) > 2 else None
        print(json.dumps(get_logs(service), indent=2))
    elif command == "full":
        # Full bootstrap
        if not check_docker_daemon():
            print(json.dumps({"error": "Docker daemon not running"}))
            return
        print(json.dumps(build_images(), indent=2))
        time.sleep(2)
        print(json.dumps(start_infrastructure(), indent=2))
        time.sleep(5)
        print(json.dumps(start_agents(), indent=2))
        time.sleep(2)
        print(json.dumps(get_container_status(), indent=2))
    else:
        print(f"Unknown command: {command}")
        print("Usage: boot_docker.py [check|status|build|start|start-agents|stop|logs|full]")
        sys.exit(1)

if __name__ == "__main__":
    main()
