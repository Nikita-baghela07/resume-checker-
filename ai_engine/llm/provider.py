"""
Abstract LLM provider interface for the resume-checker engine.

Adding support for a new LLM provider:
  1. Create ``ai_engine/llm/<name>_provider.py`` that implements ``LLMProvider``.
  2. Register it in ``get_provider()`` below.
  3. Set ``LLM_PROVIDER=<name>`` in your ``.env`` file.

Currently bundled providers
----------------------------
* ``groq``      — Groq cloud API (default; requires ``GROQ_API_KEY``)
* ``openai``    — OpenAI API (requires ``OPENAI_API_KEY``)
* ``anthropic`` — Anthropic Claude API (requires ``ANTHROPIC_API_KEY``)
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """
    Minimal interface that every LLM backend must satisfy.

    All providers must be compatible with the ``BertEmbedder`` that handles
    semantic scoring: the embedder runs locally and is completely independent
    of which cloud API is used for text generation.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable provider identifier (e.g. ``"groq"``)."""

    @abstractmethod
    def complete(
        self,
        *,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 2000,
        temperature: float = 0.4,
    ) -> str:
        """
        Send a chat-completion request and return the assistant's reply as a
        plain string.

        Parameters
        ----------
        system_prompt:  System-role message.
        user_message:   User-role message.
        max_tokens:     Maximum tokens in the completion.
        temperature:    Sampling temperature (0 = deterministic).

        Returns
        -------
        str  The raw text content of the assistant reply.

        Raises
        ------
        RuntimeError  If the API call fails for any reason.
        """


# ── Provider registry ─────────────────────────────────────────────────────────

def get_provider(provider_name: str = "groq") -> LLMProvider:
    """
    Factory function: return a ready-to-use ``LLMProvider`` instance.

    Parameters
    ----------
    provider_name:
        ``"groq"`` | ``"openai"`` | ``"anthropic"``

    Raises
    ------
    ValueError  For unknown provider names.
    ImportError For providers whose SDK is not installed.
    """
    name = provider_name.lower().strip()

    if name == "groq":
        from ai_engine.llm.groq_provider import GroqProvider
        return GroqProvider()

    if name == "openai":
        from ai_engine.llm.openai_provider import OpenAIProvider
        return OpenAIProvider()

    if name == "anthropic":
        from ai_engine.llm.anthropic_provider import AnthropicProvider
        return AnthropicProvider()

    raise ValueError(
        f"Unknown LLM provider '{provider_name}'. "
        "Supported values: 'groq', 'openai', 'anthropic'."
    )
