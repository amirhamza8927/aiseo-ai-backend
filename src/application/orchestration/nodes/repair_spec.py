"""repair_spec node – convert ValidationReport to RepairSpec (deterministic)."""

from __future__ import annotations

from src.application.orchestration.state import GraphState
from src.application.services.repair_spec_builder import build_repair_spec
from src.domain.models.repair import RepairSpec

from .deps import NodeDeps


def repair_spec(state: GraphState, deps: NodeDeps) -> dict:
    """Convert validation report to repair spec. Returns a patch dict."""
    if state.validation_report is None:
        raise ValueError("repair_spec: validation_report is required")
    if state.outline is None:
        raise ValueError("repair_spec: outline is required")
    if state.keyword_plan is None:
        raise ValueError("repair_spec: keyword_plan is required")
    if state.plan is None:
        raise ValueError("repair_spec: plan is required")

    if state.validation_report.passed:
        return {
            "current_node": "repair_spec",
            "repair_spec": RepairSpec(issues=[], instructions=[], must_edit_section_ids=[]),
        }

    spec = build_repair_spec(
        report=state.validation_report,
        outline=state.outline,
        primary_keyword=state.keyword_plan.primary,
    )
    return {"current_node": "repair_spec", "repair_spec": spec}
