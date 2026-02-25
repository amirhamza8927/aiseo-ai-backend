"""Fake LLM provider for deterministic integration and e2e tests."""

from __future__ import annotations

from typing import Any, TypeVar

from pydantic import BaseModel

from src.domain.models.keyword_plan import KeywordPlan
from src.domain.models.outline import Outline, OutlineSection
from src.domain.models.plan import Plan, PlanSection
from src.domain.models.revision import RevisionResult
from src.domain.models.seo_package import (
    ExternalReference,
    InternalLinkSuggestion,
    KeywordUsage,
    SeoMeta,
    SeoPackage,
)
from src.domain.models.themes import Themes

T = TypeVar("T", bound=BaseModel)

# Fixed topic for all fake outputs
DEFAULT_TOPIC = "seo tools"
DEFAULT_PRIMARY = "seo tools"

# Outline that build_outline returns (must match plan section_ids)
FAKE_OUTLINE = Outline(
    h1=f"Best {DEFAULT_TOPIC.title()} Guide",
    sections=[
        OutlineSection(section_id="s1", h2=f"Why {DEFAULT_TOPIC.title()} Matter"),
        OutlineSection(section_id="s2", h2="Conclusion"),
    ],
)

# Plan with budget 100 + 200 + 200 = 500 (within 0.75-1.25 of 500)
FAKE_PLAN = Plan(
    h1=f"Best {DEFAULT_TOPIC.title()} Guide",
    intro_target_word_count=100,
    sections=[
        PlanSection(
            section_id="s1",
            heading=f"Why {DEFAULT_TOPIC.title()} Matter",
            purpose="Explain importance",
            key_points=["Point 1"],
            target_word_count=200,
        ),
        PlanSection(
            section_id="s2",
            heading="Conclusion",
            purpose="Wrap up",
            key_points=["Summary"],
            target_word_count=200,
        ),
    ],
)


def _article_markdown(primary_in_intro: bool) -> str:
    """Deterministic markdown: 1 H1, H2s matching FAKE_OUTLINE, optional primary in intro.
    Word count ~500 to pass validation (target 500, tolerance 15% => 425-575).
    """
    intro = f"This intro covers {DEFAULT_PRIMARY} in depth." if primary_in_intro else "This intro covers the topic broadly."
    # ~6 words per repeat; need 425+ words for 500 target (tolerance 15% => 425-575)
    body_filler = "Lorem ipsum dolor sit amet. " * 90
    return (
        f"# Best {DEFAULT_TOPIC.title()} Guide\n\n"
        f"{intro}\n\n"
        f"## Why {DEFAULT_TOPIC.title()} Matter\n\n"
        f"{body_filler}\n\n"
        "## Conclusion\n\nFinal thoughts.\n"
    )


def _seo_package(primary: str) -> SeoPackage:
    return SeoPackage(
        seo_meta=SeoMeta(
            title_tag=f"Best {primary.title()} for 2026",
            meta_description="x" * 150,
        ),
        internal_links=[
            InternalLinkSuggestion(anchor_text=f"link{i}", target_topic="t", placement_section_id="s1")
            for i in range(4)
        ],
        external_references=[
            ExternalReference(
                source_name=f"src{i}",
                placement_hint="body",
                credibility_reason="authoritative",
            )
            for i in range(3)
        ],
        keyword_usage=KeywordUsage(primary=primary, secondary=[], counts=[]),
    )


class FakeLLMProvider:
    """Deterministic LLM replacement. No network. Returns schema-valid outputs."""

    def __init__(
        self,
        *,
        topic: str = DEFAULT_TOPIC,
        pass_validation: bool = True,
        mode: str = "pass",
    ) -> None:
        self.topic = topic
        self.primary = topic
        self.pass_validation = pass_validation
        self.mode = mode  # "pass" | "revision_loop" | "fail"
        self._write_article_calls = 0
        self._revise_calls = 0
        self._outline = FAKE_OUTLINE.model_copy(
            update={"h1": f"Best {topic.title()} Guide", "sections": [
                OutlineSection(section_id="s1", h2=f"Why {topic.title()} Matter"),
                OutlineSection(section_id="s2", h2="Conclusion"),
            ]}
        )

    def generate_structured(
        self,
        *,
        node_name: str,
        prompt: str,
        schema: type[T],
        **kwargs: Any,
    ) -> T:
        if schema == Themes:
            return schema.model_validate({
                "search_intent": f"Find best {self.topic}",
                "topic_clusters": [self.topic],
                "common_sections": ["Introduction", "Conclusion"],
                "ranking_patterns": ["Comparison", "Reviews"],
                "differentiation_angles": ["Pricing", "Features"],
            })
        if schema == Plan:
            return schema.model_validate(FAKE_PLAN.model_dump() | {"h1": f"Best {self.topic.title()} Guide"})
        if schema == Outline:
            return schema.model_validate(self._outline.model_dump())
        if schema == KeywordPlan:
            return schema.model_validate({"primary": self.primary, "secondary": ["comparison", "review"], "usage_targets": []})
        if schema == SeoPackage:
            return schema.model_validate(_seo_package(self.primary).model_dump(mode="json"))
        if schema == RevisionResult:
            self._revise_calls += 1
            if self.mode == "revision_loop" and self._revise_calls == 1:
                primary_in_intro = True
            elif self.mode == "fail":
                primary_in_intro = False
            else:
                primary_in_intro = True
            md = _article_markdown(primary_in_intro)
            return schema.model_validate({
                "article_markdown": md,
                "seo_package": _seo_package(self.primary).model_dump(mode="json"),
                "notes": [],
            })
        raise ValueError(f"FakeLLMProvider: unknown schema {schema}")

    def generate_text(
        self,
        *,
        node_name: str,
        prompt: str,
        **kwargs: Any,
    ) -> str:
        if node_name == "write_article":
            self._write_article_calls += 1
            if self.mode == "revision_loop" and self._write_article_calls == 1:
                return _article_markdown(primary_in_intro=False)
            if self.mode == "fail":
                return _article_markdown(primary_in_intro=False)
            return _article_markdown(primary_in_intro=True)
        raise ValueError(f"FakeLLMProvider: unknown node_name {node_name}")
