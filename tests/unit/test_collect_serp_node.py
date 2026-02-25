"""Tests for collect_serp node."""

from __future__ import annotations

from src.application.orchestration.nodes.collect_serp import collect_serp
from src.application.orchestration.nodes.deps import NodeDeps
from src.application.orchestration.state import GraphState
from src.infrastructure.providers.serp.mock_serp import MockSerpProvider


def _make_state(**overrides: object) -> GraphState:
    defaults = {
        "job_id": "j1",
        "topic": "project management tools",
        "target_word_count": 1500,
        "language": "en",
        "max_revisions": 2,
    }
    defaults.update(overrides)
    return GraphState.new(**defaults)


def test_collect_serp_returns_patch_with_10_results() -> None:
    state = _make_state()
    deps = NodeDeps(serp=MockSerpProvider())

    patch = collect_serp(state, deps)

    assert patch["current_node"] == "collect_serp"
    assert len(patch["serp_results"]) == 10
    assert [r.rank for r in patch["serp_results"]] == list(range(1, 11))


def test_collect_serp_does_not_mutate_state() -> None:
    state = _make_state()
    deps = NodeDeps(serp=MockSerpProvider())

    collect_serp(state, deps)

    assert state.serp_results is None
    assert state.current_node is None
