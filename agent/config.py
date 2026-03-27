"""
Configuration Manager - Handles API keys and bot settings
Securely manages all external service credentials
"""

import os
from typing import Dict, Any


class ConfigManager:
    """Centralized configuration manager for API keys"""
    
    def __init__(self):
        self.api_keys = {}
        
    def load_from_env(self) -> bool:
        """Load API keys from environment variables"""
        try:
            # LLM Service Keys
            self.api_keys['llm_api_key'] = os.getenv('LLM_API_KEY', '')
            
            # Business/Payment Service Keys
            self.api_keys['business_payment_key'] = os.getenv('BUSINESS_PAYMENT_KEY', '')
            self.api_keys['payment_gateway_key'] = os.getenv('PAYMENT_GATEWAY_KEY', '')
            
            # External API Keys
            self.api_keys['external_api_key'] = os.getenv('EXTERNAL_API_KEY', '')
            self.api_keys['notification_service_key'] = os.getenv('NOTIFICATION_SERVICE_KEY', '')
            
            return True
        except Exception as e:
            print(f"Error loading config from env: {e}")
            return False
    
    def get(self, key_name: str) -> str:
        """Get a specific API key"""
        return self.api_keys.get(key_name, '')
    
    def has_key(self, key_name: str) -> bool:
        """Check if a key exists and is set"""
        return bool(self.api_keys.get(key_name))
    
    def save_to_file(self, config_file: str = '.bot_config.json') -> bool:
        """Save configuration to file for backup"""
        try:
            import json
            with open(config_file, 'w') as f:
                json.dump({k: v for k, v in self.api_keys.items() if v}, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config to file: {e}")
            return False
    
    def load_from_file(self, config_file: str = '.bot_config.json') -> bool:
        """Load configuration from backup file"""
        try:
            import json
            with open(config_file, 'r') as f:
                loaded_keys = json.load(f)
            
            # Merge with existing keys (file takes precedence for missing keys)
            self.api_keys.update(loaded_keys)
            return True
        except Exception as e:
            print(f"Error loading config from file: {e}")
            return False


# Global config instance
config = ConfigManager()

def get_config():
    """Get the global configuration manager"""
    return config
