"""OpenRouter provider implementation."""

from __future__ import annotations

from roadmap_core.llm.providers.openai_provider import OpenAIProvider


class OpenRouterProvider(OpenAIProvider):
    """OpenRouter API provider.

    OpenRouter provides a unified API for multiple LLM providers
    using an OpenAI-compatible interface.
    """

    def __init__(self, config) -> None:
        """Initialize OpenRouter provider.

        Args:
            config: LLM configuration.
        """
        # Set default OpenRouter base URL if not provided
        if not config.base_url:
            config.base_url = "https://openrouter.ai/api/v1"
        super().__init__(config)