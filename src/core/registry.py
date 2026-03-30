"""
Agent Registry
Manages agent registration and discovery.
"""

from typing import Dict, Type, Any
from core.base_agent import BaseAgent


class AgentRegistry:
    """Registry for managing available agents."""

    _agents: Dict[str, Type[BaseAgent]] = {}

    @classmethod
    def register(cls, name: str, agent_class: Type[BaseAgent]) -> None:
        """Register an agent class."""
        cls._agents[name] = agent_class

    @classmethod
    def get(cls, name: str) -> Type[BaseAgent]:
        """Get an agent class by name."""
        if name not in cls._agents:
            raise ValueError(f"Agent '{name}' not found in registry")
        return cls._agents[name]

    @classmethod
    def list_agents(cls) -> Dict[str, Any]:
        """List all registered agents."""
        return {
            name: {
                "class": agent_class.__name__,
                "module": agent_class.__module__
            }
            for name, agent_class in cls._agents.items()
        }

    @classmethod
    def is_registered(cls, name: str) -> bool:
        """Check if an agent is registered."""
        return name in cls._agents


# Global registry instance
registry = AgentRegistry()
