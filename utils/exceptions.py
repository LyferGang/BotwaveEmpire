class AgentError(Exception):
    """Base exception class for all agent-related errors."""

    pass

class ModelNotFoundError(AgentError):
    """Raised when a model is not found in the registry."""

    def __init__(self, model_id: str):
        self.model_id = model_id
        super().__init__(f"Model '{model_id}' not found.")

class ProcessingError(AgentError):
    """Raised when an error occurs during message processing."""

    def __init__(self, exception: Exception):
        self.exception = exception
        super().__init__(f"An error occurred: {str(exception)}")
