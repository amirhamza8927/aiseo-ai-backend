"""Tests for repair_spec_builder: mapping, dedup, and empty-report edge case."""

from src.application.services.repair_spec_builder import build_repair_spec
from src.domain.models.outline import Outline, OutlineSection
from src.domain.models.validation import ValidationReport


def _outline() -> Outline:
    return Outline(
        h1="Guide",
        sections=[
            OutlineSection(section_id="s1", h2="Section A"),
            OutlineSection(section_id="s2", h2="Section B"),
        ],
    )


def test_two_failed_checks():
    report = ValidationReport(
        passed=False,
        score=0.5,
        issues=[
            "Primary keyword 'kw' missing from title_tag",
            "Meta description length 50 outside [140, 160]",
        ],
        checks={
            "primary_in_title_tag": False,
            "meta_description_length_valid": False,
            "heading_hierarchy_valid": True,
        },
    )
    spec = build_repair_spec(
        report=report, outline=_outline(), primary_keyword="kw",
    )
    assert len(spec.issues) == 2
    codes = {issue.code for issue in spec.issues}
    assert "PRIMARY_MISSING_TITLE" in codes
    assert "META_DESCRIPTION_LENGTH" in codes


def test_primary_keyword_interpolated_in_repair_instructions():
    report = ValidationReport(
        passed=False,
        score=0.0,
        issues=[],
        checks={
            "primary_in_title_tag": False,
            "primary_in_intro": False,
        },
    )
    spec = build_repair_spec(
        report=report, outline=_outline(), primary_keyword="project management",
    )
    actions = [i.required_action for i in spec.issues]
    assert any("project management" in a for a in actions)
    assert "Include 'project management' in title_tag exactly once." in actions
    assert "Rewrite intro paragraph to include 'project management' naturally." in actions


def test_must_edit_section_ids_deduped():
    report = ValidationReport(
        passed=False,
        score=0.0,
        issues=["a", "b"],
        checks={
            "primary_in_title_tag": False,
            "internal_links_count_valid": False,
        },
    )
    spec = build_repair_spec(
        report=report, outline=_outline(), primary_keyword="kw",
    )
    assert spec.must_edit_section_ids == sorted(set(spec.must_edit_section_ids))
    assert "__seo_meta__" in spec.must_edit_section_ids


def test_required_action_non_empty():
    report = ValidationReport(
        passed=False,
        score=0.0,
        issues=["x"],
        checks={"word_count_within_tolerance": False},
    )
    spec = build_repair_spec(
        report=report, outline=_outline(), primary_keyword="kw",
    )
    for issue in spec.issues:
        assert len(issue.required_action) > 0


def test_all_passed_returns_empty_spec():
    report = ValidationReport(
        passed=True,
        score=1.0,
        issues=[],
        checks={
            "primary_in_title_tag": True,
            "heading_hierarchy_valid": True,
        },
    )
    spec = build_repair_spec(
        report=report, outline=_outline(), primary_keyword="kw",
    )
    assert spec.issues == []
    assert spec.instructions == []
    assert spec.must_edit_section_ids == []
