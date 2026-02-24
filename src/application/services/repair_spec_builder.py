"""Build an actionable RepairSpec from a ValidationReport."""

from __future__ import annotations

from src.domain.models.outline import Outline
from src.domain.models.repair import RepairIssue, RepairSpec
from src.domain.models.validation import ValidationReport

_CHECK_MAP: dict[str, tuple[str, str, str]] = {
    # check_key -> (code, required_action, target_strategy)
    # target_strategy: "__seo_meta__" | "__intro__" | "first_section" | "all_sections"
    "primary_in_title_tag": (
        "PRIMARY_MISSING_TITLE",
        "Include primary keyword in title_tag exactly once.",
        "__seo_meta__",
    ),
    "primary_in_intro": (
        "PRIMARY_MISSING_INTRO",
        "Rewrite intro paragraph to include primary keyword naturally.",
        "__intro__",
    ),
    "primary_in_h2": (
        "PRIMARY_MISSING_H2",
        "Include primary keyword in at least one H2 heading.",
        "first_section",
    ),
    "heading_hierarchy_valid": (
        "HEADING_HIERARCHY",
        "Fix heading structure: exactly one H1, H3 only under H2.",
        "all_sections",
    ),
    "word_count_within_tolerance": (
        "WORD_COUNT",
        "Expand or trim content to fall within target tolerance.",
        "all_sections",
    ),
    "meta_description_length_valid": (
        "META_DESCRIPTION_LENGTH",
        "Rewrite meta description to 140-160 chars with primary keyword.",
        "__seo_meta__",
    ),
    "internal_links_count_valid": (
        "INTERNAL_LINKS_COUNT",
        "Adjust internal link suggestions to 3-5 total.",
        "__seo_meta__",
    ),
    "external_refs_count_valid": (
        "EXTERNAL_REFS_COUNT",
        "Adjust external references to 2-4 total.",
        "__seo_meta__",
    ),
    "output_schema_valid": (
        "SCHEMA_INVALID",
        "Fix output to pass SeoArticleOutput schema validation.",
        "all_sections",
    ),
}


def _all_section_ids(outline: Outline) -> list[str]:
    return [s.section_id for s in outline.sections]


def _resolve_targets(strategy: str, outline: Outline) -> list[str]:
    if strategy == "__seo_meta__":
        return ["__seo_meta__"]
    if strategy == "__intro__":
        return ["__intro__"]
    if strategy == "first_section":
        ids = _all_section_ids(outline)
        return [ids[0]] if ids else []
    return _all_section_ids(outline)


def build_repair_spec(
    *,
    report: ValidationReport,
    outline: Outline,
    primary_keyword: str,
) -> RepairSpec:
    """Translate failed validation checks into explicit repair instructions."""

    repair_issues: list[RepairIssue] = []
    instructions: list[str] = []
    all_target_ids: set[str] = set()

    for check_key, passed in report.checks.items():
        if passed:
            continue
        mapping = _CHECK_MAP.get(check_key)
        if mapping is None:
            continue

        code, action, strategy = mapping
        targets = _resolve_targets(strategy, outline)
        all_target_ids.update(targets)

        repair_issues.append(
            RepairIssue(
                code=code,
                message=f"Validation failed: {check_key}",
                target_section_ids=targets,
                required_action=action,
            )
        )
        instructions.append(f"[{code}] {action}")

    return RepairSpec(
        issues=repair_issues,
        instructions=instructions,
        must_edit_section_ids=sorted(all_target_ids),
    )
