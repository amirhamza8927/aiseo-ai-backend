"""Tests for seo_packager node – no network, fake LLM."""

from __future__ import annotations

import pytest

from src.application.orchestration.nodes.deps import NodeDeps
from src.application.orchestration.nodes.prompt_loader import PromptLoader
from src.application.orchestration.nodes.seo_packager import seo_packager
from src.application.orchestration.state import GraphState
from src.domain.models.keyword_plan import KeywordPlan, UsageTargetItem
from src.domain.models.outline import Outline, OutlineSection
from src.domain.models.plan import Plan, PlanSection
from src.domain.models.seo_package import (
    ExternalReference,
    InternalLinkSuggestion,
    KeywordCountItem,
    KeywordUsage,
    SeoMeta,
    SeoPackage,
)
from src.infrastructure.providers.serp.mock_serp import MockSerpProvider


def _make_plan() -> Plan:
    return Plan(
        h1="Project Management Tools Guide",
        intro_target_word_count=100,
        sections=[
            PlanSection(
                section_id="s1",
                heading="Introduction",
                purpose="",
                key_points=["Overview"],
                target_word_count=100,
            ),
            PlanSection(
                section_id="s2",
                heading="Key Features",
                purpose="",
                key_points=["Features"],
                target_word_count=200,
            ),
        ],
    )


def _make_outline() -> Outline:
    return Outline(
        h1="Project Management Tools Guide",
        sections=[
            OutlineSection(section_id="s1", h2="Introduction"),
            OutlineSection(section_id="s2", h2="Key Features"),
        ],
    )


def _make_keyword_plan() -> KeywordPlan:
    return KeywordPlan(
        primary="project management tools",
        secondary=["task tracking", "team collaboration"],
        usage_targets=[UsageTargetItem(keyword="project management tools", count=2)],
    )


def _make_valid_seo_package() -> SeoPackage:
    return SeoPackage(
        seo_meta=SeoMeta(
            title_tag="Project Management Tools Guide",
            meta_description="A guide to project management tools for teams. Learn about task tracking and collaboration.",
        ),
        internal_links=[
            InternalLinkSuggestion(
                anchor_text="Task Tracking",
                target_topic="task tracking",
                placement_section_id="s1",
            ),
        ],
        external_references=[
            ExternalReference(
                source_name="Asana Blog",
                url=None,
                placement_hint="Introduction",
                credibility_reason="Authoritative source on project management",
            ),
        ],
        keyword_usage=KeywordUsage(
            primary="project management tools",
            secondary=["task tracking", "team collaboration"],
            counts=[KeywordCountItem(keyword="project management tools", count=2)],
        ),
    )


def _make_state() -> GraphState:
    return GraphState.new(
        job_id="j1",
        topic="project management tools",
        target_word_count=1500,
        language="en",
        max_revisions=2,
    ).model_copy(
        update={
            "plan": _make_plan(),
            "outline": _make_outline(),
            "keyword_plan": _make_keyword_plan(),
            "article_markdown": "# Project Management Tools\n\nIntro.\n\n## Introduction\n\nContent.\n\n## Key Features\n\nContent.",
        }
    )


class FakeLLM:
    """Fake LLM that returns a configurable SeoPackage."""

    def __init__(self, seo_package: SeoPackage) -> None:
        self._pkg = seo_package

    def generate_structured(self, *, node_name: str, prompt: str, schema: type) -> SeoPackage:
        assert node_name == "seo_packager"
        assert schema is SeoPackage
        assert "project management" in prompt
        return self._pkg


def test_seo_packager_returns_patch() -> None:
    state = _make_state()
    deps = NodeDeps(
        serp=MockSerpProvider(),
        llm=FakeLLM(_make_valid_seo_package()),
        prompts=PromptLoader(),
    )

    patch = seo_packager(state, deps)

    assert patch["current_node"] == "seo_packager"
    assert "seo_package" in patch
    assert isinstance(patch["seo_package"], SeoPackage)
    assert patch["seo_package"].keyword_usage.primary == "project management tools"


def test_seo_packager_primary_mismatch_raises() -> None:
    pkg = _make_valid_seo_package().model_copy(
        update={"keyword_usage": KeywordUsage(primary="wrong primary", secondary=[], counts=[])}
    )
    state = _make_state()
    deps = NodeDeps(
        serp=MockSerpProvider(),
        llm=FakeLLM(pkg),
        prompts=PromptLoader(),
    )

    with pytest.raises(ValueError, match="seo_packager: keyword_usage.primary mismatch"):
        seo_packager(state, deps)


def test_seo_packager_invalid_placement_id_raises() -> None:
    pkg = _make_valid_seo_package().model_copy(
        update={
            "internal_links": [
                InternalLinkSuggestion(
                    anchor_text="Task Tracking",
                    target_topic="task tracking",
                    placement_section_id="s99",
                ),
            ],
        }
    )
    state = _make_state()
    deps = NodeDeps(
        serp=MockSerpProvider(),
        llm=FakeLLM(pkg),
        prompts=PromptLoader(),
    )

    with pytest.raises(ValueError, match="seo_packager: invalid placement_section_id"):
        seo_packager(state, deps)


def test_seo_packager_missing_llm_raises() -> None:
    state = _make_state()
    deps = NodeDeps(
        serp=MockSerpProvider(),
        llm=None,
        prompts=PromptLoader(),
    )

    with pytest.raises(ValueError, match="seo_packager: deps.llm is required"):
        seo_packager(state, deps)


def test_seo_packager_missing_article_markdown_raises() -> None:
    state = _make_state().model_copy(update={"article_markdown": None})
    deps = NodeDeps(
        serp=MockSerpProvider(),
        llm=FakeLLM(_make_valid_seo_package()),
        prompts=PromptLoader(),
    )

    with pytest.raises(ValueError, match="seo_packager: article_markdown is required"):
        seo_packager(state, deps)


def test_seo_packager_empty_article_markdown_raises() -> None:
    state = _make_state().model_copy(update={"article_markdown": "   "})
    deps = NodeDeps(
        serp=MockSerpProvider(),
        llm=FakeLLM(_make_valid_seo_package()),
        prompts=PromptLoader(),
    )

    with pytest.raises(ValueError, match="seo_packager: article_markdown is required"):
        seo_packager(state, deps)


def test_seo_packager_works_without_outline() -> None:
    """When outline is None, placement_section_id validation is skipped."""
    state = _make_state().model_copy(update={"outline": None})
    deps = NodeDeps(
        serp=MockSerpProvider(),
        llm=FakeLLM(_make_valid_seo_package()),
        prompts=PromptLoader(),
    )

    patch = seo_packager(state, deps)

    assert patch["current_node"] == "seo_packager"
    assert isinstance(patch["seo_package"], SeoPackage)
