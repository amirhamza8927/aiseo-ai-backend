"""Tests for repair_spec node – deterministic, no LLM."""

from __future__ import annotations

import pytest

from src.application.orchestration.nodes.deps import NodeDeps
from src.application.orchestration.nodes.repair_spec import repair_spec
from src.application.orchestration.state import GraphState
from src.domain.models.keyword_plan import KeywordPlan
from src.domain.models.outline import Outline, OutlineSection
from src.domain.models.plan import Plan, PlanSection
from src.domain.models.repair import RepairSpec
from src.domain.models.validation import ValidationReport
from src.infrastructure.providers.serp.mock_serp import MockSerpProvider


def _make_outline() -> Outline:
    return Outline(
        h1="Guide",
        sections=[
            OutlineSection(section_id="s1", h2="Section A"),
            OutlineSection(section_id="s2", h2="Section B"),
        ],
    )


def _make_plan() -> Plan:
    return Plan(
        h1="Guide",
        intro_target_word_count=100,
        sections=[
            PlanSection(section_id="s1", heading="Section A", key_points=["x"], target_word_count=50),
            PlanSection(section_id="s2", heading="Section B", key_points=["y"], target_word_count=50),
        ],
    )


def _make_keyword_plan() -> KeywordPlan:
    return KeywordPlan(
        primary="project management tools",
        secondary=["task tracking"],
        usage_targets={},
    )


def _make_state(
    *,
    validation_report: ValidationReport,
    outline: Outline | None = None,
    keyword_plan: KeywordPlan | None = None,
    plan: Plan | None = None,
) -> GraphState:
    return GraphState.new(
        job_id="j1",
        topic="project management tools",
        target_word_count=1500,
        language="en",
        max_revisions=2,
    ).model_copy(
        update={
            "validation_report": validation_report,
            "outline": outline or _make_outline(),
            "keyword_plan": keyword_plan or _make_keyword_plan(),
            "plan": plan or _make_plan(),
        }
    )


def test_repair_spec_passed_returns_empty_spec() -> None:
    report = ValidationReport(
        passed=True,
        score=1.0,
        issues=[],
        checks={"primary_in_title_tag": True, "heading_hierarchy_valid": True},
    )
    state = _make_state(validation_report=report)
    deps = NodeDeps(serp=MockSerpProvider())

    patch = repair_spec(state, deps)

    assert patch["current_node"] == "repair_spec"
    assert "repair_spec" in patch
    spec = patch["repair_spec"]
    assert isinstance(spec, RepairSpec)
    assert spec.issues == []
    assert spec.instructions == []
    assert spec.must_edit_section_ids == []


def test_repair_spec_failed_returns_non_empty_spec() -> None:
    report = ValidationReport(
        passed=False,
        score=0.5,
        issues=["Primary keyword missing from title_tag", "Missing from intro"],
        checks={
            "primary_in_title_tag": False,
            "primary_in_intro": False,
            "heading_hierarchy_valid": True,
        },
    )
    state = _make_state(validation_report=report)
    deps = NodeDeps(serp=MockSerpProvider())

    patch = repair_spec(state, deps)

    assert patch["current_node"] == "repair_spec"
    spec = patch["repair_spec"]
    assert len(spec.issues) == 2
    assert len(spec.must_edit_section_ids) > 0
    assert "__seo_meta__" in spec.must_edit_section_ids
    assert "__intro__" in spec.must_edit_section_ids


def test_repair_spec_missing_validation_report_raises() -> None:
    state = _make_state(
        validation_report=ValidationReport(passed=True, score=1.0),
    ).model_copy(update={"validation_report": None})
    deps = NodeDeps(serp=MockSerpProvider())

    with pytest.raises(ValueError, match="repair_spec: validation_report is required"):
        repair_spec(state, deps)


def test_repair_spec_missing_outline_raises() -> None:
    report = ValidationReport(passed=True, score=1.0)
    state = _make_state(validation_report=report).model_copy(update={"outline": None})
    deps = NodeDeps(serp=MockSerpProvider())

    with pytest.raises(ValueError, match="repair_spec: outline is required"):
        repair_spec(state, deps)


def test_repair_spec_missing_keyword_plan_raises() -> None:
    report = ValidationReport(passed=True, score=1.0)
    state = _make_state(validation_report=report).model_copy(update={"keyword_plan": None})
    deps = NodeDeps(serp=MockSerpProvider())

    with pytest.raises(ValueError, match="repair_spec: keyword_plan is required"):
        repair_spec(state, deps)


def test_repair_spec_missing_plan_raises() -> None:
    report = ValidationReport(passed=True, score=1.0)
    state = _make_state(validation_report=report).model_copy(update={"plan": None})
    deps = NodeDeps(serp=MockSerpProvider())

    with pytest.raises(ValueError, match="repair_spec: plan is required"):
        repair_spec(state, deps)
