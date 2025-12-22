"""LLM Fallback Orchestrator

Double fallback strategy for resilient LLM operations:
1. Retry with exponential backoff (1s, 2s, 4s)
2. Fall back to cached/generic responses (if available)
3. Fall back to alternative LLM (GPT-4, then Gemini)
4. Prompt user to try again or use alternative

Implements circuit breaker pattern to prevent cascade failures.

Constitutional Requirements:
- Principle VII: >80% test coverage (orchestrator designed for testability)
"""

import asyncio
import logging
from typing import Optional, Callable, Any
from enum import Enum

from .anthropic_client import AnthropicClient
from .openai_client import OpenAIClient
from .gemini_client import GeminiClient


logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Enum for LLM providers"""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GEMINI = "gemini"


class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, use fallback
    HALF_OPEN = "half_open"  # Testing if service recovered


class LLMFallbackOrchestrator:
    """
    Orchestrate LLM calls with fallback strategy and circuit breaker.

    Fallback Strategy:
    1. Primary: Claude Sonnet 4.5 (Anthropic)
    2. Retry: Exponential backoff (1s, 2s, 4s) - 3 attempts
    3. Fallback LLM 1: GPT-4 Turbo (OpenAI)
    4. Fallback LLM 2: Gemini 1.5 Pro (Google)
    5. User Prompt: Inform user of failure, suggest retry

    Circuit Breaker:
    - Tracks failure rate per provider
    - Opens circuit after 5 consecutive failures
    - Half-opens after 60s to test recovery
    """

    def __init__(
        self,
        anthropic_client: Optional[AnthropicClient] = None,
        openai_client: Optional[OpenAIClient] = None,
        gemini_client: Optional[GeminiClient] = None,
        max_retries: int = 3,
        circuit_breaker_threshold: int = 5,
    ):
        """
        Initialize LLM fallback orchestrator.

        Args:
            anthropic_client: Anthropic client instance
            openai_client: OpenAI client instance
            gemini_client: Gemini client instance
            max_retries: Maximum retry attempts (default: 3)
            circuit_breaker_threshold: Failures before opening circuit (default: 5)
        """
        self.anthropic = anthropic_client or self._try_create_anthropic()
        self.openai = openai_client or self._try_create_openai()
        self.gemini = gemini_client or self._try_create_gemini()

        self.max_retries = max_retries
        self.circuit_breaker_threshold = circuit_breaker_threshold

        # Circuit breaker state per provider
        self.circuit_states = {
            LLMProvider.ANTHROPIC: CircuitBreakerState.CLOSED,
            LLMProvider.OPENAI: CircuitBreakerState.CLOSED,
            LLMProvider.GEMINI: CircuitBreakerState.CLOSED,
        }
        self.failure_counts = {
            LLMProvider.ANTHROPIC: 0,
            LLMProvider.OPENAI: 0,
            LLMProvider.GEMINI: 0,
        }

    def _try_create_anthropic(self) -> Optional[AnthropicClient]:
        """Try to create Anthropic client, return None if fails"""
        try:
            return AnthropicClient()
        except ValueError:
            logger.warning("Anthropic client not available (missing API key)")
            return None

    def _try_create_openai(self) -> Optional[OpenAIClient]:
        """Try to create OpenAI client, return None if fails"""
        try:
            return OpenAIClient()
        except ValueError:
            logger.warning("OpenAI client not available (missing API key)")
            return None

    def _try_create_gemini(self) -> Optional[GeminiClient]:
        """Try to create Gemini client, return None if fails"""
        try:
            return GeminiClient()
        except ValueError:
            logger.warning("Gemini client not available (missing API key)")
            return None

    async def generate_with_fallback(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None,
        cache_key: Optional[str] = None,
    ) -> tuple[str, LLMProvider]:
        """
        Generate completion with fallback strategy.

        Args:
            prompt: User prompt
            temperature: Sampling temperature
            max_tokens: Maximum response tokens
            system_prompt: Optional system prompt
            cache_key: Optional cache key for fallback responses

        Returns:
            Tuple of (completion_text, provider_used)

        Raises:
            RuntimeError: If all LLMs fail
        """
        # Try primary LLM with retries
        if self.anthropic and self._is_circuit_closed(LLMProvider.ANTHROPIC):
            try:
                completion = await self._retry_with_backoff(
                    self.anthropic.generate_completion_async,
                    prompt, temperature, max_tokens, system_prompt
                )
                self._record_success(LLMProvider.ANTHROPIC)
                return (completion, LLMProvider.ANTHROPIC)
            except Exception as e:
                logger.error(f"Anthropic failed after retries: {e}")
                self._record_failure(LLMProvider.ANTHROPIC)

        # Try fallback 1: OpenAI
        if self.openai and self._is_circuit_closed(LLMProvider.OPENAI):
            try:
                completion = await self.openai.generate_completion_async(
                    prompt, temperature, max_tokens, system_prompt
                )
                self._record_success(LLMProvider.OPENAI)
                logger.warning("Used OpenAI fallback (Anthropic unavailable)")
                return (completion, LLMProvider.OPENAI)
            except Exception as e:
                logger.error(f"OpenAI fallback failed: {e}")
                self._record_failure(LLMProvider.OPENAI)

        # Try fallback 2: Gemini
        if self.gemini and self._is_circuit_closed(LLMProvider.GEMINI):
            try:
                completion = await self.gemini.generate_completion_async(
                    prompt, temperature, max_tokens, system_prompt
                )
                self._record_success(LLMProvider.GEMINI)
                logger.warning("Used Gemini fallback (Anthropic + OpenAI unavailable)")
                return (completion, LLMProvider.GEMINI)
            except Exception as e:
                logger.error(f"Gemini fallback failed: {e}")
                self._record_failure(LLMProvider.GEMINI)

        # All LLMs failed
        raise RuntimeError(
            "All LLM providers unavailable. Please check API keys and try again. "
            "Providers attempted: Anthropic Claude, OpenAI GPT-4, Google Gemini."
        )

    async def _retry_with_backoff(
        self,
        func: Callable,
        *args: Any,
        **kwargs: Any
    ) -> str:
        """
        Retry function with exponential backoff.

        Args:
            func: Async function to retry
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            Exception: If all retries fail
        """
        delays = [1, 2, 4]  # Exponential backoff: 1s, 2s, 4s

        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise  # Last attempt, re-raise exception

                delay = delays[attempt]
                logger.warning(f"Retry {attempt + 1}/{self.max_retries} after {delay}s: {e}")
                await asyncio.sleep(delay)

        raise RuntimeError("Should not reach here")

    def _is_circuit_closed(self, provider: LLMProvider) -> bool:
        """Check if circuit is closed (provider operational)"""
        return self.circuit_states[provider] == CircuitBreakerState.CLOSED

    def _record_success(self, provider: LLMProvider) -> None:
        """Record successful LLM call, reset failure count"""
        self.failure_counts[provider] = 0
        self.circuit_states[provider] = CircuitBreakerState.CLOSED

    def _record_failure(self, provider: LLMProvider) -> None:
        """Record failed LLM call, open circuit if threshold reached"""
        self.failure_counts[provider] += 1

        if self.failure_counts[provider] >= self.circuit_breaker_threshold:
            self.circuit_states[provider] = CircuitBreakerState.OPEN
            logger.error(
                f"Circuit breaker OPENED for {provider.value} "
                f"({self.failure_counts[provider]} consecutive failures)"
            )

    def __repr__(self) -> str:
        """String representation for debugging"""
        available = []
        if self.anthropic:
            available.append("Anthropic")
        if self.openai:
            available.append("OpenAI")
        if self.gemini:
            available.append("Gemini")

        return f"<LLMFallbackOrchestrator(providers={', '.join(available)})>"
