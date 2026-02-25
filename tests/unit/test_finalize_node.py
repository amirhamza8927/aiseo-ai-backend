"""Tests for finalize node – deterministic, stores result in JobStore."""

from __future__ import annotations

import pytest

from src.application.orchestration.nodes.deps import NodeDeps
from src.application.orchestration.nodes.finalize import finalize
from src.application.orchestration.state import GraphState
from src.domain.models.job import JobStatus
from src.domain.models.outline import Outline, OutlineSection
from src.domain.models.seo_package import (
    ExternalReference,
    InternalLinkSuggestion,
    KeywordUsage,
    SeoMeta,
    SeoPackage,
)
from src.domain.models.validation import ValidationReport
from src.infrastructure.providers.serp.mock_serp import MockSerpProvider
from src.infrastructure.stores.in_memory_job_store import InMemoryJobStore


PRIMARY = "project management tools"


def _make_outline() -> Outline:
    return Outline(
        h1="Project Management Tools Guide",
        sections=[
            OutlineSection(section_id="s1", h2="Why Project Management Tools Matter"),
            OutlineSection(section_id="s2", h2="Conclusion"),
        ],
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
        keyword_usage=KeywordUsage(primary=PRIMARY, secondary=[], counts=[]),
    )


def _make_valid_article_markdown() -> str:
    return (
        f"# {PRIMARY.title()} Guide\n\n"
        f"This intro covers {PRIMARY} in depth.\n\n"
        f"## Why {PRIMARY.title()} Matter\n\n"
        + ("Lorem ipsum dolor sit amet. " * 90)
        + "\n\n## Conclusion\n\nFinal thoughts.\n"
    )


def _make_passed_report() -> ValidationReport:
    return ValidationReport(
        passed=True,
        score=1.0,
        issues=[],
        checks={
            "primary_in_title_tag": True,
            "primary_in_intro": True,
            "primary_in_h2": True,
            "heading_hierarchy_valid": True,
            "word_count_within_tolerance": True,
            "meta_description_length_valid": True,
            "internal_links_count_valid": True,
            "external_refs_count_valid": True,
            "output_schema_valid": True,
        },
    )


def _make_state(
    *,
    validation_report: ValidationReport | None = None,
    seo_package: SeoPackage | None = None,
) -> GraphState:
    return GraphState.new(
        job_id="j1",
        topic=PRIMARY,
        target_word_count=500,
        language="en",
        max_revisions=2,
    ).model_copy(
        update={
            "outline": _make_outline(),
            "article_markdown": _make_valid_article_markdown(),
            "seo_package": seo_package or _make_seo_package(),
            "validation_report": validation_report or _make_passed_report(),
        }
    )


def test_finalize_stores_result_and_sets_completed() -> None:
    job_store = InMemoryJobStore()
    job_store.create("j1")
    state = _make_state()
    deps = NodeDeps(
        serp=MockSerpProvider(),
        job_store=job_store,
    )

    patch = finalize(state, deps)

    record = job_store.get("j1")
    assert record.status == JobStatus.COMPLETED
    assert record.result is not None
    assert record.result.article_markdown == _make_valid_article_markdown()
    assert record.result.structured_data
    assert "seo_meta" in record.result.structured_data
    assert "article_markdown" in record.result.structured_data
    assert patch["current_node"] == "finalize"


def test_finalize_validation_not_passed_raises() -> None:
    job_store = InMemoryJobStore()
    job_store.create("j1")
    report = ValidationReport(
        passed=False,
        score=0.5,
        issues=["Primary keyword missing from intro"],
        checks={"primary_in_intro": False},
    )
    state = _make_state(validation_report=report)
    deps = NodeDeps(serp=MockSerpProvider(), job_store=job_store)

    with pytest.raises(
        ValueError, match="finalize: cannot finalize when validation did not pass"
    ):
        finalize(state, deps)


def test_finalize_missing_job_store_raises() -> None:
    job_store = InMemoryJobStore()
    job_store.create("j1")
    state = _make_state()
    deps = NodeDeps(serp=MockSerpProvider(), job_store=None)

    with pytest.raises(ValueError, match="finalize: deps.job_store is required"):
        finalize(state, deps)


def test_finalize_missing_or_empty_job_id_raises() -> None:
    job_store = InMemoryJobStore()
    job_store.create("j1")
    state = _make_state().model_copy(update={"job_id": ""})
    deps = NodeDeps(serp=MockSerpProvider(), job_store=job_store)

    with pytest.raises(ValueError, match="finalize: state.job_id is required"):
        finalize(state, deps)


def test_finalize_missing_seo_package_raises() -> None:
    job_store = InMemoryJobStore()
    job_store.create("j1")
    state = _make_state().model_copy(update={"seo_package": None})
    deps = NodeDeps(serp=MockSerpProvider(), job_store=job_store)

    with pytest.raises(ValueError, match="finalize: state.seo_package is required"):
        finalize(state, deps)


def test_finalize_returns_patch() -> None:
    job_store = InMemoryJobStore()
    job_store.create("j1")
    state = _make_state()
    deps = NodeDeps(serp=MockSerpProvider(), job_store=job_store)

    patch = finalize(state, deps)

    assert patch["current_node"] == "finalize"
