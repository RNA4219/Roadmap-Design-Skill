"""Tests for HTTP validate and schema endpoints."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("fastapi.testclient")

from fastapi.testclient import TestClient

from roadmap_core.validators.schema_validator import SchemaValidator
from wrappers.http.app import app

SCHEMAS_DIR = Path(__file__).parent.parent.parent / "schemas"


class TestHttpValidate:
    """Tests for the HTTP validate endpoint."""

    def test_validate_endpoint_returns_validation_result_for_invalid_request(self):
        client = TestClient(app)
        response = client.post(
            "/v1/roadmaps:validate",
            json={
                "schema_version": "1.0.0",
                "mode": "roadmap",
                "problem_statement": {
                    "problem_id": "pb_http_invalid",
                    "title": "Invalid",
                },
                "insights": [],
                "constraints": [],
                "available_assets": [],
            },
        )

        assert response.status_code == 200
        payload = response.json()
        errors = SchemaValidator().validate_validation_result(payload)
        assert errors == []
        assert payload["valid"] is False

    def test_validate_alias_endpoint_returns_validation_result_for_valid_request(self):
        client = TestClient(app)
        response = client.post(
            "/v1/validate",
            json={
                "schema_version": "1.0.0",
                "mode": "roadmap",
                "problem_statement": {
                    "problem_id": "pb_http_valid",
                    "title": "Valid",
                    "statement": "Validate endpoint should return a shared shape.",
                },
                "insights": [{"insight_id": "in_http_01", "statement": "Test insight"}],
                "constraints": [
                    {
                        "constraint_id": "co_http_01",
                        "category": "time",
                        "statement": "Test constraint",
                        "severity": "hard",
                    }
                ],
                "available_assets": [
                    {
                        "asset_id": "as_http_01",
                        "type": "document",
                        "name": "HTTP fixture",
                        "description": "Test asset",
                    }
                ],
            },
        )

        assert response.status_code == 200
        payload = response.json()
        errors = SchemaValidator().validate_validation_result(payload)
        assert errors == []
        assert payload["valid"] is True


class TestHttpSchema:
    """Tests for the HTTP schema endpoint."""

    def test_schema_endpoint_returns_request_schema(self):
        client = TestClient(app)
        response = client.get("/v1/roadmaps:schema/request")
        expected = json.loads((SCHEMAS_DIR / "roadmap-request.schema.json").read_text(encoding="utf-8"))

        assert response.status_code == 200
        assert response.json() == expected

    def test_schema_endpoint_invalid_kind_returns_error_envelope(self):
        client = TestClient(app)
        response = client.get("/v1/roadmaps:schema/unknown")
        payload = response.json()

        assert response.status_code == 400
        assert payload["error_code"] == "INVALID_INPUT"
