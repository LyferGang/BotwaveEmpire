from agent.base_agent import BaseAgent
import requests
import json
from typing import Dict, Any

class IntelligenceAgent(BaseAgent):
    def __init__(self):
        # Using one of your verified local models from the earlier curl check
        super().__init__(model_id="qwen3.5-4b-claude-4.6-os-auto-variable-heretic-uncensored-thinking")

    def sync_brain(self) -> Dict[str, Any]:
        """Verify and synchronize with local LLM brain"""
        
        try:
            # Test connection to LM Studio by checking available models
            response = requests.post(
                "http://localhost:1234/v1/models",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract model information
                models = data.get("data", [])
                available_models = [m["id"] for m in models]
                
                # Find the best model to use
                selected_model = self._select_best_model(available_models)
                
                return {
                    "status": "success", 
                    "message": f"Brain synchronized. Available models: {len(models)}. Selected: {selected_model}",
                    "data": {
                        "models_available": len(models),
                        "selected_model": selected_model,
                        "model_ids": available_models
                    }
                }
            else:
                return {
                    "status": "error", 
                    "message": f"LM Studio returned status code {response.status_code}"
                }
        except requests.exceptions.ConnectionError:
            return {
                "status": "error", 
                "message": "Connection error. LM Studio may not be running."
            }
        except requests.exceptions.Timeout:
            return {
                "status": "error", 
                "message": "LM Studio response timeout. Check network connectivity."
            }
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Brain sync failed: {str(e)}"
            }

    def _select_best_model(self, available_models: list) -> str:
        """Select the best model based on criteria"""
        
        # Priority order for model selection
        priority_order = [
            "qwen3.5-4b-claude-4.6-os-auto-variable-heretic-uncensored-thinking",
            "new-llama-3.1-8b-lexi-uncensored-v2-i1",
            "qwen3.5-9b-abliterated",
            "agent-qwen3.5-9b-claude-4.6-opus-abliterated-heretic"
        ]
        
        for model in priority_order:
            if model in available_models:
                return model
        
        # Fallback to first available model
        return available_models[0] if available_models else "unknown"

    def query_brain(self, system_prompt: str = "", user_query: str = "") -> Dict[str, Any]:
        """Query the local LLM brain"""
        
        try:
            # Select best model
            selected_model = self._select_best_model(["qwen3.5-4b-claude-4.6-os-auto-variable-heretic-uncensored-thinking"])
            
            response = requests.post(
                "http://localhost:1234/v1/chat/completions",
                json={
                    "model": selected_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_query}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2048
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "status": "success", 
                    "message": f"Query completed successfully.",
                    "data": {"response": result["choices"][0]["message"]["content"]}
                }
            else:
                return {
                    "status": "error", 
                    "message": f"LLM query failed with status code {response.status_code}"
                }
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Brain query failed: {str(e)}"
            }

    def analyze_response(self, response_text: str) -> Dict[str, Any]:
        """Analyze the quality and relevance of a brain response"""
        
        try:
            # Simple analysis based on response length and structure
            word_count = len(response_text.split())
            
            if word_count > 100:
                return {
                    "status": "success", 
                    "message": f"Response analyzed. Word count: {word_count}. Quality: High.",
                    "data": {"analysis": "Detailed response generated"}
                }
            elif word_count > 50:
                return {
                    "status": "success", 
                    "message": f"Response analyzed. Word count: {word_count}. Quality: Medium.",
                    "data": {"analysis": "Moderate response generated"}
                }
            else:
                return {
                    "status": "warning", 
                    "message": f"Response analyzed. Word count: {word_count}. Quality: Low.",
                    "data": {"analysis": "Brief response generated"}
                }
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Response analysis failed: {str(e)}"
            }
