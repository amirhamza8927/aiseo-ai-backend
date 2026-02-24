"""Run job use case – invoke graph with thread_config, handle exceptions."""

from __future__ import annotations

from typing import Any

from src.application.orchestration.checkpointer import thread_config
from src.application.orchestration.state import GraphState
from src.domain.models.job import JobStatus
from src.infrastructure.stores.in_memory_job_store import InMemoryJobStore


def run_job(
    *,
    state: GraphState,
    graph: Any,
    job_store: InMemoryJobStore,
) -> None:
    """Run the graph for the given state. Sets RUNNING, invokes graph, handles exceptions."""
    job_id = state.job_id
    job_store.set_status(job_id, JobStatus.RUNNING, current_node="collect_serp")

    try:
        graph.invoke(state, config=thread_config(job_id))

        record = job_store.get(job_id)
        if record.status == JobStatus.RUNNING:
            job_store.set_error(job_id, "Graph ended without finalize/fail_job updating status")

    except Exception as exc:
        record = job_store.get(job_id)
        if record.status in (JobStatus.COMPLETED, JobStatus.FAILED):
            return
        job_store.set_error(job_id, f"{type(exc).__name__}: {exc}")
