"""Theme-extraction models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Themes(BaseModel):
    """Themes distilled from SERP analysis."""

    search_intent: str = Field(min_length=1)
    topic_clusters: list[str] = Field(min_length=1)
    common_sections: list[str] = Field(min_length=1)
    ranking_patterns: list[str] = Field(min_length=1)
    differentiation_angles: list[str] = Field(min_length=1)
