"""
Fast local Ollama LLM provider.
"""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from typing import Any

import httpx

from app.core.config import Settings

logger = logging.getLogger("career_xray.llm")


class LLMError(Exception):
    """Raised when the LLM provider fails."""


class LLMProvider(ABC):
    @abstractmethod
    async def generate_json(
        self, *, system_prompt: str, user_prompt: str
    ) -> dict[str, Any]:
        raise NotImplementedError


def _clean_json(text: str) -> str:
    text = text.strip()

    if "```json" in text:
        text = text.replace("```json", "").replace("```", "").strip()
    elif text.startswith("```"):
        text = text.replace("```", "").strip()

    return text


class OllamaProvider(LLMProvider):

    def __init__(self, settings: Settings):
        self._settings = settings
        self._base_url = "http://localhost:11434"

    async def generate_json(
        self, *, system_prompt: str, user_prompt: str
    ) -> dict[str, Any]:

        payload = {
            "model": self._settings.llm_model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0,
                "num_predict": 8000,
            },
            "think": False,
        }

        try:
            async with httpx.AsyncClient(
                timeout=self._settings.llm_timeout_seconds
            ) as client:

                response = await client.post(
                    f"{self._base_url}/api/chat",
                    json=payload,
                )

                # Print Ollama's actual error body if it returns 4xx/5xx.
                if response.status_code >= 400:
                    logger.error(
                        "Ollama response body: %s",
                        response.text,
                    )

                response.raise_for_status()

                data = response.json()

            message = data.get("message") or {}
            raw_text = message.get("content") or ""

            if not raw_text:
                logger.warning(
                    "Ollama returned no content. Response keys: %s",
                    list(data.keys()),
                )
                raise LLMError("Ollama returned empty content.")

            cleaned = _clean_json(raw_text)

            try:
                result = json.loads(cleaned)
            except json.JSONDecodeError as exc:
                logger.warning(
                    "Invalid JSON from Ollama: %r",
                    raw_text[:2000],
                )
                raise LLMError(
                    "Ollama returned invalid JSON."
                ) from exc

            if not isinstance(result, dict):
                raise LLMError(
                    "Ollama JSON response is not an object."
                )

            return result

        except httpx.HTTPError as exc:
            logger.exception(
                "Ollama HTTP error: %r",
                exc,
            )
            raise LLMError(
                f"Ollama HTTP request failed: {exc}"
            ) from exc


def get_llm_provider(settings: Settings) -> LLMProvider:
    if settings.llm_provider == "ollama":
        return OllamaProvider(settings)

    raise ValueError(
        f"Unsupported LLM provider: {settings.llm_provider}"
    )