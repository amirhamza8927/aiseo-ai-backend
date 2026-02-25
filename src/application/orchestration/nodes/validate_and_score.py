"""validate_and_score node – run deterministic SEO validators, return ValidationReport."""

from __future__ import annotations

from src.application.orchestration.state import GraphState
from src.application.services.seo_validators import (
    SeoValidationConfig,
    validate_seo_article,
)
from src.domain.models.output import SeoArticleOutput
from src.domain.models.validation import ValidationReport

from .deps import NodeDeps


def validate_and_score(state: GraphState, deps: NodeDeps) -> dict:
    """Run deterministic SEO checks on article output. Returns a patch dict."""
    if state.input is None:
        raise ValueError("validate_and_score: state.input is required")
    if state.keyword_plan is None:
        raise ValueError("validate_and_score: state.keyword_plan is required")
    if state.outline is None:
        raise ValueError("validate_and_score: state.outline is required")
    if not state.article_markdown or not state.article_markdown.strip():
        raise ValueError("validate_and_score: article_markdown is required")
    if state.seo_package is None:
        raise ValueError("validate_and_score: state.seo_package is required")

    output = SeoArticleOutput(
        seo_meta=state.seo_package.seo_meta,
        article_markdown=state.article_markdown,
        outline=state.outline,
        keyword_analysis=state.seo_package.keyword_usage,
        internal_links=state.seo_package.internal_links,
        external_references=state.seo_package.external_references,
        structured_data={},
        validation_report=ValidationReport(passed=False, score=0.0, issues=[], checks={}),
    )

    report = validate_seo_article(
        output=output,
        primary_keyword=state.keyword_plan.primary,
        config=SeoValidationConfig(word_count_target=state.input.target_word_count),
    )

    return {"current_node": "validate_and_score", "validation_report": report}
