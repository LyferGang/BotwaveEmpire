"""
Botwave Core Framework
Professional multi-agent automation platform
"""

__version__ = "1.0.0"
__author__ = "Botwave Empire"

from .base_agent import BaseAgent
from .config import Config
from .task import Task, TaskStatus
from .registry import AgentRegistry

__all__ = ["BaseAgent", "Config", "Task", "TaskStatus", "AgentRegistry"]
