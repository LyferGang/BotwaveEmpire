"""
Configuration Manager
Handles environment variables and configuration loading
"""

import os
from typing import Optional, Dict, Any
from pathlib import Path


class Config:
    """
    Centralized configuration management.

    Loads configuration from environment variables with sensible defaults.
    All secrets must be provided via environment - no hardcoded values.
    """

    # LLM Configuration - Optimized for Fast Response (LM Studio)
    # Model: qwen3.5-4b-uncensored-hauhaucs-aggressive (32K context, 4 parallel)
    LLM_API_URL: str = os.getenv("LLM_API_URL", "http://localhost:1234/v1")
    LLM_API_KEY: Optional[str] = os.getenv("LLM_API_KEY", "lm-studio")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "qwen3.5-4b-uncensored-hauhaucs-aggressive")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.3"))  # Lower for consistent responses
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "512"))  # Fast response, short answers
    LLM_CONTEXT_WINDOW: int = int(os.getenv("LLM_CONTEXT_WINDOW", "8192"))  # Match LM Studio setting
    LLM_REQUEST_TIMEOUT: int = int(os.getenv("LLM_REQUEST_TIMEOUT", "15"))  # Fast fail, 15 seconds
    LLM_PARALLEL_REQUESTS: int = int(os.getenv("LLM_PARALLEL_REQUESTS", "4"))  # Match LM Studio

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///data/botwave.db")

    # API Server
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8080"))
    API_SECRET_KEY: str = os.getenv("API_SECRET_KEY", "development-key-change-in-production")
    API_DEBUG: bool = os.getenv("API_DEBUG", "false").lower() == "true"

    # Agent Settings
    AGENT_TIMEOUT: int = int(os.getenv("AGENT_TIMEOUT", "300"))
    AGENT_MAX_RETRIES: int = int(os.getenv("AGENT_MAX_RETRIES", "3"))
    AGENT_LOG_LEVEL: str = os.getenv("AGENT_LOG_LEVEL", "INFO")

    # Paths
    DATA_DIR: Path = Path(os.getenv("DATA_DIR", "/app/data"))
    LOGS_DIR: Path = Path(os.getenv("LOGS_DIR", "/app/logs"))
    VAULT_DIR: Path = Path(os.getenv("VAULT_DIR", "/app/vault"))

    @classmethod
    def ensure_directories(cls) -> None:
        """Create required directories if they don't exist."""
        for path in [cls.DATA_DIR, cls.LOGS_DIR, cls.VAULT_DIR]:
            path.mkdir(parents=True, exist_ok=True)

    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Export configuration as dictionary (excludes secrets)."""
        return {
            "llm_model": cls.LLM_MODEL,
            "llm_temperature": cls.LLM_TEMPERATURE,
            "llm_max_tokens": cls.LLM_MAX_TOKENS,
            "database_url": cls.DATABASE_URL.replace("//", "//***@") if "@" in cls.DATABASE_URL else cls.DATABASE_URL,
            "api_host": cls.API_HOST,
            "api_port": cls.API_PORT,
            "agent_timeout": cls.AGENT_TIMEOUT,
            "agent_max_retries": cls.AGENT_MAX_RETRIES,
            "data_dir": str(cls.DATA_DIR),
            "logs_dir": str(cls.LOGS_DIR),
            "vault_dir": str(cls.VAULT_DIR),
        }
