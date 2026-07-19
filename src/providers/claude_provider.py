"""Provider para Anthropic Claude API."""

from __future__ import annotations

import logging
from typing import Any

from .base_provider import BaseLLMProvider

logger = logging.getLogger(__name__)


class ClaudeLLMProvider(BaseLLMProvider):
    """Integração com Claude via Anthropic SDK.

    Suporta tool use (function calling) e prompt caching.
    Requer: pip install anthropic
    Configuração: ANTHROPIC_API_KEY no .env
    """

    provider_name = "claude"

    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-5",
        prompt_caching: bool = True,
    ) -> None:
        try:
            import anthropic
        except ImportError as e:
            raise ImportError("Instale o SDK: pip install anthropic") from e

        self._client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model = model
        self.prompt_caching = prompt_caching

    def for_model(self, model: str) -> "ClaudeLLMProvider":
        """Retorna um provider irmão para outro modelo, reusando o mesmo client.

        Usado pelo Orchestrator para rotear cada papel ao seu modelo
        (Manager→Opus 4.8, execução→Sonnet 5, simples→Haiku 4.5) sem
        recriar o AsyncAnthropic client a cada agente.
        """
        if model == self.model:
            return self
        clone = ClaudeLLMProvider.__new__(ClaudeLLMProvider)
        clone._client = self._client
        clone.model = model
        clone.prompt_caching = self.prompt_caching
        return clone

    async def complete(
        self,
        system: str,
        user: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> str:
        import anthropic

        system_param = self._build_system_param(system)
        try:
            response = await self._client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_param,
                messages=[{"role": "user", "content": user}],
            )
            return response.content[0].text
        except anthropic.APIError as e:
            logger.error("Claude API error: %s", e)
            raise

    async def complete_with_tools(
        self,
        system: str,
        messages: list[dict],
        tools: list[dict],
        max_tokens: int = 4096,
        use_cache: bool = True,
    ) -> Any:
        """Retorna o objeto Message raw da Anthropic (stop_reason + content blocks)."""
        import anthropic

        system_param = self._build_system_param(system, use_cache=use_cache)
        try:
            return await self._client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_param,
                tools=tools,
                messages=messages,
            )
        except anthropic.APIError as e:
            logger.error("Claude API error (tool use): %s", e)
            raise

    def _build_system_param(self, system: str, use_cache: bool = True) -> Any:
        """Aplica prompt caching ao system prompt quando habilitado.

        Cache hits custam ~10% do preço de input normal (mínimo 1024 tokens).
        Os 5 prompts dos agentes se qualificam (todos têm >1024 tokens).
        """
        if self.prompt_caching and use_cache and len(system) >= 1024:
            return [
                {
                    "type": "text",
                    "text": system,
                    "cache_control": {"type": "ephemeral"},
                }
            ]
        return system

    async def count_tokens(self, text: str) -> int:
        return max(1, len(text) // 4)
