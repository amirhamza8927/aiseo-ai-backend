"""Tests for fail_job node – marks job as failed when revisions exhausted."""

from __future__ import annotations

import pytest

from src.application.orchestration.nodes.deps import NodeDeps
from src.application.orchestration.nodes.fail_job import fail_job
from src.application.orchestration.state import GraphState
from src.domain.models.validation import ValidationReport
from src.domain.models.job import JobStatus
from src.infrastructure.providers.serp.mock_serp import MockSerpProvider
from src.infrastructure.stores.in_memory_job_store import InMemoryJobStore


def _make_state(
    *,
    job_id: str = "j1",
    validation_report: ValidationReport | None = None,
    last_error: str | None = None,
) -> GraphState:
    return GraphState.new(
        job_id=job_id,
        topic="test topic",
        target_word_count=500,
        language="en",
        max_revisions=0,
    ).model_copy(
        update={
            "validation_report": validation_report,
            "last_error": last_error,
        }
    )


def test_fail_job_stores_error_and_sets_failed() -> None:
    job_store = InMemoryJobStore()
    job_store.create("j1")
    report = ValidationReport(
        passed=False,
        score=0.5,
        issues=["Primary keyword missing", "Word count too low"],
        checks={},
    )
    state = _make_state(validation_report=report)
    deps = NodeDeps(serp=MockSerpProvider(), job_store=job_store)

    patch = fail_job(state, deps)

    record = job_store.get("j1")
    assert record.status == JobStatus.FAILED
    assert record.error is not None
    assert "Validation failed after revisions exhausted" in record.error
    assert "Primary keyword missing" in record.error
    assert "Word count too low" in record.error
    assert patch["current_node"] == "fail_job"


def test_fail_job_includes_last_error() -> None:
    job_store = InMemoryJobStore()
    job_store.create("j1")
    report = ValidationReport(passed=False, score=0.0, issues=[], checks={})
    state = _make_state(validation_report=report, last_error="LLM timeout")
    deps = NodeDeps(serp=MockSerpProvider(), job_store=job_store)

    fail_job(state, deps)

    record = job_store.get("j1")
    assert "last_error: LLM timeout" in record.error


def test_fail_job_caps_issues_at_five() -> None:
    job_store = InMemoryJobStore()
    job_store.create("j1")
    report = ValidationReport(
        passed=False,
        score=0.0,
        issues=[f"issue_{i}" for i in range(8)],
        checks={},
    )
    state = _make_state(validation_report=report)
    deps = NodeDeps(serp=MockSerpProvider(), job_store=job_store)

    fail_job(state, deps)

    record = job_store.get("j1")
    assert "issue_0" in record.error
    assert "issue_4" in record.error
    assert "issue_5" not in record.error
    assert "issue_7" not in record.error


def test_fail_job_missing_job_store_raises() -> None:
    state = _make_state()
    deps = NodeDeps(serp=MockSerpProvider(), job_store=None)

    with pytest.raises(ValueError, match="fail_job: deps.job_store is required"):
        fail_job(state, deps)


def test_fail_job_missing_or_empty_job_id_raises() -> None:
    job_store = InMemoryJobStore()
    job_store.create("j1")
    state = _make_state().model_copy(update={"job_id": ""})
    deps = NodeDeps(serp=MockSerpProvider(), job_store=job_store)

    with pytest.raises(ValueError, match="fail_job: state.job_id is required"):
        fail_job(state, deps)
