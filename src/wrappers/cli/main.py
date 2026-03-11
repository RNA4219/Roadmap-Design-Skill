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
from roadmap_core.presenters.json_presenter import JsonPresenter


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


def run(input_path: str | None = None, output_path: str | None = None, use_llm: bool = False) -> int:
    """Run the roadmap planner from CLI.

    Args:
        input_path: Path to input JSON file. If None, reads from stdin.
        output_path: Path to output JSON file. If None, writes to stdout.
        use_llm: Whether to use LLM enhancement.

    Returns:
        Exit code: 0 for success, 1 for error.
    """
    presenter = JsonPresenter()
    load_dotenv_if_present()

    try:
        if input_path:
            with open(input_path, encoding="utf-8") as f:
                input_data = json.load(f)
        else:
            input_data = json.load(sys.stdin)

        try:
            request = RoadmapRequest.model_validate(input_data)
        except ValidationError as e:
            error = ErrorResponse.invalid_input(
                message="Request validation failed",
                details={"errors": e.errors()},
                trace_id="cli",
            )
            output = presenter.present_error(error)
            if output_path:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(output)
            else:
                print(output, file=sys.stderr)
            return 1

        if use_llm:
            from roadmap_core.planner.llm_planner import LLMRoadmapPlanner

            planner = LLMRoadmapPlanner(llm_config=LLMConfig.from_env())
            response = asyncio.run(planner.plan_async(request))
        else:
            from roadmap_core.planner.roadmap_planner import RoadmapPlanner

            planner = RoadmapPlanner()
            response = planner.plan(request)

        output = presenter.present_response(response)
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(output)
        else:
            print(output)

        return 0 if response.run.status == "completed" else 1

    except json.JSONDecodeError as e:
        error = ErrorResponse.invalid_input(
            message=f"Invalid JSON: {e}",
            trace_id="cli",
        )
        output = presenter.present_error(error)
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(output)
        else:
            print(output, file=sys.stderr)
        return 1

    except Exception as e:
        error = ErrorResponse.internal_error(
            message=str(e),
            trace_id="cli",
        )
        output = presenter.present_error(error)
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(output)
        else:
            print(output, file=sys.stderr)
        return 1


def main() -> int:
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Roadmap Design Skill - Transform problems into implementation-ready roadmaps"
    )
    parser.add_argument(
        "-i", "--input",
        type=str,
        help="Path to input JSON file (default: stdin)",
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Path to output JSON file (default: stdout)",
    )
    llm_group = parser.add_mutually_exclusive_group()
    llm_group.add_argument(
        "--llm",
        action="store_true",
        help="Enable LLM enhancement for this run",
    )
    llm_group.add_argument(
        "--no-llm",
        action="store_true",
        help="Force deterministic mode even when RDS_CLI_USE_LLM=1",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.1.0",
    )

    args = parser.parse_args()
    use_llm = resolve_use_llm(args.llm, args.no_llm)
    return run(input_path=args.input, output_path=args.output, use_llm=use_llm)


if __name__ == "__main__":
    sys.exit(main())

