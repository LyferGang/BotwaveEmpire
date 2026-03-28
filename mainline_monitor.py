#!/usr/bin/env python3
# ==============================================================================
#   S C R Y P T  K E E P E R   | B O T W A V E   E M P I R E
# ==============================================================================
#   JOB: MAINLINE MONITOR - EXFIL VAULT MANAGEMENT
#   STATION: HQ-POP_OS
#   STATUS: READY FOR DEPLOYMENT
# ==============================================================================

import os
import time
import subprocess
import sys
from pathlib import Path

VAULT_PATH = os.path.expanduser("~/BotwaveEmpire/Exfil_Vault/")

def log_event(message):
    """Logging manifold for system events using plumbing terminology."""
    print(f"[MANIFOLD REPORT] {message}")

def check_exfil():
    """Monitor Tailscale pipe for exfiltration artifacts."""
    try:
        # Run tailscale file get command
        result = subprocess.run(
            ['tailscale', 'file', 'get', '.'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        stdout = result.stdout
        
        # Check for JPS_Exfil*.zip in output
        for line in stdout.split('\n'):
            if 'JPS_Exfil*' in line and '.zip' in line:
                filename = line.strip().split()[-1] if line.strip().endswith('.zip') else line.strip()
                
                # Calculate file size
                try:
                    source_path = os.path.join(os.getcwd(), filename)
                    file_size = os.path.getsize(source_path)
                except FileNotFoundError:
                    file_size = 0
                
                # Move to vault
                dest_path = os.path.join(VAULT_PATH, filename)
                if not os.path.exists(dest_path):
                    import shutil
                    shutil.copy2(source_path, dest_path)
                    
                    log_event(f"[MONITOR] {time.strftime('%Y-%m-%d %H:%M:%S')} - Moved {filename} ({file_size} bytes)")
                    return True
        
        return False
    
    except Exception as e:
        log_event(f"Exfil check error: {e}")
        return False

def dispatch_alert(filename):
    """Dispatch alert to foreman_dispatch.py with exfil confirmation."""
    try:
        message = f"SITUATION: SIPHON SUCCESSFUL. [{filename}] HAS LANDED IN THE VAULT."
        
        # Call foreman_dispatch.py with the message parameter
        import subprocess as sp
        
        result = sp.run(
            [sys.executable, 'foreman_dispatch.py', '--message', message],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            log_event(f"Alert dispatched for {filename}")
        else:
            log_event(f"Failed to dispatch alert for {filename}: {result.stderr}")
    
    except Exception as e:
        log_event(f"Dispatch error: {e}")

def main():
    # Print startup message immediately
    print("SITUATION: MONITORING STATION ONLINE")
    
    # Create vault directory if it doesn't exist
    try:
        os.makedirs(VAULT_PATH, exist_ok=True)
        log_event(f"Vault path established: {VAULT_PATH}")
    except Exception as e:
        log_event(f"Vault creation error: {e}")
    
    while True:
        # Check for exfiltration artifacts every 30 seconds
        check_exfil()
        
        time.sleep(30)

if __name__ == "__main__":
    main()
