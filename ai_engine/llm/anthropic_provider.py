"""
Anthropic Claude provider implementation for the abstract ``LLMProvider`` interface.

Requires:
    pip install anthropic
    ANTHROPIC_API_KEY set in the environment / .env file.
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_engine.llm.provider import LLMProvider

logger = logging.getLogger(__name__)


class AnthropicProvider(LLMProvider):
    """
    LLM provider backed by the Anthropic Claude API.

    Compatible with ``BertEmbedder``: BERT runs locally for semantic scoring
    while Anthropic handles all text-generation tasks.
    """

    _DEFAULT_MODEL = "claude-3-5-haiku-20241022"

    def __init__(self) -> None:
        try:
            import anthropic as _anthropic
        except ImportError as exc:
            raise ImportError(
                "The 'anthropic' package is required for the Anthropic provider. "
                "Install it with: pip install anthropic"
            ) from exc

        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY is missing. Set it in your .env file."
            )

        self._client = _anthropic.Anthropic(api_key=api_key)
        self._model  = os.getenv("ANTHROPIC_MODEL", self._DEFAULT_MODEL)
        logger.info(f"[AnthropicProvider] Initialised with model '{self._model}'")

    @property
    def name(self) -> str:
        return "anthropic"

    def complete(
        self,
        *,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 2000,
        temperature: float = 0.4,
    ) -> str:
        response = self._client.messages.create(
            model=self._model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        # Anthropic returns a list of content blocks; extract the first text block.
        return response.content[0].text
