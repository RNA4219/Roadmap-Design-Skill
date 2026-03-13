"""Contract tests for JSON Schema validation."""

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator


SCHEMAS_DIR = Path(__file__).parent.parent.parent / "schemas"
EXAMPLES_DIR = Path(__file__).parent.parent.parent / "examples"


@pytest.fixture
def request_schema():
    """Load request schema."""
    with open(SCHEMAS_DIR / "roadmap-request.schema.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def response_schema():
    """Load response schema."""
    with open(SCHEMAS_DIR / "roadmap-response.schema.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def validation_result_schema():
    """Load validation-result schema."""
    with open(SCHEMAS_DIR / "validation-result.schema.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def error_schema():
    """Load error schema."""
    with open(SCHEMAS_DIR / "error.schema.json", encoding="utf-8") as f:
        return json.load(f)


class TestRequestSchema:
    """Tests for request schema validation."""

    @pytest.mark.parametrize(
        "filename",
        [
            "request.minimal.json",
            "request.full.json",
            "request.ai_agent_builder.json",
            "request.from_insight_agent.json",
        ],
    )
    def test_request_examples_valid(self, request_schema, filename):
        """Test that request examples are valid."""
        with open(EXAMPLES_DIR / filename, encoding="utf-8") as f:
            data = json.load(f)

        validator = Draft202012Validator(request_schema)
        errors = list(validator.iter_errors(data))
        assert errors == [], f"Validation errors in {filename}: {errors}"


class TestResponseSchema:
    """Tests for response schema validation."""

    @pytest.mark.parametrize(
        "filename",
        [
            "response.success.json",
            "response.failure.json",
            "response.ai_agent_builder.json",
        ],
    )
    def test_response_examples_valid(self, response_schema, filename):
        """Test that response examples are valid."""
        with open(EXAMPLES_DIR / filename, encoding="utf-8") as f:
            data = json.load(f)

        validator = Draft202012Validator(response_schema)
        errors = list(validator.iter_errors(data))
        assert errors == [], f"Validation errors in {filename}: {errors}"


class TestValidationResultSchema:
    """Tests for validation-result schema validation."""

    @pytest.mark.parametrize(
        "filename",
        [
            "validation.success.json",
            "validation.failure.json",
        ],
    )
    def test_validation_result_examples_valid(self, validation_result_schema, filename):
        """Test that validation-result examples are valid."""
        with open(EXAMPLES_DIR / filename, encoding="utf-8") as f:
            data = json.load(f)

        validator = Draft202012Validator(validation_result_schema)
        errors = list(validator.iter_errors(data))
        assert errors == [], f"Validation errors in {filename}: {errors}"


class TestErrorSchema:
    """Tests for error schema validation."""

    def test_error_schema_has_required_fields(self, error_schema):
        """Test that error schema has all required fields."""
        required = error_schema.get("required", [])
        assert "schema_version" in required
        assert "error_code" in required
        assert "message" in required
        assert "details" in required
        assert "trace_id" in required

    def test_error_sample_valid(self, error_schema):
        """Test that a sample error is valid."""
        sample_error = {
            "schema_version": "1.0.0",
            "error_code": "INVALID_INPUT",
            "message": "Test error",
            "details": {"field": "test"},
            "trace_id": "test-123",
        }

        validator = Draft202012Validator(error_schema)
        errors = list(validator.iter_errors(sample_error))
        assert errors == [], f"Validation errors: {errors}"
