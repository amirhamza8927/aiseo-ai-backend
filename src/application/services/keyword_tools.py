"""Pure helpers for keyword counting and intro-paragraph extraction."""

from __future__ import annotations

import re

_WHITESPACE_RE = re.compile(r"\s+")
_CODE_FENCE_RE = re.compile(r"```[\s\S]*?```", re.MULTILINE)


def count_keyword_occurrences(text: str, keyword: str) -> int:
    """Count case-insensitive occurrences of *keyword* in *text*.

    Single-word keywords use word-boundary matching.  Multi-word keywords
    use exact-phrase substring matching on normalised text to avoid
    regex boundary edge cases around punctuation.
    """
    normalised_kw = _WHITESPACE_RE.sub(" ", keyword.strip()).lower()
    if not normalised_kw:
        return 0
    normalised_text = _WHITESPACE_RE.sub(" ", text).lower()

    if " " in normalised_kw:
        return normalised_text.count(normalised_kw)

    pattern = r"\b" + re.escape(normalised_kw) + r"\b"
    return len(re.findall(pattern, normalised_text))


def extract_intro_paragraph(markdown: str) -> str:
    """Return the first content paragraph between H1 and the first H2.

    If there is no H2, returns the first non-empty paragraph after H1.
    Returns ``""`` when nothing qualifies.  Fenced code blocks are
    stripped so they don't pollute the intro text.
    """
    markdown = _CODE_FENCE_RE.sub("", markdown)
    lines = markdown.splitlines()

    after_h1 = False
    collected: list[str] = []

    for line in lines:
        stripped = line.strip()
        if re.match(r"^#\s+", stripped):
            after_h1 = True
            continue
        if after_h1 and re.match(r"^##\s+", stripped):
            break
        if after_h1:
            collected.append(stripped)

    paragraph: list[str] = []
    for line in collected:
        if line:
            paragraph.append(line)
        elif paragraph:
            break

    return " ".join(paragraph)


def primary_in_intro(markdown: str, primary_keyword: str) -> bool:
    """Return True if *primary_keyword* appears in the intro paragraph."""
    return count_keyword_occurrences(extract_intro_paragraph(markdown), primary_keyword) > 0
