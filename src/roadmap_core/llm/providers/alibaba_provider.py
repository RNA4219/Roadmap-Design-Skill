"""Alibaba DashScope provider implementation."""

from __future__ import annotations

import json
from typing import Any

from roadmap_core.llm.base import BaseLLMProvider, LLMConfig, LLMResponse


class AlibabaProvider(BaseLLMProvider):
    """Alibaba DashScope (Qwen) API provider.

    Uses OpenAI-compatible API from Alibaba Cloud Model Studio.
    """

    def __init__(self, config: LLMConfig) -> None:
        """Initialize Alibaba provider.

        Args:
            config: LLM configuration.
        """
        super().__init__(config)
        self._client = None
        # Default base URL for DashScope OpenAI-compatible API
        self._base_url = config.base_url or "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"

    def _get_client(self) -> Any:
        """Get or create OpenAI client for Alibaba.

        Returns:
            OpenAI client instance configured for Alibaba.
        """
        if self._client is None:
            try:
                from openai import AsyncOpenAI
            except ImportError:
                raise ImportError(
                    "openai package not installed. "
                    "Install with: pip install openai"
                )

            self._client = AsyncOpenAI(
                api_key=self.config.api_key,
                base_url=self._base_url,
                timeout=self.config.timeout_seconds,
            )
        return self._client

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate response from Alibaba/Qwen.

        Args:
            prompt: User prompt.
            system_prompt: Optional system prompt.
            **kwargs: Additional options.

        Returns:
            LLMResponse with generated content.
        """
        client = self._get_client()
        model = self.config.model or "qwen-plus"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            temperature=kwargs.get("temperature", self.config.temperature),
        )

        choice = response.choices[0]
        return LLMResponse(
            content=choice.message.content or "",
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            finish_reason=choice.finish_reason,
            raw_response=response,
        )

    async def generate_json(
        self,
        prompt: str,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate JSON response from Alibaba/Qwen.

        Args:
            prompt: User prompt.
            system_prompt: Optional system prompt.
            **kwargs: Additional options.

        Returns:
            Parsed JSON dictionary.
        """
        client = self._get_client()
        model = self.config.model or "qwen-plus"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            temperature=kwargs.get("temperature", self.config.temperature),
            response_format={"type": "json_object"},
        )

        choice = response.choices[0]
        content = choice.message.content or "{}"
        return json.loads(content)