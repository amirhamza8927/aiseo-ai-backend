"""E2E test fixtures – override app dependencies with fakes."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.api.deps import get_graph, get_job_store, get_settings
from src.application.orchestration.graph_builder import build_graph
from src.application.orchestration.nodes.deps import NodeDeps
from src.application.orchestration.nodes.prompt_loader import PromptLoader
from src.infrastructure.providers.serp.mock_serp import MockSerpProvider
from src.infrastructure.stores.in_memory_job_store import InMemoryJobStore
from src.main import app
from src.settings import Settings

from tests.integration.fakes import FakeLLMProvider


@pytest.fixture
def e2e_job_store() -> InMemoryJobStore:
    """Fresh job store for each e2e test."""
    return InMemoryJobStore()


@pytest.fixture
def e2e_settings() -> Settings:
    """Test settings for e2e."""
    return Settings(
        MAX_REVISIONS=1,
        DEFAULT_WORD_COUNT=500,
        DEFAULT_LANGUAGE="en",
        SERP_PROVIDER="mock",
        APP_ENV="dev",
    )


@pytest.fixture
def e2e_client(e2e_job_store: InMemoryJobStore, e2e_settings: Settings):
    """TestClient with overridden deps (FakeLLM, MockSerp, no network)."""
    from fastapi.testclient import TestClient

    prompts_dir = Path(__file__).resolve().parent.parent.parent / "src" / "application" / "orchestration" / "prompts"
    prompt_loader = PromptLoader(base_dir=prompts_dir)
    fake_llm = FakeLLMProvider(topic="seo tools", pass_validation=True, mode="pass")
    serp = MockSerpProvider()

    def _get_settings():
        return e2e_settings

    def _get_job_store():
        return e2e_job_store

    def _get_graph():
        deps = NodeDeps(
            serp=serp,
            llm=fake_llm,
            job_store=e2e_job_store,
            settings=e2e_settings,
            prompts=prompt_loader,
        )
        return build_graph(deps=deps)

    app.dependency_overrides[get_settings] = _get_settings
    app.dependency_overrides[get_job_store] = _get_job_store
    app.dependency_overrides[get_graph] = _get_graph

    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
