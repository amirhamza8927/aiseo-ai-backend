"""Get result use case – return SeoArticleOutput if job completed."""

from __future__ import annotations

from src.domain.models.job import JobStatus
from src.domain.models.output import SeoArticleOutput
from src.infrastructure.stores.in_memory_job_store import InMemoryJobStore


def get_result(*, job_id: str, job_store: InMemoryJobStore) -> SeoArticleOutput:
    """Return completed job result. Raises KeyError if not found, RuntimeError if not completed."""
    record = job_store.get(job_id)
    if record.status != JobStatus.COMPLETED:
        if record.status == JobStatus.FAILED:
            raise RuntimeError("Job failed")
        raise RuntimeError("Job not completed")
    if record.result is None:
        raise RuntimeError("Job completed but result is missing")
    return record.result
