"""Tests for MCP validation and schema contracts."""

from __future__ import annotations

import json
from pathlib import Path

from roadmap_core.validators.schema_validator import SchemaValidator
from wrappers.mcp.server import MCPServer

SCHEMAS_DIR = Path(__file__).parent.parent.parent / "schemas"


class TestMcpValidate:
    """Tests for MCP validate output shape."""

    def test_canonical_validate_tool_returns_validation_result(self):
        server = MCPServer()
        result = server.call_tool(
            "roadmap.validate",
            {
                "schema_version": "1.0.0",
                "mode": "roadmap",
                "problem_statement": {
                    "problem_id": "pb_mcp_invalid",
                    "title": "Invalid MCP request",
                },
                "insights": [],
                "constraints": [],
                "available_assets": [],
            },
        )
        payload = json.loads(result["content"][0]["text"])

        errors = SchemaValidator().validate_validation_result(payload)
        assert errors == []
        assert payload["valid"] is False

    def test_legacy_validate_alias_still_works(self):
        server = MCPServer()
        result = server.call_tool(
            "roadmap_validate",
            {
                "request": {
                    "schema_version": "1.0.0",
                    "mode": "roadmap",
                    "problem_statement": {
                        "problem_id": "pb_mcp_valid",
                        "title": "Valid MCP request",
                        "statement": "Alias should still return a validation result.",
                    },
                    "insights": [{"insight_id": "in_mcp_01", "statement": "MCP insight"}],
                    "constraints": [
                        {
                            "constraint_id": "co_mcp_01",
                            "category": "time",
                            "statement": "MCP constraint",
                            "severity": "soft",
                        }
                    ],
                    "available_assets": [
                        {
                            "asset_id": "as_mcp_01",
                            "type": "document",
                            "name": "MCP asset",
                            "description": "Alias validation asset",
                        }
                    ],
                }
            },
        )
        payload = json.loads(result["content"][0]["text"])

        errors = SchemaValidator().validate_validation_result(payload)
        assert errors == []
        assert payload["valid"] is True


class TestMcpSchema:
    """Tests for the MCP schema tool."""

    def test_schema_tool_returns_request_schema(self):
        server = MCPServer()
        result = server.call_tool("roadmap.schema", {"kind": "request"})
        payload = json.loads(result["content"][0]["text"])
        expected = json.loads((SCHEMAS_DIR / "roadmap-request.schema.json").read_text(encoding="utf-8"))

        assert payload == expected

    def test_schema_tool_invalid_kind_returns_error_envelope(self):
        server = MCPServer()
        result = server.call_tool("roadmap.schema", {"kind": "unknown"})
        payload = json.loads(result["content"][0]["text"])

        assert result["isError"] is True
        assert payload["error_code"] == "INVALID_INPUT"
