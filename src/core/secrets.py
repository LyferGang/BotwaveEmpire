"""
Secure Secrets Management
Handles credential loading from environment variables only.
No hardcoded secrets - ever.
"""

import os
from typing import Optional, Dict, Any
from pathlib import Path


class SecretsManager:
    """
    Professional secrets management.

    All credentials are loaded from environment variables.
    Supports:
    - Local .env file (not in git)
    - Docker secrets
    - CI/CD environment variables
    - Cloud secret managers (extensible)
    """

    _instance = None
    _secrets: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_secrets()
        return cls._instance

    def _load_secrets(self) -> None:
        """Load all secrets from environment."""
        self._secrets = {
            # AI Providers
            'openrouter': os.getenv('OPENROUTER_API_KEY'),
            'gemini': os.getenv('GEMINI_API_KEY'),
            'xai': os.getenv('XAI_API_KEY'),
            'groq': os.getenv('GROQ_API_KEY'),
            'anthropic': os.getenv('ANTHROPIC_API_KEY'),

            # Communication
            'telegram_foreman': os.getenv('TG_FOREMAN_TOKEN'),
            'telegram_chat_id': os.getenv('TELEGRAM_CHAT_ID'),
            'discord_bot': os.getenv('DISCORD_BOT_TOKEN'),
            'discord_webhook': os.getenv('DISCORD_WEBHOOK_URL'),

            # Search
            'brave': os.getenv('BRAVE_API_KEY'),

            # Cloud
            'cloudflare_token': os.getenv('CF_API_TOKEN'),
            'cloudflare_zone': os.getenv('CF_ZONE_ID'),
            'cloudflare_account': os.getenv('CF_ACCOUNT_ID'),

            # Git
            'github_token': os.getenv('GH_PAT_TOKEN') or os.getenv('GITHUB_TOKEN'),

            # API Security
            'api_secret': os.getenv('API_SECRET_KEY'),
            'debug_key': os.getenv('DEBUG_API_KEY'),

            # Blockchain
            'polymarket_secret': os.getenv('POLYMARKET_SECRET_KEY'),
            'polymarket_wallet': os.getenv('POLYMARKET_WALLET_ADDRESS'),
        }

    def get(self, key: str) -> Optional[str]:
        """Get a secret by key."""
        return self._secrets.get(key)

    def has(self, key: str) -> bool:
        """Check if a secret exists and is not empty."""
        value = self._secrets.get(key)
        return bool(value and value.strip() and not value.startswith('your-'))

    def mask(self, key: str) -> str:
        """Return masked version of secret for logging."""
        value = self._secrets.get(key)
        if not value:
            return "[NOT SET]"
        if len(value) <= 8:
            return "***"
        return f"{value[:4]}...{value[-4:]}"

    def validate_required(self, required: list) -> bool:
        """Validate that required secrets are present."""
        missing = [key for key in required if not self.has(key)]
        if missing:
            raise ValueError(f"Missing required secrets: {', '.join(missing)}")
        return True


# Global instance
secrets = SecretsManager()
