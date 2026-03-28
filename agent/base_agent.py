import logging
from typing import Dict, Any

class BaseAgent:
    """Base class for all agents in the system."""

    def __init__(self, model_id: str):
        self.model_id = model_id
        self.logger = logging.getLogger(self.__class__.__name__)

    def process_message(self, message: str) -> Dict[str, Any]:
        """Process an incoming message and return a response."""
        
        raise NotImplementedError("Subclasses must implement this method")

    def handle_exception(self, exception: Exception) -> Dict[str, Any]:
        """Handle any exceptions that occur during processing."""
        
        self.logger.error(f"Error occurred: {str(exception)}")
        return {
            "status": "error",
            "message": f"An error occurred: {str(exception)}"
        }
