"""build_outline node – generate Outline via LLM, hard-match Plan section IDs."""

from __future__ import annotations

from src.application.orchestration.state import GraphState
from .deps import NodeDeps
from .prompt_loader import render_prompt
from src.domain.models.outline import Outline


def build_outline(state: GraphState, deps: NodeDeps) -> dict:
    """Generate Outline from plan. Returns a patch dict. Hard-fails if section IDs mismatch."""
    if deps.llm is None:
        raise ValueError("build_outline: deps.llm is required")
    if deps.prompts is None:
        raise ValueError("build_outline: deps.prompts is required")
    if state.input is None:
        raise ValueError("build_outline: state.input is required")
    if state.plan is None:
        raise ValueError("build_outline: state.plan is required")

    plan_data = state.plan.model_dump(mode="json")
    themes_data = state.themes.model_dump(mode="json") if state.themes else None
    template = deps.prompts.get("outline")
    prompt = render_prompt(
        template,
        topic=state.input.topic,
        language=state.input.language,
        plan=plan_data,
        themes=themes_data,
    )

    outline = deps.llm.generate_structured(
        node_name="build_outline",
        prompt=prompt,
        schema=Outline,
    )

    plan_ids = [s.section_id for s in state.plan.sections]
    outline_ids = [s.section_id for s in outline.sections]
    if len(outline_ids) != len(plan_ids) or outline_ids != plan_ids:
        raise ValueError(
            f"build_outline: outline section IDs must exactly match plan section IDs. "
            f"plan_ids={plan_ids!r}, outline_ids={outline_ids!r}"
        )

    return {"current_node": "build_outline", "outline": outline}
