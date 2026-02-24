"""Domain models – convenience re-exports."""

from __future__ import annotations

from src.domain.models.job import JobRecord, JobStatus
from src.domain.models.keyword_plan import KeywordPlan
from src.domain.models.outline import Outline, OutlineSection
from src.domain.models.output import SeoArticleOutput
from src.domain.models.plan import (
    ExternalCitationPlanItem,
    FAQPlanItem,
    InternalLinkPlanItem,
    Plan,
    PlanSection,
)
from src.domain.models.repair import RepairIssue, RepairSpec
from src.domain.models.seo_package import (
    ExternalReference,
    InternalLinkSuggestion,
    KeywordUsage,
    SeoMeta,
    SeoPackage,
)
from src.domain.models.serp import SerpResult, SerpResults
from src.domain.models.themes import Themes
from src.domain.models.validation import ValidationReport

__all__ = [
    # serp
    "SerpResult",
    "SerpResults",
    # themes
    "Themes",
    # plan
    "PlanSection",
    "InternalLinkPlanItem",
    "ExternalCitationPlanItem",
    "FAQPlanItem",
    "Plan",
    # outline
    "OutlineSection",
    "Outline",
    # keyword
    "KeywordPlan",
    # seo package
    "SeoMeta",
    "InternalLinkSuggestion",
    "ExternalReference",
    "KeywordUsage",
    "SeoPackage",
    # validation
    "ValidationReport",
    # repair
    "RepairIssue",
    "RepairSpec",
    # output
    "SeoArticleOutput",
    # job
    "JobStatus",
    "JobRecord",
]
