#!/usr/bin/env python3
"""
SCRYPT KEEPER STYLE - Tailscale Mesh Bootstrap
Manages Tailscale for secure client SSH access and OpenClaw integration
"""
import subprocess
import sys
import json
import time
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
TAILSCALE_SOCK = "/var/run/tailscale/tailscaled.sock"

def run_tailscale_command(args, capture=True):
    """Run a tailscale command."""
    cmd = ["tailscale"] + args
    try:
        if capture:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        else:
            subprocess.run(cmd, check=True, timeout=30)
            return {"success": True}
    except FileNotFoundError:
        return {"success": False, "error": "tailscale not installed"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def check_tailscale_running():
    """Check if Tailscale is running."""
    result = run_tailscale_command(["status"])
    return result["success"]

def get_tailscale_status():
    """Get full Tailscale status."""
    result = run_tailscale_command(["status", "--json"])
    if result["success"]:
        try:
            return json.loads(result["stdout"])
        except:
            return {"error": "Failed to parse status"}
    return {"error": result.get("stderr", "Unknown error")}

def get_nodes():
    """Get all Tailscale nodes in the mesh."""
    status = get_tailscale_status()
    if "Peer" in status:
        nodes = []
        for node_id, node_info in status.get("Peer", {}).items():
            nodes.append({
                "id": node_id,
                "name": node_info.get("DNSName", "unknown"),
                "ip": node_info.get("TailscaleIPs", []),
                "online": node_info.get("Online", False),
                "os": node_info.get("OS", "unknown"),
                "last_seen": node_info.get("LastSeen", None)
            })
        return nodes
    return []

def ssh_to_node(node_ip, command=None):
    """SSH to a Tailscale node."""
    ssh_cmd = ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null"]

    # Use tailscale SSH if available
    if command:
        ssh_cmd.extend([f"root@{node_ip}", command])
    else:
        ssh_cmd.append(f"root@{node_ip}")

    return run_tailscale_command([])  # Placeholder for actual SSH

def advertise_subnet(route):
    """Advertise a subnet route."""
    return run_tailscale_command(["up", "--advertise-routes", route])

def create_temp_authkey(ephemeral=True, expiry_hours=24):
    """Create a temporary auth key for client access."""
    expiry = f"{expiry_hours}h"
    args = ["web", "create", "--ephemeral" if ephemeral else "", "--expiry", expiry]
    args = [a for a in args if a]  # Remove empty strings

    # This requires tailscale API - placeholder for implementation
    return {
        "success": True,
        "auth_key": "tskey-auth-placeholder",
        "expiry": expiry,
        "ephemeral": ephemeral
    }

def generate_client_invite(client_name):
    """Generate an invitation for a client."""
    # Create ephemeral key for client
    auth = create_temp_authkey(ephemeral=True, expiry_hours=168)  # 7 days

    invite = {
        "client_name": client_name,
        "auth_key": auth.get("auth_key"),
        "install_url": "https://tailscale.com/download",
        "setup_script": f"""
# Botwave Tailscale Setup for {client_name}
# 1. Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# 2. Connect with auth key
sudo tailscale up --auth-key={auth.get('auth_key')} --accept-routes

# 3. Verify connection
tailscale status

# 4. Your node will appear in the Botwave mesh
# OpenClaw integration will be configured automatically
        """.strip(),
        "expires": time.time() + (168 * 3600)
    }

    return invite

def get_opencalw_integration_node():
    """Get or create OpenClaw integration node."""
    nodes = get_nodes()
    for node in nodes:
        if "opencalw" in node.get("name", "").lower():
            return node
    return None

def main():
    if len(sys.argv) < 2:
        # Default: show status
        running = check_tailscale_running()
        print(json.dumps({
            "running": running,
            "nodes": get_nodes() if running else [],
            "timestamp": time.time()
        }, indent=2))
        return

    command = sys.argv[1]

    if command == "status":
        print(json.dumps(get_tailscale_status(), indent=2))
    elif command == "nodes":
        print(json.dumps({"nodes": get_nodes()}, indent=2))
    elif command == "invite":
        client_name = sys.argv[2] if len(sys.argv) > 2 else "Client"
        print(json.dumps(generate_client_invite(client_name), indent=2))
    elif command == "check":
        running = check_tailscale_running()
        print(json.dumps({
            "running": running,
            "timestamp": time.time()
        }))
    elif command == "setup-client":
        # Setup script for client machines
        client_name = sys.argv[2] if len(sys.argv) > 2 else "unknown-client"
        invite = generate_client_invite(client_name)
        print(invite.get("setup_script", ""))
    elif command == "ssh":
        node_ip = sys.argv[2] if len(sys.argv) > 2 else None
        if node_ip:
            os.execvp("ssh", ["ssh", f"root@{node_ip}"])
        else:
            print("Usage: boot_tailscale.py ssh <node-ip>")
    else:
        print(f"Unknown command: {command}")
        print("Usage: boot_tailscale.py [status|nodes|invite|check|setup-client|ssh]")
        sys.exit(1)

if __name__ == "__main__":
    main()
