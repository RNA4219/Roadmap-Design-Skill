"""LLM-enhanced roadmap planner."""

from __future__ import annotations

from datetime import datetime, timezone

from roadmap_core.llm.base import BaseLLMProvider, LLMConfig, LLMProviderType
from roadmap_core.llm.factory import create_provider
from roadmap_core.models.request import RoadmapRequest
from roadmap_core.models.response import RoadmapResponse
from roadmap_core.planner.prompts import PromptTemplates
from roadmap_core.planner.roadmap_planner import RoadmapPlanner as DeterministicPlanner


class LLMRoadmapPlanner:
    """LLM-enhanced roadmap planner.

    Flow:
    1. Deterministic planner generates baseline roadmap
    2. LLM refines and enhances the roadmap
    3. Final validated roadmap is returned
    """

    def __init__(
        self,
        llm_config: LLMConfig | None = None,
        llm_provider: BaseLLMProvider | None = None,
    ) -> None:
        """Initialize LLM planner.

        Args:
            llm_config: LLM configuration (used if llm_provider not provided).
            llm_provider: Pre-configured LLM provider.
        """
        self._deterministic_planner = DeterministicPlanner()
        self._prompt_templates = PromptTemplates()
        self._llm_config = llm_config
        self._llm = llm_provider
        self._planner_version = "1.1.0-llm"

    def _get_llm(self) -> BaseLLMProvider | None:
        """Create the provider lazily so deterministic runs stay fast."""
        if self._llm is not None:
            return self._llm
        if self._llm_config is None or self._llm_config.provider == LLMProviderType.NONE:
            return None
        self._llm = create_provider(self._llm_config)
        return self._llm

    def is_llm_available(self) -> bool:
        """Check if LLM is available.

        Returns:
            True if LLM is configured and available.
        """
        try:
            llm = self._get_llm()
        except Exception:
            return False
        return llm is not None and llm.is_available()

    async def plan_async(self, request: RoadmapRequest) -> RoadmapResponse:
        """Generate roadmap asynchronously (supports LLM calls).

        Args:
            request: The roadmap request.

        Returns:
            Enhanced RoadmapResponse.
        """
        baseline_response = self._deterministic_planner.plan(request)

        if not self.is_llm_available():
            return baseline_response

        try:
            enhanced_response = await self._enhance_with_llm(request, baseline_response)
            return enhanced_response
        except Exception as e:
            import sys

            print(f"LLM enhancement failed: {e}", file=sys.stderr)
            return baseline_response

    def plan(self, request: RoadmapRequest) -> RoadmapResponse:
        """Generate roadmap synchronously (uses deterministic only).

        For async LLM support, use plan_async().

        Args:
            request: The roadmap request.

        Returns:
            RoadmapResponse (deterministic baseline if no LLM).
        """
        return self._deterministic_planner.plan(request)

    async def _enhance_with_llm(
        self,
        request: RoadmapRequest,
        baseline: RoadmapResponse,
    ) -> RoadmapResponse:
        """Enhance baseline roadmap with LLM."""
        llm = self._get_llm()
        if llm is None:
            return baseline

        system_prompt = self._prompt_templates.get_system_prompt(
            language=request.response_language or "en"
        )
        user_prompt = self._prompt_templates.get_enhancement_prompt(
            request=request.model_dump(mode="json"),
            baseline=baseline.model_dump(mode="json"),
        )

        llm_response = await llm.generate_json(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.5,
        )

        return self._parse_llm_response(llm_response, baseline)

    def _parse_llm_response(
        self,
        llm_output: dict,
        fallback: RoadmapResponse,
    ) -> RoadmapResponse:
        """Parse LLM output into RoadmapResponse."""
        try:
            now = datetime.now(timezone.utc)
            response = RoadmapResponse.model_validate(llm_output)
            response.run.updated_at = now
            response.run.planner_version = self._planner_version
            return response
        except Exception:
            return fallback
