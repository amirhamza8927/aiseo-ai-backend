"""Tests for keyword_tools: counting, intro extraction, primary_in_intro."""

from src.application.services.keyword_tools import (
    count_keyword_occurrences,
    extract_intro_paragraph,
    primary_in_intro,
)


# -- count_keyword_occurrences -----------------------------------------------

def test_count_basic():
    assert count_keyword_occurrences("the cat sat on the mat", "cat") == 1


def test_count_case_insensitive():
    assert count_keyword_occurrences("SEO tools for SEO experts", "seo") == 2


def test_count_multi_word():
    text = "Learn about content marketing and why content marketing matters."
    assert count_keyword_occurrences(text, "content marketing") == 2


def test_count_no_match():
    assert count_keyword_occurrences("hello world", "python") == 0


def test_count_empty_keyword():
    assert count_keyword_occurrences("some text", "") == 0


def test_count_multi_word_with_punctuation():
    text = "We love remote teams, and remote teams love us."
    assert count_keyword_occurrences(text, "remote teams") == 2


def test_count_keyword_at_punctuation_boundary():
    """Keyword at punctuation boundaries (e.g. 'word.') is counted."""
    text = "The best word. Another word, and word."
    assert count_keyword_occurrences(text, "word") == 3


# -- extract_intro_paragraph -------------------------------------------------

def test_intro_with_h2():
    md = "# Title\n\nThis is the intro paragraph.\n\n## Section\n\nBody text.\n"
    assert extract_intro_paragraph(md) == "This is the intro paragraph."


def test_intro_without_h2():
    md = "# Title\n\nOnly paragraph here.\n"
    assert extract_intro_paragraph(md) == "Only paragraph here."


def test_intro_multiline():
    md = "# Title\n\nLine one\nline two.\n\n## Section\n"
    assert extract_intro_paragraph(md) == "Line one line two."


def test_intro_empty():
    assert extract_intro_paragraph("no heading") == ""


def test_intro_ignores_code_fences():
    md = "# Title\n\n```\ncode example\n```\n\nReal intro here.\n\n## Section\n"
    assert extract_intro_paragraph(md) == "Real intro here."


# -- primary_in_intro --------------------------------------------------------

def test_primary_in_intro_true():
    md = "# Guide\n\nLearn about SEO strategies today.\n\n## Tips\n"
    assert primary_in_intro(md, "seo strategies") is True


def test_primary_in_intro_false():
    md = "# Guide\n\nLearn about marketing today.\n\n## Tips\n"
    assert primary_in_intro(md, "seo strategies") is False
