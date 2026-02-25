"""write_article node – generate Markdown via LLM text output."""

from __future__ import annotations

from src.application.orchestration.state import GraphState
from src.application.services.markdown_tools import extract_headings

from .deps import NodeDeps
from .prompt_loader import render_prompt


def _norm(s: str) -> str:
    """Normalize for whitespace-tolerant comparison."""
    return " ".join(s.lower().split())


def write_article(state: GraphState, deps: NodeDeps) -> dict:
    """Generate article Markdown from plan, outline, keyword_plan. Returns a patch dict."""
    if deps.llm is None:
        raise ValueError("write_article: deps.llm is required")
    if deps.prompts is None:
        raise ValueError("write_article: deps.prompts is required")
    if state.input is None:
        raise ValueError("write_article: state.input is required")
    if state.plan is None:
        raise ValueError("write_article: state.plan is required")
    if state.outline is None:
        raise ValueError("write_article: state.outline is required")
    if state.keyword_plan is None:
        raise ValueError("write_article: state.keyword_plan is required")

    template = deps.prompts.get("writer")
    prompt = render_prompt(
        template,
        topic=state.input.topic,
        language=state.input.language,
        target_word_count=state.input.target_word_count,
        plan=state.plan.model_dump(mode="json"),
        outline=state.outline.model_dump(mode="json"),
        keyword_plan=state.keyword_plan.model_dump(mode="json"),
    )

    md = deps.llm.generate_text(node_name="write_article", prompt=prompt)
    md = md.strip()
    if not md:
        raise ValueError("write_article: LLM returned empty markdown")

    headings = extract_headings(md)
    h1_count = sum(1 for lvl, _ in headings if lvl == 1)
    if h1_count != 1:
        raise ValueError(f"write_article: expected exactly 1 H1, found {h1_count}")

    md_norm = _norm(md)
    missing: list[str] = []
    for sec in state.outline.sections:
        if _norm(f"## {sec.h2}") not in md_norm:
            missing.append(sec.h2)
    if missing:
        raise ValueError(f"write_article: missing required H2 headings: {missing}")

    return {"current_node": "write_article", "article_markdown": md}
