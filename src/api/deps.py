"""API dependency injection – only module that imports infrastructure."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

from src.application.orchestration.graph_builder import build_graph
from src.application.orchestration.nodes.deps import NodeDeps
from src.application.orchestration.nodes.prompt_loader import PromptLoader
from src.infrastructure.providers.llm.openai_provider import OpenAIProvider
from src.infrastructure.providers.serp.serp_provider_factory import (
    SerpProviderProtocol,
    get_serp_provider as _get_serp_provider,
)
from src.infrastructure.stores.in_memory_job_store import InMemoryJobStore
from src.settings import Settings, get_settings as _get_settings


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""
    return _get_settings()


@lru_cache(maxsize=1)
def get_job_store() -> InMemoryJobStore:
    """Return singleton job store. Same instance used by graph checkpointer."""
    return InMemoryJobStore()


@lru_cache(maxsize=1)
def get_serp_provider() -> SerpProviderProtocol:
    """Return SERP provider based on settings."""
    return _get_serp_provider(get_settings())


@lru_cache(maxsize=1)
def get_llm_provider() -> OpenAIProvider | None:
    """Return LLM provider. None in dev when OPENAI_API_KEY is not set."""
    settings = get_settings()
    if settings.APP_ENV == "dev" and not settings.OPENAI_API_KEY:
        return None
    return OpenAIProvider(settings=settings)


@lru_cache(maxsize=1)
def get_prompt_loader() -> PromptLoader:
    """Return prompt loader with base_dir pointing to orchestration prompts."""
    base_dir = Path(__file__).resolve().parent.parent / "application" / "orchestration" / "prompts"
    return PromptLoader(base_dir=base_dir)


def get_node_deps() -> NodeDeps:
    """Build NodeDeps for graph nodes."""
    return NodeDeps(
        serp=get_serp_provider(),
        llm=get_llm_provider(),
        job_store=get_job_store(),
        settings=get_settings(),
        prompts=get_prompt_loader(),
    )


@lru_cache(maxsize=1)
def get_graph() -> Any:
    """Return compiled LangGraph. Uses shared job_store.saver for checkpointer."""
    return build_graph(deps=get_node_deps())
