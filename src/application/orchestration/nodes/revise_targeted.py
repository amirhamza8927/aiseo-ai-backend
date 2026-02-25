"""revise_targeted node – targeted LLM revisions from RepairSpec."""

from __future__ import annotations

from src.application.orchestration.state import GraphState
from src.application.services.markdown_tools import extract_headings
from src.domain.models.revision import RevisionResult

from .deps import NodeDeps
from .prompt_loader import render_prompt


def _norm(s: str) -> str:
    """Normalize for whitespace-tolerant comparison."""
    return " ".join(s.lower().split())


def _word_count_budget(target: int, outline) -> str:
    """Compute per-section word count caps for reviser prompt."""
    tolerance = 0.15
    wc_min = int(target * (1 - tolerance))
    wc_max = int(target * (1 + tolerance))
    parts = [f"total target range: {wc_min}–{wc_max}"]
    if outline and outline.sections:
        n_sections = len(outline.sections)
        intro_cap = max(50, int(wc_max * 0.2))
        section_cap = max(50, int((wc_max - intro_cap) / n_sections))
        parts.append(f"intro <= {intro_cap}")
        for sec in outline.sections:
            parts.append(f"{sec.section_id} <= {section_cap}")
    return ". ".join(parts)


def revise_targeted(state: GraphState, deps: NodeDeps) -> dict:
    """Revise article per RepairSpec. Returns patch with article_markdown, optional seo_package."""
    if deps.llm is None:
        raise ValueError("revise_targeted: deps.llm is required")
    if deps.prompts is None:
        raise ValueError("revise_targeted: deps.prompts is required")
    if state.input is None:
        raise ValueError("revise_targeted: state.input is required")
    if state.repair_spec is None:
        raise ValueError("revise_targeted: repair_spec is required")
    if not state.article_markdown or not state.article_markdown.strip():
        raise ValueError("revise_targeted: article_markdown is required")
    if state.seo_package is None:
        raise ValueError("revise_targeted: seo_package is required")
    if state.revisions_left <= 0:
        raise ValueError("revise_targeted: revisions_left must be > 0")

    template = deps.prompts.get("reviser")
    word_count_budget = _word_count_budget(
        state.input.target_word_count, state.outline
    )
    prompt = render_prompt(
        template,
        topic=state.input.topic,
        language=state.input.language,
        target_word_count=state.input.target_word_count,
        word_count_budget=word_count_budget,
        keyword_plan=state.keyword_plan.model_dump(mode="json") if state.keyword_plan else {},
        outline=state.outline.model_dump(mode="json") if state.outline else {},
        current_seo_package=state.seo_package.model_dump(mode="json"),
        current_article_markdown=state.article_markdown,
        repair_spec=state.repair_spec.model_dump(mode="json"),
    )

    revision = deps.llm.generate_structured(
        node_name="revise_targeted",
        prompt=prompt,
        schema=RevisionResult,
    )

    md = revision.article_markdown.strip()
    headings = extract_headings(md)
    h1_count = sum(1 for lvl, _ in headings if lvl == 1)
    if h1_count != 1:
        raise ValueError(f"revise_targeted: expected exactly 1 H1, found {h1_count}")

    if state.outline:
        md_norm = _norm(md)
        missing: list[str] = []
        for sec in state.outline.sections:
            if _norm(f"## {sec.h2}") not in md_norm:
                missing.append(sec.h2)
        if missing:
            raise ValueError(f"revise_targeted: missing required H2 headings: {missing}")

    targets = set(state.repair_spec.must_edit_section_ids)
    if targets == {"__seo_meta__"}:
        if _norm(md) != _norm(state.article_markdown):
            raise ValueError(
                "revise_targeted: only __seo_meta__ targeted; article text must not change"
            )

    if revision.seo_package is not None:
        if state.keyword_plan and revision.seo_package.keyword_usage.primary != state.keyword_plan.primary:
            raise ValueError(
                f"revise_targeted: keyword_usage.primary mismatch "
                f"(expected {state.keyword_plan.primary!r}, got {revision.seo_package.keyword_usage.primary!r})"
            )
        if state.outline:
            valid_ids = {s.section_id for s in state.outline.sections}
            for link in revision.seo_package.internal_links:
                if link.placement_section_id is not None and link.placement_section_id not in valid_ids:
                    raise ValueError(
                        f"revise_targeted: invalid placement_section_id {link.placement_section_id!r}"
                    )

    new_revisions_left = max(state.revisions_left - 1, 0)
    patch: dict = {
        "current_node": "revise_targeted",
        "article_markdown": md,
        "revisions_left": new_revisions_left,
    }
    if revision.seo_package is not None:
        patch["seo_package"] = revision.seo_package
    return patch
