"""Domain models – convenience re-exports."""

from __future__ import annotations

from .job import JobRecord, JobStatus
from .job_input import JobInput
from .keyword_plan import KeywordPlan
from .outline import Outline, OutlineSection
from .output import SeoArticleOutput
from .plan import (
    ExternalCitationPlanItem,
    FAQPlanItem,
    InternalLinkPlanItem,
    Plan,
    PlanSection,
)
from .repair import RepairIssue, RepairSpec
from .seo_package import (
    ExternalReference,
    InternalLinkSuggestion,
    KeywordUsage,
    SeoMeta,
    SeoPackage,
)
from .serp import SerpResult, SerpResults
from .themes import Themes
from .validation import ValidationReport

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
    "JobInput",
    "JobRecord",
    "JobStatus",
]
