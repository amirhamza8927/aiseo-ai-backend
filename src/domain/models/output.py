"""Final article output model."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from .outline import Outline
from .seo_package import (
    ExternalReference,
    InternalLinkSuggestion,
    KeywordUsage,
    SeoMeta,
)
from .validation import ValidationReport


class SeoArticleOutput(BaseModel):
    """Complete output of the SEO article pipeline."""

    seo_meta: SeoMeta
    article_markdown: str = Field(min_length=1)
    outline: Outline
    keyword_analysis: KeywordUsage
    internal_links: list[InternalLinkSuggestion] = Field(default_factory=list)
    external_references: list[ExternalReference] = Field(default_factory=list)
    structured_data: dict[str, Any] = Field(default_factory=dict)
    validation_report: ValidationReport
