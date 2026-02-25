"""Integration test: graph fails when validation never passes and revisions exhausted."""

from __future__ import annotations

from src.application.orchestration.checkpointer import thread_config
from src.application.use_cases import create_job, get_job
from src.domain.models.job import JobStatus


def test_graph_fail_when_revisions_exhausted(
    job_store,
    settings,
    fake_llm_fail,
    prompts_base_dir,
    serp_provider,
) -> None:
    """FakeLLM always returns failing validation; reviser does not fix; job fails."""
    from src.application.orchestration.graph_builder import build_graph
    from src.application.orchestration.nodes.deps import NodeDeps
    from src.application.orchestration.nodes.prompt_loader import PromptLoader

    prompts = PromptLoader(base_dir=prompts_base_dir)
    deps = NodeDeps(
        serp=serp_provider,
        llm=fake_llm_fail,
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
    assert record.status == JobStatus.FAILED
    assert record.error is not None
    assert "Validation failed after revisions exhausted" in record.error
