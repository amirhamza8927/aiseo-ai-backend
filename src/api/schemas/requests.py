"""API request schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CreateJobRequest(BaseModel):
    """Request body for creating a job."""

    topic: str = Field(min_length=1)
    target_word_count: int | None = None
    language: str | None = None
    run_immediately: bool = True
