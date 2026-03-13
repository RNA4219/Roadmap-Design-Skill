"""JSON presenter for formatting roadmap outputs."""

from __future__ import annotations

import json
from typing import Any

from roadmap_core.models.error import ErrorResponse
from roadmap_core.models.response import RoadmapResponse
from roadmap_core.models.validation import ValidationResult


class JsonPresenter:
    """Presents roadmap outputs as JSON."""

    @staticmethod
    def present_response(response: RoadmapResponse, indent: int = 2) -> str:
        """Format a roadmap response as JSON."""
        return response.model_dump_json(indent=indent)

    @staticmethod
    def present_error(error: ErrorResponse, indent: int = 2) -> str:
        """Format an error response as JSON."""
        return error.model_dump_json(indent=indent)

    @staticmethod
    def present_validation_result(result: ValidationResult, indent: int = 2) -> str:
        """Format a validation result as JSON."""
        return result.model_dump_json(indent=indent)

    @staticmethod
    def parse_request(json_str: str) -> dict[str, Any]:
        """Parse a JSON request string."""
        return json.loads(json_str)
