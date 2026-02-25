"""seo_packager node – produce SeoPackage via LLM structured output."""

from __future__ import annotations

from src.application.orchestration.state import GraphState
from src.domain.models.seo_package import SeoPackage

from .deps import NodeDeps
from .prompt_loader import render_prompt


def seo_packager(state: GraphState, deps: NodeDeps) -> dict:
    """Produce SeoPackage from article_markdown, plan, keyword_plan. Returns a patch dict."""
    if deps.llm is None:
        raise ValueError("seo_packager: deps.llm is required")
    if deps.prompts is None:
        raise ValueError("seo_packager: deps.prompts is required")
    if state.input is None:
        raise ValueError("seo_packager: state.input is required")
    if state.plan is None:
        raise ValueError("seo_packager: state.plan is required")
    if state.keyword_plan is None:
        raise ValueError("seo_packager: state.keyword_plan is required")
    if not state.article_markdown or not state.article_markdown.strip():
        raise ValueError("seo_packager: article_markdown is required")

    template = deps.prompts.get("seo_packager")
    prompt = render_prompt(
        template,
        topic=state.input.topic,
        language=state.input.language,
        article_markdown=state.article_markdown,
        outline=state.outline.model_dump(mode="json") if state.outline else None,
        keyword_plan=state.keyword_plan.model_dump(mode="json"),
        plan=state.plan.model_dump(mode="json"),
        primary=state.keyword_plan.primary,
    )

    pkg = deps.llm.generate_structured(
        node_name="seo_packager",
        prompt=prompt,
        schema=SeoPackage,
    )

    if pkg.keyword_usage.primary != state.keyword_plan.primary:
        raise ValueError(
            f"seo_packager: keyword_usage.primary mismatch "
            f"(expected {state.keyword_plan.primary!r}, got {pkg.keyword_usage.primary!r})"
        )

    if state.outline:
        valid_ids = {s.section_id for s in state.outline.sections}
        for link in pkg.internal_links:
            if link.placement_section_id is not None and link.placement_section_id not in valid_ids:
                raise ValueError(
                    f"seo_packager: invalid placement_section_id {link.placement_section_id!r}"
                )

    return {"current_node": "seo_packager", "seo_package": pkg}
