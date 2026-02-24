"""Tests for markdown_tools: heading extraction and hierarchy validation."""

from src.application.services.markdown_tools import (
    extract_headings,
    strip_markdown_for_word_count,
    validate_heading_hierarchy,
)


# -- extract_headings --------------------------------------------------------

def test_extract_headings_basic():
    md = "# Title\n\n## Section A\n\ntext\n\n### Sub A1\n"
    assert extract_headings(md) == [(1, "Title"), (2, "Section A"), (3, "Sub A1")]


def test_extract_headings_ignores_code_blocks():
    md = (
        "# Real Title\n\n"
        "```\n"
        "## Not a heading\n"
        "```\n\n"
        "## Real Section\n"
    )
    result = extract_headings(md)
    assert (2, "Not a heading") not in result
    assert (1, "Real Title") in result
    assert (2, "Real Section") in result


def test_extract_headings_empty():
    assert extract_headings("") == []
    assert extract_headings("no headings here") == []


# -- validate_heading_hierarchy ----------------------------------------------

def test_valid_hierarchy():
    md = "# Title\n\n## A\n\n### A1\n\n## B\n"
    passed, issues = validate_heading_hierarchy(md)
    assert passed is True
    assert issues == []


def test_no_h1():
    md = "## Section\n\ntext\n"
    passed, issues = validate_heading_hierarchy(md)
    assert passed is False
    assert any("No H1" in i for i in issues)


def test_multiple_h1():
    md = "# First\n\n# Second\n\n## Section\n"
    passed, issues = validate_heading_hierarchy(md)
    assert passed is False
    assert any("1 H1" in i for i in issues)


def test_h3_before_h2():
    md = "# Title\n\n### Orphan Sub\n\n## Late Section\n"
    passed, issues = validate_heading_hierarchy(md)
    assert passed is False
    assert any("H3" in i and "before" in i for i in issues)


def test_h4_flagged():
    md = "# Title\n\n## Section\n\n#### Deep\n"
    passed, issues = validate_heading_hierarchy(md)
    assert passed is False
    assert any("H4" in i for i in issues)


# -- strip_markdown_for_word_count -------------------------------------------

def test_strip_markdown_excludes_syntax():
    md = "# Title\n\n**bold** text and [a link](http://x.com).\n\n```\ncode block\n```\n"
    cleaned = strip_markdown_for_word_count(md)
    assert "```" not in cleaned
    assert "bold" in cleaned
    assert "text" in cleaned
    assert "a link" in cleaned
    assert "http://x.com" not in cleaned


def test_strip_markdown_preserves_heading_text():
    md = "# My Heading\n\nSome body text.\n"
    cleaned = strip_markdown_for_word_count(md)
    assert "My" in cleaned
    assert "Heading" in cleaned


def test_strip_markdown_word_count_accuracy():
    md = "# Heading\n\nOne two three.\n"
    words = strip_markdown_for_word_count(md).split()
    assert len(words) == 4
