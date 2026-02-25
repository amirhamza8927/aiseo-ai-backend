"""finalize node – build SeoArticleOutput and store in JobStore."""

from __future__ import annotations

from src.application.orchestration.state import GraphState
from src.domain.models.output import SeoArticleOutput

from .deps import NodeDeps


def finalize(state: GraphState, deps: NodeDeps) -> dict:
    """Build output from state, store in job_store, return patch."""
    if deps.job_store is None:
        raise ValueError("finalize: deps.job_store is required")
    if not state.job_id or not state.job_id.strip():
        raise ValueError("finalize: state.job_id is required")
    if state.input is None:
        raise ValueError("finalize: state.input is required")
    if state.outline is None:
        raise ValueError("finalize: state.outline is required")
    if not state.article_markdown or not state.article_markdown.strip():
        raise ValueError("finalize: article_markdown is required")
    if state.seo_package is None:
        raise ValueError("finalize: state.seo_package is required")
    if state.validation_report is None:
        raise ValueError("finalize: state.validation_report is required")
    if not state.validation_report.passed:
        raise ValueError("finalize: cannot finalize when validation did not pass")

    output = SeoArticleOutput(
        seo_meta=state.seo_package.seo_meta,
        article_markdown=state.article_markdown,
        outline=state.outline,
        keyword_analysis=state.seo_package.keyword_usage,
        internal_links=state.seo_package.internal_links,
        external_references=state.seo_package.external_references,
        structured_data={},
        validation_report=state.validation_report,
    )
    structured = output.model_dump(mode="json")
    output = output.model_copy(update={"structured_data": structured})

    deps.job_store.set_result(state.job_id, output)
    return {"current_node": "finalize"}
