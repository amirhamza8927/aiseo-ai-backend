"""Tests for GraphState and JobInput models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.application.orchestration.state import GraphState, JobInput

_OPTIONAL_FIELDS = (
    "serp_results",
    "themes",
    "plan",
    "outline",
    "keyword_plan",
    "article_markdown",
    "seo_package",
    "validation_report",
    "repair_spec",
    "current_node",
    "last_error",
)


def _make_state(**overrides: object) -> GraphState:
    defaults = {
        "job_id": "job-1",
        "topic": "project management tools",
        "target_word_count": 1500,
        "language": "en",
        "max_revisions": 2,
    }
    defaults.update(overrides)
    return GraphState.new(**defaults)


class TestGraphStateNew:
    def test_creates_correct_defaults(self) -> None:
        state = _make_state()
        assert state.job_id == "job-1"
        assert state.input.topic == "project management tools"
        assert state.input.target_word_count == 1500
        assert state.input.language == "en"
        assert state.revisions_left == 2
        for field in _OPTIONAL_FIELDS:
            assert getattr(state, field) is None

    def test_max_revisions_propagated(self) -> None:
        state = _make_state(max_revisions=5)
        assert state.revisions_left == 5


class TestSerialization:
    def test_model_dump_json_roundtrip(self) -> None:
        state = _make_state()
        dumped = state.model_dump(mode="json")
        restored = GraphState.model_validate(dumped)
        assert restored == state

    def test_optional_fields_serialize_as_none(self) -> None:
        dumped = _make_state().model_dump(mode="json")
        for field in _OPTIONAL_FIELDS:
            assert dumped[field] is None, f"{field} should be None"


class TestJobInputValidation:
    def test_empty_topic_rejected(self) -> None:
        with pytest.raises(ValidationError):
            JobInput(topic="", target_word_count=1500, language="en")

    def test_zero_word_count_rejected(self) -> None:
        with pytest.raises(ValidationError):
            JobInput(topic="seo", target_word_count=0, language="en")

    def test_empty_language_rejected(self) -> None:
        with pytest.raises(ValidationError):
            JobInput(topic="seo", target_word_count=1500, language="")
