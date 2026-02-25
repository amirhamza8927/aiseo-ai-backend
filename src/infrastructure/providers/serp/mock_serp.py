"""Deterministic, offline mock SERP provider for development and testing."""

from __future__ import annotations

import hashlib
import random
import re

from src.domain.models.serp import SerpResult

# ---------------------------------------------------------------------------
# Curated data pools – sizes must be >= 10 to guarantee unique picks per call
# ---------------------------------------------------------------------------

_DOMAINS: list[str] = [
    "zapier.com",
    "asana.com",
    "notion.so",
    "atlassian.com",
    "microsoft.com",
    "hubspot.com",
    "semrush.com",
    "ahrefs.com",
    "nerdwallet.com",
    "forbes.com",
    "techradar.com",
    "pcmag.com",
    "g2.com",
    "capterra.com",
    "shopify.com",
]

_TITLE_PATTERNS: list[str] = [
    "{n} Best {topic} for {audience} ({year})",
    "{topic}: The Complete Guide ({year})",
    "Top {n} {topic} Compared: Pros, Cons, Pricing",
    "Best {topic} for Small Businesses",
    "Free vs Paid {topic}: What to Choose in {year}",
    "{topic} Review: An Honest Look ({year})",
    "How to Choose the Right {topic} for {audience}",
    "The Ultimate {topic} Buyer's Guide",
    "{n} {topic} You Should Know About in {year}",
    "{topic} for {audience}: A Practical Overview",
    "Why {topic} Matter More Than Ever in {year}",
    "Beginner's Guide to {topic} ({year} Edition)",
    "{topic} vs Alternatives: Which Is Best?",
    "{n} Affordable {topic} for {audience}",
    "What Experts Say About {topic} in {year}",
]

_SNIPPET_PATTERNS: list[str] = [
    "Discover the top {topic} options available today. We compare features, pricing, and user reviews to help you decide.",
    "Looking for the best {topic}? This guide covers everything you need to know before making a decision.",
    "Our experts evaluated dozens of {topic} to find the most reliable choices for {audience}.",
    "Not sure which {topic} to pick? Here is a side-by-side comparison of the leading options in {year}.",
    "This in-depth review of {topic} highlights the strengths and weaknesses of each option.",
    "Find out which {topic} offer the best value for money. Updated for {year}.",
    "Learn how {topic} can streamline your workflow and save time for {audience}.",
    "We tested {n} popular {topic} and ranked them based on ease of use, cost, and support.",
    "Explore our curated list of {topic} trusted by thousands of professionals worldwide.",
    "Stay ahead with the latest {topic} trends and recommendations for {audience} in {year}.",
    "A comprehensive breakdown of {topic} features that matter most to {audience}.",
    "Get expert insights on choosing the right {topic}. Includes real user feedback and benchmarks.",
]

_AUDIENCES: list[str] = [
    "Small Businesses",
    "Remote Teams",
    "Startups",
    "Enterprises",
    "Beginners",
    "Freelancers",
    "Marketing Teams",
]

_CATEGORIES: list[str] = [
    "blog",
    "resources",
    "guides",
    "articles",
    "tools",
    "reviews",
    "comparisons",
]

_YEAR = "2026"


def _slugify(text: str) -> str:
    """Convert *text* to a URL-safe slug (lowercase, hyphens, no specials)."""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _make_seed(topic: str, language: str | None) -> int:
    """Return a stable integer seed derived from *topic* + *language*."""
    key = f"{topic}|{language or ''}"
    digest = hashlib.sha256(key.encode()).digest()
    return int.from_bytes(digest[:8], "big")


class MockSerpProvider:
    """Offline SERP provider that returns deterministic, realistic results.

    Same ``(topic, language)`` pair always produces the identical result list
    across runs and processes (seed via SHA-256, local RNG instance).
    """

    _K = 10  # assessment requirement: always top 10

    def fetch_top_results(
        self,
        *,
        topic: str,
        language: str | None = None,
        k: int = 10,
    ) -> list[SerpResult]:
        """Return exactly 10 deterministic ``SerpResult`` items for *topic*.

        The *k* parameter is accepted for interface compatibility but is
        clamped to 10 to satisfy the assessment requirement.
        """
        k = self._K
        rng = random.Random(_make_seed(topic, language))

        domains = list(_DOMAINS)
        titles = list(_TITLE_PATTERNS)
        snippets = list(_SNIPPET_PATTERNS)
        categories = list(_CATEGORIES)

        rng.shuffle(domains)
        rng.shuffle(titles)
        rng.shuffle(snippets)
        rng.shuffle(categories)

        slug = _slugify(topic)
        results: list[SerpResult] = []

        for i in range(k):
            domain = domains[i]
            category = categories[i % len(categories)]
            audience = rng.choice(_AUDIENCES)
            n = rng.randint(5, 15)

            fmt = {"topic": topic, "audience": audience, "n": n, "year": _YEAR}

            title = titles[i].format(**fmt)
            snippet = snippets[i].format(**fmt)
            url = f"https://{domain}/{category}/{slug}-{i + 1}"

            results.append(
                SerpResult(
                    rank=i + 1,
                    url=url,
                    title=title,
                    snippet=snippet,
                )
            )

        return results
