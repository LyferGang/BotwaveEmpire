"""
Intelligence Agent
LLM-powered analysis and data processing
"""

import requests
import json
from typing import Dict, Any, Optional
from datetime import datetime

from core.base_agent import BaseAgent
from core.config import Config


class IntelligenceAgent(BaseAgent):
    """
    Agent for LLM-powered intelligence operations.

    Capabilities:
    - Text analysis and summarization
    - Code review and generation
    - Data extraction and transformation
    - Reasoning and problem solving
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("intelligence", config)
        self.model = config.get("model", Config.LLM_MODEL) if config else Config.LLM_MODEL
        self.api_url = Config.LLM_API_URL
        self.api_key = Config.LLM_API_KEY

    def run(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute intelligence task.

        Args:
            task_input: Must contain 'action' and 'prompt' or 'text'

        Returns:
            Standardized result with LLM response
        """
        action = task_input.get("action", "analyze")

        try:
            if action == "analyze":
                return self._analyze(task_input)
            elif action == "summarize":
                return self._summarize(task_input)
            elif action == "generate":
                return self._generate(task_input)
            elif action == "review":
                return self._review_code(task_input)
            else:
                return self._format_error(
                    ValueError(f"Unknown action: {action}"),
                    "Supported: analyze, summarize, generate, review"
                )
        except Exception as e:
            return self._format_error(e)

    def _query_llm(self, messages: list, temperature: float = None) -> str:
        """Query the local LLM via API."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or Config.LLM_TEMPERATURE,
            "max_tokens": Config.LLM_MAX_TOKENS
        }

        response = requests.post(
            f"{self.api_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=Config.AGENT_TIMEOUT
        )
        response.raise_for_status()

        return response.json()["choices"][0]["message"]["content"]

    def _analyze(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze text or data."""
        text = task_input.get("text", "")
        context = task_input.get("context", "")

        if not text:
            return self._format_error(
                ValueError("No text provided"),
                "Analysis requires text input"
            )

        messages = [
            {"role": "system", "content": "You are an analytical assistant. Provide clear, structured analysis."},
            {"role": "user", "content": f"Context: {context}\n\nAnalyze the following:\n{text}"}
        ]

        result = self._query_llm(messages)

        return self._format_success({
            "analysis": result,
            "model_used": self.model,
            "input_length": len(text)
        }, "Analysis complete")

    def _summarize(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize text."""
        text = task_input.get("text", "")
        max_length = task_input.get("max_length", "concise")

        if not text:
            return self._format_error(ValueError("No text provided"))

        messages = [
            {"role": "system", "content": f"Summarize the following text in a {max_length} manner."},
            {"role": "user", "content": text}
        ]

        result = self._query_llm(messages)

        return self._format_success({
            "summary": result,
            "original_length": len(text),
            "summary_length": len(result)
        }, "Summary generated")

    def _generate(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content."""
        prompt = task_input.get("prompt", "")
        content_type = task_input.get("content_type", "text")

        messages = [
            {"role": "system", "content": f"You are a helpful assistant generating {content_type}."},
            {"role": "user", "content": prompt}
        ]

        result = self._query_llm(messages, temperature=0.8)

        return self._format_success({
            "generated": result,
            "content_type": content_type
        }, "Content generated")

    def _review_code(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """Review code for issues."""
        code = task_input.get("code", "")
        language = task_input.get("language", "python")

        if not code:
            return self._format_error(ValueError("No code provided"))

        messages = [
            {"role": "system", "content": f"You are a code reviewer. Review {language} code for bugs, security issues, and improvements."},
            {"role": "user", "content": f"Review this code:\n\n```{language}\n{code}\n```"}
        ]

        result = self._query_llm(messages, temperature=0.3)

        return self._format_success({
            "review": result,
            "language": language,
            "lines_analyzed": len(code.splitlines())
        }, "Code review complete")

    def health_check(self) -> Dict[str, Any]:
        """Check LLM connectivity."""
        try:
            response = requests.get(f"{self.api_url}/models", timeout=10)
            if response.status_code == 200:
                models = response.json().get("data", [])
                return {
                    "status": "healthy",
                    "llm_connection": "connected",
                    "available_models": len(models),
                    "current_model": self.model
                }
            else:
                return {
                    "status": "degraded",
                    "llm_connection": "error",
                    "error": f"Status {response.status_code}"
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "llm_connection": "failed",
                "error": str(e)
            }


if __name__ == "__main__":
    import logging
    import time
    import os

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("intelligence_agent")

    agent = IntelligenceAgent()
    logger.info(f"Intelligence Agent started - PID {os.getpid()}")

    while True:
        health = agent.health_check()
        logger.debug(f"Health check: {health}")
        time.sleep(30)
