import os
from typing import Any, Dict, List

import httpx

from backend.config.logging_config import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are the CyberShield XDR AI Assistant, an expert SOC Analyst and Cybersecurity Engineer.
Your goal is to help users analyze alerts, understand malware analysis reports, parse threat intelligence, and provide actionable remediation steps.
Be concise, professional, and accurate. Use markdown formatting to organize your responses.
If asked about a specific IP, domain, or hash, recommend checking the Threat Intelligence module.
"""

class AIAssistantService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o")

    async def chat(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        if not self.api_key:
            logger.info("No OPENAI_API_KEY found. Falling back to mock AI response.")
            return {
                "response": "I am operating in mock mode because the `OPENAI_API_KEY` is not configured in the environment variables. I can simulate responses, but I cannot perform real analysis right now. Please configure the key to enable full AI capabilities.",
                "model_used": "mock-ai-1.0",
                "is_mock": True
            }

        # Ensure system prompt is the first message
        api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for msg in messages:
            api_messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": api_messages,
                        "temperature": 0.2,
                        "max_tokens": 1000
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    return {
                        "response": content,
                        "model_used": self.model,
                        "is_mock": False
                    }
                else:
                    logger.error(f"OpenAI API Error: {response.text}")
                    return {
                        "response": f"Failed to reach AI service (Status {response.status_code}).",
                        "model_used": "error",
                        "is_mock": False
                    }
        except Exception as e:
            logger.error(f"AI Assistant Error: {e}")
            return {
                "response": "An error occurred while communicating with the AI service.",
                "model_used": "error",
                "is_mock": False
            }

ai_service = AIAssistantService()
