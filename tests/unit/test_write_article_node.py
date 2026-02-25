"""Tests for write_article node – no network, fake LLM."""

from __future__ import annotations

import pytest

from src.application.orchestration.nodes.deps import NodeDeps
from src.application.orchestration.nodes.prompt_loader import PromptLoader
from src.application.orchestration.nodes.write_article import write_article
from src.application.orchestration.state import GraphState
from src.domain.models.keyword_plan import KeywordPlan, UsageTargetItem
from src.domain.models.outline import Outline, OutlineSection
from src.domain.models.plan import Plan, PlanSection
from src.infrastructure.providers.serp.mock_serp import MockSerpProvider


def _make_plan() -> Plan:
    return Plan(
        h1="Project Management Tools Guide",
        intro_target_word_count=100,
        sections=[
            PlanSection(
                section_id="s1",
                heading="Introduction",
                purpose="",
                key_points=["Overview"],
                target_word_count=100,
            ),
            PlanSection(
                section_id="s2",
                heading="Key Features",
                purpose="",
                key_points=["Features"],
                target_word_count=200,
            ),
        ],
    )


def _make_outline() -> Outline:
    return Outline(
        h1="Project Management Tools Guide",
        sections=[
            OutlineSection(section_id="s1", h2="Introduction"),
            OutlineSection(section_id="s2", h2="Key Features"),
        ],
    )


def _make_keyword_plan() -> KeywordPlan:
    return KeywordPlan(
        primary="project management tools",
        secondary=["task tracking", "team collaboration"],
        usage_targets=[UsageTargetItem(keyword="project management tools", count=2)],
    )


def _make_state() -> GraphState:
    return GraphState.new(
        job_id="j1",
        topic="project management tools",
        target_word_count=1500,
        language="en",
        max_revisions=2,
    ).model_copy(
        update={
            "plan": _make_plan(),
            "outline": _make_outline(),
            "keyword_plan": _make_keyword_plan(),
        }
    )


class FakeLLM:
    """Fake LLM that returns configurable markdown."""

    def __init__(self, markdown: str) -> None:
        self._markdown = markdown

    def generate_text(self, *, node_name: str, prompt: str) -> str:
        assert node_name == "write_article"
        assert "project management" in prompt
        return self._markdown


def test_write_article_returns_patch() -> None:
    md = """# Project Management Tools Guide

Intro paragraph with project management tools.

## Introduction

Content for intro.

## Key Features

Content for features.
"""
    state = _make_state()
    deps = NodeDeps(
        serp=MockSerpProvider(),
        llm=FakeLLM(md),
        prompts=PromptLoader(),
    )

    patch = write_article(state, deps)

    assert patch["current_node"] == "write_article"
    assert "article_markdown" in patch
    assert patch["article_markdown"].strip() == md.strip()


def test_write_article_missing_h2_raises() -> None:
    md = """# Project Management Tools Guide

Intro paragraph.

## Introduction

Content only for intro. Missing Key Features H2.
"""
    state = _make_state()
    deps = NodeDeps(
        serp=MockSerpProvider(),
        llm=FakeLLM(md),
        prompts=PromptLoader(),
    )

    with pytest.raises(ValueError, match="write_article: missing required H2 headings"):
        write_article(state, deps)


def test_write_article_missing_llm_raises() -> None:
    state = _make_state()
    deps = NodeDeps(
        serp=MockSerpProvider(),
        llm=None,
        prompts=PromptLoader(),
    )

    with pytest.raises(ValueError, match="write_article: deps.llm is required"):
        write_article(state, deps)
