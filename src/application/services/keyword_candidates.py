"""Pure functions for extracting secondary keyword candidates from SERP."""

from __future__ import annotations

import re
from collections import Counter

from src.domain.models.serp import SerpResult

_STOPWORDS = frozenset(
    {
        "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "of",
        "with", "by", "is", "are", "was", "were", "be", "been", "have", "has", "had",
        "do", "does", "did", "will", "would", "could", "it", "its", "this", "that",
        "best", "top", "guide", "review", "vs", "comparison",
    }
)


def extract_secondary_candidates(
    serp_results: list[SerpResult],
    *,
    primary: str,
    max_candidates: int = 20,
) -> list[str]:
    """Extract secondary keyword candidates from SERP titles and snippets.

    Deterministic: same input yields same output. Excludes primary (case-insensitive).
    Returns top candidates by frequency, tie-broken lexicographically, in Title Case.
    """
    corpus = " ".join(r.title + " " + r.snippet for r in serp_results)
    text = corpus.lower().strip()
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    tokens = [t for t in text.split() if t not in _STOPWORDS]

    phrases: list[str] = []
    for i in range(len(tokens) - 1):
        bigram = tokens[i] + " " + tokens[i + 1]
        phrases.append(bigram)
    for i in range(len(tokens) - 2):
        trigram = tokens[i] + " " + tokens[i + 1] + " " + tokens[i + 2]
        phrases.append(trigram)

    primary_lower = primary.lower()
    filtered: list[str] = []
    for p in phrases:
        if not (4 <= len(p) <= 60):
            continue
        if primary_lower in p.lower():
            continue
        if p.replace(" ", "").isdigit():
            continue
        filtered.append(p)

    counts = Counter(filtered)
    sorted_phrases = sorted(
        counts.keys(),
        key=lambda x: (-counts[x], x),
    )
    result = [p.title() for p in sorted_phrases[:max_candidates]]
    return result
