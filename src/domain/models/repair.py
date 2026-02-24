"""Repair specification models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RepairIssue(BaseModel):
    """A single issue that the reviser must fix."""

    code: str = Field(min_length=1)
    message: str = Field(min_length=1)
    target_section_ids: list[str] = Field(default_factory=list)
    required_action: str = Field(min_length=1)


class RepairSpec(BaseModel):
    """Instructions for the revise_targeted node."""

    issues: list[RepairIssue] = Field(default_factory=list)
    instructions: list[str] = Field(default_factory=list)
    must_edit_section_ids: list[str] = Field(default_factory=list)
    max_changes: int | None = None
