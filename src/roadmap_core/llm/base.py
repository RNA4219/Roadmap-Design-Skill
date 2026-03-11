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
    OPENROUTER = "openrouter"
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

    @staticmethod
    def get_env_flag(name: str, default: bool = False) -> bool:
        """Read a boolean environment flag."""
        import os

        value = os.getenv(name)
        if value is None:
            return default
        return value.strip().lower() in {"1", "true", "yes", "on"}

    @staticmethod
    def _get_first_env(*names: str, default: str = "") -> str:
        """Return the first non-empty environment value."""
        import os

        for name in names:
            value = os.getenv(name)
            if value:
                return value
        return default

    @classmethod
    def from_env(
        cls,
        *,
        enable_var: str | None = None,
        default_enabled: bool = True,
    ) -> "LLMConfig":
        """Create config from environment variables.

        Args:
            enable_var: Optional boolean env var that gates LLM usage.
            default_enabled: Default gate value when enable_var is unset.

        Returns:
            LLMConfig populated from environment.
        """
        import os

        if enable_var is not None and not cls.get_env_flag(enable_var, default_enabled):
            return cls(provider=LLMProviderType.NONE)

        provider_str = os.getenv("LLM_PROVIDER", "none").lower()
        provider = (
            LLMProviderType(provider_str)
            if provider_str in {p.value for p in LLMProviderType}
            else LLMProviderType.NONE
        )

        api_key = ""
        model = ""
        base_url = None
        timeout_seconds = int(os.getenv("LLM_TIMEOUT_SECONDS", "180"))

        if provider == LLMProviderType.OPENAI:
            api_key = os.getenv("OPENAI_API_KEY", "")
            model = os.getenv("LLM_MODEL", "gpt-4o-mini")
            base_url = os.getenv("LLM_BASE_URL")
            timeout_seconds = int(os.getenv("LLM_TIMEOUT_SECONDS", "180"))
        elif provider == LLMProviderType.ALIBABA:
            api_key = os.getenv("DASHSCOPE_API_KEY", "")
            model = os.getenv("LLM_MODEL", "qwen-plus")
            base_url = os.getenv("LLM_BASE_URL")
            timeout_seconds = int(os.getenv("LLM_TIMEOUT_SECONDS", "180"))
        elif provider == LLMProviderType.OPENROUTER:
            api_key = os.getenv("OPENROUTER_API_KEY", "")
            model = os.getenv("LLM_MODEL", "openai/gpt-4o-mini")
            base_url = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
            timeout_seconds = int(os.getenv("LLM_TIMEOUT_SECONDS", "180"))
        elif provider == LLMProviderType.LOCAL:
            model = os.getenv("LLM_MODEL", "llama3")
            base_url = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
            timeout_seconds = int(os.getenv("LLM_TIMEOUT_SECONDS", "180"))
        else:
            api_key = os.getenv("LLM_API_KEY", "")
            model = os.getenv("LLM_MODEL", "")

        return cls(
            provider=provider,
            model=model,
            api_key=api_key,
            base_url=base_url,
            timeout_seconds=timeout_seconds,
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "8192")),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
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