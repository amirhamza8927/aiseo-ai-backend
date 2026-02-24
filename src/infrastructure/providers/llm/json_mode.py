"""Safe JSON parsing with fallback extraction for LLM responses."""

from __future__ import annotations

import json


def _extract_first_json_object(text: str) -> str | None:
    """Return the first brace-balanced ``{...}`` substring, or *None*."""
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(text)):
        ch = text[i]
        if escape:
            escape = False
            continue
        if ch == "\\":
            escape = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return None


def ensure_json_parseable(text: str) -> dict:
    """Parse *text* as a JSON object, with a fallback extraction step.

    1. Try ``json.loads(text)`` directly.
    2. If that fails, locate the first brace-balanced ``{...}`` block and
       parse it.
    3. If both fail, raise ``ValueError`` with the original error and a
       short excerpt of the raw text.

    Always returns a ``dict`` -- JSON arrays or scalars are rejected.
    """
    try:
        result = json.loads(text)
        if isinstance(result, dict):
            return result
        raise ValueError(f"Expected a JSON object (dict), got {type(result).__name__}")
    except (json.JSONDecodeError, ValueError) as first_err:
        snippet = _extract_first_json_object(text)
        if snippet is not None:
            try:
                result = json.loads(snippet)
                if isinstance(result, dict):
                    return result
            except json.JSONDecodeError:
                pass

        excerpt = text[:300]
        raise ValueError(
            f"Cannot parse JSON object: {first_err}\n  raw excerpt: {excerpt}"
        ) from first_err
