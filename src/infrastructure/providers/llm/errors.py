"""Infrastructure-level exceptions for LLM provider operations."""

from __future__ import annotations


class LLMProviderError(Exception):
    """Rich error raised by OpenAIProvider on LLM failures.

    All contextual fields are stored as public attributes for
    programmatic access by callers (e.g. graph nodes logging errors).
    """

    def __init__(
        self,
        *,
        node_name: str,
        model: str,
        message: str,
        raw_excerpt: str | None = None,
        original_exc: Exception | None = None,
    ) -> None:
        self.node_name = node_name
        self.model = model
        self.message = message
        self.raw_excerpt = raw_excerpt[:300] if raw_excerpt else None
        self.original_exc = original_exc
        super().__init__(str(self))

    def __str__(self) -> str:
        parts = [f"[{self.node_name}] {self.model}: {self.message}"]
        if self.raw_excerpt:
            parts.append(f"  raw excerpt: {self.raw_excerpt}")
        if self.original_exc:
            parts.append(f"  caused by: {type(self.original_exc).__name__}: {self.original_exc}")
        return "\n".join(parts)
