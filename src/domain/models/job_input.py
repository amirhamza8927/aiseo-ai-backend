"""Job input – user-provided parameters for a pipeline run."""

from __future__ import annotations

from pydantic import BaseModel, Field


class JobInput(BaseModel):
    """User-provided inputs that kick off a pipeline run."""

    topic: str = Field(min_length=1)
    target_word_count: int = Field(gt=0)
    language: str = Field(min_length=1)
