"""SERP provider infrastructure – mock provider and factory."""

from __future__ import annotations

from .mock_serp import MockSerpProvider
from .serp_provider_factory import SerpProviderProtocol, get_serp_provider

__all__ = [
    "MockSerpProvider",
    "SerpProviderProtocol",
    "get_serp_provider",
]
