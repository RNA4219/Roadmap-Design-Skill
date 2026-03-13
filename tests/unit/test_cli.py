"""Tests for CLI runtime configuration, validate command, and schema command."""

from __future__ import annotations

import json
from pathlib import Path

from wrappers.cli.main import main, resolve_use_llm

EXAMPLES_DIR = Path(__file__).parent.parent.parent / "examples"
SCHEMAS_DIR = Path(__file__).parent.parent.parent / "schemas"


class TestResolveUseLlm:
    """Tests for CLI LLM mode resolution."""

    def test_defaults_to_deterministic_when_env_unset(self, monkeypatch):
        monkeypatch.delenv("RDS_CLI_USE_LLM", raising=False)
        assert resolve_use_llm(False, False) is False

    def test_env_can_enable_llm(self, monkeypatch):
        monkeypatch.setenv("RDS_CLI_USE_LLM", "1")
        assert resolve_use_llm(False, False) is True

    def test_no_llm_flag_wins_over_env_default(self, monkeypatch):
        monkeypatch.setenv("RDS_CLI_USE_LLM", "1")
        assert resolve_use_llm(False, True) is False

    def test_llm_flag_enables_immediately(self, monkeypatch):
        monkeypatch.delenv("RDS_CLI_USE_LLM", raising=False)
        assert resolve_use_llm(True, False) is True


class TestValidateCommand:
    """Tests for the CLI validate subcommand."""

    def test_validate_subcommand_returns_validation_result_for_valid_input(self, capsys):
        exit_code = main(["validate", "-i", str(EXAMPLES_DIR / "request.full.json")])
        captured = capsys.readouterr()
        payload = json.loads(captured.out)

        assert exit_code == 0
        assert payload["schema_version"] == "1.0.0"
        assert payload["mode"] == "roadmap"
        assert payload["valid"] is True
        assert payload["errors"] == []

    def test_validate_subcommand_returns_validation_result_for_invalid_input(self, tmp_path, capsys):
        invalid_request = {
            "schema_version": "1.0.0",
            "mode": "roadmap",
            "problem_statement": {
                "problem_id": "pb_invalid",
                "title": "Invalid request",
            },
            "insights": [],
            "constraints": [],
            "available_assets": [],
        }
        input_path = tmp_path / "invalid.json"
        input_path.write_text(json.dumps(invalid_request), encoding="utf-8")

        exit_code = main(["validate", "-i", str(input_path)])
        captured = capsys.readouterr()
        payload = json.loads(captured.out)

        assert exit_code == 1
        assert payload["valid"] is False
        assert {issue["field"] for issue in payload["errors"]} >= {
            "problem_statement.statement",
            "insights",
            "constraints",
            "available_assets",
        }
        assert payload["warnings"][0]["code"] == "DEFAULT_LANGUAGE"


class TestSchemaCommand:
    """Tests for the CLI schema subcommand."""

    def test_schema_command_prints_request_schema(self, capsys):
        exit_code = main(["schema", "--kind", "request"])
        captured = capsys.readouterr()
        payload = json.loads(captured.out)
        expected = json.loads((SCHEMAS_DIR / "roadmap-request.schema.json").read_text(encoding="utf-8"))

        assert exit_code == 0
        assert payload == expected

    def test_schema_command_invalid_kind_returns_error_envelope(self, capsys):
        exit_code = main(["schema", "--kind", "unknown"])
        captured = capsys.readouterr()
        payload = json.loads(captured.err)

        assert exit_code == 2
        assert payload["error_code"] == "INVALID_INPUT"
