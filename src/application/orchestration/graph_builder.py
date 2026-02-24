"""Graph builder – builds and compiles the LangGraph StateGraph for the SEO pipeline.

State machine: linear pipeline (collect_serp -> ... -> validate_and_score) -> conditional
(finalize | repair_spec -> revise_targeted -> validate_and_score loop | fail_job).

Durability: shared InMemorySaver from job_store.saver for thread-level checkpoints.

Run: compiled.invoke(initial_state, config=thread_config(job_id)) where thread_id == job_id.
"""

from __future__ import annotations

from typing import Any

from langgraph.graph import END, START, StateGraph

from src.application.orchestration.checkpointer import make_checkpointer
from src.application.orchestration.nodes import (
    build_outline,
    collect_serp,
    extract_themes,
    fail_job,
    finalize,
    keyword_plan,
    planner,
    repair_spec,
    revise_targeted,
    seo_packager,
    validate_and_score,
    write_article,
)
from src.application.orchestration.nodes.deps import NodeDeps
from src.application.orchestration.state import GraphState


def _route_after_validate(state: GraphState) -> str:
    """Route to finalize, repair_spec, or fail_job based on validation result."""
    report = state.validation_report
    if report is None:
        return "fail_job"
    if report.passed:
        return "finalize"
    if state.revisions_left > 0:
        return "repair_spec"
    return "fail_job"


def build_graph(*, deps: NodeDeps) -> Any:
    """Build and compile the LangGraph StateGraph for GraphState."""
    if deps.job_store is None:
        raise ValueError("build_graph: deps.job_store is required")

    graph = StateGraph(GraphState)

    graph.add_node("collect_serp", lambda s: collect_serp(s, deps))
    graph.add_node("extract_themes", lambda s: extract_themes(s, deps))
    graph.add_node("planner", lambda s: planner(s, deps))
    graph.add_node("build_outline", lambda s: build_outline(s, deps))
    graph.add_node("keyword_plan", lambda s: keyword_plan(s, deps))
    graph.add_node("write_article", lambda s: write_article(s, deps))
    graph.add_node("seo_packager", lambda s: seo_packager(s, deps))
    graph.add_node("validate_and_score", lambda s: validate_and_score(s, deps))
    graph.add_node("repair_spec", lambda s: repair_spec(s, deps))
    graph.add_node("revise_targeted", lambda s: revise_targeted(s, deps))
    graph.add_node("finalize", lambda s: finalize(s, deps))
    graph.add_node("fail_job", lambda s: fail_job(s, deps))

    graph.add_edge(START, "collect_serp")
    graph.add_edge("collect_serp", "extract_themes")
    graph.add_edge("extract_themes", "planner")
    graph.add_edge("planner", "build_outline")
    graph.add_edge("build_outline", "keyword_plan")
    graph.add_edge("keyword_plan", "write_article")
    graph.add_edge("write_article", "seo_packager")
    graph.add_edge("seo_packager", "validate_and_score")

    graph.add_conditional_edges(
        "validate_and_score",
        _route_after_validate,
        {"finalize": "finalize", "repair_spec": "repair_spec", "fail_job": "fail_job"},
    )

    graph.add_edge("repair_spec", "revise_targeted")
    graph.add_edge("revise_targeted", "validate_and_score")
    graph.add_edge("finalize", END)
    graph.add_edge("fail_job", END)

    checkpointer = make_checkpointer(saver=deps.job_store.saver)
    return graph.compile(checkpointer=checkpointer)
