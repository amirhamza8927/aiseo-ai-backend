"""Pure helpers for parsing and validating markdown heading structure."""

from __future__ import annotations

import re

_CODE_FENCE_RE = re.compile(r"```[\s\S]*?```", re.MULTILINE)
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
_MD_SYNTAX_RE = re.compile(r"[*_`>#\[\]()!|~]")


def strip_markdown_for_word_count(markdown: str) -> str:
    """Return markdown with code blocks, links, and formatting stripped for word counting.

    Link anchor text and heading text are preserved so they count as real words.
    """
    cleaned = _CODE_FENCE_RE.sub("", markdown)
    cleaned = _LINK_RE.sub(r"\1", cleaned)
    cleaned = _HEADING_RE.sub(r"\2", cleaned)
    cleaned = _MD_SYNTAX_RE.sub(" ", cleaned)
    return " ".join(cleaned.split())


def extract_headings(markdown: str) -> list[tuple[int, str]]:
    """Return ``[(level, text), ...]`` for every markdown heading.

    Fenced code blocks are stripped first so headings inside them are
    not counted.
    """
    cleaned = _CODE_FENCE_RE.sub("", markdown)
    return [(len(m.group(1)), m.group(2).strip()) for m in _HEADING_RE.finditer(cleaned)]


def validate_heading_hierarchy(markdown: str) -> tuple[bool, list[str]]:
    """Check heading hierarchy rules.

    Returns ``(passed, issues)`` where *issues* is a list of
    human-readable problems found.

    Rules:
    - Exactly one H1.
    - H3 may only appear after at least one H2.
    - H4+ are flagged as issues (strict hierarchy for publishing).
    """
    headings = extract_headings(markdown)
    issues: list[str] = []

    h1_count = sum(1 for lvl, _ in headings if lvl == 1)
    if h1_count == 0:
        issues.append("No H1 heading found")
    elif h1_count > 1:
        issues.append(f"Expected exactly 1 H1, found {h1_count}")

    h2_seen = False
    for level, text in headings:
        if level == 2:
            h2_seen = True
        elif level == 3 and not h2_seen:
            issues.append(f"H3 '{text}' appears before any H2")
        elif level >= 4:
            issues.append(f"H{level} '{text}' found; prefer H1-H3 only")

    return (len(issues) == 0, issues)
