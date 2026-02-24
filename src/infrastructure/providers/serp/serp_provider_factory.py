"""Factory for selecting the active SERP provider based on settings."""

from __future__ import annotations

from typing import Protocol

from src.domain.models.serp import SerpResult
from src.settings import Settings


class SerpProviderProtocol(Protocol):
    """Structural interface every SERP provider must satisfy."""

    def fetch_top_results(
        self,
        *,
        topic: str,
        language: str | None = None,
        k: int = 10,
    ) -> list[SerpResult]: ...


def get_serp_provider(settings: Settings) -> SerpProviderProtocol:
    """Return the SERP provider indicated by ``settings.SERP_PROVIDER``."""
    if settings.SERP_PROVIDER == "mock":
        from .mock_serp import MockSerpProvider

        return MockSerpProvider()

    raise ValueError(f"Unsupported SERP provider: {settings.SERP_PROVIDER!r}")
