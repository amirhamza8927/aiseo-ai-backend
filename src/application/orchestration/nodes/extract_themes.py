"""extract_themes node – distill Themes from SERP results via LLM."""

from __future__ import annotations

from src.application.orchestration.state import GraphState
from .deps import NodeDeps
from .prompt_loader import render_prompt
from src.domain.models.themes import Themes


def extract_themes(state: GraphState, deps: NodeDeps) -> dict:
    """Extract themes from SERP results using the LLM. Returns a patch dict."""
    if deps.llm is None:
        raise ValueError("extract_themes: deps.llm is required")
    if deps.prompts is None:
        raise ValueError("extract_themes: deps.prompts is required")
    if not state.serp_results:
        raise ValueError("extract_themes: serp_results is required")
    if state.input is None:
        raise ValueError("extract_themes: state.input is required")

    topic = state.input.topic
    language = state.input.language
    serp_data = [r.model_dump(mode="json") for r in state.serp_results]

    template = deps.prompts.get("themes")
    prompt = render_prompt(
        template,
        topic=topic,
        language=language,
        serp_results=serp_data,
    )

    themes = deps.llm.generate_structured(
        node_name="extract_themes",
        prompt=prompt,
        schema=Themes,
    )

    return {"current_node": "extract_themes", "themes": themes}
