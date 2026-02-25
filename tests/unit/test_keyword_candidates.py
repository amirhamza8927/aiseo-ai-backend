"""Tests for keyword_candidates – deterministic extraction from SERP."""

from __future__ import annotations

import pytest

from src.application.services.keyword_candidates import extract_secondary_candidates
from src.domain.models.serp import SerpResult


def _serp(title: str, snippet: str, rank: int = 1) -> SerpResult:
    return SerpResult(
        rank=rank,
        url=f"https://example.com/{rank}",
        title=title,
        snippet=snippet,
    )


def test_extraction_excludes_primary() -> None:
    serp = [
        _serp("Project Management Tools", "Project management tools for teams.", 1),
        _serp("Task Tracking Software", "Task tracking and project management.", 2),
    ]
    result = extract_secondary_candidates(serp, primary="project management tools")

    assert "project management tools" not in [r.lower() for r in result]
    assert "Project Management Tools" not in result


def test_deterministic_output() -> None:
    serp = [
        _serp("Project Management Tools", "Project management tools for teams.", 1),
        _serp("Task Tracking Software", "Task tracking and project management.", 2),
        _serp("Team Collaboration", "Team collaboration and task tracking.", 3),
    ]
    r1 = extract_secondary_candidates(serp, primary="project management tools")
    r2 = extract_secondary_candidates(serp, primary="project management tools")

    assert r1 == r2


def test_returns_at_most_max_candidates() -> None:
    serp = [
        _serp("Project Management Tools", "Project management tools for teams.", 1),
        _serp("Task Tracking Software", "Task tracking and project management.", 2),
    ]
    result = extract_secondary_candidates(serp, primary="project management tools", max_candidates=5)

    assert len(result) <= 5


def test_phrase_length_filter() -> None:
    serp = [
        _serp("Project Management Tools", "Project management tools for teams.", 1),
        _serp("Task Tracking Software", "Task tracking and project management.", 2),
    ]
    result = extract_secondary_candidates(serp, primary="project management tools")

    for phrase in result:
        assert 4 <= len(phrase) <= 60, f"phrase {phrase!r} length {len(phrase)}"


def test_no_numbers_only() -> None:
    serp = [
        _serp("Project Management Tools", "Project management tools for teams.", 1),
        _serp("Task Tracking 2024", "Task tracking and 2024 updates.", 2),
    ]
    result = extract_secondary_candidates(serp, primary="project management tools")

    for phrase in result:
        assert not phrase.replace(" ", "").isdigit(), f"phrase {phrase!r} is digits only"


def test_extraction_with_repeated_phrases() -> None:
    """Repeated phrases should rank higher in output."""
    serp = [
        _serp("Task Tracking Software", "Task tracking for teams.", 1),
        _serp("Task Tracking Guide", "Task tracking best practices.", 2),
        _serp("Team Collaboration", "Team collaboration and task tracking.", 3),
    ]
    result = extract_secondary_candidates(serp, primary="project management tools")

    assert len(result) > 0
    assert "task tracking" in [r.lower() for r in result]
    assert "team collaboration" in [r.lower() for r in result]
