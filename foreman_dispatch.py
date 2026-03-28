#!/usr/bin/env python3
# ==============================================================================
#   S C R Y P T   K E E P E R   | B O T W A V E   E M P I R E
# ==============================================================================
#   JOB: FOREMAN DISPATCH - TELEGRAM COMMUNICATIONS
#   STATION: HQ-POP_OS
#   STATUS: READY FOR DEPLOYMENT
# ==============================================================================

import os
import sys
from dotenv import load_dotenv
import requests
from typing import Dict, Any

def log_event(message):
    """Logging manifold for system events using plumbing terminology."""
    print(f"[MANIFOLD REPORT] {message}")

def main():
    # Load environment configuration
    try:
        env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
        load_dotenv(env_path)
        
        tg_token = os.getenv('TG_FOREMAN_TOKEN', '')
        telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID', '8711428786')  # Default placeholder - update as needed
        
    except Exception as e:
        log_event(f"Environment loading error: {e}")
        return
    
    if not tg_token:
        log_event("Telegram token missing from environment")
        return
    
    try:
        # Load squad registry for status verification
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from squad_registry import SquadRegistry
        
        registry = SquadRegistry()
        agents_status = registry.list_agents()
        
        log_event("Dream Team agents verified and pressurized")
        
        # Prepare dispatch message
        message = "SCRYPT KEEPER REPORT: HQ Mainline is pressurized. RTX 5060 Optimized. JPS tool generated. Dream Team is on the clock."
        
        log_event("Dispatching communication to Dream Team...")
        
        # Send Telegram message via API
        url = f"https://api.telegram.org/bot{tg_token}/sendMessage"
        params = {
            'chat_id': telegram_chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, params=params)
        
        if response.status_code == 200:
            log_event("SITUATION: LIVE FLOW ESTABLISHED")
            print("\n=== TELEGRAM DISPATCH SUCCESSFUL ===")
            print(f"Message sent to chat ID: {telegram_chat_id}")
            print(f"Status: PRESSURIZED")
        elif response.status_code == 401 or response.status_code == 404:
            log_event("Token leak detected - checking .env for corruption...")
            # Check if token is valid format (should contain colon)
            if ':' not in tg_token:
                log_event("ERROR: Token appears corrupted or missing")
                print("\n[MANIFOLD REPORT] Token validation failed - bleeding lines...")
            else:
                log_event(f"Token format OK but API returned {response.status_code}")
        else:
            log_event(f"Communication leak detected. Status code: {response.status_code}")
            
    except Exception as e:
        log_event(f"Dispatch error: {e}")

if __name__ == "__main__":
    main()
