"""Checkpointer wiring – helpers that bind LangGraph persistence to job IDs."""

from __future__ import annotations

from langgraph.checkpoint.memory import InMemorySaver


def thread_config(job_id: str) -> dict:
    """Return a LangGraph config dict enforcing ``thread_id == job_id``."""
    return {"configurable": {"thread_id": job_id}}


def make_checkpointer(*, saver: InMemorySaver) -> InMemorySaver:
    """Return the shared *saver* instance for graph compilation.

    This thin wiring point exists so the caller (e.g. a runner service)
    can inject the ``InMemorySaver`` owned by ``InMemoryJobStore`` without
    the graph module knowing where the saver came from.
    """
    return saver
