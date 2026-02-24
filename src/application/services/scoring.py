"""Scoring utilities for validation reports.

The deterministic score is the ratio of passed checks.  A future
LLM-based rubric score can be added here but is non-gating for the
validate-and-repair loop.
"""

from __future__ import annotations

from src.domain.models.validation import ValidationReport


def deterministic_score(report: ValidationReport) -> float:
    """Return the deterministic check-pass ratio already on the report."""
    return report.score
