"""collect_serp node – fetch top 10 SERP results for the topic."""

from __future__ import annotations

from src.application.orchestration.state import GraphState
from .deps import NodeDeps


def collect_serp(state: GraphState, deps: NodeDeps) -> dict:
    """Fetch top 10 SERP results for the topic. Returns a patch dict."""
    if state.input is None:
        raise ValueError("collect_serp: state.input is required")
    topic = state.input.topic
    if not topic or not topic.strip():
        raise ValueError("collect_serp: state.input.topic must be non-empty")
    language = state.input.language if state.input.language else None

    results = deps.serp.fetch_top_results(topic=topic, language=language, k=10)
    if len(results) != 10:
        raise ValueError(
            f"collect_serp: expected 10 results, got {len(results)}"
        )

    return {
        "current_node": "collect_serp",
        "serp_results": results,
    }
