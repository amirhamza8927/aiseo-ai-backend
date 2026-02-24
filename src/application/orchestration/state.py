"""Graph state model – the typed bag of data flowing through the pipeline."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from src.domain.models.serp import SerpResult
from src.domain.models.themes import Themes
from src.domain.models.plan import Plan
from src.domain.models.outline import Outline
from src.domain.models.keyword_plan import KeywordPlan
from src.domain.models.seo_package import SeoPackage
from src.domain.models.validation import ValidationReport
from src.domain.models.repair import RepairSpec


class JobInput(BaseModel):
    """User-provided inputs that kick off a pipeline run."""

    model_config = ConfigDict(extra="forbid")

    topic: str = Field(min_length=1)
    target_word_count: int = Field(gt=0)
    language: str = Field(min_length=1)


class GraphState(BaseModel):
    """Full state carried between LangGraph nodes.

    All intermediate fields default to ``None`` so nodes can populate them
    progressively.  The ``new`` constructor provides a convenient way to
    build initial state from user inputs.
    """

    model_config = ConfigDict(extra="forbid")

    job_id: str = Field(min_length=1)
    input: JobInput

    serp_results: list[SerpResult] | None = None
    themes: Themes | None = None
    plan: Plan | None = None
    outline: Outline | None = None
    keyword_plan: KeywordPlan | None = None
    article_markdown: str | None = None
    seo_package: SeoPackage | None = None
    validation_report: ValidationReport | None = None
    repair_spec: RepairSpec | None = None

    revisions_left: int = 0
    current_node: str | None = None
    last_error: str | None = None

    @classmethod
    def new(
        cls,
        *,
        job_id: str,
        topic: str,
        target_word_count: int,
        language: str,
        max_revisions: int,
    ) -> GraphState:
        """Create initial state with all intermediate fields set to ``None``."""
        return cls(
            job_id=job_id,
            input=JobInput(
                topic=topic,
                target_word_count=target_word_count,
                language=language,
            ),
            revisions_left=max_revisions,
        )
