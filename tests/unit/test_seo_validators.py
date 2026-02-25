"""Tests for seo_validators: full-pass and individual-fail scenarios."""

from src.application.services.seo_validators import (
    SeoValidationConfig,
    validate_seo_article,
)
from src.domain.models.outline import Outline, OutlineSection
from src.domain.models.output import SeoArticleOutput
from src.domain.models.seo_package import (
    ExternalReference,
    InternalLinkSuggestion,
    KeywordUsage,
    SeoMeta,
)
from src.domain.models.validation import ValidationReport


def _valid_markdown(keyword: str = "seo tools") -> str:
    """Markdown that passes all heading and keyword checks.
    Word count ~500 for target 500 with 15% tolerance (425-575).
    """
    return (
        f"# Best {keyword.title()} Guide\n\n"
        f"This intro covers {keyword} in depth.\n\n"
        f"## Why {keyword.title()} Matter\n\n"
        + ("Lorem ipsum dolor sit amet. " * 85)
        + "\n\n## Conclusion\n\nFinal thoughts.\n"
    )


def _valid_output(
    keyword: str = "seo tools",
    meta_desc_len: int = 150,
    internal_count: int = 4,
    external_count: int = 3,
) -> SeoArticleOutput:
    md = _valid_markdown(keyword)
    return SeoArticleOutput(
        seo_meta=SeoMeta(
            title_tag=f"Best {keyword.title()} for 2026",
            meta_description="x" * meta_desc_len,
        ),
        article_markdown=md,
        outline=Outline(
            h1=f"Best {keyword.title()} Guide",
            sections=[
                OutlineSection(section_id="s1", h2=f"Why {keyword.title()} Matter"),
                OutlineSection(section_id="s2", h2="Conclusion"),
            ],
        ),
        keyword_analysis=KeywordUsage(primary=keyword, secondary=[], counts={}),
        internal_links=[
            InternalLinkSuggestion(anchor_text=f"link{i}", target_topic="t")
            for i in range(internal_count)
        ],
        external_references=[
            ExternalReference(
                source_name=f"src{i}",
                placement_hint="body",
                credibility_reason="authoritative",
            )
            for i in range(external_count)
        ],
        structured_data={},
        validation_report=ValidationReport(passed=True, score=1.0),
    )


CFG = SeoValidationConfig(word_count_target=500, word_count_tolerance_ratio=0.15)


def test_all_checks_pass():
    output = _valid_output()
    report = validate_seo_article(
        output=output, primary_keyword="seo tools", config=CFG,
    )
    assert report.passed is True
    assert all(report.checks.values())
    assert report.score == 1.0
    assert report.issues == []


def test_missing_keyword_in_title():
    output = _valid_output()
    output = output.model_copy(
        update={"seo_meta": SeoMeta(title_tag="No Match", meta_description="x" * 150)}
    )
    report = validate_seo_article(
        output=output, primary_keyword="seo tools", config=CFG,
    )
    assert report.checks["primary_in_title_tag"] is False
    assert report.passed is False
    assert report.score < 1.0


def test_bad_meta_description_length():
    output = _valid_output(meta_desc_len=50)
    report = validate_seo_article(
        output=output, primary_keyword="seo tools", config=CFG,
    )
    assert report.checks["meta_description_length_valid"] is False
    assert any("Meta description" in i for i in report.issues)


def test_internal_links_out_of_range():
    output = _valid_output(internal_count=0)
    report = validate_seo_article(
        output=output, primary_keyword="seo tools", config=CFG,
    )
    assert report.checks["internal_links_count_valid"] is False


def test_score_calculation():
    output = _valid_output(internal_count=0, external_count=0)
    report = validate_seo_article(
        output=output, primary_keyword="seo tools", config=CFG,
    )
    total = len(report.checks)
    failed = sum(1 for v in report.checks.values() if not v)
    expected_score = (total - failed) / total
    assert abs(report.score - expected_score) < 1e-9


def test_word_count_within_tolerance():
    """Word count within target +/- 15% passes."""
    output = _valid_output()
    report = validate_seo_article(
        output=output, primary_keyword="seo tools", config=CFG,
    )
    assert report.checks["word_count_within_tolerance"] is True


def test_word_count_outside_tolerance():
    """Word count outside [425, 575] for target 500 fails."""
    short_md = "# Title\n\nShort intro.\n\n## Section\n\n" + ("x " * 50)
    output = _valid_output()
    output = output.model_copy(update={"article_markdown": short_md})
    report = validate_seo_article(
        output=output, primary_keyword="seo tools", config=CFG,
    )
    assert report.checks["word_count_within_tolerance"] is False
    assert any("Word count" in i for i in report.issues)


def test_meta_description_140_to_160_bounds():
    """Meta description 140-160 chars passes; 139 or 161 fails."""
    output_139 = _valid_output(meta_desc_len=139)
    report_139 = validate_seo_article(
        output=output_139, primary_keyword="seo tools", config=CFG,
    )
    assert report_139.checks["meta_description_length_valid"] is False

    output_150 = _valid_output(meta_desc_len=150)
    report_150 = validate_seo_article(
        output=output_150, primary_keyword="seo tools", config=CFG,
    )
    assert report_150.checks["meta_description_length_valid"] is True

    output_161 = _valid_output(meta_desc_len=161)
    report_161 = validate_seo_article(
        output=output_161, primary_keyword="seo tools", config=CFG,
    )
    assert report_161.checks["meta_description_length_valid"] is False
