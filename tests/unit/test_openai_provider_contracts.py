"""Contract tests for OpenAIProvider -- all mocked, zero network calls."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel

from src.infrastructure.providers.llm.errors import LLMProviderError
from src.infrastructure.providers.llm.openai_provider import OpenAIProvider


class _SampleSchema(BaseModel):
    title: str
    score: int


def _make_provider(**kwargs: object) -> OpenAIProvider:
    """Build a provider with a dummy key, bypassing real ChatOpenAI init."""
    with patch(
        "src.infrastructure.providers.llm.openai_provider.ChatOpenAI",
        return_value=MagicMock(),
    ):
        return OpenAIProvider(api_key="test-key", **kwargs)


# -- generate_structured ----------------------------------------------------


def test_generate_structured_returns_pydantic():
    provider = _make_provider()
    expected = _SampleSchema(title="Hello", score=42)

    mock_runnable = MagicMock()
    mock_runnable.invoke.return_value = {
        "raw": MagicMock(content='{"title":"Hello","score":42}'),
        "parsed": expected,
        "parsing_error": None,
    }
    provider._llm_json.with_structured_output = MagicMock(return_value=mock_runnable)

    result = provider.generate_structured(
        node_name="planner",
        prompt="make a plan",
        schema=_SampleSchema,
    )

    assert isinstance(result, _SampleSchema)
    assert result.title == "Hello"
    assert result.score == 42


def test_generate_structured_raises_on_parse_error():
    provider = _make_provider()

    mock_runnable = MagicMock()
    mock_runnable.invoke.return_value = {
        "raw": MagicMock(content="bad output"),
        "parsed": None,
        "parsing_error": ValueError("could not parse"),
    }
    provider._llm_json.with_structured_output = MagicMock(return_value=mock_runnable)

    with pytest.raises(LLMProviderError) as exc_info:
        provider.generate_structured(
            node_name="planner",
            prompt="make a plan",
            schema=_SampleSchema,
        )

    err = exc_info.value
    assert err.node_name == "planner"
    assert "gpt-4.1" in err.model
    assert "parsing failed" in err.message.lower()


def test_generate_structured_raises_when_parsed_is_none():
    provider = _make_provider()

    mock_runnable = MagicMock()
    mock_runnable.invoke.return_value = {
        "raw": MagicMock(content="{}"),
        "parsed": None,
        "parsing_error": None,
    }
    provider._llm_json.with_structured_output = MagicMock(return_value=mock_runnable)

    with pytest.raises(LLMProviderError):
        provider.generate_structured(
            node_name="planner",
            prompt="make a plan",
            schema=_SampleSchema,
        )


# -- generate_text -----------------------------------------------------------


def test_generate_text_returns_content():
    provider = _make_provider()
    provider._llm_text.invoke = MagicMock(
        return_value=MagicMock(content="Hello world"),
    )

    result = provider.generate_text(node_name="writer", prompt="write something")
    assert result == "Hello world"


def test_generate_text_raises_on_empty():
    provider = _make_provider()
    provider._llm_text.invoke = MagicMock(
        return_value=MagicMock(content=""),
    )

    with pytest.raises(LLMProviderError) as exc_info:
        provider.generate_text(node_name="writer", prompt="write something")

    assert exc_info.value.node_name == "writer"
    assert "empty" in exc_info.value.message.lower()


# -- retry behaviour ---------------------------------------------------------


def test_retry_on_transient_error():
    provider = _make_provider()

    call_count = 0

    def _flaky(*args: object, **kwargs: object) -> MagicMock:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise ConnectionError("Connection timeout")
        return MagicMock(content="recovered")

    provider._llm_text.invoke = _flaky

    with patch("src.infrastructure.providers.llm.openai_provider.time.sleep"):
        result = provider.generate_text(node_name="writer", prompt="try again")

    assert result == "recovered"
    assert call_count == 2


def test_non_transient_error_limited_retries():
    provider = _make_provider()

    call_count = 0

    def _always_fail(*args: object, **kwargs: object) -> None:
        nonlocal call_count
        call_count += 1
        raise RuntimeError("unexpected internal error")

    provider._llm_text.invoke = _always_fail

    with patch("src.infrastructure.providers.llm.openai_provider.time.sleep"):
        with pytest.raises(LLMProviderError):
            provider.generate_text(node_name="writer", prompt="fail", max_retries=3)

    assert call_count == 2


# -- constructor -------------------------------------------------------------


def test_missing_api_key_raises():
    with patch(
        "src.infrastructure.providers.llm.openai_provider.ChatOpenAI",
        return_value=MagicMock(),
    ):
        with pytest.raises(LLMProviderError, match="No API key"):
            OpenAIProvider()
