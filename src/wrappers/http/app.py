"""HTTP API wrapper using FastAPI."""

from __future__ import annotations

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from roadmap_core.llm.base import LLMConfig
from roadmap_core.models.error import ErrorResponse
from roadmap_core.models.request import RoadmapRequest
from roadmap_core.planner.llm_planner import LLMRoadmapPlanner

app = FastAPI(
    title="Roadmap Design Skill",
    description="Transform ambiguous problems into implementation-ready roadmaps",
    version="1.1.0",
)

# Initialize LLM config from environment
_llm_config = LLMConfig.from_env()
_planner = LLMRoadmapPlanner(llm_config=_llm_config)


@app.post("/v1/run")
async def run_roadmap(request: dict) -> dict:
    """Run roadmap generation.

    Args:
        request: The roadmap request as a dictionary.

    Returns:
        The generated roadmap response.

    Raises:
        HTTPException: If request is invalid or processing fails.
    """
    try:
        # Validate schema version
        schema_version = request.get("schema_version")
        if schema_version != "1.0.0":
            error = ErrorResponse.unsupported_version(
                version=str(schema_version),
                trace_id="http",
            )
            raise HTTPException(status_code=400, detail=error.model_dump())

        # Parse and validate request
        validated_request = RoadmapRequest.model_validate(request)

        # Generate roadmap (async for LLM support)
        response = await _planner.plan_async(validated_request)
        return response.model_dump(mode="json")

    except ValidationError as e:
        error = ErrorResponse.invalid_input(
            message="Request validation failed",
            details={"errors": e.errors()},
            trace_id="http",
        )
        raise HTTPException(status_code=422, detail=error.model_dump())

    except HTTPException:
        raise

    except Exception as e:
        error = ErrorResponse.internal_error(
            message=str(e),
            trace_id="http",
        )
        raise HTTPException(status_code=500, detail=error.model_dump())


@app.post("/v1/validate")
async def validate_request(request: dict) -> dict:
    """Validate a roadmap request without generating.

    Args:
        request: The roadmap request to validate.

    Returns:
        Validation result.
    """
    try:
        RoadmapRequest.model_validate(request)
        return {"valid": True, "errors": []}
    except ValidationError as e:
        return {"valid": False, "errors": e.errors()}


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint.

    Returns:
        Health status.
    """
    llm_available = _planner.is_llm_available()
    return {
        "status": "healthy",
        "version": "1.1.0",
        "llm_enabled": llm_available,
        "llm_provider": _llm_config.provider.value if llm_available else "none",
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):  # noqa: ANN001, ARG001
    """Handle HTTP exceptions with error schema compliance."""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail,
    )


def run_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    """Run the HTTP server.

    Args:
        host: Host to bind to.
        port: Port to listen on.
    """
    uvicorn.run(app, host=host, port=port)