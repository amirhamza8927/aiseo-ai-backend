"""Article outline models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class OutlineSection(BaseModel):
    """One section of the outline, keyed by section_id for plan mapping."""

    section_id: str = Field(min_length=1)
    h2: str = Field(min_length=1)
    h3: list[str] = Field(default_factory=list)


class Outline(BaseModel):
    """Full article outline derived from the plan."""

    h1: str = Field(min_length=1)
    intro_h2: str | None = None
    sections: list[OutlineSection] = Field(default_factory=list)
