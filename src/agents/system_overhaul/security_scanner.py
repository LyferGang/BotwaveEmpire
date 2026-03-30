#!/usr/bin/env python3
"""
SECURITY SCANNER - Botwave System Overhaul Agent
Scans for malware, suspicious processes, and security vulnerabilities
Works over Tailscale mesh network
"""

import os
import subprocess
import platform
from typing import Dict, Any, List
from datetime import datetime


class SecurityScanner:
    """Specialized agent for security scanning - part of Botwave Janitor Squad."""

    def __init__(self):
        self.name = "security_scanner"
        self.platform = platform.system().lower()
        self.findings = {
            "threats": [],
            "warnings": [],
            "info": [],
            "score": 100
        }

    def run(self, task_input: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute security scan - works local or remote via SSH."""
        task_input = task_input or {}

        if "host" in task_input:
            # Remote scan via Tailscale SSH
            return self._remote_scan(
                task_input["host"],
                task_input.get("user", "admin"),
                task_input.get("os", "auto")
            )
        else:
            # Local scan
            return self._local_scan()

    def _local_scan(self) -> Dict[str, Any]:
        """Run security scan on local machine."""
        results = {
            "malware_scan": self._scan_malware(),
            "processes": self._scan_processes(),
            "network": self._scan_network(),
            "browser": self._scan_browser_extensions(),
            "scheduled_tasks": self._scan_scheduled_tasks(),
            "hosts_file": self._scan_hosts_file(),
            "startup": self._scan_startup_items()
        }

        self._calculate_score(results)
        return {
            "status": "success",
            "agent": self.name,
            "platform": self.platform,
            "findings": self.findings,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }

    def _remote_scan(self, host: str, user: str, os_type: str) -> Dict[str, Any]:
        """Run security scan on remote machine via Tailscale SSH."""
        script = self._get_scan_script(os_type)

        try:
            result = subprocess.run(
                ["ssh", "-o", "ConnectTimeout=10",
                 "-o", "StrictHostKeyChecking=no",
                 f"{user}@{host}", script],
                capture_output=True,
                text=True,
                timeout=300
            )
            return {
                "status": "success",
                "agent": self.name,
                "host": host,
                "output": result.stdout,
                "error": result.stderr if result.stderr else None,
                "timestamp": datetime.now().isoformat()
            }
        except subprocess.TimeoutExpired:
            return {"status": "error", "message": "SSH timeout - check Tailscale connection"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _get_scan_script(self, os_type: str = "auto") -> str:
        """Get appropriate scan script for OS."""
        if os_type == "windows":
            return self._windows_scan_script()
        elif os_type == "darwin":
            return self._macos_scan_script()
        else:
            return self._linux_scan_script()

    def _linux_scan_script(self) -> str:
        """Linux security scan script."""
        return r'''
echo "=== BOTWAVE SECURITY SCAN ==="
echo "Started: $(date)"
echo ""

# Malware indicators
echo "--- SUSPICIOUS FILES ---"
find /home -type f \( -name "*.exe" -o -name "*.bat" -o -name "*.scr" -o -name "*.pif" \) 2>/dev/null
echo ""

# High CPU processes (potential miners)
echo "--- HIGH CPU PROCESSES ---"
ps aux --sort=-%cpu 2>/dev/null | head -15
echo ""

# Suspicious network listeners
echo "--- NETWORK LISTENERS ---"
ss -tuln 2>/dev/null | grep LISTEN | grep -v "127.0.0.1"
netstat -tuln 2>/dev/null | grep LISTEN | grep -v "127.0.0.1" || true
echo ""

# Crontab entries
echo "--- CRON JOBS ---"
crontab -l 2>/dev/null || echo "No user crontab"
ls -la /etc/cron.* 2>/dev/null | grep -v "^d" | grep -v "^total"
echo ""

# Recent logins
echo "--- RECENT LOGINS ---"
last -5 2>/dev/null || true
echo ""

# Failed login attempts
echo "--- FAILED LOGINS ---"
grep "Failed password" /var/log/auth.log 2>/dev/null | tail -10 || true
journalctl -u ssh --no-pager -n 20 2>/dev/null | grep -i "failed" || true
echo ""

# Root/sudo access
echo "--- SUDO ACTIVITY ---"
grep "sudo:" /var/log/auth.log 2>/dev/null | tail -10 || true
echo ""

# Hosts file modifications
echo "--- HOSTS FILE ---"
cat /etc/hosts 2>/dev/null | grep -v "^#" | grep -v "^$"
echo ""

echo "Completed: $(date)"
'''

    def _windows_scan_script(self) -> str:
        """Windows security scan script (PowerShell)."""
        return r'''
Write-Host "=== BOTWAVE SECURITY SCAN ===" -ForegroundColor Cyan
Write-Host "Started: $(Get-Date)"
Write-Host ""

# Suspicious processes
Write-Host "--- RUNNING PROCESSES BY CPU ---" -ForegroundColor Yellow
Get-Process | Sort-Object CPU -Descending | Select-Object -First 15 Name, CPU, Id, Path
Write-Host ""

# Network connections
Write-Host "--- ESTABLISHED CONNECTIONS ---" -ForegroundColor Yellow
Get-NetTCPConnection -State Established 2>$null | Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort, OwningProcess | Format-Table
Write-Host ""

# Scheduled tasks
Write-Host "--- SCHEDULED TASKS (recently created) ---" -ForegroundColor Yellow
Get-ScheduledTask | Where-Object {$_.Date -gt (Get-Date).AddDays(-30)} | Select-Object TaskName, State, LastRunTime
Write-Host ""

# Startup items
Write-Host "--- STARTUP PROGRAMS ---" -ForegroundColor Yellow
Get-CimInstance Win32_StartupCommand | Select-Object Name, Command, Location
Write-Host ""

# Windows Defender status
Write-Host "--- DEFENDER STATUS ---" -ForegroundColor Yellow
Get-MpComputerStatus 2>$null | Select-Object RealTimeProtectionEnabled, AntivirusEnabled, LastQuickScanDate
Write-Host ""

# Recent security logs
Write-Host "--- RECENT SECURITY EVENTS ---" -ForegroundColor Yellow
Get-EventLog -LogName Security -Newest 10 2>$null | Select-Object TimeGenerated, EntryType, Message
Write-Host ""

# Hosts file
Write-Host "--- HOSTS FILE ---" -ForegroundColor Yellow
Get-Content "$env:SystemRoot\System32\drivers\etc\hosts" | Where-Object {$_ -notmatch "^#" -and $_ -match "\S"}
Write-Host ""

Write-Host "Completed: $(Get-Date)"
'''

    def _macos_scan_script(self) -> str:
        """macOS security scan script."""
        return r'''
echo "=== BOTWAVE SECURITY SCAN ==="
echo "Started: $(date)"
echo ""

# Suspicious processes
echo "--- HIGH CPU PROCESSES ---"
ps aux -r | head -15
echo ""

# Network listeners
echo "--- NETWORK LISTENERS ---"
lsof -i -P | grep LISTEN
echo ""

# LaunchAgents/LaunchDaemons
echo "--- LAUNCH AGENTS/DAEMONS ---"
ls -la ~/Library/LaunchAgents/ 2>/dev/null
ls -la /Library/LaunchAgents/ 2>/dev/null
ls -la /Library/LaunchDaemons/ 2>/dev/null
echo ""

# Login items
echo "--- LOGIN ITEMS ---"
osascript -e 'tell application "System Events" to get the name of every login item' 2>/dev/null
echo ""

# Recent installs
echo "--- RECENTLY INSTALLED APPS ---"
ls -lt /Applications/ 2>/dev/null | head -10
echo ""

# Hosts file
echo "--- HOSTS FILE ---"
cat /etc/hosts | grep -v "^#" | grep -v "^$"
echo ""

echo "Completed: $(date)"
'''

    # Local scan methods
    def _scan_malware(self) -> Dict[str, Any]:
        """Scan for malware indicators."""
        if self.platform == "windows":
            return self._windows_malware_scan()
        return self._linux_malware_scan()

    def _windows_malware_scan(self) -> Dict[str, Any]:
        """Windows malware scan using PowerShell."""
        try:
            result = subprocess.run(
                ["powershell", "-Command", "Get-MpThreatDetection | Select-Object -First 10"],
                capture_output=True, text=True, timeout=60
            )
            return {"output": result.stdout, "threats": []}
        except:
            return {"output": "Defender scan unavailable", "threats": []}

    def _linux_malware_scan(self) -> Dict[str, Any]:
        """Linux malware indicators."""
        suspicious = []
        try:
            # Check for suspicious executables in home
            result = subprocess.run(
                ["find", os.path.expanduser("~"), "-type", "f",
                 "(", "-name", "*.exe", "-o", "-name", "*.scr", "-o", "-name", "*.pif", ")"],
                capture_output=True, text=True, timeout=60
            )
            suspicious = [f for f in result.stdout.strip().split('\n') if f]
        except:
            pass

        return {"suspicious_files": suspicious, "count": len(suspicious)}

    def _scan_processes(self) -> Dict[str, Any]:
        """Scan running processes for anomalies."""
        try:
            result = subprocess.run(
                ["ps", "aux", "--sort=-%cpu"] if self.platform != "windows"
                else ["powershell", "-Command", "Get-Process | Sort-Object CPU -Descending | Select-Object -First 15"],
                capture_output=True, text=True, timeout=30
            )
            return {"output": result.stdout[:2000], "status": "ok"}
        except:
            return {"output": "Process scan failed", "status": "error"}

    def _scan_network(self) -> Dict[str, Any]:
        """Scan network connections."""
        try:
            if self.platform == "linux":
                result = subprocess.run(
                    ["ss", "-tuln"], capture_output=True, text=True, timeout=30
                )
            elif self.platform == "windows":
                result = subprocess.run(
                    ["powershell", "-Command", "Get-NetTCPConnection -State Established"],
                    capture_output=True, text=True, timeout=30
                )
            else:
                result = subprocess.run(
                    ["lsof", "-i", "-P"], capture_output=True, text=True, timeout=30
                )
            return {"output": result.stdout[:2000], "status": "ok"}
        except:
            return {"output": "Network scan failed", "status": "error"}

    def _scan_browser_extensions(self) -> Dict[str, Any]:
        """Check for suspicious browser extensions."""
        extensions = {"chrome": [], "firefox": []}

        home = os.path.expanduser("~")

        # Chrome extensions (Linux)
        chrome_path = os.path.join(home, ".config/google-chrome/Default/Extensions")
        if os.path.exists(chrome_path):
            try:
                extensions["chrome"] = os.listdir(chrome_path)[:20]
            except:
                pass

        # Firefox extensions
        firefox_glob = os.path.join(home, ".mozilla/firefox/*/extensions")
        if os.path.exists(os.path.dirname(firefox_glob)):
            extensions["firefox"] = ["Found"]

        return {"browsers": extensions, "status": "review_recommended"}

    def _scan_scheduled_tasks(self) -> Dict[str, Any]:
        """Scan scheduled tasks/cron jobs."""
        tasks = []

        if self.platform == "linux":
            try:
                result = subprocess.run(
                    ["crontab", "-l"], capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    tasks = [l for l in result.stdout.split('\n') if l and not l.startswith('#')]
            except:
                pass

        return {"tasks": tasks, "count": len(tasks)}

    def _scan_hosts_file(self) -> Dict[str, Any]:
        """Check hosts file for hijacks."""
        hosts_path = "/etc/hosts" if self.platform != "windows" else r"C:\Windows\System32\drivers\etc\hosts"

        try:
            with open(hosts_path, 'r') as f:
                lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]

            suspicious = [l for l in lines if any(
                domain in l.lower() for domain in
                ['google', 'facebook', 'bank', 'paypal', 'amazon', 'microsoft', 'apple']
            ) and 'localhost' not in l.lower()]

            return {"entries": lines[:20], "suspicious": suspicious, "warning": bool(suspicious)}
        except:
            return {"entries": [], "suspicious": [], "warning": False}

    def _scan_startup_items(self) -> Dict[str, Any]:
        """Scan startup items."""
        startup = []

        if self.platform == "linux":
            autostart = os.path.expanduser("~/.config/autostart")
            if os.path.exists(autostart):
                try:
                    startup = os.listdir(autostart)
                except:
                    pass

        return {"items": startup, "count": len(startup)}

    def _calculate_score(self, results: Dict) -> None:
        """Calculate security score from 0-100."""
        score = 100

        # Deduct for suspicious findings
        if results.get("malware_scan", {}).get("count", 0) > 0:
            score -= 20
            self.findings["threats"].append("Suspicious executables found")

        if results.get("hosts_file", {}).get("warning"):
            score -= 30
            self.findings["threats"].append("Hosts file may be hijacked")

        if len(results.get("scheduled_tasks", {}).get("tasks", [])) > 10:
            score -= 10
            self.findings["warnings"].append("Many scheduled tasks - review for suspicious entries")

        self.findings["score"] = max(0, score)

    def get_recommendations(self) -> List[str]:
        """Get security recommendations based on findings."""
        recs = []

        if self.findings["threats"]:
            recs.append("CRITICAL: Review threats immediately")

        if self.findings["warnings"]:
            recs.append("WARNING: " + "; ".join(self.findings["warnings"]))

        recs.extend([
            "Enable automatic security updates",
            "Use a password manager",
            "Enable two-factor authentication everywhere",
            "Review browser extensions quarterly",
            "Run security scans monthly"
        ])

        return recs


def main():
    """CLI entry point."""
    import json

    print("=" * 60)
    print("  BOTWAVE SECURITY SCANNER")
    print("=" * 60)
    print()

    scanner = SecurityScanner()
    result = scanner.run()

    print(f"\nSECURITY SCORE: {result['findings']['score']}/100")
    print(f"\nTHREATS: {len(result['findings']['threats'])}")
    for t in result['findings']['threats']:
        print(f"  ⚠️  {t}")

    print(f"\nWARNINGS: {len(result['findings']['warnings'])}")
    for w in result['findings']['warnings']:
        print(f"  ⚡ {w}")

    print("\nRECOMMENDATIONS:")
    for r in scanner.get_recommendations():
        print(f"  • {r}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()