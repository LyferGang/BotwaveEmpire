from typing import Dict, Any

class PlumbingManager:
    """Manages the plumbing infrastructure and provides services to other agents."""

    def __init__(self):
        self.plumbing_agents = {}

    def register_agent(self, agent_name: str, agent_instance: object) -> None:
        """Register a new plumbing agent with the manager."""
        
        self.plumbing_agents[agent_name] = agent_instance

    def get_agent(self, agent_name: str) -> object:
        """Retrieve an existing plumbing agent from the registry."""
        
        return self.plumbing_agents.get(agent_name)
