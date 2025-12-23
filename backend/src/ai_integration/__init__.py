"""AI Integration Module

LLM clients and fallback orchestration for Phase III AI Teaching Roles.
"""

from .anthropic_client import AnthropicClient
from .openai_client import OpenAIClient
from .gemini_client import GeminiClient
from .llm_fallback import LLMFallbackOrchestrator, LLMProvider

__all__ = [
    "AnthropicClient",
    "OpenAIClient",
    "GeminiClient",
    "LLMFallbackOrchestrator",
    "LLMProvider",
]
