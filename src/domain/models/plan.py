"""Content plan models with cross-reference validation."""

from __future__ import annotations

from pydantic import BaseModel, Field, HttpUrl, model_validator


class PlanSection(BaseModel):
    """A single section in the content plan."""

    section_id: str = Field(min_length=1)
    heading: str = Field(min_length=1)
    purpose: str = ""
    key_points: list[str] = Field(min_length=1)
    target_word_count: int = Field(gt=0)
    required_keywords: list[str] = Field(default_factory=list)


class InternalLinkPlanItem(BaseModel):
    """Planned internal link placement."""

    anchor_text: str = Field(min_length=1)
    target_topic: str = Field(min_length=1)
    placement_section_id: str = Field(min_length=1)


class ExternalCitationPlanItem(BaseModel):
    """Planned external citation."""

    source_type: str = Field(min_length=1)
    suggested_source: str = Field(min_length=1)
    url: HttpUrl | None = None
    claim_supported: str = Field(min_length=1)
    placement_section_id: str = Field(min_length=1)


class FAQPlanItem(BaseModel):
    """Planned FAQ entry."""

    question: str = Field(min_length=1)
    placement_section_id: str = Field(min_length=1)


class Plan(BaseModel):
    """Full content plan – the single source of truth for downstream nodes."""

    h1: str = Field(min_length=1)
    intro_target_word_count: int = Field(gt=0)
    sections: list[PlanSection] = Field(min_length=1)
    internal_links: list[InternalLinkPlanItem] = Field(default_factory=list)
    external_citations: list[ExternalCitationPlanItem] = Field(default_factory=list)
    faqs: list[FAQPlanItem] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_plan_integrity(self) -> Plan:
        ids = [s.section_id for s in self.sections]
        if len(ids) != len(set(ids)):
            seen: set[str] = set()
            dupes = [sid for sid in ids if sid in seen or seen.add(sid)]  # type: ignore[func-returns-value]
            raise ValueError(f"Duplicate section_id(s): {dupes}")

        valid_ids = set(ids)

        for link in self.internal_links:
            if link.placement_section_id not in valid_ids:
                raise ValueError(
                    f"internal_links placement_section_id "
                    f"'{link.placement_section_id}' not in plan sections"
                )
        for cite in self.external_citations:
            if cite.placement_section_id not in valid_ids:
                raise ValueError(
                    f"external_citations placement_section_id "
                    f"'{cite.placement_section_id}' not in plan sections"
                )
        for faq in self.faqs:
            if faq.placement_section_id not in valid_ids:
                raise ValueError(
                    f"faqs placement_section_id "
                    f"'{faq.placement_section_id}' not in plan sections"
                )
        return self
