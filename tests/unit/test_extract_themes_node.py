"""Tests for extract_themes node – no network, fake LLM."""

from __future__ import annotations

import pytest

from src.application.orchestration.nodes.extract_themes import extract_themes
from src.application.orchestration.nodes.deps import NodeDeps
from src.application.orchestration.nodes.prompt_loader import PromptLoader
from src.application.orchestration.state import GraphState
from src.domain.models.themes import Themes
from src.infrastructure.providers.serp.mock_serp import MockSerpProvider


class FakeLLM:
    """Fake LLM that returns a Themes instance without calling the network."""

    def generate_structured(self, *, node_name: str, prompt: str, schema: type) -> Themes:
        assert node_name == "extract_themes"
        assert schema is Themes
        assert "project management" in prompt
        return Themes(
            search_intent="find tools",
            topic_clusters=["tools", "comparison"],
            common_sections=["Overview", "Pricing"],
            ranking_patterns=["listicle"],
            differentiation_angles=["depth"],
        )


def _make_state_with_serp() -> GraphState:
    serp = MockSerpProvider()
    results = serp.fetch_top_results(topic="project management tools", language="en")
    return GraphState.new(
        job_id="j1",
        topic="project management tools",
        target_word_count=1500,
        language="en",
        max_revisions=2,
    ).model_copy(update={"serp_results": results})


def test_extract_themes_returns_patch_with_themes() -> None:
    state = _make_state_with_serp()
    deps = NodeDeps(
        serp=MockSerpProvider(),
        llm=FakeLLM(),
        prompts=PromptLoader(),
    )

    patch = extract_themes(state, deps)

    assert patch["current_node"] == "extract_themes"
    assert isinstance(patch["themes"], Themes)
    assert patch["themes"].search_intent == "find tools"


def test_extract_themes_missing_llm_raises() -> None:
    state = _make_state_with_serp()
    deps = NodeDeps(serp=MockSerpProvider(), llm=None, prompts=PromptLoader())

    with pytest.raises(ValueError, match="extract_themes: deps.llm is required"):
        extract_themes(state, deps)


def test_extract_themes_missing_prompts_raises() -> None:
    state = _make_state_with_serp()
    deps = NodeDeps(serp=MockSerpProvider(), llm=FakeLLM(), prompts=None)

    with pytest.raises(ValueError, match="extract_themes: deps.prompts is required"):
        extract_themes(state, deps)


def test_extract_themes_missing_serp_results_raises() -> None:
    state = GraphState.new(
        job_id="j1",
        topic="project management tools",
        target_word_count=1500,
        language="en",
        max_revisions=2,
    )
    deps = NodeDeps(
        serp=MockSerpProvider(),
        llm=FakeLLM(),
        prompts=PromptLoader(),
    )

    with pytest.raises(ValueError, match="extract_themes: serp_results is required"):
        extract_themes(state, deps)
