"""Shared request-payload validation helpers."""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from roadmap_core.models.request import RoadmapRequest
from roadmap_core.models.validation import ValidationIssue, ValidationResult


def validate_request_payload(data: Any) -> ValidationResult:
    """Validate raw request payloads into a shared validation result."""
    warnings = _build_warnings(data)
    try:
        RoadmapRequest.model_validate(data)
        return ValidationResult.from_issues(warnings=warnings)
    except ValidationError as exc:
        return ValidationResult.from_issues(
            errors=[_normalize_pydantic_error(error) for error in exc.errors()],
            warnings=warnings,
        )


def _build_warnings(data: Any) -> list[ValidationIssue]:
    if not isinstance(data, dict):
        return []

    warnings: list[ValidationIssue] = []
    if "response_language" not in data:
        warnings.append(
            ValidationIssue(
                code="DEFAULT_LANGUAGE",
                field="response_language",
                message="response_language is omitted and would default to ja",
            )
        )
    return warnings


def _normalize_pydantic_error(error: dict[str, Any]) -> ValidationIssue:
    loc = error.get("loc", ())
    field = ".".join(str(item) for item in loc) if loc else "$"
    error_type = str(error.get("type", "validation_error"))
    message = str(error.get("msg", "Invalid input"))

    return ValidationIssue(
        code=_error_code(error_type, field),
        field=field,
        message=message,
    )


def _error_code(error_type: str, field: str) -> str:
    if error_type == "missing":
        return "MISSING_REQUIRED_FIELD"
    if error_type in {"json_invalid", "json_type"}:
        return "INVALID_JSON"
    if error_type in {"dict_type", "model_type", "list_type", "string_type"}:
        return "INVALID_TYPE"
    if error_type == "enum":
        return "INVALID_ENUM"
    if error_type in {"literal_error", "string_pattern_mismatch"}:
        return "INVALID_VALUE"
    if error_type == "too_short" and field in {"insights", "constraints", "available_assets"}:
        return "EMPTY_ARRAY"
    if error_type in {"too_short", "string_too_short"}:
        return "TOO_SHORT"
    return "VALIDATION_ERROR"
