"""JSON presenter for formatting roadmap outputs."""

from __future__ import annotations

import json
from typing import Any

from roadmap_core.models.error import ErrorResponse
from roadmap_core.models.response import RoadmapResponse


class JsonPresenter:
    """Presents roadmap outputs as JSON."""

    @staticmethod
    def present_response(response: RoadmapResponse, indent: int = 2) -> str:
        """Format a roadmap response as JSON.

        Args:
            response: The response to format.
            indent: JSON indentation level.

        Returns:
            JSON string representation.
        """
        return response.model_dump_json(indent=indent)

    @staticmethod
    def present_error(error: ErrorResponse, indent: int = 2) -> str:
        """Format an error response as JSON.

        Args:
            error: The error to format.
            indent: JSON indentation level.

        Returns:
            JSON string representation.
        """
        return error.model_dump_json(indent=indent)

    @staticmethod
    def parse_request(json_str: str) -> dict[str, Any]:
        """Parse a JSON request string.

        Args:
            json_str: JSON string to parse.

        Returns:
            Parsed dictionary.
        """
        return json.loads(json_str)