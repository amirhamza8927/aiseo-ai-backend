"""Shared dependencies for graph nodes – DI container."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from src.infrastructure.providers.serp.serp_provider_factory import SerpProviderProtocol
from src.settings import Settings

from .prompt_loader import PromptLoader

if TYPE_CHECKING:
    from src.infrastructure.providers.llm.openai_provider import OpenAIProvider
    from src.infrastructure.stores.in_memory_job_store import InMemoryJobStore


@dataclass(frozen=True)
class NodeDeps:
    """Lightweight DI container for node dependencies."""

    serp: SerpProviderProtocol
    llm: OpenAIProvider | None = None
    job_store: InMemoryJobStore | None = None
    settings: Settings | None = None
    prompts: PromptLoader | None = None
