"""Keyword plan model."""

from __future__ import annotations

from pydantic import BaseModel, Field


class UsageTargetItem(BaseModel):
    """Per-keyword usage target (OpenAI structured output does not support dict[str,int])."""

    keyword: str = Field(min_length=1)
    count: int = Field(gt=0)


class KeywordPlan(BaseModel):
    """Target keywords and optional per-keyword usage targets."""

    primary: str = Field(min_length=1)
    secondary: list[str] = Field(default_factory=list)
    usage_targets: list[UsageTargetItem] = Field(default_factory=list)
