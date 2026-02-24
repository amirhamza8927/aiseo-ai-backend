"""Tests for the SERP provider factory."""

from __future__ import annotations

import pytest

from src.infrastructure.providers.serp.mock_serp import MockSerpProvider
from src.infrastructure.providers.serp.serp_provider_factory import (
    get_serp_provider,
)
from src.settings import Settings


def _make_settings(**overrides: object) -> Settings:
    """Build a Settings instance with safe defaults for testing."""
    defaults = {"APP_ENV": "dev", "OPENAI_API_KEY": None}
    defaults.update(overrides)
    return Settings(**defaults)


def test_mock_provider_returned() -> None:
    settings = _make_settings(SERP_PROVIDER="mock")
    provider = get_serp_provider(settings)
    assert isinstance(provider, MockSerpProvider)


def test_unsupported_provider_raises() -> None:
    settings = _make_settings(SERP_PROVIDER="google")
    with pytest.raises(ValueError, match="Unsupported"):
        get_serp_provider(settings)
