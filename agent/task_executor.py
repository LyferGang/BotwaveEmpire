import importlib
import logging

class TaskExecutor:
    def __init__(self):
        self.registry = {
            "handshake": {"module": "agent.handshake_agent", "class": "HandshakeAgent", "method": "capture_handshake"},
            "audit": {"module": "agent.business_agent", "class": "BusinessAgent", "method": "display_audit"},
            "brain_sync": {"module": "agent.intelligence_agent", "class": "IntelligenceAgent", "method": "sync_brain"}
        }

    def run_task(self, task_name):
        if task_name not in self.registry:
            return f"Error: {task_name} not found."
            
        info = self.registry[task_name]
        try:
            module = importlib.import_module(info["module"])
            agent_class = getattr(module, info["class"])
            agent_instance = agent_class()
            method = getattr(agent_instance, info["method"])
            return method()
        except Exception as e:
            return f"Orchestration Error: {str(e)}"
