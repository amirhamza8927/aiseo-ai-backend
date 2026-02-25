"""Integration test: graph completes successfully with FakeLLM."""

from __future__ import annotations

from src.application.orchestration.checkpointer import thread_config
from src.application.use_cases import create_job, get_job, get_result
from src.domain.models.job import JobStatus


def test_graph_happy_path(
    graph,
    job_store,
    settings,
) -> None:
    """Graph runs to completion; job is COMPLETED with valid result."""
    record, state = create_job(
        topic="seo tools",
        target_word_count=500,
        language="en",
        job_store=job_store,
        settings=settings,
    )
    job_id = record.id

    graph.invoke(state, config=thread_config(job_id))

    record = get_job(job_id=job_id, job_store=job_store)
    assert record.status == JobStatus.COMPLETED, record.error or "expected completed"
    assert record.result is not None
    assert record.result.validation_report is not None
    assert record.result.validation_report.passed is True
    assert record.result.article_markdown
    assert record.result.seo_meta
