"""Tests for build_outline node – section ID matching, no network."""

from __future__ import annotations

import pytest

from src.application.orchestration.nodes.build_outline import build_outline
from src.application.orchestration.nodes.deps import NodeDeps
from src.application.orchestration.nodes.prompt_loader import PromptLoader
from src.application.orchestration.state import GraphState
from src.domain.models.outline import Outline, OutlineSection
from src.domain.models.plan import Plan, PlanSection
from src.infrastructure.providers.serp.mock_serp import MockSerpProvider


def _make_plan() -> Plan:
    return Plan(
        h1="Test Article",
        intro_target_word_count=100,
        sections=[
            PlanSection(
                section_id="s1",
                heading="Intro",
                purpose="",
                key_points=["x"],
                target_word_count=50,
            ),
            PlanSection(
                section_id="s2",
                heading="Body",
                purpose="",
                key_points=["y"],
                target_word_count=50,
            ),
            PlanSection(
                section_id="s3",
                heading="End",
                purpose="",
                key_points=["z"],
                target_word_count=50,
            ),
        ],
    )


def _make_state_with_plan() -> GraphState:
    return GraphState.new(
        job_id="j1",
        topic="project management tools",
        target_word_count=1500,
        language="en",
        max_revisions=2,
    ).model_copy(update={"plan": _make_plan()})


class FakeLLM:
    """Fake LLM that returns a configurable Outline."""

    def __init__(self, outline: Outline) -> None:
        self._outline = outline

    def generate_structured(self, *, node_name: str, prompt: str, schema: type) -> Outline:
        assert node_name == "build_outline"
        assert schema is Outline
        assert "project management" in prompt
        return self._outline


def test_build_outline_returns_patch_with_outline() -> None:
    outline = Outline(
        h1="Test Article",
        sections=[
            OutlineSection(section_id="s1", h2="Introduction"),
            OutlineSection(section_id="s2", h2="Main Body"),
            OutlineSection(section_id="s3", h2="Conclusion"),
        ],
    )
    state = _make_state_with_plan()
    deps = NodeDeps(
        serp=MockSerpProvider(),
        llm=FakeLLM(outline),
        prompts=PromptLoader(),
    )

    patch = build_outline(state, deps)

    assert patch["current_node"] == "build_outline"
    assert isinstance(patch["outline"], Outline)
    assert [s.section_id for s in patch["outline"].sections] == ["s1", "s2", "s3"]


def test_build_outline_wrong_order_raises() -> None:
    outline = Outline(
        h1="Test",
        sections=[
            OutlineSection(section_id="s1", h2="A"),
            OutlineSection(section_id="s3", h2="C"),
            OutlineSection(section_id="s2", h2="B"),
        ],
    )
    state = _make_state_with_plan()
    deps = NodeDeps(
        serp=MockSerpProvider(),
        llm=FakeLLM(outline),
        prompts=PromptLoader(),
    )

    with pytest.raises(ValueError, match="plan_ids=.*outline_ids="):
        build_outline(state, deps)


def test_build_outline_missing_id_raises() -> None:
    outline = Outline(
        h1="Test",
        sections=[
            OutlineSection(section_id="s1", h2="A"),
            OutlineSection(section_id="s2", h2="B"),
        ],
    )
    state = _make_state_with_plan()
    deps = NodeDeps(
        serp=MockSerpProvider(),
        llm=FakeLLM(outline),
        prompts=PromptLoader(),
    )

    with pytest.raises(ValueError, match="plan_ids=.*outline_ids="):
        build_outline(state, deps)


def test_build_outline_extra_id_raises() -> None:
    outline = Outline(
        h1="Test",
        sections=[
            OutlineSection(section_id="s1", h2="A"),
            OutlineSection(section_id="s2", h2="B"),
            OutlineSection(section_id="s3", h2="C"),
            OutlineSection(section_id="s4", h2="D"),
        ],
    )
    state = _make_state_with_plan()
    deps = NodeDeps(
        serp=MockSerpProvider(),
        llm=FakeLLM(outline),
        prompts=PromptLoader(),
    )

    with pytest.raises(ValueError, match="plan_ids=.*outline_ids="):
        build_outline(state, deps)


def test_build_outline_missing_llm_raises() -> None:
    outline = Outline(
        h1="Test",
        sections=[
            OutlineSection(section_id="s1", h2="A"),
            OutlineSection(section_id="s2", h2="B"),
            OutlineSection(section_id="s3", h2="C"),
        ],
    )
    state = _make_state_with_plan()
    deps = NodeDeps(
        serp=MockSerpProvider(),
        llm=None,
        prompts=PromptLoader(),
    )

    with pytest.raises(ValueError, match="build_outline: deps.llm is required"):
        build_outline(state, deps)


def test_build_outline_missing_plan_raises() -> None:
    outline = Outline(
        h1="Test",
        sections=[
            OutlineSection(section_id="s1", h2="A"),
            OutlineSection(section_id="s2", h2="B"),
            OutlineSection(section_id="s3", h2="C"),
        ],
    )
    state = _make_state_with_plan().model_copy(update={"plan": None})
    deps = NodeDeps(
        serp=MockSerpProvider(),
        llm=FakeLLM(outline),
        prompts=PromptLoader(),
    )

    with pytest.raises(ValueError, match="build_outline: state.plan is required"):
        build_outline(state, deps)


def test_build_outline_missing_prompts_raises() -> None:
    outline = Outline(
        h1="Test",
        sections=[
            OutlineSection(section_id="s1", h2="A"),
            OutlineSection(section_id="s2", h2="B"),
            OutlineSection(section_id="s3", h2="C"),
        ],
    )
    state = _make_state_with_plan()
    deps = NodeDeps(
        serp=MockSerpProvider(),
        llm=FakeLLM(outline),
        prompts=None,
    )

    with pytest.raises(ValueError, match="build_outline: deps.prompts is required"):
        build_outline(state, deps)
