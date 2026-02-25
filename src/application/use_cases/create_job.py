"""Create job use case – create pending job and initial GraphState."""

from __future__ import annotations

import uuid

from src.application.orchestration.state import GraphState
from src.domain.models.job import JobRecord
from src.domain.models.job_input import JobInput
from src.infrastructure.stores.in_memory_job_store import InMemoryJobStore
from src.settings import Settings


def create_job(
    *,
    topic: str,
    language: str,
    target_word_count: int,
    job_store: InMemoryJobStore,
    settings: Settings,
) -> tuple[JobRecord, GraphState]:
    """Create a pending job and initial graph state. Does not run the graph."""
    if not topic or not topic.strip():
        raise ValueError("create_job: topic must be non-empty")
    if not language or not language.strip():
        raise ValueError("create_job: language must be non-empty")
    if target_word_count <= 0:
        raise ValueError("create_job: target_word_count must be > 0")

    job_id = str(uuid.uuid4())
    job_input = JobInput(
        topic=topic.strip(),
        target_word_count=target_word_count,
        language=language.strip(),
    )
    record = job_store.create(job_id)
    record = job_store.set_input(job_id, job_input)
    state = GraphState.new(
        job_id=job_id,
        topic=job_input.topic,
        target_word_count=job_input.target_word_count,
        language=job_input.language,
        max_revisions=settings.MAX_REVISIONS,
    )
    return (record, state)
