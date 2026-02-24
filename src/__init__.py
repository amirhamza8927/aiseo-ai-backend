"""Foundation module – shared enums, constants, and re-exports."""

from __future__ import annotations

from enum import Enum

from src.logging_config import configure_logging, get_logger
from src.settings import Settings, get_settings


class NodeName(str, Enum):
    """Canonical names for every graph node."""

    COLLECT_SERP = "collect_serp"
    EXTRACT_THEMES = "extract_themes"
    PLANNER = "planner"
    BUILD_OUTLINE = "build_outline"
    KEYWORD_PLAN = "keyword_plan"
    WRITE_ARTICLE = "write_article"
    SEO_PACKAGER = "seo_packager"
    VALIDATE_AND_SCORE = "validate_and_score"
    REPAIR_SPEC = "repair_spec"
    REVISE_TARGETED = "revise_targeted"
    FINALIZE = "finalize"


class JobStatus(str, Enum):
    """Lifecycle states for a pipeline job."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


__all__ = [
    "NodeName",
    "JobStatus",
    "Settings",
    "get_settings",
    "configure_logging",
    "get_logger",
]
