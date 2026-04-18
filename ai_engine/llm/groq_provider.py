"""
Groq provider implementation for the abstract ``LLMProvider`` interface.

Requires:
    pip install groq
    GROQ_API_KEY set in the environment / .env file.
"""

from __future__ import annotations

import logging
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_engine.llm.provider import LLMProvider

logger = logging.getLogger(__name__)


class GroqProvider(LLMProvider):
    """
    LLM provider backed by the Groq cloud API.

    Compatible with ``BertEmbedder``: BERT runs locally for semantic scoring
    while Groq handles all text-generation tasks (rewriting, structuring).
    """

    def __init__(self) -> None:
        try:
            from groq import Groq
        except ImportError as exc:
            raise ImportError(
                "The 'groq' package is required for the Groq provider. "
                "Install it with: pip install groq"
            ) from exc

        from app.core.config import settings

        api_key = settings.GROQ_API_KEY
        if not api_key or "gsk_" not in api_key:
            raise RuntimeError(
                "GROQ_API_KEY is missing or invalid. "
                "Set it in your .env file (it must start with 'gsk_')."
            )

        self._client = Groq(api_key=api_key)
        self._model  = settings.MODEL_NAME
        logger.info(f"[GroqProvider] Initialised with model '{self._model}'")

    @property
    def name(self) -> str:
        return "groq"

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
