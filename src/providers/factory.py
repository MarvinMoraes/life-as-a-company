"""Factory de providers — instancia o provider correto conforme configuração."""

from __future__ import annotations

from .base_provider import BaseLLMProvider


def get_provider(provider_name: str | None = None, **kwargs) -> BaseLLMProvider:
    """Retorna instância do provider configurado.

    Args:
        provider_name: "mock" | "claude" | "openai". Se None, usa DEFAULT_PROVIDER do .env.
        **kwargs: Argumentos extras para o provider (ex: api_key, model).
    """
    from ..config import get_settings
    settings = get_settings()

    name = provider_name or settings.default_provider

    if name == "mock":
        from .mock_provider import MockLLMProvider
        return MockLLMProvider()

    if name == "claude":
        from .claude_provider import ClaudeLLMProvider
        api_key = kwargs.get("api_key") or settings.anthropic_api_key
        model = kwargs.get("model") or settings.default_model
        return ClaudeLLMProvider(api_key=api_key, model=model)

    if name == "openai":
        raise NotImplementedError("OpenAI provider ainda não implementado — contribuições bem-vindas.")

    raise ValueError(f"Provider desconhecido: '{name}'. Use 'mock', 'claude' ou 'openai'.")
