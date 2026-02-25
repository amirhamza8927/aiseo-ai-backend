"""Deterministic SEO validation of a draft article output."""

from __future__ import annotations

from pydantic import BaseModel

from src.application.services.keyword_tools import (
    count_keyword_occurrences,
    primary_in_intro,
)
from src.application.services.markdown_tools import (
    extract_headings,
    strip_markdown_for_word_count,
    validate_heading_hierarchy,
)
from src.domain.models.output import SeoArticleOutput
from src.domain.models.validation import ValidationReport


class SeoValidationConfig(BaseModel):
    """Thresholds used by :func:`validate_seo_article`."""

    word_count_target: int = 1500
    word_count_tolerance_ratio: float = 0.15
    meta_description_min: int = 140
    meta_description_max: int = 160
    internal_links_min: int = 3
    internal_links_max: int = 5
    external_refs_min: int = 2
    external_refs_max: int = 4


def validate_seo_article(
    *,
    output: SeoArticleOutput,
    primary_keyword: str,
    config: SeoValidationConfig,
) -> ValidationReport:
    """Run all deterministic SEO checks and return a structured report."""

    checks: dict[str, bool] = {}
    issues: list[str] = []
    md = output.article_markdown

    # 1 — primary keyword in title tag
    checks["primary_in_title_tag"] = (
        primary_keyword.lower() in output.seo_meta.title_tag.lower()
    )
    if not checks["primary_in_title_tag"]:
        issues.append(
            f"Primary keyword '{primary_keyword}' missing from title_tag"
        )

    # 2 — primary keyword in intro paragraph
    checks["primary_in_intro"] = primary_in_intro(md, primary_keyword)
    if not checks["primary_in_intro"]:
        issues.append(
            f"Primary keyword '{primary_keyword}' missing from intro paragraph"
        )

    # 3 — primary keyword in at least one H2
    headings = extract_headings(md)
    h2_texts = [text for level, text in headings if level == 2]
    checks["primary_in_h2"] = any(
        count_keyword_occurrences(h2, primary_keyword) > 0 for h2 in h2_texts
    )
    if not checks["primary_in_h2"]:
        issues.append(
            f"Primary keyword '{primary_keyword}' missing from all H2 headings"
        )

    # 4 — heading hierarchy
    hierarchy_ok, hierarchy_issues = validate_heading_hierarchy(md)
    checks["heading_hierarchy_valid"] = hierarchy_ok
    if not hierarchy_ok:
        issues.extend(hierarchy_issues)

    # 5 — word count tolerance (strip markdown syntax before counting)
    clean_text = strip_markdown_for_word_count(md)
    word_count = len(clean_text.split())
    tolerance = config.word_count_target * config.word_count_tolerance_ratio
    wc_min = int(config.word_count_target - tolerance)
    wc_max = int(config.word_count_target + tolerance)
    checks["word_count_within_tolerance"] = wc_min <= word_count <= wc_max
    if not checks["word_count_within_tolerance"]:
        issues.append(
            f"Word count {word_count} outside tolerance "
            f"[{wc_min}, {wc_max}]"
        )

    # 6 — meta description length
    desc_len = len(output.seo_meta.meta_description)
    checks["meta_description_length_valid"] = (
        config.meta_description_min <= desc_len <= config.meta_description_max
    )
    if not checks["meta_description_length_valid"]:
        issues.append(
            f"Meta description length {desc_len} outside "
            f"[{config.meta_description_min}, {config.meta_description_max}]"
        )

    # 7 — internal links count
    il_count = len(output.internal_links)
    checks["internal_links_count_valid"] = (
        config.internal_links_min <= il_count <= config.internal_links_max
    )
    if not checks["internal_links_count_valid"]:
        issues.append(
            f"Internal links count {il_count} outside "
            f"[{config.internal_links_min}, {config.internal_links_max}]"
        )

    # 8 — external references count
    er_count = len(output.external_references)
    checks["external_refs_count_valid"] = (
        config.external_refs_min <= er_count <= config.external_refs_max
    )
    if not checks["external_refs_count_valid"]:
        issues.append(
            f"External references count {er_count} outside "
            f"[{config.external_refs_min}, {config.external_refs_max}]"
        )

    # 9 — output schema round-trip
    try:
        SeoArticleOutput.model_validate(output.model_dump())
        checks["output_schema_valid"] = True
    except Exception:
        checks["output_schema_valid"] = False
        issues.append("SeoArticleOutput failed schema round-trip validation")

    passed = all(checks.values())
    score = sum(checks.values()) / len(checks) if checks else 0.0

    return ValidationReport(
        passed=passed,
        score=score,
        issues=issues,
        checks=checks,
    )
