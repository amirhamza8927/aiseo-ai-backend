"""Shared pytest fixtures for unit, integration, and e2e tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.application.orchestration.graph_builder import build_graph
from src.application.orchestration.nodes.deps import NodeDeps
from src.application.orchestration.nodes.prompt_loader import PromptLoader
from src.infrastructure.providers.serp.mock_serp import MockSerpProvider
from src.infrastructure.stores.in_memory_job_store import InMemoryJobStore
from src.settings import Settings

from tests.integration.fakes import FakeLLMProvider


@pytest.fixture
def settings() -> Settings:
    """Test settings: minimal revisions, mock SERP, no external calls."""
    return Settings(
        MAX_REVISIONS=1,
        DEFAULT_WORD_COUNT=500,
        DEFAULT_LANGUAGE="en",
        SERP_PROVIDER="mock",
        APP_ENV="dev",
    )


@pytest.fixture
def job_store() -> InMemoryJobStore:
    """Fresh in-memory job store per test."""
    return InMemoryJobStore()


@pytest.fixture
def fake_llm_pass() -> FakeLLMProvider:
    """Fake LLM that returns validation-passing outputs."""
    return FakeLLMProvider(topic="seo tools", pass_validation=True, mode="pass")


@pytest.fixture
def fake_llm_revision_loop() -> FakeLLMProvider:
    """Fake LLM: first write_article fails validation, first reviser fixes it."""
    return FakeLLMProvider(topic="seo tools", pass_validation=False, mode="revision_loop")


@pytest.fixture
def fake_llm_fail() -> FakeLLMProvider:
    """Fake LLM that always returns validation-failing outputs."""
    return FakeLLMProvider(topic="seo tools", pass_validation=False, mode="fail")


@pytest.fixture
def serp_provider() -> MockSerpProvider:
    """Deterministic mock SERP provider."""
    return MockSerpProvider()


@pytest.fixture
def prompts_base_dir() -> Path:
    """Base directory for orchestration prompts."""
    return Path(__file__).resolve().parent.parent / "src" / "application" / "orchestration" / "prompts"


@pytest.fixture
def prompt_loader(prompts_base_dir: Path) -> PromptLoader:
    """Prompt loader with test prompts directory."""
    return PromptLoader(base_dir=prompts_base_dir)


@pytest.fixture
def node_deps(
    settings: Settings,
    job_store: InMemoryJobStore,
    fake_llm_pass: FakeLLMProvider,
    serp_provider: MockSerpProvider,
    prompt_loader: PromptLoader,
) -> NodeDeps:
    """Node dependencies for graph execution."""
    return NodeDeps(
        serp=serp_provider,
        llm=fake_llm_pass,
        job_store=job_store,
        settings=settings,
        prompts=prompt_loader,
    )


@pytest.fixture
def graph(node_deps: NodeDeps):
    """Compiled LangGraph for integration tests."""
    return build_graph(deps=node_deps)
