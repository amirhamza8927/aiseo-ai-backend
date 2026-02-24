"""Tests for json_mode: safe JSON parsing with fallback extraction."""

import pytest

from src.infrastructure.providers.llm.json_mode import ensure_json_parseable


def test_valid_json():
    assert ensure_json_parseable('{"a": 1}') == {"a": 1}


def test_json_embedded_in_text():
    text = 'Here is output: {"key": "val"} done'
    assert ensure_json_parseable(text) == {"key": "val"}


def test_nested_json():
    text = '{"a": {"b": 1}, "c": [2, 3]}'
    result = ensure_json_parseable(text)
    assert result == {"a": {"b": 1}, "c": [2, 3]}


def test_nested_json_with_surrounding_text():
    text = 'prefix {"outer": {"inner": true}} suffix'
    assert ensure_json_parseable(text) == {"outer": {"inner": True}}


def test_invalid_json_raises():
    with pytest.raises(ValueError, match="Cannot parse JSON"):
        ensure_json_parseable("not json at all")


def test_invalid_json_includes_excerpt():
    raw = "x" * 500
    with pytest.raises(ValueError) as exc_info:
        ensure_json_parseable(raw)
    assert "raw excerpt" in str(exc_info.value)


def test_json_array_not_object():
    with pytest.raises(ValueError, match="Expected a JSON object"):
        ensure_json_parseable("[1, 2, 3]")


def test_empty_string_raises():
    with pytest.raises(ValueError):
        ensure_json_parseable("")


def test_braces_inside_string_values():
    text = '{"msg": "use { and } carefully"}'
    assert ensure_json_parseable(text) == {"msg": "use { and } carefully"}
