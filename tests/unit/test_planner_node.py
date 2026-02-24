"""Tests for planner node – no network, fake LLM."""

from __future__ import annotations

import pytest

from src.application.orchestration.nodes.planner import planner
from src.application.orchestration.nodes.deps import NodeDeps
from src.application.orchestration.nodes.prompt_loader import PromptLoader
from src.application.orchestration.state import GraphState
from src.domain.models.plan import Plan, PlanSection
from src.domain.models.themes import Themes
from src.infrastructure.providers.serp.mock_serp import MockSerpProvider


class FakeLLM:
    """Fake LLM that returns a Plan instance without calling the network."""

    def generate_structured(self, *, node_name: str, prompt: str, schema: type) -> Plan:
        assert node_name == "planner"
        assert schema is Plan
        assert "project management" in prompt
        return Plan(
            h1="Best Project Management Tools",
            intro_target_word_count=300,
            sections=[
                PlanSection(
                    section_id="s1",
                    heading="Overview",
                    purpose="Introduce the topic",
                    key_points=["Key point 1"],
                    target_word_count=300,
                ),
                PlanSection(
                    section_id="s2",
                    heading="Comparison",
                    purpose="Compare tools",
                    key_points=["Key point 2"],
                    target_word_count=300,
                ),
                PlanSection(
                    section_id="s3",
                    heading="Pricing",
                    purpose="Discuss pricing",
                    key_points=["Key point 3"],
                    target_word_count=300,
                ),
                PlanSection(
                    section_id="s4",
                    heading="Conclusion",
                    purpose="Wrap up",
                    key_points=["Key point 4"],
                    target_word_count=300,
                ),
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


def test_planner_returns_patch_with_plan() -> None:
    state = _make_state_with_serp_and_themes()
    deps = NodeDeps(
        serp=MockSerpProvider(),
        llm=FakeLLM(),
        prompts=PromptLoader(),
    )

    patch = planner(state, deps)

    assert patch["current_node"] == "planner"
    assert isinstance(patch["plan"], Plan)
    assert patch["plan"].h1 == "Best Project Management Tools"
    assert len(patch["plan"].sections) == 4


def test_planner_missing_llm_raises() -> None:
    state = _make_state_with_serp_and_themes()
    deps = NodeDeps(serp=MockSerpProvider(), llm=None, prompts=PromptLoader())

    with pytest.raises(ValueError, match="planner: deps.llm is required"):
        planner(state, deps)


def test_planner_missing_prompts_raises() -> None:
    state = _make_state_with_serp_and_themes()
    deps = NodeDeps(serp=MockSerpProvider(), llm=FakeLLM(), prompts=None)

    with pytest.raises(ValueError, match="planner: deps.prompts is required"):
        planner(state, deps)


def test_planner_missing_input_raises() -> None:
    base = _make_state_with_serp_and_themes()
    state = GraphState.model_construct(
        job_id=base.job_id,
        input=None,
        serp_results=base.serp_results,
        themes=base.themes,
        revisions_left=base.revisions_left,
    )
    deps = NodeDeps(
        serp=MockSerpProvider(),
        llm=FakeLLM(),
        prompts=PromptLoader(),
    )

    with pytest.raises(ValueError, match="planner: state.input is required"):
        planner(state, deps)


def test_planner_missing_themes_raises() -> None:
    state = _make_state_with_serp_and_themes()
    state = state.model_copy(update={"themes": None})
    deps = NodeDeps(
        serp=MockSerpProvider(),
        llm=FakeLLM(),
        prompts=PromptLoader(),
    )

    with pytest.raises(ValueError, match="planner: themes is required"):
        planner(state, deps)


def test_planner_missing_serp_results_raises() -> None:
    state = _make_state_with_serp_and_themes()
    state = state.model_copy(update={"serp_results": None})
    deps = NodeDeps(
        serp=MockSerpProvider(),
        llm=FakeLLM(),
        prompts=PromptLoader(),
    )

    with pytest.raises(ValueError, match="planner: serp_results is required"):
        planner(state, deps)


def test_planner_empty_serp_results_raises() -> None:
    state = _make_state_with_serp_and_themes()
    state = state.model_copy(update={"serp_results": []})
    deps = NodeDeps(
        serp=MockSerpProvider(),
        llm=FakeLLM(),
        prompts=PromptLoader(),
    )

    with pytest.raises(ValueError, match="planner: serp_results is required"):
        planner(state, deps)


def test_planner_budget_mismatch_raises() -> None:
    """FakeLLM returns Plan with total 100 when target is 1500 – outside +/- 25%."""

    class BadBudgetLLM:
        def generate_structured(self, *, node_name: str, prompt: str, schema: type) -> Plan:
            return Plan(
                h1="Test",
                intro_target_word_count=50,
                sections=[
                    PlanSection(
                        section_id="s1",
                        heading="One",
                        purpose="",
                        key_points=["x"],
                        target_word_count=50,
                    ),
                ],
            )

    state = _make_state_with_serp_and_themes()
    deps = NodeDeps(
        serp=MockSerpProvider(),
        llm=BadBudgetLLM(),
        prompts=PromptLoader(),
    )

    with pytest.raises(ValueError, match="planner: budgets .* outside 0.75x"):
        planner(state, deps)
