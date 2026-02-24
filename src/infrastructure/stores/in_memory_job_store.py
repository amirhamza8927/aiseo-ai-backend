"""Job store backed by LangGraph's InMemoryStore (KV) and InMemorySaver (checkpointer)."""

from __future__ import annotations

import threading
from datetime import datetime, timezone

from pydantic import BaseModel

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore

from src.domain.models.job import JobRecord, JobStatus
from src.domain.models.output import SeoArticleOutput


class StoredJobState(BaseModel):
    """Minimal persisted state for job tracking.

    This is NOT the full GraphState -- only the fields needed by the job
    store.  Module 7 will align GraphState with these fields later.
    """

    job_id: str
    status: JobStatus
    current_node: str | None = None
    error: str | None = None
    result: SeoArticleOutput | None = None
    updated_at: datetime


_JOBS_NS: tuple[str, ...] = ("jobs",)


def _to_record(state: StoredJobState) -> JobRecord:
    return JobRecord(
        id=state.job_id,
        status=state.status,
        current_node=state.current_node,
        error=state.error,
        result=state.result,
    )


class InMemoryJobStore:
    """Thread-safe job store using LangGraph built-in persistence.

    Job metadata lives in ``InMemoryStore`` (official KV store).
    ``InMemorySaver`` is held here so Module 7 can share it when
    compiling the graph -- but this class never calls ``put()`` on the
    saver directly.
    """

    def __init__(
        self,
        *,
        store: InMemoryStore | None = None,
        saver: InMemorySaver | None = None,
    ) -> None:
        self._store = store or InMemoryStore()
        self._saver = saver or InMemorySaver()
        self._lock = threading.Lock()

    @property
    def store(self) -> InMemoryStore:
        """The KV store used for job metadata."""
        return self._store

    @property
    def saver(self) -> InMemorySaver:
        """The checkpointer for graph compilation (Module 7+)."""
        return self._saver

    # -- internal helpers ----------------------------------------------------

    def _save(self, state: StoredJobState) -> None:
        self._store.put(_JOBS_NS, state.job_id, state.model_dump(mode="json"))

    def _load(self, job_id: str) -> StoredJobState:
        item = self._store.get(_JOBS_NS, job_id)
        if item is None:
            raise KeyError(f"Job '{job_id}' not found")
        return StoredJobState.model_validate(item.value)

    def _update(self, state: StoredJobState, **fields: object) -> StoredJobState:
        """Return a new validated state with *fields* merged in."""
        return StoredJobState.model_validate(
            state.model_dump() | {"updated_at": datetime.now(timezone.utc)} | fields
        )

    # -- public API ----------------------------------------------------------

    def create(self, job_id: str) -> JobRecord:
        """Create a new job in *pending* state.

        Raises ``ValueError`` if *job_id* already exists (idempotency guard).
        """
        with self._lock:
            if self._store.get(_JOBS_NS, job_id) is not None:
                raise ValueError(f"Job '{job_id}' already exists")
            state = StoredJobState(
                job_id=job_id,
                status=JobStatus.PENDING,
                updated_at=datetime.now(timezone.utc),
            )
            self._save(state)
        return _to_record(state)

    def get(self, job_id: str) -> JobRecord:
        """Retrieve current job record."""
        with self._lock:
            return _to_record(self._load(job_id))

    def set_status(
        self,
        job_id: str,
        status: JobStatus,
        current_node: str | None = None,
    ) -> JobRecord:
        """Update job status and optionally the current node."""
        with self._lock:
            state = self._update(
                self._load(job_id), status=status, current_node=current_node,
            )
            self._save(state)
            return _to_record(state)

    def set_current_node(self, job_id: str, current_node: str) -> JobRecord:
        """Update the node currently being executed."""
        with self._lock:
            state = self._update(self._load(job_id), current_node=current_node)
            self._save(state)
            return _to_record(state)

    def set_error(self, job_id: str, error: str) -> JobRecord:
        """Mark job as failed with an error message."""
        with self._lock:
            state = self._update(
                self._load(job_id), status=JobStatus.FAILED, error=error,
            )
            self._save(state)
            return _to_record(state)

    def set_result(self, job_id: str, result: SeoArticleOutput) -> JobRecord:
        """Mark job as completed with the final output."""
        with self._lock:
            state = self._update(
                self._load(job_id),
                status=JobStatus.COMPLETED,
                result=result,
                error=None,
            )
            self._save(state)
            return _to_record(state)

    def delete(self, job_id: str) -> None:
        """Remove a job entry. No-op if it doesn't exist."""
        with self._lock:
            self._store.delete(_JOBS_NS, job_id)
