"""planner node – produce a strict Plan via LLM structured output."""

from __future__ import annotations

from src.application.orchestration.state import GraphState
from .deps import NodeDeps
from .prompt_loader import render_prompt
from src.domain.models.plan import Plan


def planner(state: GraphState, deps: NodeDeps) -> dict:
    """Produce a Plan from themes and input constraints. Returns a patch dict."""
    if deps.llm is None:
        raise ValueError("planner: deps.llm is required")
    if deps.prompts is None:
        raise ValueError("planner: deps.prompts is required")
    if state.input is None:
        raise ValueError("planner: state.input is required")
    if not state.input.topic or not state.input.topic.strip():
        raise ValueError("planner: state.input.topic must be non-empty")
    if not state.input.language or not state.input.language.strip():
        raise ValueError("planner: state.input.language must be non-empty")
    if state.input.target_word_count <= 0:
        raise ValueError("planner: state.input.target_word_count must be > 0")
    if not state.serp_results:
        raise ValueError("planner: serp_results is required")
    if state.themes is None:
        raise ValueError("planner: themes is required")

    themes_data = state.themes.model_dump(mode="json")
    serp_data = [r.model_dump(mode="json") for r in state.serp_results]
    template = deps.prompts.get("planner")
    prompt = render_prompt(
        template,
        topic=state.input.topic,
        language=state.input.language,
        target_word_count=state.input.target_word_count,
        themes=themes_data,
        serp_results=serp_data,
    )

    plan = deps.llm.generate_structured(
        node_name="planner",
        prompt=prompt,
        schema=Plan,
    )

    total_budget = plan.intro_target_word_count + sum(
        s.target_word_count for s in plan.sections
    )
    target = state.input.target_word_count
    if total_budget < target * 0.75 or total_budget > target * 1.25:
        raise ValueError(
            f"planner: budgets {total_budget} outside 0.75x–1.25x of target {target}"
        )

    return {"current_node": "planner", "plan": plan}
