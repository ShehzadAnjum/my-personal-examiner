"""Anthropic Claude Sonnet 4.5 Client

Primary LLM for all 6 AI teaching agents.

Constitutional Requirements:
- Principle VII: >80% test coverage (client designed for testability with dependency injection)
"""

import os
from typing import Optional

from anthropic import Anthropic, AsyncAnthropic
from anthropic.types import Message


class AnthropicClient:
    """
    Client for Anthropic Claude Sonnet 4.5 API.

    Primary LLM for Phase III AI Teaching Roles:
    - Teacher Agent: PhD-level concept explanations (temp=0.3)
    - Coach Agent: Socratic questioning (temp=0.5)
    - Marker Agent: Strict marking (temp=0.1)
    - Reviewer Agent: A* model answers (temp=0.4)
    - Planner Agent: Study schedule optimization (temp=0.3)

    Temperature settings per agent optimize for:
    - Low temp (0.1-0.3): Deterministic, precise (Marker, Teacher)
    - Medium temp (0.4-0.5): Creative, empathetic (Coach, Reviewer)
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-20250514"):
        """
        Initialize Anthropic client.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Model name (defaults to Claude Sonnet 4.5)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable or api_key parameter required")

        self.model = model
        self.client = Anthropic(api_key=self.api_key)
        self.async_client = AsyncAnthropic(api_key=self.api_key)

    def generate_completion(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Generate completion using Claude Sonnet 4.5 (synchronous).

        Args:
            prompt: User prompt
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum response tokens
            system_prompt: Optional system prompt

        Returns:
            Generated completion text

        Raises:
            anthropic.APIError: If API call fails
        """
        messages = [{"role": "user", "content": prompt}]

        response: Message = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt or "",
            messages=messages,
        )

        return response.content[0].text

    async def generate_completion_async(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Generate completion using Claude Sonnet 4.5 (asynchronous).

        Args:
            prompt: User prompt
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum response tokens
            system_prompt: Optional system prompt

        Returns:
            Generated completion text

        Raises:
            anthropic.APIError: If API call fails
        """
        messages = [{"role": "user", "content": prompt}]

        response: Message = await self.async_client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt or "",
            messages=messages,
        )

        return response.content[0].text

    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"<AnthropicClient(model={self.model})>"
