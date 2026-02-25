"""Integration test: graph completes after revision loop fixes validation."""

from __future__ import annotations

from src.application.orchestration.checkpointer import thread_config
from src.application.use_cases import create_job, get_job
from src.domain.models.job import JobStatus


def test_graph_revision_loop(
    job_store,
    settings,
    fake_llm_revision_loop,
    prompts_base_dir,
    serp_provider,
) -> None:
    """First write_article fails validation (no primary in intro); reviser fixes; graph completes."""
    from src.application.orchestration.graph_builder import build_graph
    from src.application.orchestration.nodes.deps import NodeDeps
    from src.application.orchestration.nodes.prompt_loader import PromptLoader

    prompts = PromptLoader(base_dir=prompts_base_dir)
    deps = NodeDeps(
        serp=serp_provider,
        llm=fake_llm_revision_loop,
        job_store=job_store,
        settings=settings,
        prompts=prompts,
    )
    graph = build_graph(deps=deps)

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
