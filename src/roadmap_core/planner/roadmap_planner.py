"""Roadmap planner - core pipeline for generating roadmaps."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from roadmap_core.models.request import RoadmapRequest
from roadmap_core.models.response import (
    Confidence,
    Experiment,
    FailureItem,
    Fallback,
    Hypothesis,
    HypothesisStatus,
    NextAction,
    OpenQuestion,
    ProblemDefinition,
    RoadmapPhase,
    RoadmapResponse,
    RoadmapTask,
    Risk,
    RunMeta,
    RunStatus,
    SolutionOption,
    SuccessCriterion,
)
from roadmap_core.validators.request_validator import RequestValidator


class RoadmapPlanner:
    """Core planner for generating structured roadmaps from problem statements."""

    def __init__(self) -> None:
        """Initialize the roadmap planner."""
        self._validator = RequestValidator()
        self._planner_version = "1.0.0"

    def plan(self, request: RoadmapRequest) -> RoadmapResponse:
        """Generate a roadmap from a request.

        Args:
            request: The roadmap request.

        Returns:
            RoadmapResponse with the generated plan or failure information.
        """
        # Generate run metadata
        run_id = request.run_id or f"run_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc)

        # Validate request
        validation_errors = self._validator.validate(request)
        if validation_errors:
            return self._create_failure_response(
                run_id=run_id,
                now=now,
                problem_id=request.problem_statement.problem_id,
                title=request.problem_statement.title,
                errors=validation_errors,
            )

        # Check for broad problem (soft failure)
        broad_problem_check = self._check_broad_problem(request)
        if broad_problem_check:
            return self._create_partial_response(
                request=request,
                run_id=run_id,
                now=now,
                failures=broad_problem_check,
            )

        # Generate full roadmap
        return self._generate_roadmap(request, run_id, now)

    def _generate_roadmap(
        self, request: RoadmapRequest, run_id: str, now: datetime
    ) -> RoadmapResponse:
        """Generate a complete roadmap.

        Args:
            request: The validated request.
            run_id: Run identifier.
            now: Current timestamp.

        Returns:
            Complete RoadmapResponse.
        """
        # Step 1: Problem definition
        problem_definition = self._create_problem_definition(request)

        # Step 2: Success criteria
        success_criteria = self._create_success_criteria(request)

        # Step 3: Hypotheses
        hypotheses = self._create_hypotheses(request)

        # Step 4: Solution options
        solution_options = self._create_solution_options(request, hypotheses)

        # Step 5: Experiments
        experiments = self._create_experiments(request, hypotheses)

        # Step 6: Roadmap phases
        roadmap = self._create_roadmap_phases(request, experiments)

        # Step 7: Risks
        risks = self._create_risks(request)

        # Step 8: Fallbacks
        fallbacks = self._create_fallbacks(request)

        # Step 9: Next actions
        next_actions = self._create_next_actions(roadmap)

        # Confidence
        confidence = Confidence(
            score=0.75,
            reason="Standard planning based on provided insights and constraints.",
        )

        return RoadmapResponse(
            schema_version="1.0.0",
            run=RunMeta(
                run_id=run_id,
                mode="roadmap",
                status=RunStatus.COMPLETED,
                created_at=now,
                updated_at=now,
                planner_version=self._planner_version,
                response_language=request.response_language or "en",
            ),
            problem_definition=problem_definition,
            success_criteria=success_criteria,
            hypotheses=hypotheses,
            solution_options=solution_options,
            experiment_plan=experiments,
            roadmap=roadmap,
            risks=risks,
            fallback_options=fallbacks,
            next_actions=next_actions,
            open_questions=[],
            assumptions=request.assumptions or [],
            failures=[],
            confidence=confidence,
        )

    def _create_problem_definition(self, request: RoadmapRequest) -> ProblemDefinition:
        """Create problem definition from request."""
        ps = request.problem_statement
        derived_from = [ins.insight_id for ins in request.insights[:3]]
        derived_from.extend(c.constraint_id for c in request.constraints[:2])

        return ProblemDefinition(
            problem_id=ps.problem_id,
            title=ps.title,
            statement=ps.statement,
            scope=f"Addressed by {len(request.constraints)} constraints with {len(request.available_assets)} available assets.",
            non_goals=["External system integration", "Authentication"] if ps.desired_outcome else [],
            derived_from=derived_from,
        )

    def _create_success_criteria(self, request: RoadmapRequest) -> list[SuccessCriterion]:
        """Create success criteria from request."""
        criteria = [
            SuccessCriterion(
                criterion_id="sc_01",
                statement=f"Resolve: {request.problem_statement.statement[:80]}...",
                verification_method="Manual review",
                priority=1,
            ),
        ]
        return criteria

    def _create_hypotheses(self, request: RoadmapRequest) -> list[Hypothesis]:
        """Create hypotheses from insights."""
        hypotheses = []
        for i, insight in enumerate(request.insights[:3], start=1):
            hypotheses.append(
                Hypothesis(
                    hypothesis_id=f"hy_{i:02d}",
                    statement=f"Based on insight: {insight.statement[:60]}...",
                    why_this_might_work="Derived from provided insight with supporting context.",
                    priority=i,
                    related_insight_ids=[insight.insight_id],
                    related_constraint_ids=[c.constraint_id for c in request.constraints[:2]],
                    status=HypothesisStatus.OPEN,
                )
            )
        return hypotheses

    def _create_solution_options(
        self, request: RoadmapRequest, hypotheses: list[Hypothesis]
    ) -> list[SolutionOption]:
        """Create solution options."""
        return [
            SolutionOption(
                option_id="op_01",
                title="Primary approach",
                summary="Implement solution addressing key hypotheses.",
                addresses_hypothesis_ids=[h.hypothesis_id for h in hypotheses[:2]],
                tradeoffs=["Requires initial investment", "May need iteration"],
                recommended=True,
            ),
        ]

    def _create_experiments(
        self, request: RoadmapRequest, hypotheses: list[Hypothesis]
    ) -> list[Experiment]:
        """Create experiment plan."""
        return [
            Experiment(
                experiment_id="exp_01",
                title="Validate core hypothesis",
                goal="Verify primary approach feasibility",
                verifies_hypothesis_ids=[hypotheses[0].hypothesis_id] if hypotheses else [],
                method="Prototype implementation and testing",
                success_condition="Prototype passes validation",
                failure_signal="Core assumption invalidated",
                depends_on=[],
                estimated_effort="1-2d",
            ),
        ]

    def _create_roadmap_phases(
        self, request: RoadmapRequest, experiments: list[Experiment]
    ) -> list[RoadmapPhase]:
        """Create roadmap phases."""
        return [
            RoadmapPhase(
                phase_id="ph_01",
                order=1,
                title="Initial Planning",
                goal="Establish foundation and validate approach",
                exit_criteria=["Core hypothesis validated", "Architecture defined"],
                tasks=[
                    RoadmapTask(
                        task_id="tk_01",
                        title="Define architecture",
                        description="Create initial architecture design",
                        deliverable="Architecture document",
                        depends_on=[],
                    ),
                ],
            ),
            RoadmapPhase(
                phase_id="ph_02",
                order=2,
                title="Implementation",
                goal="Build core functionality",
                exit_criteria=["Core features implemented", "Tests passing"],
                tasks=[
                    RoadmapTask(
                        task_id="tk_02",
                        title="Implement core",
                        description="Implement main functionality",
                        deliverable="Working implementation",
                        depends_on=["tk_01"],
                    ),
                ],
            ),
        ]

    def _create_risks(self, request: RoadmapRequest) -> list[Risk]:
        """Create risk assessment."""
        return [
            Risk(
                risk_id="rk_01",
                statement="Scope creep may delay delivery",
                severity="medium",
                mitigation="Define clear scope boundaries and prioritize ruthlessly.",
            ),
        ]

    def _create_fallbacks(self, request: RoadmapRequest) -> list[Fallback]:
        """Create fallback options."""
        return [
            Fallback(
                fallback_id="fb_01",
                trigger="Primary approach fails",
                statement="Pivot to alternative approach",
                tradeoff="May require rework and extended timeline.",
            ),
        ]

    def _create_next_actions(self, roadmap: list[RoadmapPhase]) -> list[NextAction]:
        """Create next actions from roadmap."""
        actions = []
        if roadmap and roadmap[0].tasks:
            for i, task in enumerate(roadmap[0].tasks[:3], start=1):
                actions.append(
                    NextAction(
                        action_id=f"na_{i:02d}",
                        title=task.title,
                        description=task.description,
                        deliverable=task.deliverable,
                        depends_on=[],
                    )
                )
        return actions

    def _check_broad_problem(self, request: RoadmapRequest) -> list[FailureItem] | None:
        """Check if the problem is too broad for planning.

        Args:
            request: The request to check.

        Returns:
            List of failure items if problem is too broad, None otherwise.
        """
        # Simple heuristic: if problem statement is very short or vague
        statement = request.problem_statement.statement
        if len(statement) < 20:
            return [
                FailureItem(
                    failure_id="fl_01",
                    type="input_gap",
                    summary="Problem statement is too brief for meaningful planning.",
                    recoverable=True,
                )
            ]
        return None

    def _create_failure_response(
        self,
        run_id: str,
        now: datetime,
        problem_id: str,
        title: str,
        errors: list[str],
    ) -> RoadmapResponse:
        """Create a failure response for validation errors."""
        return RoadmapResponse(
            schema_version="1.0.0",
            run=RunMeta(
                run_id=run_id,
                mode="roadmap",
                status=RunStatus.FAILED,
                created_at=now,
                updated_at=now,
                planner_version=self._planner_version,
                response_language="en",
            ),
            problem_definition=ProblemDefinition(
                problem_id=problem_id,
                title=title,
                statement="Validation failed",
                scope="N/A",
                non_goals=[],
                derived_from=[],
            ),
            success_criteria=[],
            hypotheses=[],
            solution_options=[],
            experiment_plan=[],
            roadmap=[],
            risks=[],
            fallback_options=[],
            next_actions=[],
            open_questions=[],
            assumptions=[],
            failures=[
                FailureItem(
                    failure_id="fl_01",
                    type="input_gap",
                    summary=errors[0] if errors else "Validation failed",
                    recoverable=True,
                )
            ],
            confidence=Confidence(score=0.0, reason="Request validation failed."),
        )

    def _create_partial_response(
        self,
        request: RoadmapRequest,
        run_id: str,
        now: datetime,
        failures: list[FailureItem],
    ) -> RoadmapResponse:
        """Create a partial response for broad problems."""
        ps = request.problem_statement
        return RoadmapResponse(
            schema_version="1.0.0",
            run=RunMeta(
                run_id=run_id,
                mode="roadmap",
                status=RunStatus.PARTIAL,
                created_at=now,
                updated_at=now,
                planner_version=self._planner_version,
                response_language=request.response_language or "en",
            ),
            problem_definition=ProblemDefinition(
                problem_id=ps.problem_id,
                title=ps.title,
                statement=ps.statement,
                scope="Too broad for complete planning",
                non_goals=[],
                derived_from=[],
            ),
            success_criteria=[],
            hypotheses=[],
            solution_options=[],
            experiment_plan=[],
            roadmap=[],
            risks=[],
            fallback_options=[],
            next_actions=[],
            open_questions=[
                OpenQuestion(
                    question_id="oq_01",
                    statement="Problem scope needs clarification",
                    blocking=True,
                    affects=["roadmap generation"],
                )
            ],
            assumptions=[],
            failures=failures,
            confidence=Confidence(score=0.3, reason="Problem is too broad for complete planning."),
        )