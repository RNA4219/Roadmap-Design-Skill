"""MCP server for Roadmap Design Skill."""

from __future__ import annotations

import json
from typing import Any

from pydantic import ValidationError

from roadmap_core.models.error import ErrorResponse
from roadmap_core.models.request import RoadmapRequest
from roadmap_core.planner.roadmap_planner import RoadmapPlanner

# MCP tool definitions
TOOLS = [
    {
        "name": "roadmap_run",
        "description": "Generate a roadmap from a problem statement with insights and constraints.",
        "inputSchema": {
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
        },
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
]


class MCPServer:
    """Simple MCP server implementation for Roadmap Design Skill."""

    def __init__(self) -> None:
        """Initialize the MCP server."""
        self._planner = RoadmapPlanner()

    def list_tools(self) -> list[dict[str, Any]]:
        """List available tools.

        Returns:
            List of tool definitions.
        """
        return TOOLS

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Call a tool by name.

        Args:
            name: Tool name.
            arguments: Tool arguments.

        Returns:
            Tool result.
        """
        if name == "roadmap_run":
            return self._run_roadmap(arguments)
        elif name == "roadmap_validate":
            return self._validate_request(arguments.get("request", {}))
        else:
            return {"error": f"Unknown tool: {name}"}

    def _run_roadmap(self, request: dict[str, Any]) -> dict[str, Any]:
        """Run roadmap generation.

        Args:
            request: The roadmap request.

        Returns:
            Generated roadmap or error.
        """
        try:
            validated_request = RoadmapRequest.model_validate(request)
            response = _planner.plan(validated_request)
            return {"content": [{"type": "text", "text": response.model_dump_json()}]}
        except ValidationError as e:
            error = ErrorResponse.invalid_input(
                message="Validation failed",
                details={"errors": e.errors()},
                trace_id="mcp",
            )
            return {"content": [{"type": "text", "text": error.model_dump_json()}], "isError": True}
        except Exception as e:
            error = ErrorResponse.internal_error(
                message=str(e),
                trace_id="mcp",
            )
            return {"content": [{"type": "text", "text": error.model_dump_json()}], "isError": True}

    def _validate_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """Validate a request.

        Args:
            request: The request to validate.

        Returns:
            Validation result.
        """
        try:
            RoadmapRequest.model_validate(request)
            return {
                "content": [
                    {"type": "text", "text": json.dumps({"valid": True, "errors": []})}
                ]
            }
        except ValidationError as e:
            return {
                "content": [
                    {"type": "text", "text": json.dumps({"valid": False, "errors": e.errors()})}
                ]
            }


_planner = RoadmapPlanner()


def run_server() -> None:
    """Run the MCP server (placeholder for actual MCP implementation).

    Note: This is a minimal implementation. For full MCP support,
    integrate with the official MCP Python SDK.
    """
    # Placeholder - actual MCP server would use stdio transport
    server = MCPServer()
    print("MCP server initialized with tools:", [t["name"] for t in server.list_tools()])