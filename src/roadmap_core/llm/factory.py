"""Factory for creating LLM providers."""

from __future__ import annotations

from roadmap_core.llm.base import BaseLLMProvider, LLMConfig, LLMProviderType
from roadmap_core.llm.providers.alibaba_provider import AlibabaProvider
from roadmap_core.llm.providers.local_provider import LocalProvider
from roadmap_core.llm.providers.openai_provider import OpenAIProvider


def create_provider(config: LLMConfig) -> BaseLLMProvider:
    """Create an LLM provider based on config.

    Args:
        config: LLM configuration.

    Returns:
        Configured provider instance.

    Raises:
        ValueError: If provider type is not supported.
    """
    providers = {
        LLMProviderType.OPENAI: OpenAIProvider,
        LLMProviderType.ALIBABA: AlibabaProvider,
        LLMProviderType.LOCAL: LocalProvider,
    }

    provider_class = providers.get(config.provider)
    if provider_class is None:
        raise ValueError(f"Unsupported provider: {config.provider}")

    return provider_class(config)


def get_default_provider() -> BaseLLMProvider:
    """Get the default LLM provider from environment.

    Returns:
        Configured provider instance.
    """
    config = LLMConfig.from_env()
    return create_provider(config)