"""Test placeholders for validators."""

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
from roadmap_core.validators.request_validator import RequestValidator


class TestRequestValidator:
    """Tests for RequestValidator."""

    @pytest.fixture
    def validator(self):
        """Create a validator instance."""
        return RequestValidator()

    def test_valid_request_passes(self, validator):
        """Test that valid request passes validation."""
        request = RoadmapRequest(
            schema_version="1.0.0",
            mode="roadmap",
            problem_statement=ProblemStatement(
                problem_id="pb_test",
                title="Test",
                statement="Test statement",
            ),
            insights=[InsightItem(insight_id="in_01", statement="Test")],
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
        errors = validator.validate(request)
        assert errors == []

    def test_empty_insights_fails(self, validator):
        """Test that empty insights fails validation."""
        request = RoadmapRequest(
            schema_version="1.0.0",
            mode="roadmap",
            problem_statement=ProblemStatement(
                problem_id="pb_test",
                title="Test",
                statement="Test",
            ),
            insights=[],
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
        # This should fail at Pydantic validation level, not business logic
        # But if it somehow gets through, our validator should catch it
        with pytest.raises(Exception):
            RoadmapRequest.model_validate(request.model_dump())