"""Tests for CLI runtime configuration."""

from wrappers.cli.main import resolve_use_llm


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
