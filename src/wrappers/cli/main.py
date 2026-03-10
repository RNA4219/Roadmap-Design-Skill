"""CLI main entry point for Roadmap Design Skill."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pydantic import ValidationError

from roadmap_core.models.error import ErrorResponse
from roadmap_core.models.request import RoadmapRequest
from roadmap_core.planner.roadmap_planner import RoadmapPlanner
from roadmap_core.presenters.json_presenter import JsonPresenter


def run(input_path: str | None = None, output_path: str | None = None) -> int:
    """Run the roadmap planner from CLI.

    Args:
        input_path: Path to input JSON file. If None, reads from stdin.
        output_path: Path to output JSON file. If None, writes to stdout.

    Returns:
        Exit code: 0 for success, 1 for error.
    """
    presenter = JsonPresenter()
    planner = RoadmapPlanner()

    try:
        # Read input
        if input_path:
            with open(input_path, encoding="utf-8") as f:
                input_data = json.load(f)
        else:
            input_data = json.load(sys.stdin)

        # Parse and validate request
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

        # Generate roadmap
        response = planner.plan(request)

        # Output result
        output = presenter.present_response(response)
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(output)
        else:
            print(output)

        # Return appropriate exit code
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
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0",
    )

    args = parser.parse_args()
    return run(input_path=args.input, output_path=args.output)


if __name__ == "__main__":
    sys.exit(main())