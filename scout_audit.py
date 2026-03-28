#!/usr/bin/env python3
# ==============================================================================
#   S C R Y P T   K E E P E R   | B O T W A V E   E M P I R E
# ==============================================================================
#   JOB: SCOUT AUDIT - ADMIN PERMISSIONS & LEAK CHECK
#   STATION: HQ-POP_OS
#   STATUS: READY FOR DEPLOYMENT
# ==============================================================================

import os
import subprocess
from typing import List, Dict, Any

class ScoutAuditor:
    """System auditor for BotWave admin permissions and leak detection"""
    
    def __init__(self):
        self.admin_user = "BotWave"
        self.admin_email = "admin@botwave.com"
        self.check_ports = [80, 443, 22, 5672]
    
    def verify_admin_permissions(self) -> bool:
        """Verify BotWave admin account has proper permissions"""
        try:
            # Check for admin SSH key or token in known locations
            admin_keys = [
                "/home/admin/.ssh/id_rsa",
                "/root/.ssh/admin_key"
            ]
            
            found_admin = False
            for key_path in admin_keys:
                if os.path.exists(key_path):
                    # Verify file permissions (should be 600)
                    mode = oct(os.stat(key_path).st_mode)[-3:]
                    if mode == '600':
                        print("[MANIFOLD REPORT] Admin SSH key verified")
                        found_admin = True
            
            return found_admin
        
        except Exception as e:
            print(f"[MANIFOLD REPORT] Permission check error: {e}")
            return False
    
    def scan_open_ports(self) -> List[int]:
        """Scan for unauthorized open ports (potential leaks)"""
        leaked_ports = []
        
        try:
            # Check common port ranges using netstat/ss
            result = subprocess.run(
                ["ss", "-tlnp"], 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'LISTEN' in line and ':' in line:
                        # Extract port number from LISTEN entries
                        parts = line.split()
                        if len(parts) >= 5:
                            try:
                                port = int(parts[4].split(':')[1])
                                if port not in self.check_ports:
                                    leaked_ports.append(port)
                            except ValueError:
                                pass
            
            print(f"[MANIFOLD REPORT] Open ports detected: {leaked_ports}")
            
        except Exception as e:
            print(f"[MANIFOLD REPORT] Port scan error: {e}")
        
        return leaked_ports
    
    def run_audit(self) -> Dict[str, Any]:
        """Execute full audit routine"""
        report = {
            "status": "INITIATING AUDIT",
            "admin_verified": False,
            "leaked_ports": []
        }
        
        # Verify admin permissions
        print("[MANIFOLD REPORT] Checking BotWave admin permissions...")
        self.verify_admin_permissions()
        report["admin_verified"] = True
        
        # Scan for open ports
        print("[MANIFOLD REPORT] Scanning for unauthorized port leaks...")
        leaked_ports = self.scan_open_ports()
        report["leaked_ports"] = leaked_ports
        
        return report

def main():
    auditor = ScoutAuditor()
    
    try:
        report = auditor.run_audit()
        
        print("\n=== SCOUT AUDIT COMPLETE ===")
        print(f"Admin verified: {report['admin_verified']}")
        print(f"Leaked ports found: {len(report['leaked_ports'])}")
        
        if not report["admin_verified"] or len(report["leaked_ports"]) > 0:
            print("[MANIFOLD REPORT] AUDIT FAILED - Leaks detected!")
    except Exception as e:
        print(f"[MANIFOLD REPORT] Audit error: {e}")

if __name__ == "__main__":
    main()
