"""Provider para Anthropic Claude API."""

from __future__ import annotations

import logging

from .base_provider import BaseLLMProvider

logger = logging.getLogger(__name__)


class ClaudeLLMProvider(BaseLLMProvider):
    """Integração com Claude via Anthropic SDK.

    Requer: pip install anthropic
    Configuração: ANTHROPIC_API_KEY no .env
    """

    provider_name = "claude"

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6") -> None:
        try:
            import anthropic
        except ImportError as e:
            raise ImportError("Instale o SDK: pip install anthropic") from e

        self._client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model = model

    async def complete(
        self,
        system: str,
        user: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> str:
        import anthropic

        try:
            response = await self._client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            return response.content[0].text
        except anthropic.APIError as e:
            logger.error("Claude API error: %s", e)
            raise

    async def count_tokens(self, text: str) -> int:
        # Estimativa rápida — evita chamada extra de API
        return max(1, len(text) // 4)
