"""HTTP API wrapper using FastAPI."""

from __future__ import annotations

from functools import lru_cache
from json import JSONDecodeError
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from roadmap_core.llm.base import LLMConfig, LLMProviderType
from roadmap_core.models.error import ErrorResponse
from roadmap_core.models.request import RoadmapRequest
from roadmap_core.models.validation import ValidationResult
from roadmap_core.planner.llm_planner import LLMRoadmapPlanner
from roadmap_core.planner.roadmap_planner import RoadmapPlanner
from roadmap_core.schema_loader import UnknownSchemaKindError, load_schema
from roadmap_core.validators.request_payload_validator import validate_request_payload as build_validation_result

app = FastAPI(
    title="Roadmap Design Skill",
    description="Transform ambiguous problems into implementation-ready roadmaps",
    version="1.1.0",
)


def load_dotenv_if_present() -> None:
    """Load the nearest .env file when python-dotenv is available."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return

    candidates = [
        Path(".env"),
        Path(__file__).resolve().parents[3] / ".env",
    ]
    for env_path in candidates:
        if env_path.exists():
            load_dotenv(env_path)
            return


load_dotenv_if_present()


@lru_cache(maxsize=1)
def get_planner() -> RoadmapPlanner | LLMRoadmapPlanner:
    """Create the planner lazily so startup stays fast."""
    llm_config = LLMConfig.from_env(enable_var="RDS_HTTP_USE_LLM", default_enabled=False)
    if llm_config.provider == LLMProviderType.NONE:
        return RoadmapPlanner()
    return LLMRoadmapPlanner(llm_config=llm_config)


@app.post("/v1/run")
@app.post("/v1/roadmaps:plan")
async def run_roadmap(request: dict) -> dict:
    """Run roadmap generation."""
    try:
        schema_version = request.get("schema_version")
        if schema_version != "1.0.0":
            error = ErrorResponse.unsupported_version(
                version=str(schema_version),
                trace_id="http",
            )
            raise HTTPException(status_code=400, detail=error.model_dump())

        validated_request = RoadmapRequest.model_validate(request)
        planner = get_planner()
        if isinstance(planner, LLMRoadmapPlanner):
            response = await planner.plan_async(validated_request)
        else:
            response = planner.plan(validated_request)
        return response.model_dump(mode="json")

    except ValidationError as exc:
        error = ErrorResponse.invalid_input(
            message="Request validation failed",
            details={"errors": exc.errors()},
            trace_id="http",
        )
        raise HTTPException(status_code=400, detail=error.model_dump())
    except HTTPException:
        raise
    except Exception as exc:
        error = ErrorResponse.internal_error(
            message=str(exc),
            trace_id="http",
        )
        raise HTTPException(status_code=500, detail=error.model_dump())


@app.post("/v1/validate")
@app.post("/v1/roadmaps:validate")
async def validate_roadmap_request(request: Request) -> dict:
    """Validate a roadmap request without generating."""
    try:
        payload = await request.json()
    except JSONDecodeError as exc:
        return ValidationResult.invalid_json(f"Invalid JSON: {exc.msg}").model_dump(mode="json")
    except Exception as exc:
        error = ErrorResponse.internal_error(
            message=str(exc),
            trace_id="http-validate",
        )
        raise HTTPException(status_code=500, detail=error.model_dump())

    return build_validation_result(payload).model_dump(mode="json")


@app.get("/v1/roadmaps:schema/{kind}")
async def get_schema_document(kind: str) -> dict:
    """Return one of the canonical JSON schemas."""
    try:
        return load_schema(kind)
    except UnknownSchemaKindError as exc:
        error = ErrorResponse.invalid_input(
            message=str(exc),
            details={"kind": kind},
            trace_id="http-schema",
        )
        raise HTTPException(status_code=400, detail=error.model_dump())
    except Exception as exc:
        error = ErrorResponse.internal_error(
            message=str(exc),
            trace_id="http-schema",
        )
        raise HTTPException(status_code=500, detail=error.model_dump())


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    planner = get_planner()
    llm_enabled = isinstance(planner, LLMRoadmapPlanner) and planner.is_llm_available()
    llm_config = LLMConfig.from_env(enable_var="RDS_HTTP_USE_LLM", default_enabled=False)
    return {
        "status": "healthy",
        "version": "1.1.0",
        "llm_enabled": llm_enabled,
        "llm_provider": llm_config.provider.value if llm_enabled else "none",
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):  # noqa: ANN001, ARG001
    """Handle HTTP exceptions with error schema compliance."""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail,
    )


def run_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    """Run the HTTP server."""
    uvicorn.run(app, host=host, port=port)
