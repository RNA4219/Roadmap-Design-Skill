"""Request models for Roadmap Design Skill."""

from __future__ import annotations

from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field, field_validator


class PriorityHint(str, Enum):
    """Priority hint enumeration."""

    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ConstraintCategory(str, Enum):
    """Constraint category enumeration."""

    TIME = "time"
    RESOURCE = "resource"
    TECHNOLOGY = "technology"
    TEAM = "team"
    COMPLIANCE = "compliance"
    OTHER = "other"


class ConstraintSeverity(str, Enum):
    """Constraint severity enumeration."""

    HARD = "hard"
    SOFT = "soft"


class AssetType(str, Enum):
    """Asset type enumeration."""

    COMPONENT = "component"
    DATASET = "dataset"
    DOCUMENT = "document"
    SKILL = "skill"
    PEOPLE = "people"
    OTHER = "other"


class EvidenceKind(str, Enum):
    """Evidence kind enumeration."""

    DOCUMENT = "document"
    ISSUE = "issue"
    EXPERIMENT = "experiment"
    NOTE = "note"
    OTHER = "other"


class ProblemStatement(BaseModel):
    """Problem statement model."""

    problem_id: Annotated[str, Field(pattern=r"^pb_[A-Za-z0-9_-]+$")]
    title: Annotated[str, Field(min_length=1)]
    statement: Annotated[str, Field(min_length=1)]
    background: str | None = None
    desired_outcome: str | None = None


class InsightItem(BaseModel):
    """Insight item model."""

    insight_id: Annotated[str, Field(pattern=r"^in_[A-Za-z0-9_-]+$")]
    statement: Annotated[str, Field(min_length=1)]
    source: str | None = None
    importance: str | None = None

    @field_validator("importance")
    @classmethod
    def validate_importance(cls, v: str | None) -> str | None:
        if v is not None and v not in ("high", "medium", "low"):
            raise ValueError("importance must be 'high', 'medium', or 'low'")
        return v


class ConstraintItem(BaseModel):
    """Constraint item model."""

    constraint_id: Annotated[str, Field(pattern=r"^co_[A-Za-z0-9_-]+$")]
    category: ConstraintCategory
    statement: Annotated[str, Field(min_length=1)]
    severity: ConstraintSeverity


class AssetItem(BaseModel):
    """Asset item model."""

    asset_id: Annotated[str, Field(pattern=r"^as_[A-Za-z0-9_-]+$")]
    type: AssetType
    name: Annotated[str, Field(min_length=1)]
    description: Annotated[str, Field(min_length=1)]


class KnownFailure(BaseModel):
    """Known failure model."""

    failure_id: Annotated[str, Field(pattern=r"^kf_[A-Za-z0-9_-]+$")]
    statement: Annotated[str, Field(min_length=1)]
    source: str | None = None


class EvidenceRef(BaseModel):
    """Evidence reference model."""

    ref_id: Annotated[str, Field(pattern=r"^ev_[A-Za-z0-9_-]+$")]
    kind: EvidenceKind
    summary: Annotated[str, Field(min_length=1)]


class RoadmapRequest(BaseModel):
    """Roadmap request model."""

    schema_version: Annotated[str, Field(pattern=r"^1\.0\.0$")]
    mode: Annotated[str, Field(pattern=r"^roadmap$")]
    problem_statement: ProblemStatement
    insights: Annotated[list[InsightItem], Field(min_length=1)]
    constraints: Annotated[list[ConstraintItem], Field(min_length=1)]
    available_assets: Annotated[list[AssetItem], Field(min_length=1)]
    run_id: str | None = None
    response_language: str | None = None
    known_failures: list[KnownFailure] | None = None
    evidence_refs: list[EvidenceRef] | None = None
    notes: list[str] | None = None
    priority_hint: PriorityHint | None = None
    assumptions: list[str] | None = None