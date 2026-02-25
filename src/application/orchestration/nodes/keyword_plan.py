"""keyword_plan node – produce KeywordPlan via deterministic candidates + LLM."""

from __future__ import annotations

from src.application.orchestration.state import GraphState
from .deps import NodeDeps
from src.application.services.keyword_candidates import extract_secondary_candidates
from .prompt_loader import render_prompt
from src.domain.models.keyword_plan import KeywordPlan


def keyword_plan(state: GraphState, deps: NodeDeps) -> dict:
    """Produce KeywordPlan from SERP candidates and themes. Returns a patch dict."""
    if deps.llm is None:
        raise ValueError("keyword_plan: deps.llm is required")
    if deps.prompts is None:
        raise ValueError("keyword_plan: deps.prompts is required")
    if state.input is None:
        raise ValueError("keyword_plan: state.input is required")
    if not state.serp_results:
        raise ValueError("keyword_plan: serp_results is required")
    if state.themes is None:
        raise ValueError("keyword_plan: themes is required")

    primary = state.input.topic
    candidates = extract_secondary_candidates(
        state.serp_results, primary=primary, max_candidates=20
    )
    themes_data = state.themes.model_dump(mode="json")
    template = deps.prompts.get("keyword_plan")
    prompt = render_prompt(
        template,
        topic=state.input.topic,
        language=state.input.language,
        primary=primary,
        candidates=candidates,
        themes=themes_data,
    )

    kp = deps.llm.generate_structured(
        node_name="keyword_plan",
        prompt=prompt,
        schema=KeywordPlan,
    )

    if kp.primary != primary:
        raise ValueError("keyword_plan: LLM returned wrong primary")
    if any(primary.lower() in s.lower() for s in kp.secondary):
        raise ValueError("keyword_plan: primary must not appear in secondary")

    seen: set[str] = set()
    deduped: list[str] = []
    for s in kp.secondary:
        if s.lower() not in seen:
            seen.add(s.lower())
            deduped.append(s)
    kp = kp.model_copy(update={"secondary": deduped})

    return {"current_node": "keyword_plan", "keyword_plan": kp}
