"""Tests for validate_and_score node – deterministic validation, no LLM."""

from __future__ import annotations

import pytest

from src.application.orchestration.nodes.deps import NodeDeps
from src.application.orchestration.nodes.validate_and_score import validate_and_score
from src.application.orchestration.state import GraphState
from src.domain.models.keyword_plan import KeywordPlan
from src.domain.models.outline import Outline, OutlineSection
from src.domain.models.seo_package import (
    ExternalReference,
    InternalLinkSuggestion,
    KeywordUsage,
    SeoMeta,
    SeoPackage,
)
from src.infrastructure.providers.serp.mock_serp import MockSerpProvider


PRIMARY = "project management tools"

EXPECTED_CHECK_KEYS = {
    "primary_in_title_tag",
    "primary_in_intro",
    "primary_in_h2",
    "heading_hierarchy_valid",
    "word_count_within_tolerance",
    "meta_description_length_valid",
    "internal_links_count_valid",
    "external_refs_count_valid",
    "output_schema_valid",
}


def _make_outline() -> Outline:
    return Outline(
        h1="Project Management Tools Guide",
        sections=[
            OutlineSection(section_id="s1", h2="Why Project Management Tools Matter"),
            OutlineSection(section_id="s2", h2="Conclusion"),
        ],
    )


def _make_keyword_plan() -> KeywordPlan:
    return KeywordPlan(
        primary=PRIMARY,
        secondary=["task tracking", "team collaboration"],
        usage_targets={PRIMARY: 2},
    )


def _make_valid_article_markdown() -> str:
    return (
        f"# {PRIMARY.title()} Guide\n\n"
        f"This intro covers {PRIMARY} in depth.\n\n"
        f"## Why {PRIMARY.title()} Matter\n\n"
        + ("Lorem ipsum dolor sit amet. " * 90)
        + "\n\n## Conclusion\n\nFinal thoughts.\n"
    )


def _make_seo_package() -> SeoPackage:
    return SeoPackage(
        seo_meta=SeoMeta(
            title_tag=f"Best {PRIMARY.title()} for 2026",
            meta_description="x" * 150,
        ),
        internal_links=[
            InternalLinkSuggestion(anchor_text=f"link{i}", target_topic="t")
            for i in range(3)
        ],
        external_references=[
            ExternalReference(
                source_name=f"src{i}",
                placement_hint="body",
                credibility_reason="authoritative",
            )
            for i in range(2)
        ],
        keyword_usage=KeywordUsage(primary=PRIMARY, secondary=[], counts={}),
    )


def _make_state() -> GraphState:
    return GraphState.new(
        job_id="j1",
        topic=PRIMARY,
        target_word_count=500,
        language="en",
        max_revisions=2,
    ).model_copy(
        update={
            "outline": _make_outline(),
            "keyword_plan": _make_keyword_plan(),
            "article_markdown": _make_valid_article_markdown(),
            "seo_package": _make_seo_package(),
        }
    )


def test_validate_and_score_returns_patch() -> None:
    state = _make_state()
    deps = NodeDeps(serp=MockSerpProvider())

    patch = validate_and_score(state, deps)

    assert patch["current_node"] == "validate_and_score"
    assert "validation_report" in patch
    report = patch["validation_report"]
    assert report.checks.keys() == EXPECTED_CHECK_KEYS
    assert report.passed is True


def test_validate_and_score_fails_when_primary_missing_from_intro() -> None:
    md = (
        f"# {PRIMARY.title()} Guide\n\n"
        "This intro has no primary keyword here.\n\n"
        f"## Why {PRIMARY.title()} Matter\n\n"
        + ("Lorem ipsum dolor sit amet. " * 90)
        + "\n\n## Conclusion\n\nFinal thoughts.\n"
    )
    state = _make_state().model_copy(update={"article_markdown": md})
    deps = NodeDeps(serp=MockSerpProvider())

    patch = validate_and_score(state, deps)

    assert patch["validation_report"].passed is False
    assert patch["validation_report"].checks["primary_in_intro"] is False
    assert any(
        "missing from intro paragraph" in i for i in patch["validation_report"].issues
    )


def test_validate_and_score_missing_seo_package_raises() -> None:
    state = _make_state().model_copy(update={"seo_package": None})
    deps = NodeDeps(serp=MockSerpProvider())

    with pytest.raises(
        ValueError, match="validate_and_score: state.seo_package is required"
    ):
        validate_and_score(state, deps)
