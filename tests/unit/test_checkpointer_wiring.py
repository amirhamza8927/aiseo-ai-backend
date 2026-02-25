"""Tests for checkpointer wiring helpers."""

from __future__ import annotations

from langgraph.checkpoint.memory import InMemorySaver

from src.application.orchestration.checkpointer import (
    make_checkpointer,
    thread_config,
)
from src.infrastructure.stores.in_memory_job_store import InMemoryJobStore


def test_thread_config_shape() -> None:
    cfg = thread_config("job-123")
    assert cfg == {"configurable": {"thread_id": "job-123"}}


def test_make_checkpointer_returns_same_saver() -> None:
    saver = InMemorySaver()
    assert make_checkpointer(saver=saver) is saver


def test_integration_with_job_store() -> None:
    job_store = InMemoryJobStore()
    checkpointer = make_checkpointer(saver=job_store.saver)
    assert checkpointer is job_store.saver
