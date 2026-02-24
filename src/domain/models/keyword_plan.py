"""Keyword plan model."""

from __future__ import annotations

from pydantic import BaseModel, Field


class KeywordPlan(BaseModel):
    """Target keywords and optional per-keyword usage targets."""

    primary: str = Field(min_length=1)
    secondary: list[str] = Field(default_factory=list)
    usage_targets: dict[str, int] = Field(default_factory=dict)
