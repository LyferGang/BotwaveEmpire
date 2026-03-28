#!/usr/bin/env python3
# ==============================================================================
#   S C R Y P T   K E E P E R   | B O T W A V E   E M P I R E
# ==============================================================================
#   JOB: FULL SYSTEM COMMISSIONING
#   STATION: HQ-POP_OS
#   STATUS: READY FOR DEPLOYMENT
# ==============================================================================

import subprocess
import os
from typing import Dict, Any

def log_event(message):
    """Logging manifold for system events using plumbing terminology."""
    print(f"[MANIFOLD REPORT] {message}")

def run_script(script_path: str) -> bool:
    """Execute a script and return success status"""
    try:
        result = subprocess.run(
            ["python3", script_path], 
            capture_output=True, 
            text=True
        )
        
        if result.returncode == 0:
            print(f"[MANIFOLD REPORT] Script executed successfully: {os.path.basename(script_path)}")
            return True
        else:
            log_event(f"Script failed with exit code: {result.returncode}")
            return False
            
    except Exception as e:
        log_event(f"Script execution error: {e}")
        return False

def main():
    scripts = [
        "forensic_clean.py",
        "scout_audit.py", 
        "system_overhaul.py",
        "foreman_dispatch.py"
    ]
    
    report = {
        "status": "COMMISSIONING SEQUENCE INITIATED",
        "all_passed": True,
        "failed_at": None
    }
    
    try:
        # THE FLUSH (SIPHONER)
        print("\n=== PHASE 1: THE FLUSH ===")
        if not run_script("forensic_clean.py"):
            report["status"] = "CLEANUP FAILED"
            report["all_passed"] = False
            report["failed_at"] = "FORENSIC CLEAN"
            break
        
        # THE INSPECTION (SCOUT)
        print("\n=== PHASE 2: THE INSPECTION ===")
        if not run_script("scout_audit.py"):
            report["status"] = "AUDIT FAILED"
            report["all_passed"] = False
            report["failed_at"] = "SCOUT AUDIT"
            break
        
        # THE OVERHAUL
        print("\n=== PHASE 3: THE OVERHAUL ===")
        if not run_script("system_overhaul.py"):
            report["status"] = "OVERHAUL FAILED"
            report["all_passed"] = False
            report["failed_at"] = "SYSTEM OVERHAUL"
            break
        
        # THE DISPATCH (FOREMAN)
        print("\n=== PHASE 4: THE DISPATCH ===")
        if not run_script("foreman_dispatch.py"):
            log_event("Dispatch failed - bleeding lines...")
            report["status"] = "DISPATCH FAILED"
            report["all_passed"] = False
            report["failed_at"] = "FOREMAN DISPATCH"
            break
        
    except Exception as e:
        print(f"[MANIFOLD REPORT] Commissioning error: {e}")
    
    # Final status report
    if report["all_passed"]:
        print("\n=== SITUATION: HQ FULLY OPTIMIZED ===")
    else:
        print(f"\n=== COMMISSIONING FAILED AT: {report['failed_at']} ===")

if __name__ == "__main__":
    main()
