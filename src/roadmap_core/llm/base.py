"""Base LLM provider interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class LLMProviderType(str, Enum):
    """Supported LLM provider types."""

    OPENAI = "openai"
    ALIBABA = "alibaba"
    LOCAL = "local"
    NONE = "none"  # Deterministic fallback


@dataclass
class LLMConfig:
    """Configuration for LLM provider."""

    provider: LLMProviderType = LLMProviderType.NONE
    model: str = ""
    api_key: str = ""
    base_url: str | None = None
    timeout_seconds: int = 60
    max_tokens: int = 4096
    temperature: float = 0.7
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_env(cls) -> "LLMConfig":
        """Create config from environment variables.

        Returns:
            LLMConfig populated from environment.
        """
        import os

        provider_str = os.getenv("RDS_LLM_PROVIDER", "none").lower()
        provider = LLMProviderType(provider_str) if provider_str in [p.value for p in LLMProviderType] else LLMProviderType.NONE

        return cls(
            provider=provider,
            model=os.getenv("RDS_LLM_MODEL", ""),
            api_key=os.getenv("RDS_LLM_API_KEY", ""),
            base_url=os.getenv("RDS_LLM_BASE_URL"),
            timeout_seconds=int(os.getenv("RDS_LLM_TIMEOUT_SECONDS", "60")),
            max_tokens=int(os.getenv("RDS_LLM_MAX_TOKENS", "4096")),
            temperature=float(os.getenv("RDS_LLM_TEMPERATURE", "0.7")),
        )


@dataclass
class LLMResponse:
    """Response from LLM provider."""

    content: str
    model: str
    usage: dict[str, int] = field(default_factory=dict)
    finish_reason: str = "stop"
    raw_response: Any = None


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, config: LLMConfig) -> None:
        """Initialize provider with config.

        Args:
            config: LLM configuration.
        """
        self.config = config

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate response from LLM.

        Args:
            prompt: User prompt.
            system_prompt: Optional system prompt.
            **kwargs: Additional provider-specific options.

        Returns:
            LLMResponse with generated content.
        """
        pass

    @abstractmethod
    async def generate_json(
        self,
        prompt: str,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate JSON response from LLM.

        Args:
            prompt: User prompt.
            system_prompt: Optional system prompt.
            **kwargs: Additional provider-specific options.

        Returns:
            Parsed JSON dictionary.
        """
        pass

    def is_available(self) -> bool:
        """Check if provider is available (has valid config).

        Returns:
            True if provider can be used.
        """
        return bool(self.config.api_key or self.config.provider == LLMProviderType.LOCAL)