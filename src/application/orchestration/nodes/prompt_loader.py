"""Prompt loading and rendering – cached file reads, simple {{key}} substitution."""

from __future__ import annotations

import json
from pathlib import Path


def render_prompt(template: str, **kwargs: object) -> str:
    """Replace {{key}} placeholders in *template* with values from *kwargs*.

    Strings are injected as-is; other values are JSON-serialized.
    """
    result = template
    for key, value in kwargs.items():
        placeholder = "{{" + key + "}}"
        if isinstance(value, str):
            text = value
        else:
            text = json.dumps(value, ensure_ascii=False, indent=2)
        result = result.replace(placeholder, text)
    return result


class PromptLoader:
    """Load prompt templates from disk with in-memory caching."""

    def __init__(self, base_dir: Path | None = None) -> None:
        self._base_dir = base_dir or (
            Path(__file__).resolve().parent.parent / "prompts"
        )
        self._cache: dict[str, str] = {}

    def get(self, name: str) -> str:
        """Load and return the prompt template for *name* (e.g. 'themes' -> themes.v1.md)."""
        if name not in self._cache:
            path = self._base_dir / f"{name}.v1.md"
            self._cache[name] = path.read_text(encoding="utf-8")
        return self._cache[name]
