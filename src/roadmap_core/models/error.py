"""Error models for Roadmap Design Skill."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ErrorCode(str, Enum):
    """Error code enumeration."""

    INVALID_INPUT = "INVALID_INPUT"
    UNSUPPORTED_SCHEMA_VERSION = "UNSUPPORTED_SCHEMA_VERSION"
    PROCESSING_FAILED = "PROCESSING_FAILED"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class ErrorResponse(BaseModel):
    """Error response model."""

    schema_version: str = "1.0.0"
    error_code: ErrorCode
    message: str = Field(min_length=1)
    details: dict[str, Any] = Field(default_factory=dict)
    trace_id: str = Field(min_length=1)

    @classmethod
    def invalid_input(
        cls, message: str, details: dict[str, Any] | None = None, trace_id: str = "unknown"
    ) -> "ErrorResponse":
        """Create an invalid input error response.

        Args:
            message: Error message.
            details: Additional error details.
            trace_id: Trace ID for debugging.

        Returns:
            ErrorResponse instance.
        """
        return cls(
            error_code=ErrorCode.INVALID_INPUT,
            message=message,
            details=details or {},
            trace_id=trace_id,
        )

    @classmethod
    def unsupported_version(
        cls, version: str, trace_id: str = "unknown"
    ) -> "ErrorResponse":
        """Create an unsupported schema version error response.

        Args:
            version: The unsupported version.
            trace_id: Trace ID for debugging.

        Returns:
            ErrorResponse instance.
        """
        return cls(
            error_code=ErrorCode.UNSUPPORTED_SCHEMA_VERSION,
            message=f"Unsupported schema version: {version}",
            details={"provided_version": version, "supported_versions": ["1.0.0"]},
            trace_id=trace_id,
        )

    @classmethod
    def processing_failed(
        cls, message: str, details: dict[str, Any] | None = None, trace_id: str = "unknown"
    ) -> "ErrorResponse":
        """Create a processing failed error response.

        Args:
            message: Error message.
            details: Additional error details.
            trace_id: Trace ID for debugging.

        Returns:
            ErrorResponse instance.
        """
        return cls(
            error_code=ErrorCode.PROCESSING_FAILED,
            message=message,
            details=details or {},
            trace_id=trace_id,
        )

    @classmethod
    def internal_error(
        cls, message: str = "Internal error occurred", trace_id: str = "unknown"
    ) -> "ErrorResponse":
        """Create an internal error response.

        Args:
            message: Error message.
            trace_id: Trace ID for debugging.

        Returns:
            ErrorResponse instance.
        """
        return cls(
            error_code=ErrorCode.INTERNAL_ERROR,
            message=message,
            details={},
            trace_id=trace_id,
        )