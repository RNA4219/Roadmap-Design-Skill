"""Local LLM provider implementation (Ollama, etc.)."""

from __future__ import annotations

import json
from typing import Any

from roadmap_core.llm.base import BaseLLMProvider, LLMConfig, LLMResponse


class LocalProvider(BaseLLMProvider):
    """Local LLM provider (Ollama, LM Studio, etc.).

    Uses OpenAI-compatible API typically available on localhost.
    """

    def __init__(self, config: LLMConfig) -> None:
        """Initialize local provider.

        Args:
            config: LLM configuration.
        """
        super().__init__(config)
        self._client = None
        # Default base URL for Ollama
        self._base_url = config.base_url or "http://localhost:11434/v1"

    def _get_client(self) -> Any:
        """Get or create OpenAI client for local LLM.

        Returns:
            OpenAI client instance configured for local LLM.
        """
        if self._client is None:
            try:
                from openai import AsyncOpenAI
            except ImportError:
                raise ImportError(
                    "openai package not installed. "
                    "Install with: pip install openai"
                )

            # Local LLMs often don't need a real API key
            self._client = AsyncOpenAI(
                api_key=self.config.api_key or "local",
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
        """Generate response from local LLM.

        Args:
            prompt: User prompt.
            system_prompt: Optional system prompt.
            **kwargs: Additional options.

        Returns:
            LLMResponse with generated content.
        """
        client = self._get_client()
        model = self.config.model or "llama3"

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
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0,
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
        """Generate JSON response from local LLM.

        Args:
            prompt: User prompt.
            system_prompt: Optional system prompt.
            **kwargs: Additional options.

        Returns:
            Parsed JSON dictionary.
        """
        # Add JSON instruction to prompt for models that don't support response_format
        json_prompt = f"{prompt}\n\nRespond with valid JSON only."

        response = await self.generate(json_prompt, system_prompt, **kwargs)

        # Try to extract JSON from response
        content = response.content
        try:
            # Try direct parse
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            if "```json" in content:
                start = content.find("```json") + 7
                end = content.find("```", start)
                if end > start:
                    return json.loads(content[start:end].strip())
            elif "```" in content:
                start = content.find("```") + 3
                end = content.find("```", start)
                if end > start:
                    return json.loads(content[start:end].strip())

            # Return empty dict if parsing fails
            return {"error": "Failed to parse JSON", "raw": content}