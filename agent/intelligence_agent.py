from agent.base_agent import BaseAgent

class IntelligenceAgent(BaseAgent):
    def __init__(self):
        # Using one of your verified local models from the earlier curl check
        super().__init__(model_id="qwen3.5-9b-abliterated")

    def sync_brain(self):
        print("\n[INTELLIGENCE] Pinging Local Brain at localhost:1234...")
        
        system_prompt = "You are the Scrypt Keeper Core Intelligence."
        user_query = "Respond with the word 'SUCCESS' if you are online and ready."
        
        # Test the connection to LM Studio
        response = self.query_brain(system_prompt, user_query)
        
        if "SUCCESS" in response.upper():
            return "SUCCESS: OpenClaw Brain is Synchronized."
        else:
            return f"Brain Error: Received unexpected response -> {response}"
