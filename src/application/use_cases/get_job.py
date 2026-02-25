"""Get job use case – retrieve job record by id."""

from __future__ import annotations

from src.domain.models.job import JobRecord
from src.infrastructure.stores.in_memory_job_store import InMemoryJobStore


def get_job(*, job_id: str, job_store: InMemoryJobStore) -> JobRecord:
    """Retrieve job record. Raises KeyError if not found."""
    return job_store.get(job_id)
