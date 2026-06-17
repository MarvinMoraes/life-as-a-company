"""Interface abstrata para providers LLM."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseLLMProvider(ABC):
    """Contrato que todo provider LLM deve implementar.

    Providers disponíveis:
    - MockLLMProvider   — testes locais, sem API
    - ClaudeLLMProvider — Anthropic Claude API
    - OpenAILLMProvider — OpenAI-compatible APIs
    """

    provider_name: str = "base"

    @abstractmethod
    async def complete(
        self,
        system: str,
        user: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> str:
        """Envia uma mensagem ao LLM e retorna a resposta como string."""
        ...

    async def complete_with_tools(
        self,
        system: str,
        messages: list[dict],
        tools: list[dict],
        max_tokens: int = 4096,
        use_cache: bool = False,
    ) -> Any:
        """Envia mensagens com tools e retorna o objeto Message raw.

        Deve ser sobrescrito por providers que suportam tool use.
        Retorna o objeto com .stop_reason e .content (list de blocos).
        """
        raise NotImplementedError(f"{self.provider_name} não suporta tool use.")

    @abstractmethod
    async def count_tokens(self, text: str) -> int:
        """Conta tokens de um texto (para controle de budget)."""
        ...
