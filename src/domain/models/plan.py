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

        duplicates: list[str] = []
        seen: set[str] = set()
        for sid in ids:
            if sid in seen:
                duplicates.append(sid)
            else:
                seen.add(sid)
        if duplicates:
            raise ValueError(
                f"Duplicate section_id(s) in plan.sections: {sorted(set(duplicates))}"
            )

        valid_ids = set(ids)

        def _ensure_valid(ref_id: str, kind: str) -> None:
            if ref_id not in valid_ids:
                raise ValueError(
                    f"{kind}.placement_section_id '{ref_id}' "
                    f"not found in plan.sections"
                )

        for link in self.internal_links:
            _ensure_valid(link.placement_section_id, "internal_links")
        for cite in self.external_citations:
            _ensure_valid(cite.placement_section_id, "external_citations")
        for faq in self.faqs:
            _ensure_valid(faq.placement_section_id, "faqs")

        return self
