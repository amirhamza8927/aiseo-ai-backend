"""Validation report model."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ValidationReport(BaseModel):
    """Result of the validate_and_score step."""

    passed: bool
    score: float = Field(default=0.0, ge=0.0, le=1.0)
    issues: list[str] = Field(default_factory=list)
    checks: dict[str, bool] = Field(default_factory=dict)
