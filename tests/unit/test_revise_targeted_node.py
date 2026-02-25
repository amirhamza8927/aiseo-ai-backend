"""Tests for revise_targeted node – no network, fake LLM."""

from __future__ import annotations

import pytest

from src.application.orchestration.nodes.deps import NodeDeps
from src.application.orchestration.nodes.prompt_loader import PromptLoader
from src.application.orchestration.nodes.revise_targeted import revise_targeted
from src.application.orchestration.state import GraphState
from src.domain.models.keyword_plan import KeywordPlan, UsageTargetItem
from src.domain.models.outline import Outline, OutlineSection
from src.domain.models.repair import RepairSpec
from src.domain.models.revision import RevisionResult
from src.domain.models.seo_package import (
    KeywordCountItem,
    KeywordUsage,
    SeoMeta,
    SeoPackage,
)
from src.infrastructure.providers.serp.mock_serp import MockSerpProvider


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


def _make_seo_package() -> SeoPackage:
    return SeoPackage(
        seo_meta=SeoMeta(
            title_tag="Project Management Tools Guide",
            meta_description="A guide to project management tools for teams.",
        ),
        internal_links=[],
        external_references=[],
        keyword_usage=KeywordUsage(
            primary="project management tools",
            secondary=["task tracking", "team collaboration"],
            counts=[KeywordCountItem(keyword="project management tools", count=2)],
        ),
    )


def _make_repair_spec() -> RepairSpec:
    return RepairSpec(
        issues=[],
        instructions=["Add primary keyword to intro"],
        must_edit_section_ids=["__intro__"],
    )


ARTICLE_MD = "# Project Management Tools Guide\n\nIntro.\n\n## Introduction\n\nContent.\n\n## Key Features\n\nContent."


def _make_state(
    *,
    repair_spec: RepairSpec | None = None,
    article_markdown: str | None = None,
    seo_package: SeoPackage | None = None,
    outline: Outline | None = None,
    keyword_plan: KeywordPlan | None = None,
    revisions_left: int = 2,
) -> GraphState:
    return GraphState.new(
        job_id="j1",
        topic="project management tools",
        target_word_count=1500,
        language="en",
        max_revisions=2,
    ).model_copy(
        update={
            "repair_spec": repair_spec or _make_repair_spec(),
            "article_markdown": article_markdown or ARTICLE_MD,
            "seo_package": seo_package or _make_seo_package(),
            "outline": outline or _make_outline(),
            "keyword_plan": keyword_plan or _make_keyword_plan(),
            "revisions_left": revisions_left,
        }
    )


class FakeLLM:
    """Fake LLM that returns a configurable RevisionResult."""

    def __init__(self, result: RevisionResult) -> None:
        self._result = result

    def generate_structured(self, *, node_name: str, prompt: str, schema: type) -> RevisionResult:
        assert node_name == "revise_targeted"
        assert schema is RevisionResult
        assert "project management" in prompt
        return self._result


def test_revise_targeted_returns_patch() -> None:
    result = RevisionResult(
        article_markdown=ARTICLE_MD,
        seo_package=None,
        notes=[],
    )
    state = _make_state()
    deps = NodeDeps(
        serp=MockSerpProvider(),
        llm=FakeLLM(result),
        prompts=PromptLoader(),
    )

    patch = revise_targeted(state, deps)

    assert patch["current_node"] == "revise_targeted"
    assert patch["article_markdown"] == ARTICLE_MD
    assert patch["revisions_left"] == 1
    assert "seo_package" not in patch


def test_revise_targeted_includes_seo_package_when_returned() -> None:
    pkg = _make_seo_package()
    result = RevisionResult(
        article_markdown=ARTICLE_MD,
        seo_package=pkg,
        notes=[],
    )
    state = _make_state()
    deps = NodeDeps(
        serp=MockSerpProvider(),
        llm=FakeLLM(result),
        prompts=PromptLoader(),
    )

    patch = revise_targeted(state, deps)

    assert patch["current_node"] == "revise_targeted"
    assert patch["seo_package"] is pkg
    assert patch["revisions_left"] == 1


def test_revise_targeted_revisions_left_zero_raises() -> None:
    result = RevisionResult(article_markdown=ARTICLE_MD, seo_package=None, notes=[])
    state = _make_state(revisions_left=0)
    deps = NodeDeps(
        serp=MockSerpProvider(),
        llm=FakeLLM(result),
        prompts=PromptLoader(),
    )

    with pytest.raises(ValueError, match="revise_targeted: revisions_left must be > 0"):
        revise_targeted(state, deps)


def test_revise_targeted_missing_repair_spec_raises() -> None:
    result = RevisionResult(article_markdown=ARTICLE_MD, seo_package=None, notes=[])
    state = _make_state().model_copy(update={"repair_spec": None})
    deps = NodeDeps(
        serp=MockSerpProvider(),
        llm=FakeLLM(result),
        prompts=PromptLoader(),
    )

    with pytest.raises(ValueError, match="revise_targeted: repair_spec is required"):
        revise_targeted(state, deps)


def test_revise_targeted_missing_article_markdown_raises() -> None:
    result = RevisionResult(article_markdown=ARTICLE_MD, seo_package=None, notes=[])
    state = _make_state().model_copy(update={"article_markdown": None})
    deps = NodeDeps(
        serp=MockSerpProvider(),
        llm=FakeLLM(result),
        prompts=PromptLoader(),
    )

    with pytest.raises(ValueError, match="revise_targeted: article_markdown is required"):
        revise_targeted(state, deps)


def test_revise_targeted_drops_required_h2_raises() -> None:
    md_missing_h2 = "# Project Management Tools Guide\n\nIntro.\n\n## Introduction\n\nContent."
    result = RevisionResult(article_markdown=md_missing_h2, seo_package=None, notes=[])
    state = _make_state()
    deps = NodeDeps(
        serp=MockSerpProvider(),
        llm=FakeLLM(result),
        prompts=PromptLoader(),
    )

    with pytest.raises(ValueError, match="revise_targeted: missing required H2 headings"):
        revise_targeted(state, deps)


def test_revise_targeted_seo_package_primary_mismatch_raises() -> None:
    pkg = _make_seo_package().model_copy(
        update={"keyword_usage": KeywordUsage(primary="wrong primary", secondary=[], counts=[])}
    )
    result = RevisionResult(article_markdown=ARTICLE_MD, seo_package=pkg, notes=[])
    state = _make_state()
    deps = NodeDeps(
        serp=MockSerpProvider(),
        llm=FakeLLM(result),
        prompts=PromptLoader(),
    )

    with pytest.raises(ValueError, match="revise_targeted: keyword_usage.primary mismatch"):
        revise_targeted(state, deps)
