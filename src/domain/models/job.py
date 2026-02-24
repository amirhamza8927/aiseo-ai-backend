"""Job lifecycle models."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel

from .output import SeoArticleOutput


class JobStatus(str, Enum):
    """Lifecycle states for a pipeline job."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class JobRecord(BaseModel):
    """Tracks a single pipeline execution."""

    id: str
    status: JobStatus
    current_node: str | None = None
    error: str | None = None
    result: SeoArticleOutput | None = None
