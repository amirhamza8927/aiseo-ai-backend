"""SERP result models."""

from __future__ import annotations

from pydantic import BaseModel, Field, HttpUrl


class SerpResult(BaseModel):
    """A single search-engine result page entry."""

    rank: int = Field(ge=1)
    url: HttpUrl
    title: str = Field(min_length=1)
    snippet: str = Field(min_length=1)


SerpResults = list[SerpResult]
