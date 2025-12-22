"""Google Gemini Client (Fallback LLM)

Tertiary/fallback LLM when both Claude and GPT-4 are unavailable.
Uses OpenAI-compatible API for better compatibility.

Constitutional Requirements:
- Principle VII: >80% test coverage (client designed for testability)
"""

import os
from typing import Optional

from openai import AsyncOpenAI


class GeminiClient:
    """
    Client for Google Gemini API (tertiary fallback LLM).

    Used as final fallback when both Claude Sonnet 4.5 and GPT-4 are unavailable.
    Uses Gemini's OpenAI-compatible API endpoint.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash"):
        """
        Initialize Gemini client using OpenAI-compatible API.

        Args:
            api_key: Google API key (defaults to GEMINI_API_KEY env var)
            model: Model name (defaults to gemini-2.0-flash-exp)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable or api_key parameter required")

        # Use OpenAI-compatible endpoint for Gemini
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
        self.model_name = model

    def generate_completion(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Generate completion using Gemini (synchronous).

        Args:
            prompt: User prompt
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum response tokens
            system_prompt: Optional system prompt

        Returns:
            Generated completion text

        Raises:
            Exception: If API call fails
        """
        # Use sync version by running async in sync context
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(
            self.generate_completion_async(prompt, temperature, max_tokens, system_prompt)
        )

    async def generate_completion_async(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Generate completion using Gemini (asynchronous).

        Args:
            prompt: User prompt
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum response tokens
            system_prompt: Optional system prompt

        Returns:
            Generated completion text

        Raises:
            Exception: If API call fails
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content

    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"<GeminiClient(model={self.model_name})>"
