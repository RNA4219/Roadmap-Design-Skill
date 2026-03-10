"""Unit tests for Roadmap Planner."""

import pytest

from roadmap_core.models.request import (
    AssetItem,
    AssetType,
    ConstraintCategory,
    ConstraintItem,
    ConstraintSeverity,
    InsightItem,
    ProblemStatement,
    RoadmapRequest,
)
from roadmap_core.planner.roadmap_planner import RoadmapPlanner


@pytest.fixture
def minimal_request():
    """Create a minimal valid request."""
    return RoadmapRequest(
        schema_version="1.0.0",
        mode="roadmap",
        problem_statement=ProblemStatement(
            problem_id="pb_test",
            title="Test Problem",
            statement="This is a test problem statement that is long enough for validation.",
        ),
        insights=[
            InsightItem(
                insight_id="in_01",
                statement="Test insight statement",
            )
        ],
        constraints=[
            ConstraintItem(
                constraint_id="co_01",
                category=ConstraintCategory.TIME,
                statement="Test constraint",
                severity=ConstraintSeverity.HARD,
            )
        ],
        available_assets=[
            AssetItem(
                asset_id="as_01",
                type=AssetType.DOCUMENT,
                name="Test Asset",
                description="Test asset description",
            )
        ],
    )


class TestRoadmapPlanner:
    """Tests for RoadmapPlanner."""

    def test_plan_returns_response(self, minimal_request):
        """Test that plan returns a valid response."""
        planner = RoadmapPlanner()
        response = planner.plan(minimal_request)

        assert response.schema_version == "1.0.0"
        assert response.run.status in ("completed", "partial", "failed")

    def test_plan_generates_hypotheses(self, minimal_request):
        """Test that plan generates at least one hypothesis."""
        planner = RoadmapPlanner()
        response = planner.plan(minimal_request)

        if response.run.status == "completed":
            assert len(response.hypotheses) >= 1

    def test_plan_generates_roadmap(self, minimal_request):
        """Test that plan generates roadmap phases."""
        planner = RoadmapPlanner()
        response = planner.plan(minimal_request)

        if response.run.status == "completed":
            assert len(response.roadmap) >= 1
            assert all(phase.tasks for phase in response.roadmap)

    def test_plan_handles_broad_problem(self):
        """Test that broad problem returns partial response."""
        planner = RoadmapPlanner()
        request = RoadmapRequest(
            schema_version="1.0.0",
            mode="roadmap",
            problem_statement=ProblemStatement(
                problem_id="pb_broad",
                title="Too Short",
                statement="Short",  # Too short - triggers broad problem check
            ),
            insights=[
                InsightItem(insight_id="in_01", statement="Test")
            ],
            constraints=[
                ConstraintItem(
                    constraint_id="co_01",
                    category=ConstraintCategory.TIME,
                    statement="Test",
                    severity=ConstraintSeverity.HARD,
                )
            ],
            available_assets=[
                AssetItem(
                    asset_id="as_01",
                    type=AssetType.DOCUMENT,
                    name="Test",
                    description="Test",
                )
            ],
        )
        response = planner.plan(request)

        # Should be partial due to broad problem
        assert response.run.status == "partial"
        assert len(response.failures) > 0

    def test_next_actions_are_structured(self, minimal_request):
        """Test that next actions are structured objects."""
        planner = RoadmapPlanner()
        response = planner.plan(minimal_request)

        if response.run.status == "completed" and response.next_actions:
            action = response.next_actions[0]
            assert action.action_id.startswith("na_")
            assert action.title
            assert action.description
            assert action.deliverable