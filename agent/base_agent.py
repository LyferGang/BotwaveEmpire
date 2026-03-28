import logging

class BaseAgent:
    """The foundational AI agent class for the Scrypt Keeper stack."""
    
    def __init__(self, model_id="qwen3.5-4b-uncensored-hauhaucs-aggressive"):
        # Locks the target model for any agent that inherits this class
        self.model_id = model_id
        self.api_base = "http://localhost:1234/v1"
        self.headers = {"Content-Type": "application/json"}
        
        # Setup tactical logging
        logging.basicConfig(
            level=logging.INFO,
            format='[FORGE] %(asctime)s - %(message)s',
            datefmt='%H:%M:%S'
        )
