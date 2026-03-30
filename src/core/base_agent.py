"""
Base Agent Class
All agents inherit from this base class for consistent behavior
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime


class BaseAgent(ABC):
    """
    Abstract base class for all Botwave agents.

    Provides common functionality for:
    - Configuration management
    - Logging
    - Task execution tracking
    - Result formatting
    """

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the agent.

        Args:
            name: Unique agent identifier
            config: Optional configuration dictionary
        """
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"agent.{name}")
        self.created_at = datetime.utcnow().isoformat()

    @abstractmethod
    def run(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's primary task.

        Args:
            task_input: Task parameters and context

        Returns:
            Standardized result dictionary with status, data, and metadata
        """
        pass

    def health_check(self) -> Dict[str, Any]:
        """
        Verify agent is operational.

        Returns:
            Health status dictionary
        """
        return {
            "status": "healthy",
            "agent": self.name,
            "timestamp": datetime.utcnow().isoformat()
        }

    def _format_success(self, data: Dict[str, Any], message: str = "") -> Dict[str, Any]:
        """Format a successful result."""
        return {
            "status": "success",
            "agent": self.name,
            "message": message,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }

    def _format_error(self, error: Exception, message: str = "") -> Dict[str, Any]:
        """Format an error result."""
        self.logger.error(f"Agent {self.name} error: {str(error)}")
        return {
            "status": "error",
            "agent": self.name,
            "message": message or str(error),
            "error_type": type(error).__name__,
            "timestamp": datetime.utcnow().isoformat()
        }
