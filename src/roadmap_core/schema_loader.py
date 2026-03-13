"""Shared schema loading helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SCHEMA_FILES = {
    "request": "roadmap-request.schema.json",
    "response": "roadmap-response.schema.json",
    "validation-result": "validation-result.schema.json",
    "error": "error.schema.json",
}


class UnknownSchemaKindError(ValueError):
    """Raised when a schema kind is not supported."""


def available_schema_kinds() -> tuple[str, ...]:
    """Return supported schema kinds."""
    return tuple(SCHEMA_FILES.keys())


def _resolve_schemas_dir(schemas_dir: Path | None = None) -> Path:
    if schemas_dir is not None:
        return schemas_dir
    return Path(__file__).parent.parent.parent / "schemas"


def get_schema_path(kind: str, schemas_dir: Path | None = None) -> Path:
    """Resolve a schema file path from kind."""
    normalized = kind.strip().lower()
    if normalized not in SCHEMA_FILES:
        supported = ", ".join(available_schema_kinds())
        raise UnknownSchemaKindError(f"Unknown schema kind: {kind}. Supported kinds: {supported}")
    return _resolve_schemas_dir(schemas_dir) / SCHEMA_FILES[normalized]


def load_schema(kind: str, schemas_dir: Path | None = None) -> dict[str, Any]:
    """Load a schema as parsed JSON."""
    with open(get_schema_path(kind, schemas_dir), encoding="utf-8") as f:
        return json.load(f)


def load_schema_text(kind: str, schemas_dir: Path | None = None) -> str:
    """Load a schema as raw JSON text."""
    return get_schema_path(kind, schemas_dir).read_text(encoding="utf-8")
