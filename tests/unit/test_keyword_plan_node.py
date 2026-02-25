"""Tests for keyword_plan node – no network, fake LLM."""

from __future__ import annotations

import pytest

from src.application.orchestration.nodes.keyword_plan import keyword_plan
from src.application.orchestration.nodes.deps import NodeDeps
from src.application.orchestration.nodes.prompt_loader import PromptLoader
from src.application.orchestration.state import GraphState
from src.domain.models.keyword_plan import KeywordPlan, UsageTargetItem
from src.domain.models.themes import Themes
from src.infrastructure.providers.serp.mock_serp import MockSerpProvider


class FakeLLM:
    """Fake LLM that returns a configurable KeywordPlan."""

    def __init__(self, primary: str, secondary: list[str] | None = None) -> None:
        self._primary = primary
        self._secondary = secondary or ["Task Tracking", "Team Collaboration", "Project Planning"]

    def generate_structured(self, *, node_name: str, prompt: str, schema: type) -> KeywordPlan:
        assert node_name == "keyword_plan"
        assert schema is KeywordPlan
        assert "project management" in prompt
        return KeywordPlan(
            primary=self._primary,
            secondary=self._secondary,
            usage_targets=[
                UsageTargetItem(keyword=self._primary, count=2),
                UsageTargetItem(keyword="Task Tracking", count=1),
            ],
        )


def _make_state_with_serp_and_themes() -> GraphState:
    serp = MockSerpProvider()
    results = serp.fetch_top_results(topic="project management tools", language="en")
    themes = Themes(
        search_intent="find tools",
        topic_clusters=["tools", "comparison"],
        common_sections=["Overview", "Pricing"],
        ranking_patterns=["listicle"],
        differentiation_angles=["depth"],
    )
    return GraphState.new(
        job_id="j1",
        topic="project management tools",
        target_word_count=1500,
        language="en",
        max_revisions=2,
    ).model_copy(update={"serp_results": results, "themes": themes})


def test_keyword_plan_returns_patch() -> None:
    state = _make_state_with_serp_and_themes()
    deps = NodeDeps(
        serp=MockSerpProvider(),
        llm=FakeLLM(primary="project management tools"),
        prompts=PromptLoader(),
    )

    patch = keyword_plan(state, deps)

    assert patch["current_node"] == "keyword_plan"
    assert isinstance(patch["keyword_plan"], KeywordPlan)
    assert patch["keyword_plan"].primary == "project management tools"
    assert len(patch["keyword_plan"].secondary) > 0


def test_keyword_plan_wrong_primary_raises() -> None:
    state = _make_state_with_serp_and_themes()
    deps = NodeDeps(
        serp=MockSerpProvider(),
        llm=FakeLLM(primary="wrong topic"),
        prompts=PromptLoader(),
    )

    with pytest.raises(ValueError, match="keyword_plan: LLM returned wrong primary"):
        keyword_plan(state, deps)


def test_keyword_plan_primary_in_secondary_raises() -> None:
    state = _make_state_with_serp_and_themes()
    deps = NodeDeps(
        serp=MockSerpProvider(),
        llm=FakeLLM(
            primary="project management tools",
            secondary=["Task Tracking", "project management tools", "Team Collaboration"],
        ),
        prompts=PromptLoader(),
    )

    with pytest.raises(ValueError, match="keyword_plan: primary must not appear in secondary"):
        keyword_plan(state, deps)


def test_keyword_plan_missing_themes_raises() -> None:
    state = _make_state_with_serp_and_themes().model_copy(update={"themes": None})
    deps = NodeDeps(
        serp=MockSerpProvider(),
        llm=FakeLLM(primary="project management tools"),
        prompts=PromptLoader(),
    )

    with pytest.raises(ValueError, match="keyword_plan: themes is required"):
        keyword_plan(state, deps)


def test_keyword_plan_missing_llm_raises() -> None:
    state = _make_state_with_serp_and_themes()
    deps = NodeDeps(
        serp=MockSerpProvider(),
        llm=None,
        prompts=PromptLoader(),
    )

    with pytest.raises(ValueError, match="keyword_plan: deps.llm is required"):
        keyword_plan(state, deps)


def test_keyword_plan_dedupes_secondary() -> None:
    state = _make_state_with_serp_and_themes()
    deps = NodeDeps(
        serp=MockSerpProvider(),
        llm=FakeLLM(
            primary="project management tools",
            secondary=["Task Tracking", "task tracking", "Team Collaboration"],
        ),
        prompts=PromptLoader(),
    )

    patch = keyword_plan(state, deps)

    secondary_lower = [s.lower() for s in patch["keyword_plan"].secondary]
    assert len(secondary_lower) == len(set(secondary_lower))
