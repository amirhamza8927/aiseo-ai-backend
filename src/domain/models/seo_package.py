"""SEO packaging models – metadata, links, references, keyword usage."""

from __future__ import annotations

from pydantic import BaseModel, Field, HttpUrl


class SeoMeta(BaseModel):
    """HTML meta tags for the article."""

    title_tag: str = Field(min_length=1)
    meta_description: str = Field(min_length=1)


class InternalLinkSuggestion(BaseModel):
    """A suggested internal link to place in the article."""

    anchor_text: str = Field(min_length=1)
    target_topic: str = Field(min_length=1)
    placement_section_id: str | None = None


class ExternalReference(BaseModel):
    """An external citation / reference."""

    source_name: str = Field(min_length=1)
    url: HttpUrl | None = None
    placement_hint: str = Field(min_length=1)
    credibility_reason: str = Field(min_length=1)


class KeywordUsage(BaseModel):
    """Tracked keyword occurrences in the article."""

    primary: str = Field(min_length=1)
    secondary: list[str] = Field(default_factory=list)
    counts: dict[str, int] = Field(default_factory=dict)


class SeoPackage(BaseModel):
    """Complete SEO metadata bundle produced by the seo_packager node."""

    seo_meta: SeoMeta
    internal_links: list[InternalLinkSuggestion] = Field(default_factory=list)
    external_references: list[ExternalReference] = Field(default_factory=list)
    keyword_usage: KeywordUsage
