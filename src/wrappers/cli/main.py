"""CLI main entry point for Roadmap Design Skill."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

from pydantic import ValidationError

from roadmap_core.llm.base import LLMConfig
from roadmap_core.models.error import ErrorResponse
from roadmap_core.models.request import RoadmapRequest
from roadmap_core.models.validation import ValidationResult
from roadmap_core.presenters.json_presenter import JsonPresenter
from roadmap_core.schema_loader import UnknownSchemaKindError, load_schema_text
from roadmap_core.validators.request_payload_validator import validate_request_payload


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


def resolve_use_llm(explicit_enable: bool, explicit_disable: bool) -> bool:
    """Resolve whether CLI execution should use the LLM path."""
    if explicit_enable:
        return True
    if explicit_disable:
        return False
    return LLMConfig.get_env_flag("RDS_CLI_USE_LLM", default=False)


def _load_input_data(input_path: str | None) -> object:
    if input_path:
        with open(input_path, encoding="utf-8") as f:
            return json.load(f)
    return json.load(sys.stdin)


def _write_output(output: str, output_path: str | None, *, stderr: bool = False) -> None:
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output)
        return
    if stderr:
        print(output, file=sys.stderr)
    else:
        print(output)


def run(input_path: str | None = None, output_path: str | None = None, use_llm: bool = False) -> int:
    """Run the roadmap planner from CLI."""
    presenter = JsonPresenter()
    load_dotenv_if_present()

    try:
        input_data = _load_input_data(input_path)

        try:
            request = RoadmapRequest.model_validate(input_data)
        except ValidationError as exc:
            error = ErrorResponse.invalid_input(
                message="Request validation failed",
                details={"errors": exc.errors()},
                trace_id="cli",
            )
            _write_output(presenter.present_error(error), output_path, stderr=output_path is None)
            return 1

        if use_llm:
            from roadmap_core.planner.llm_planner import LLMRoadmapPlanner

            planner = LLMRoadmapPlanner(llm_config=LLMConfig.from_env())
            response = asyncio.run(planner.plan_async(request))
        else:
            from roadmap_core.planner.roadmap_planner import RoadmapPlanner

            planner = RoadmapPlanner()
            response = planner.plan(request)

        _write_output(presenter.present_response(response), output_path)
        return 0 if response.run.status == "completed" else 1

    except json.JSONDecodeError as exc:
        error = ErrorResponse.invalid_input(
            message=f"Invalid JSON: {exc}",
            trace_id="cli",
        )
        _write_output(presenter.present_error(error), output_path, stderr=output_path is None)
        return 1
    except Exception as exc:
        error = ErrorResponse.internal_error(
            message=str(exc),
            trace_id="cli",
        )
        _write_output(presenter.present_error(error), output_path, stderr=output_path is None)
        return 2


def validate(input_path: str | None = None, output_path: str | None = None) -> int:
    """Validate a roadmap request from CLI."""
    presenter = JsonPresenter()
    try:
        input_data = _load_input_data(input_path)
    except json.JSONDecodeError as exc:
        result = ValidationResult.invalid_json(f"Invalid JSON: {exc.msg}")
        _write_output(presenter.present_validation_result(result), output_path)
        return 1
    except Exception as exc:
        error = ErrorResponse.internal_error(
            message=str(exc),
            trace_id="cli-validate",
        )
        _write_output(presenter.present_error(error), output_path, stderr=output_path is None)
        return 2

    result = validate_request_payload(input_data)
    _write_output(presenter.present_validation_result(result), output_path)
    return 0 if result.valid else 1


def schema(kind: str, output_path: str | None = None) -> int:
    """Print one of the canonical JSON schemas."""
    presenter = JsonPresenter()
    try:
        schema_text = load_schema_text(kind)
        _write_output(schema_text, output_path)
        return 0
    except UnknownSchemaKindError as exc:
        error = ErrorResponse.invalid_input(
            message=str(exc),
            details={"kind": kind},
            trace_id="cli-schema",
        )
        _write_output(presenter.present_error(error), output_path, stderr=output_path is None)
        return 2
    except Exception as exc:
        error = ErrorResponse.internal_error(
            message=str(exc),
            trace_id="cli-schema",
        )
        _write_output(presenter.present_error(error), output_path, stderr=output_path is None)
        return 2


def _build_legacy_run_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Roadmap Design Skill - Transform problems into implementation-ready roadmaps"
    )
    parser.add_argument("-i", "--input", type=str, help="Path to input JSON file (default: stdin)")
    parser.add_argument("-o", "--output", type=str, help="Path to output JSON file (default: stdout)")
    llm_group = parser.add_mutually_exclusive_group()
    llm_group.add_argument("--llm", action="store_true", help="Enable LLM enhancement for this run")
    llm_group.add_argument(
        "--no-llm",
        action="store_true",
        help="Force deterministic mode even when RDS_CLI_USE_LLM=1",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 1.1.0")
    return parser


def _build_command_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Roadmap Design Skill - Transform problems into implementation-ready roadmaps"
    )
    parser.add_argument("--version", action="version", version="%(prog)s 1.1.0")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Generate a roadmap")
    run_parser.add_argument("-i", "--input", type=str, help="Path to input JSON file (default: stdin)")
    run_parser.add_argument("-o", "--output", type=str, help="Path to output JSON file (default: stdout)")
    run_group = run_parser.add_mutually_exclusive_group()
    run_group.add_argument("--llm", action="store_true", help="Enable LLM enhancement for this run")
    run_group.add_argument(
        "--no-llm",
        action="store_true",
        help="Force deterministic mode even when RDS_CLI_USE_LLM=1",
    )

    validate_parser = subparsers.add_parser("validate", help="Validate a roadmap request")
    validate_parser.add_argument("-i", "--input", type=str, help="Path to input JSON file (default: stdin)")
    validate_parser.add_argument("-o", "--output", type=str, help="Path to output JSON file (default: stdout)")

    schema_parser = subparsers.add_parser("schema", help="Print a canonical JSON schema")
    schema_parser.add_argument("--kind", required=True, type=str, help="request | response | validation-result | error")
    schema_parser.add_argument("-o", "--output", type=str, help="Path to output file (default: stdout)")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Main entry point for CLI."""
    args_list = sys.argv[1:] if argv is None else argv
    if args_list and args_list[0] in {"run", "validate", "schema"}:
        parser = _build_command_parser()
        args = parser.parse_args(args_list)
        if args.command == "validate":
            return validate(input_path=args.input, output_path=args.output)
        if args.command == "schema":
            return schema(kind=args.kind, output_path=args.output)
        use_llm = resolve_use_llm(args.llm, args.no_llm)
        return run(input_path=args.input, output_path=args.output, use_llm=use_llm)

    legacy_parser = _build_legacy_run_parser()
    legacy_args = legacy_parser.parse_args(args_list)
    use_llm = resolve_use_llm(legacy_args.llm, legacy_args.no_llm)
    return run(input_path=legacy_args.input, output_path=legacy_args.output, use_llm=use_llm)


if __name__ == "__main__":
    sys.exit(main())
