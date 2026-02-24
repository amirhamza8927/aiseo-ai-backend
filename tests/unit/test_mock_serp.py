"""Tests for MockSerpProvider – determinism, validity, and edge cases."""

from __future__ import annotations

import pytest

from src.domain.models.serp import SerpResult
from src.infrastructure.providers.serp.mock_serp import MockSerpProvider


@pytest.fixture()
def provider() -> MockSerpProvider:
    return MockSerpProvider()


class TestDeterminism:
    def test_same_topic_returns_identical_results(
        self, provider: MockSerpProvider
    ) -> None:
        first = provider.fetch_top_results(topic="project management tools")
        second = provider.fetch_top_results(topic="project management tools")
        assert first == second

    def test_different_topics_produce_different_results(
        self, provider: MockSerpProvider
    ) -> None:
        a = provider.fetch_top_results(topic="project management tools")
        b = provider.fetch_top_results(topic="email marketing platforms")
        a_urls = {str(r.url) for r in a}
        b_urls = {str(r.url) for r in b}
        assert a_urls != b_urls

    def test_language_affects_seed(self, provider: MockSerpProvider) -> None:
        en = provider.fetch_top_results(topic="crm software", language="en")
        de = provider.fetch_top_results(topic="crm software", language="de")
        assert en != de


class TestResultCount:
    def test_default_returns_10_results(
        self, provider: MockSerpProvider
    ) -> None:
        results = provider.fetch_top_results(topic="seo tools")
        assert len(results) == 10

    def test_k_is_clamped_to_10(self, provider: MockSerpProvider) -> None:
        results = provider.fetch_top_results(topic="seo tools", k=5)
        assert len(results) == 10


class TestResultValidity:
    def test_ranks_are_sequential(self, provider: MockSerpProvider) -> None:
        results = provider.fetch_top_results(topic="accounting software")
        ranks = [r.rank for r in results]
        assert ranks == list(range(1, 11))

    def test_urls_are_unique(self, provider: MockSerpProvider) -> None:
        results = provider.fetch_top_results(topic="time tracking apps")
        urls = [str(r.url) for r in results]
        assert len(urls) == len(set(urls))

    def test_pydantic_validation(self, provider: MockSerpProvider) -> None:
        results = provider.fetch_top_results(topic="payroll software")
        for r in results:
            validated = SerpResult.model_validate(r.model_dump())
            assert validated == r
