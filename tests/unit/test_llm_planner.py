"""Tests for LLM Roadmap Planner."""

import pytest

from roadmap_core.llm.base import LLMConfig, LLMProviderType
from roadmap_core.models.request import (
    AssetItem,
    AssetType,
    ConstraintCategory,
    ConstraintItem,
    ConstraintSeverity,
    InsightItem,
    ProblemStatement,
    RoadmapRequest,
)
from roadmap_core.planner.llm_planner import LLMRoadmapPlanner


@pytest.fixture
def minimal_request():
    """Create a minimal valid request."""
    return RoadmapRequest(
        schema_version="1.0.0",
        mode="roadmap",
        problem_statement=ProblemStatement(
            problem_id="pb_test",
            title="Test Problem",
            statement="This is a test problem statement that is long enough for validation.",
        ),
        insights=[
            InsightItem(
                insight_id="in_01",
                statement="Test insight statement",
            )
        ],
        constraints=[
            ConstraintItem(
                constraint_id="co_01",
                category=ConstraintCategory.TIME,
                statement="Test constraint",
                severity=ConstraintSeverity.HARD,
            )
        ],
        available_assets=[
            AssetItem(
                asset_id="as_01",
                type=AssetType.DOCUMENT,
                name="Test Asset",
                description="Test asset description",
            )
        ],
    )


class TestLLMRoadmapPlanner:
    """Tests for LLMRoadmapPlanner."""

    def test_plan_without_llm_returns_baseline(self, minimal_request):
        """Test that plan returns baseline when no LLM configured."""
        config = LLMConfig(provider=LLMProviderType.NONE)
        planner = LLMRoadmapPlanner(llm_config=config)

        response = planner.plan(minimal_request)

        assert response.schema_version == "1.0.0"
        assert response.run.status in ("completed", "partial")

    def test_is_llm_available_false_without_config(self):
        """Test that LLM is not available without config."""
        config = LLMConfig(provider=LLMProviderType.NONE)
        planner = LLMRoadmapPlanner(llm_config=config)

        assert planner.is_llm_available() is False

    def test_is_llm_available_true_with_mock(self):
        """Test that LLM is available with mock provider."""
        from roadmap_core.llm.base import BaseLLMProvider, LLMResponse

        class MockProvider(BaseLLMProvider):
            def is_available(self) -> bool:
                return True

            async def generate(self, prompt, system_prompt=None, **kwargs):
                return LLMResponse(content="{}", model="mock")

            async def generate_json(self, prompt, system_prompt=None, **kwargs):
                return {}

        planner = LLMRoadmapPlanner(llm_provider=MockProvider(LLMConfig()))
        assert planner.is_llm_available() is True

    @pytest.mark.asyncio
    async def test_plan_async_without_llm(self, minimal_request):
        """Test async plan without LLM returns baseline."""
        config = LLMConfig(provider=LLMProviderType.NONE)
        planner = LLMRoadmapPlanner(llm_config=config)

        response = await planner.plan_async(minimal_request)

        assert response.schema_version == "1.0.0"
        assert response.run.status in ("completed", "partial")

    def test_planner_version_includes_llm(self):
        """Test that planner version indicates LLM support."""
        config = LLMConfig(provider=LLMProviderType.NONE)
        planner = LLMRoadmapPlanner(llm_config=config)

        assert "llm" in planner._planner_version.lower() or planner._planner_version.startswith("1.1")


class TestLLMConfig:
    """Tests for LLMConfig."""

    def test_default_config_has_none_provider(self):
        """Test that default config uses NONE provider."""
        config = LLMConfig()
        assert config.provider == LLMProviderType.NONE

    def test_from_env_defaults(self, monkeypatch):
        """Test config from environment defaults."""
        for key in ["RDS_LLM_PROVIDER", "RDS_LLM_MODEL", "RDS_LLM_API_KEY"]:
            monkeypatch.delenv(key, raising=False)

        config = LLMConfig.from_env()
        assert config.provider == LLMProviderType.NONE
        assert config.model == ""
        assert config.api_key == ""
