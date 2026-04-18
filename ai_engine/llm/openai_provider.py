"""
OpenAI provider implementation for the abstract ``LLMProvider`` interface.

Requires:
    pip install openai
    OPENAI_API_KEY set in the environment / .env file.
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_engine.llm.provider import LLMProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """
    LLM provider backed by the OpenAI API (GPT-4o, GPT-4-turbo, …).

    Compatible with ``BertEmbedder``: BERT runs locally for semantic scoring
    while OpenAI handles all text-generation tasks.
    """

    # Default model; can be overridden via the OPENAI_MODEL env variable.
    _DEFAULT_MODEL = "gpt-4o-mini"

    def __init__(self) -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError(
                "The 'openai' package is required for the OpenAI provider. "
                "Install it with: pip install openai"
            ) from exc

        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is missing. Set it in your .env file."
            )

        self._client = OpenAI(api_key=api_key)
        self._model  = os.getenv("OPENAI_MODEL", self._DEFAULT_MODEL)
        logger.info(f"[OpenAIProvider] Initialised with model '{self._model}'")

    @property
    def name(self) -> str:
        return "openai"

    def complete(
        self,
        *,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 2000,
        temperature: float = 0.4,
    ) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_message},
            ],
        )
        return response.choices[0].message.content
