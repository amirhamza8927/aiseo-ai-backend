"""Tests for graph builder – compiles LangGraph StateGraph."""

from __future__ import annotations

import pytest

from src.application.orchestration.graph_builder import build_graph
from src.application.orchestration.nodes.deps import NodeDeps
from src.infrastructure.providers.serp.mock_serp import MockSerpProvider
from src.infrastructure.stores.in_memory_job_store import InMemoryJobStore


def test_build_graph_compiles() -> None:
    """Graph compiles with valid deps."""
    job_store = InMemoryJobStore()
    deps = NodeDeps(serp=MockSerpProvider(), job_store=job_store)
    compiled = build_graph(deps=deps)
    assert compiled is not None


def test_build_graph_missing_job_store_raises() -> None:
    """Raises when job_store is None."""
    deps = NodeDeps(serp=MockSerpProvider(), job_store=None)
    with pytest.raises(ValueError, match="job_store"):
        build_graph(deps=deps)
