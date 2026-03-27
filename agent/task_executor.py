import importlib
import logging
from typing import Dict, Any

class TaskExecutor:
    def __init__(self):
        self.registry = {
            "handshake": {"module": "agent.handshake_agent", "class": "HandshakeAgent", "method": "capture_handshake"},
            "audit": {"module": "agent.business_agent", "class": "BusinessAgent", "method": "display_audit"},
            "brain_sync": {"module": "agent.intelligence_agent", "class": "IntelligenceAgent", "method": "sync_brain"}
        }

    def run_task(self, task_name: str) -> Dict[str, Any]:
        """Execute a registered task"""
        
        if task_name not in self.registry:
            return {
                "status": "error", 
                "message": f"Task '{task_name}' not found. Available tasks: {', '.join(self.registry.keys())}"
            }
            
        info = self.registry[task_name]
        
        try:
            # Dynamically import the module
            module = importlib.import_module(info["module"])
            
            # Get the agent class
            agent_class = getattr(module, info["class"])
            
            # Instantiate the agent
            agent_instance = agent_class()
            
            # Execute the method
            result = getattr(agent_instance, info["method"])(**info.get("kwargs", {}))
            
            return {
                "status": "success", 
                "message": f"Task '{task_name}' executed successfully.",
                "data": result.get("data", {})
            }
        except Exception as e:
            logging.error(f"Error executing task '{task_name}': {str(e)}")
            return {
                "status": "error", 
                "message": f"Task execution failed for '{task_name}': {str(e)}"
            }

    def list_available_tasks(self) -> Dict[str, Any]:
        """List all available tasks"""
        
        return {
            "status": "success", 
            "message": "Available tasks listed.",
            "data": {"tasks": list(self.registry.keys())}
        }

    def get_task_info(self, task_name: str) -> Dict[str, Any]:
        """Get information about a specific task"""
        
        if task_name not in self.registry:
            return {
                "status": "error", 
                "message": f"Task '{task_name}' not found."
            }
            
        info = self.registry[task_name]
        
        return {
            "status": "success", 
            "message": f"Task information retrieved.",
            "data": {
                "name": task_name,
                "module": info["module"],
                "class": info["class"],
                "method": info["method"]
            }
        }

    def execute_task_with_args(self, task_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a registered task with additional arguments"""
        
        if task_name not in self.registry:
            return {
                "status": "error", 
                "message": f"Task '{task_name}' not found."
            }
            
        info = self.registry[task_name]
        
        try:
            # Dynamically import the module
            module = importlib.import_module(info["module"])
            
            # Get the agent class
            agent_class = getattr(module, info["class"])
            
            # Instantiate the agent
            agent_instance = agent_class()
            
            # Execute the method with arguments
            result = getattr(agent_instance, info["method"])(**kwargs)
            
            return {
                "status": "success", 
                "message": f"Task '{task_name}' executed successfully.",
                "data": result.get("data", {})
            }
        except Exception as e:
            logging.error(f"Error executing task '{task_name}': {str(e)}")
            return {
                "status": "error", 
                "message": f"Task execution failed for '{task_name}': {str(e)}"
            }

    def health_check(self) -> Dict[str, Any]:
        """Perform a health check on all agents"""
        
        try:
            # Check each agent module can be imported
            modules = [
                "agent.handshake_agent",
                "agent.business_agent", 
                "agent.intelligence_agent"
            ]
            
            healthy_count = 0
            
            for module_name in modules:
                try:
                    importlib.import_module(module_name)
                    healthy_count += 1
                except Exception as e:
                    logging.error(f"Module {module_name} failed: {str(e)}")
            
            return {
                "status": "success", 
                "message": f"Health check complete. {healthy_count}/{len(modules)} modules healthy.",
                "data": {"healthy_modules": healthy_count, "total_modules": len(modules)}
            }
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Health check failed: {str(e)}"
            }

    def reload_registry(self) -> Dict[str, Any]:
        """Reload the task registry from files"""
        
        try:
            # Clear current registry
            self.registry.clear()
            
            # Reload each module
            modules = [
                "agent.handshake_agent",
                "agent.business_agent", 
                "agent.intelligence_agent"
            ]
            
            for module_name in modules:
                try:
                    importlib.import_module(module_name)
                except Exception as e:
                    logging.error(f"Failed to reload {module_name}: {str(e)}")
            
            return {
                "status": "success", 
                "message": f"Registry reloaded. Available tasks: {', '.join(self.registry.keys())}",
                "data": {"tasks": list(self.registry.keys())}
            }
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Registry reload failed: {str(e)}"
            }

    def shutdown(self) -> Dict[str, Any]:
        """Gracefully shut down the task executor"""
        
        try:
            # Log shutdown message
            logging.info("TaskExecutor shutting down...")
            
            return {
                "status": "success", 
                "message": "TaskExecutor shutdown complete.",
                "data": {}
            }
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Shutdown failed: {str(e)}"
            }

    def __del__(self):
        """Destructor for cleanup"""
        
        try:
            self.shutdown()
        except Exception:
            pass
