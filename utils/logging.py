import logging.config
from typing import Dict

class CustomLogger:
    """Custom logger class with a predefined configuration."""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    @staticmethod
    def configure_logging(config: Dict[str, Any]) -> None:
        """Configure the root logger using a provided dictionary."""
        
        logging.config.dictConfig(config)
