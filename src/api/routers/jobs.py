"""Jobs router – create, run, status, result."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from src.api.deps import get_graph, get_job_store, get_settings
from src.api.schemas.requests import CreateJobRequest
from src.api.schemas.responses import (
    CreateJobResponse,
    JobResponse,
    ResultResponse,
    job_response_from_record,
)
from src.application.orchestration.state import GraphState
from src.application.use_cases import create_job, get_job, get_result, run_job
from src.domain.models.job import JobStatus
from src.infrastructure.stores.in_memory_job_store import InMemoryJobStore
from src.settings import Settings

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=CreateJobResponse)
def create_job_endpoint(
    body: CreateJobRequest,
    job_store: InMemoryJobStore = Depends(get_job_store),
    settings: Settings = Depends(get_settings),
    graph: Any = Depends(get_graph),
) -> CreateJobResponse:
    """Create a job. Optionally run immediately."""
    target_word_count = body.target_word_count if body.target_word_count is not None else settings.DEFAULT_WORD_COUNT
    language = body.language if body.language is not None else settings.DEFAULT_LANGUAGE

    try:
        record, state = create_job(
            topic=body.topic,
            target_word_count=target_word_count,
            language=language,
            job_store=job_store,
            settings=settings,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    if body.run_immediately:
        run_job(state=state, graph=graph, job_store=job_store)
        record = get_job(job_id=record.id, job_store=job_store)

    return CreateJobResponse(job=job_response_from_record(record))


@router.post("/{job_id}/run", response_model=JobResponse)
def run_job_endpoint(
    job_id: str,
    job_store: InMemoryJobStore = Depends(get_job_store),
    settings: Settings = Depends(get_settings),
    graph: Any = Depends(get_graph),
) -> JobResponse:
    """Run a pending job."""
    try:
        record = get_job(job_id=job_id, job_store=job_store)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    if record.status == JobStatus.COMPLETED:
        raise HTTPException(status_code=409, detail="Job already completed")
    if record.status == JobStatus.RUNNING:
        raise HTTPException(status_code=409, detail="Job already running")
    if record.input is None:
        raise HTTPException(status_code=409, detail="Job input missing")

    state = GraphState.new(
        job_id=job_id,
        topic=record.input.topic,
        target_word_count=record.input.target_word_count,
        language=record.input.language,
        max_revisions=settings.MAX_REVISIONS,
    )
    run_job(state=state, graph=graph, job_store=job_store)
    record = get_job(job_id=job_id, job_store=job_store)
    return job_response_from_record(record)


@router.get("/{job_id}", response_model=JobResponse)
def get_job_endpoint(
    job_id: str,
    job_store: InMemoryJobStore = Depends(get_job_store),
) -> JobResponse:
    """Get job status."""
    try:
        record = get_job(job_id=job_id, job_store=job_store)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return job_response_from_record(record)


@router.get("/{job_id}/result", response_model=ResultResponse)
def get_result_endpoint(
    job_id: str,
    job_store: InMemoryJobStore = Depends(get_job_store),
) -> ResultResponse:
    """Get completed job result."""
    try:
        result = get_result(job_id=job_id, job_store=job_store)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return ResultResponse(result=result)
