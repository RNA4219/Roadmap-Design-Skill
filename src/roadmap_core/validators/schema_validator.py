"""Schema validator using JSON Schema."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema
from jsonschema import Draft202012Validator


class SchemaValidator:
    """Validates JSON data against JSON Schema definitions."""

    def __init__(self, schemas_dir: Path | None = None) -> None:
        """Initialize the schema validator.

        Args:
            schemas_dir: Directory containing JSON Schema files.
        """
        if schemas_dir is None:
            schemas_dir = Path(__file__).parent.parent.parent.parent / "schemas"
        self._schemas_dir = schemas_dir
        self._validators: dict[str, Draft202012Validator] = {}
        self._load_schemas()

    def _load_schemas(self) -> None:
        """Load all schema files from the schemas directory."""
        schema_files = {
            "request": "roadmap-request.schema.json",
            "response": "roadmap-response.schema.json",
            "error": "error.schema.json",
        }

        for name, filename in schema_files.items():
            schema_path = self._schemas_dir / filename
            if schema_path.exists():
                with open(schema_path, encoding="utf-8") as f:
                    schema = json.load(f)
                self._validators[name] = Draft202012Validator(schema)

    def validate_request(self, data: dict[str, Any]) -> list[str]:
        """Validate a request against the request schema.

        Args:
            data: The request data to validate.

        Returns:
            List of validation error messages. Empty if valid.
        """
        return self._validate("request", data)

    def validate_response(self, data: dict[str, Any]) -> list[str]:
        """Validate a response against the response schema.

        Args:
            data: The response data to validate.

        Returns:
            List of validation error messages. Empty if valid.
        """
        return self._validate("response", data)

    def validate_error(self, data: dict[str, Any]) -> list[str]:
        """Validate an error response against the error schema.

        Args:
            data: The error data to validate.

        Returns:
            List of validation error messages. Empty if valid.
        """
        return self._validate("error", data)

    def _validate(self, schema_name: str, data: dict[str, Any]) -> list[str]:
        """Validate data against a named schema.

        Args:
            schema_name: Name of the schema to use.
            data: The data to validate.

        Returns:
            List of validation error messages. Empty if valid.
        """
        validator = self._validators.get(schema_name)
        if validator is None:
            return [f"Schema '{schema_name}' not found"]

        errors = []
        for error in validator.iter_errors(data):
            path = ".".join(str(p) for p in error.absolute_path)
            errors.append(f"{path}: {error.message}" if path else error.message)
        return errors

    def is_valid_request(self, data: dict[str, Any]) -> bool:
        """Check if a request is valid.

        Args:
            data: The request data to validate.

        Returns:
            True if valid, False otherwise.
        """
        return len(self.validate_request(data)) == 0

    def is_valid_response(self, data: dict[str, Any]) -> bool:
        """Check if a response is valid.

        Args:
            data: The response data to validate.

        Returns:
            True if valid, False otherwise.
        """
        return len(self.validate_response(data)) == 0