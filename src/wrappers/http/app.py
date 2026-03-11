"""HTTP API wrapper using FastAPI."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from roadmap_core.llm.base import LLMConfig, LLMProviderType
from roadmap_core.models.error import ErrorResponse
from roadmap_core.models.request import RoadmapRequest
from roadmap_core.planner.llm_planner import LLMRoadmapPlanner
from roadmap_core.planner.roadmap_planner import RoadmapPlanner

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
    """Validate a roadmap request without generating."""
    try:
        RoadmapRequest.model_validate(request)
        return {"valid": True, "errors": []}
    except ValidationError as e:
        return {"valid": False, "errors": e.errors()}


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

