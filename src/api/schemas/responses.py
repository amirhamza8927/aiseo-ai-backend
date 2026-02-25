"""API response schemas."""

from __future__ import annotations

from pydantic import BaseModel

from src.domain.models.job import JobRecord
from src.domain.models.output import SeoArticleOutput


def job_response_from_record(record: JobRecord) -> "JobResponse":
    """Build JobResponse from JobRecord."""
    return JobResponse(
        id=record.id,
        status=record.status.value,
        current_node=record.current_node,
        error=record.error,
    )


class JobResponse(BaseModel):
    """Job status response."""

    id: str
    status: str
    current_node: str | None = None
    error: str | None = None


class CreateJobResponse(BaseModel):
    """Response for job creation."""

    job: JobResponse


class ResultResponse(BaseModel):
    """Response with completed article result."""

    result: SeoArticleOutput


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "ok"
