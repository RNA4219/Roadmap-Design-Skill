"""Integration tests for end-to-end functionality."""

import json

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
from roadmap_core.validators.schema_validator import SchemaValidator


class TestEndToEnd:
    """End-to-end integration tests."""

    @pytest.fixture
    def planner(self):
        """Create a planner instance."""
        return RoadmapPlanner()

    @pytest.fixture
    def schema_validator(self):
        """Create a schema validator instance."""
        return SchemaValidator()

    @pytest.fixture
    def valid_request(self):
        """Create a valid request."""
        return RoadmapRequest(
            schema_version="1.0.0",
            mode="roadmap",
            response_language="en",
            problem_statement=ProblemStatement(
                problem_id="pb_integration",
                title="Integration Test Problem",
                statement="This is a comprehensive test of the roadmap generation pipeline.",
                background="Testing the full flow from request to response.",
            ),
            insights=[
                InsightItem(
                    insight_id="in_01",
                    statement="First insight about the problem",
                    importance="high",
                ),
                InsightItem(
                    insight_id="in_02",
                    statement="Second insight providing additional context",
                ),
            ],
            constraints=[
                ConstraintItem(
                    constraint_id="co_time",
                    category=ConstraintCategory.TIME,
                    statement="Must complete within 2 weeks",
                    severity=ConstraintSeverity.HARD,
                ),
                ConstraintItem(
                    constraint_id="co_resource",
                    category=ConstraintCategory.RESOURCE,
                    statement="Limited budget available",
                    severity=ConstraintSeverity.SOFT,
                ),
            ],
            available_assets=[
                AssetItem(
                    asset_id="as_docs",
                    type=AssetType.DOCUMENT,
                    name="Existing Documentation",
                    description="Design docs and specifications",
                ),
                AssetItem(
                    asset_id="as_team",
                    type=AssetType.PEOPLE,
                    name="Development Team",
                    description="3 developers available",
                ),
            ],
        )

    def test_valid_request_produces_valid_response(
        self, planner, schema_validator, valid_request
    ):
        """Test that a valid request produces a schema-valid response."""
        # Generate response
        response = planner.plan(valid_request)

        # Convert to dict for schema validation (use mode='json' for datetime serialization)
        response_dict = response.model_dump(mode='json')

        # Validate against schema
        errors = schema_validator.validate_response(response_dict)
        assert errors == [], f"Schema validation errors: {errors}"

    def test_response_status_consistency(self, planner, valid_request):
        """Test that response status is consistent with content."""
        response = planner.plan(valid_request)

        if response.run.status == "completed":
            assert len(response.roadmap) > 0
            assert len(response.hypotheses) >= 2
            assert len(response.next_actions) > 0
            assert response.confidence.score > 0.5
        elif response.run.status == "partial":
            assert len(response.failures) > 0 or len(response.open_questions) > 0
        elif response.run.status == "failed":
            assert len(response.failures) > 0

    def test_experiments_verify_hypotheses(self, planner, valid_request):
        """Test that experiments reference valid hypothesis IDs."""
        response = planner.plan(valid_request)

        if response.run.status == "completed" and response.experiment_plan:
            hypothesis_ids = {h.hypothesis_id for h in response.hypotheses}
            for experiment in response.experiment_plan:
                for hyp_id in experiment.verifies_hypothesis_ids:
                    assert hyp_id in hypothesis_ids, (
                        f"Experiment {experiment.experiment_id} references "
                        f"unknown hypothesis {hyp_id}"
                    )

    def test_roadmap_phase_ordering(self, planner, valid_request):
        """Test that roadmap phases are properly ordered."""
        response = planner.plan(valid_request)

        if response.run.status == "completed" and response.roadmap:
            orders = [phase.order for phase in response.roadmap]
            assert orders == sorted(orders), "Phases are not in order"
            assert orders[0] == 1, "First phase should have order 1"