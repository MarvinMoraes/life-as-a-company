"""Interface abstrata para providers LLM."""

from __future__ import annotations

from abc import ABC, abstractmethod


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

    @abstractmethod
    async def count_tokens(self, text: str) -> int:
        """Conta tokens de um texto (para controle de budget)."""
        ...
