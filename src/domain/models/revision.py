"""Revision result model – LLM output for targeted article edits."""

from __future__ import annotations

from pydantic import BaseModel, Field

from src.domain.models.seo_package import SeoPackage


class RevisionResult(BaseModel):
    """Structured output from the revise_targeted LLM call."""

    article_markdown: str = Field(min_length=1)
    seo_package: SeoPackage | None = None
    notes: list[str] = Field(default_factory=list)
