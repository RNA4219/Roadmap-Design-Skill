"""Response models for Roadmap Design Skill."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field


class RunStatus(str, Enum):
    """Run status enumeration."""

    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"


class HypothesisStatus(str, Enum):
    """Hypothesis status enumeration."""

    OPEN = "open"
    SUCCESS = "success"
    FAILURE = "failure"
    INCONCLUSIVE = "inconclusive"


class RiskSeverity(str, Enum):
    """Risk severity enumeration."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class FailureType(str, Enum):
    """Failure type enumeration."""

    INPUT_GAP = "input_gap"
    SCOPE_ERROR = "scope_error"
    PLANNING_BLOCKER = "planning_blocker"
    INTERNAL_ERROR = "internal_error"


class RunMeta(BaseModel):
    """Run metadata model."""

    run_id: Annotated[str, Field(min_length=1)]
    mode: Annotated[str, Field(pattern=r"^roadmap$")]
    status: RunStatus
    created_at: datetime
    updated_at: datetime
    planner_version: Annotated[str, Field(min_length=1)]
    response_language: Annotated[str, Field(min_length=2)]


class ProblemDefinition(BaseModel):
    """Problem definition model."""

    problem_id: Annotated[str, Field(pattern=r"^pb_[A-Za-z0-9_-]+$")]
    title: Annotated[str, Field(min_length=1)]
    statement: Annotated[str, Field(min_length=1)]
    scope: Annotated[str, Field(min_length=1)]
    non_goals: list[str]
    derived_from: list[str]


class SuccessCriterion(BaseModel):
    """Success criterion model."""

    criterion_id: Annotated[str, Field(pattern=r"^sc_[A-Za-z0-9_-]+$")]
    statement: Annotated[str, Field(min_length=1)]
    verification_method: Annotated[str, Field(min_length=1)]
    priority: Annotated[int, Field(ge=1)]


class Hypothesis(BaseModel):
    """Hypothesis model."""

    hypothesis_id: Annotated[str, Field(pattern=r"^hy_[A-Za-z0-9_-]+$")]
    statement: Annotated[str, Field(min_length=1)]
    why_this_might_work: Annotated[str, Field(min_length=1)]
    priority: Annotated[int, Field(ge=1)]
    related_insight_ids: list[str]
    related_constraint_ids: list[str]
    status: HypothesisStatus


class SolutionOption(BaseModel):
    """Solution option model."""

    option_id: Annotated[str, Field(pattern=r"^op_[A-Za-z0-9_-]+$")]
    title: Annotated[str, Field(min_length=1)]
    summary: Annotated[str, Field(min_length=1)]
    addresses_hypothesis_ids: list[str]
    tradeoffs: list[str]
    recommended: bool


class Experiment(BaseModel):
    """Experiment model."""

    experiment_id: Annotated[str, Field(pattern=r"^exp_[A-Za-z0-9_-]+$")]
    title: Annotated[str, Field(min_length=1)]
    goal: Annotated[str, Field(min_length=1)]
    verifies_hypothesis_ids: list[str]
    method: Annotated[str, Field(min_length=1)]
    success_condition: Annotated[str, Field(min_length=1)]
    failure_signal: Annotated[str, Field(min_length=1)]
    depends_on: list[str]
    estimated_effort: Annotated[str, Field(min_length=1)]


class RoadmapTask(BaseModel):
    """Roadmap task model."""

    task_id: Annotated[str, Field(pattern=r"^tk_[A-Za-z0-9_-]+$")]
    title: Annotated[str, Field(min_length=1)]
    description: Annotated[str, Field(min_length=1)]
    deliverable: Annotated[str, Field(min_length=1)]
    depends_on: list[str]


class RoadmapPhase(BaseModel):
    """Roadmap phase model."""

    phase_id: Annotated[str, Field(pattern=r"^ph_[A-Za-z0-9_-]+$")]
    order: Annotated[int, Field(ge=1)]
    title: Annotated[str, Field(min_length=1)]
    goal: Annotated[str, Field(min_length=1)]
    exit_criteria: list[str]
    tasks: Annotated[list[RoadmapTask], Field(min_length=1)]


class Risk(BaseModel):
    """Risk model."""

    risk_id: Annotated[str, Field(pattern=r"^rk_[A-Za-z0-9_-]+$")]
    statement: Annotated[str, Field(min_length=1)]
    severity: RiskSeverity
    mitigation: Annotated[str, Field(min_length=1)]


class Fallback(BaseModel):
    """Fallback option model."""

    fallback_id: Annotated[str, Field(pattern=r"^fb_[A-Za-z0-9_-]+$")]
    trigger: Annotated[str, Field(min_length=1)]
    statement: Annotated[str, Field(min_length=1)]
    tradeoff: Annotated[str, Field(min_length=1)]


class NextAction(BaseModel):
    """Next action model."""

    action_id: Annotated[str, Field(pattern=r"^na_[A-Za-z0-9_-]+$")]
    title: Annotated[str, Field(min_length=1)]
    description: Annotated[str, Field(min_length=1)]
    deliverable: Annotated[str, Field(min_length=1)]
    depends_on: list[str]


class OpenQuestion(BaseModel):
    """Open question model."""

    question_id: Annotated[str, Field(pattern=r"^oq_[A-Za-z0-9_-]+$")]
    statement: Annotated[str, Field(min_length=1)]
    blocking: bool
    affects: list[str]


class FailureItem(BaseModel):
    """Failure item model."""

    failure_id: Annotated[str, Field(pattern=r"^fl_[A-Za-z0-9_-]+$")]
    type: FailureType
    summary: Annotated[str, Field(min_length=1)]
    recoverable: bool


class Confidence(BaseModel):
    """Confidence model."""

    score: Annotated[float, Field(ge=0.0, le=1.0)]
    reason: Annotated[str, Field(min_length=1)]


class RoadmapResponse(BaseModel):
    """Roadmap response model."""

    schema_version: Annotated[str, Field(pattern=r"^1\.0\.0$")]
    run: RunMeta
    problem_definition: ProblemDefinition
    success_criteria: list[SuccessCriterion]
    hypotheses: list[Hypothesis]
    solution_options: list[SolutionOption]
    experiment_plan: list[Experiment]
    roadmap: list[RoadmapPhase]
    risks: list[Risk]
    fallback_options: list[Fallback]
    next_actions: list[NextAction]
    open_questions: list[OpenQuestion]
    assumptions: list[str]
    failures: list[FailureItem]
    confidence: Confidence