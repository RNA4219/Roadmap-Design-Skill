"""MCP server for Roadmap Design Skill."""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from roadmap_core.models.error import ErrorResponse
from roadmap_core.models.request import RoadmapRequest
from roadmap_core.planner.roadmap_planner import RoadmapPlanner
from roadmap_core.schema_loader import UnknownSchemaKindError, available_schema_kinds, load_schema_text
from roadmap_core.validators.request_payload_validator import validate_request_payload

REQUEST_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "schema_version": {"type": "string", "const": "1.0.0"},
        "mode": {"type": "string", "const": "roadmap"},
        "problem_statement": {
            "type": "object",
            "properties": {
                "problem_id": {"type": "string"},
                "title": {"type": "string"},
                "statement": {"type": "string"},
            },
            "required": ["problem_id", "title", "statement"],
        },
        "insights": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "insight_id": {"type": "string"},
                    "statement": {"type": "string"},
                },
                "required": ["insight_id", "statement"],
            },
        },
        "constraints": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "constraint_id": {"type": "string"},
                    "category": {"type": "string"},
                    "statement": {"type": "string"},
                    "severity": {"type": "string"},
                },
                "required": ["constraint_id", "category", "statement", "severity"],
            },
        },
        "available_assets": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "asset_id": {"type": "string"},
                    "type": {"type": "string"},
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["asset_id", "type", "name", "description"],
            },
        },
    },
    "required": [
        "schema_version",
        "mode",
        "problem_statement",
        "insights",
        "constraints",
        "available_assets",
    ],
}

TOOLS = [
    {
        "name": "roadmap_run",
        "description": "Generate a roadmap from a problem statement with insights and constraints.",
        "inputSchema": REQUEST_INPUT_SCHEMA,
    },
    {
        "name": "roadmap.plan",
        "description": "Generate a roadmap from a problem statement with insights and constraints.",
        "inputSchema": REQUEST_INPUT_SCHEMA,
    },
    {
        "name": "roadmap_validate",
        "description": "Validate a roadmap request without generating.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "request": {"type": "object"},
            },
            "required": ["request"],
        },
    },
    {
        "name": "roadmap.validate",
        "description": "Validate a roadmap request without generating.",
        "inputSchema": REQUEST_INPUT_SCHEMA,
    },
    {
        "name": "roadmap.schema",
        "description": "Return one of the canonical JSON schemas.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "kind": {
                    "type": "string",
                    "enum": list(available_schema_kinds()),
                }
            },
            "required": ["kind"],
        },
    },
]


class MCPServer:
    """Simple MCP server implementation for Roadmap Design Skill."""

    def __init__(self) -> None:
        self._planner = RoadmapPlanner()

    def list_tools(self) -> list[dict[str, Any]]:
        return TOOLS

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if name in {"roadmap_run", "roadmap.plan"}:
            return self._run_roadmap(arguments)
        if name in {"roadmap_validate", "roadmap.validate"}:
            payload = arguments.get("request", arguments)
            return self._validate_request(payload)
        if name == "roadmap.schema":
            return self._schema(arguments)
        return {"error": f"Unknown tool: {name}"}

    def _run_roadmap(self, request: dict[str, Any]) -> dict[str, Any]:
        try:
            validated_request = RoadmapRequest.model_validate(request)
            response = self._planner.plan(validated_request)
            return {"content": [{"type": "text", "text": response.model_dump_json()}]}
        except ValidationError as exc:
            error = ErrorResponse.invalid_input(
                message="Validation failed",
                details={"errors": exc.errors()},
                trace_id="mcp",
            )
            return {"content": [{"type": "text", "text": error.model_dump_json()}], "isError": True}
        except Exception as exc:
            error = ErrorResponse.internal_error(
                message=str(exc),
                trace_id="mcp",
            )
            return {"content": [{"type": "text", "text": error.model_dump_json()}], "isError": True}

    def _validate_request(self, request: dict[str, Any]) -> dict[str, Any]:
        result = validate_request_payload(request)
        return {
            "content": [
                {"type": "text", "text": result.model_dump_json()}
            ]
        }

    def _schema(self, arguments: dict[str, Any]) -> dict[str, Any]:
        kind = str(arguments.get("kind", ""))
        try:
            schema_text = load_schema_text(kind)
            return {
                "content": [
                    {"type": "text", "text": schema_text}
                ]
            }
        except UnknownSchemaKindError as exc:
            error = ErrorResponse.invalid_input(
                message=str(exc),
                details={"kind": kind},
                trace_id="mcp-schema",
            )
            return {"content": [{"type": "text", "text": error.model_dump_json()}], "isError": True}
        except Exception as exc:
            error = ErrorResponse.internal_error(
                message=str(exc),
                trace_id="mcp-schema",
            )
            return {"content": [{"type": "text", "text": error.model_dump_json()}], "isError": True}


def run_server() -> None:
    """Run the MCP server (placeholder for actual MCP implementation)."""
    server = MCPServer()
    print("MCP server initialized with tools:", [tool["name"] for tool in server.list_tools()])
