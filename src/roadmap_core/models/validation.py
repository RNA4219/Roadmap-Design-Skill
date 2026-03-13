"""Validation-result models for Roadmap Design Skill."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ValidationIssue(BaseModel):
    """Single validation issue item."""

    code: str = Field(min_length=1)
    field: str = Field(min_length=1)
    message: str = Field(min_length=1)


class ValidationResult(BaseModel):
    """Structured validation result shared across wrappers."""

    schema_version: str = "1.0.0"
    mode: str = "roadmap"
    valid: bool
    errors: list[ValidationIssue] = Field(default_factory=list)
    warnings: list[ValidationIssue] = Field(default_factory=list)

    @classmethod
    def from_issues(
        cls,
        errors: list[ValidationIssue] | None = None,
        warnings: list[ValidationIssue] | None = None,
    ) -> "ValidationResult":
        """Build a validation result from issue lists."""
        error_items = errors or []
        return cls(
            valid=len(error_items) == 0,
            errors=error_items,
            warnings=warnings or [],
        )

    @classmethod
    def invalid_json(cls, message: str) -> "ValidationResult":
        """Create a validation result for malformed JSON input."""
        return cls.from_issues(
            errors=[
                ValidationIssue(
                    code="INVALID_JSON",
                    field="$",
                    message=message,
                )
            ]
        )

    def model_dump_json(self, **kwargs: Any) -> str:
        """Keep type checkers happy when callers serialize directly."""
        return super().model_dump_json(**kwargs)
