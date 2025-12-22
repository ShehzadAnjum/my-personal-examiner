"""OpenAI GPT-4 Client (Fallback LLM)

Secondary/fallback LLM when Claude Sonnet is unavailable.

Constitutional Requirements:
- Principle VII: >80% test coverage (client designed for testability)
"""

import os
from typing import Optional

from openai import OpenAI, AsyncOpenAI


class OpenAIClient:
    """
    Client for OpenAI GPT-4 API (fallback LLM).

    Used as fallback when Claude Sonnet 4.5 is unavailable.
    Provides similar capabilities with slightly different prompt formatting.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4-turbo-preview"):
        """
        Initialize OpenAI client.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model name (defaults to GPT-4 Turbo)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable or api_key parameter required")

        self.model = model
        self.client = OpenAI(api_key=self.api_key)
        self.async_client = AsyncOpenAI(api_key=self.api_key)

    def generate_completion(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Generate completion using GPT-4 (synchronous).

        Args:
            prompt: User prompt
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum response tokens
            system_prompt: Optional system prompt

        Returns:
            Generated completion text

        Raises:
            openai.OpenAIError: If API call fails
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content or ""

    async def generate_completion_async(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Generate completion using GPT-4 (asynchronous).

        Args:
            prompt: User prompt
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum response tokens
            system_prompt: Optional system prompt

        Returns:
            Generated completion text

        Raises:
            openai.OpenAIError: If API call fails
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await self.async_client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content or ""

    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"<OpenAIClient(model={self.model})>"
