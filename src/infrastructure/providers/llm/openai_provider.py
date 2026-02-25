"""OpenAI provider -- the only module that talks to OpenAI via langchain-openai."""

from __future__ import annotations

import random
import time
from typing import Any, Callable, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

from langchain_openai import ChatOpenAI

from .errors import LLMProviderError
from src.settings import Settings

_TRANSIENT_PATTERNS = (
    "rate limit",
    "timeout",
    "connection",
    "429",
    "500",
    "502",
    "503",
    "529",
)

_BACKOFF_BASE = 0.5
_BACKOFF_FACTOR = 2
_BACKOFF_JITTER = 0.25
_BACKOFF_CAP = 8.0


def _is_transient(exc: Exception) -> bool:
    """Heuristic: match error message against known transient patterns.

    langchain-openai surfaces varied exception types from httpx/openai,
    so string matching is the most portable approach here.
    """
    msg = str(exc).lower()
    return any(p in msg for p in _TRANSIENT_PATTERNS)


class OpenAIProvider:
    """Thin wrapper around ``ChatOpenAI`` for structured JSON and text generation.

    Provides consistent retry/backoff and rich error context (node name,
    model, raw excerpt) on every failure path.
    """

    def __init__(
        self,
        settings: Settings | None = None,
        *,
        api_key: str | None = None,
        model_json: str = "gpt-4.1",
        model_text: str = "gpt-4.1",
        temperature_json: float = 0,
        temperature_text: float = 0.7,
    ) -> None:
        resolved_key = api_key or (settings.OPENAI_API_KEY if settings else None)
        if not resolved_key:
            raise LLMProviderError(
                node_name="__init__",
                model="n/a",
                message="No API key: pass api_key or provide Settings with OPENAI_API_KEY",
            )

        self._model_json = model_json
        self._model_text = model_text

        self._llm_json = ChatOpenAI(
            api_key=resolved_key,
            model=model_json,
            temperature=temperature_json,
        )
        self._llm_text = ChatOpenAI(
            api_key=resolved_key,
            model=model_text,
            temperature=temperature_text,
        )

    # -- public API ----------------------------------------------------------

    def generate_structured(
        self,
        *,
        node_name: str,
        prompt: str,
        schema: type[T],
        max_retries: int = 3,
    ) -> T:
        """Call the LLM and return a validated Pydantic model instance.

        Uses OpenAI native JSON schema mode via LangChain's
        ``with_structured_output``.
        """
        runnable = self._llm_json.with_structured_output(
            schema,
            method="json_schema",
            strict=True,
            include_raw=True,
        )

        result = self._call_with_retry(
            runnable.invoke,
            prompt,
            node_name=node_name,
            model=self._model_json,
            max_retries=max_retries,
        )

        parsing_error = result.get("parsing_error")
        parsed = result.get("parsed")

        if parsing_error is not None or parsed is None:
            raw_content = ""
            raw_msg = result.get("raw")
            if raw_msg is not None:
                raw_content = getattr(raw_msg, "content", str(raw_msg))

            raise LLMProviderError(
                node_name=node_name,
                model=self._model_json,
                message=f"Structured output parsing failed: {parsing_error}",
                raw_excerpt=raw_content[:300] if raw_content else None,
                original_exc=parsing_error if isinstance(parsing_error, Exception) else None,
            )

        return parsed

    def generate_text(
        self,
        *,
        node_name: str,
        prompt: str,
        max_retries: int = 3,
    ) -> str:
        """Call the LLM and return plain text content."""
        ai_message = self._call_with_retry(
            self._llm_text.invoke,
            prompt,
            node_name=node_name,
            model=self._model_text,
            max_retries=max_retries,
        )

        content = ai_message.content if hasattr(ai_message, "content") else str(ai_message)

        if not content or not content.strip():
            raise LLMProviderError(
                node_name=node_name,
                model=self._model_text,
                message="LLM returned empty text content",
            )

        return content

    # -- internal retry helper -----------------------------------------------

    def _call_with_retry(
        self,
        fn: Callable[..., Any],
        *args: object,
        node_name: str,
        model: str,
        max_retries: int,
    ) -> Any:
        last_exc: Exception | None = None

        for attempt in range(max_retries):
            try:
                return fn(*args)
            except Exception as exc:
                last_exc = exc
                is_last = attempt == max_retries - 1
                if is_last:
                    break

                transient = _is_transient(exc)
                if not transient and attempt >= 1:
                    break

                delay = min(
                    _BACKOFF_BASE * (_BACKOFF_FACTOR ** attempt)
                    + random.uniform(0, _BACKOFF_JITTER),
                    _BACKOFF_CAP,
                )
                time.sleep(delay)

        raise LLMProviderError(
            node_name=node_name,
            model=model,
            message=f"LLM call failed after {max_retries} attempt(s): {last_exc}",
            original_exc=last_exc,
        )
