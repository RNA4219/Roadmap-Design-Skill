"""Request validator for business logic validation."""

from __future__ import annotations

from roadmap_core.models.request import RoadmapRequest


class ValidationError(Exception):
    """Validation error exception."""

    def __init__(self, errors: list[str]) -> None:
        """Initialize validation error.

        Args:
            errors: List of validation error messages.
        """
        self.errors = errors
        super().__init__(f"Validation failed: {', '.join(errors)}")


class RequestValidator:
    """Validates roadmap requests for business logic compliance."""

    def validate(self, request: RoadmapRequest) -> list[str]:
        """Validate a roadmap request.

        Args:
            request: The request to validate.

        Returns:
            List of validation error messages. Empty if valid.
        """
        errors: list[str] = []

        # Check for empty required collections
        if not request.insights:
            errors.append("insights cannot be empty")
        if not request.constraints:
            errors.append("constraints cannot be empty")
        if not request.available_assets:
            errors.append("available_assets cannot be empty")

        # Check problem statement
        if not request.problem_statement.statement.strip():
            errors.append("problem_statement.statement cannot be empty")

        return errors

    def validate_and_raise(self, request: RoadmapRequest) -> None:
        """Validate and raise if invalid.

        Args:
            request: The request to validate.

        Raises:
            ValidationError: If validation fails.
        """
        errors = self.validate(request)
        if errors:
            raise ValidationError(errors)