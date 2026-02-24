"""fail_job node – mark job as failed when validation fails and revisions exhausted."""

from __future__ import annotations

from src.application.orchestration.state import GraphState

from .deps import NodeDeps


def fail_job(state: GraphState, deps: NodeDeps) -> dict:
    """Mark job as failed in job_store. Returns patch dict."""
    if deps.job_store is None:
        raise ValueError("fail_job: deps.job_store is required")
    if not state.job_id or not state.job_id.strip():
        raise ValueError("fail_job: state.job_id is required")

    parts = ["Validation failed after revisions exhausted"]
    report = state.validation_report
    if report and report.issues:
        issues_summary = "; ".join(report.issues[:5])
        parts.append(f"; issues: {issues_summary}")
    if state.last_error:
        parts.append(f"; last_error: {state.last_error}")

    error_message = "".join(parts)
    deps.job_store.set_error(state.job_id, error_message)
    return {"current_node": "fail_job"}
