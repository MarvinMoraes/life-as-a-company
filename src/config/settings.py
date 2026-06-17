"""Configurações centrais da SaaS Factory."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Identidade da fábrica
    factory_name: str = "life-as-a-company"

    # Providers
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    default_provider: str = "mock"
    default_model: str = "claude-sonnet-4-6"

    # Token governance
    max_tokens_per_call: int = 4096
    max_context_tokens: int = 8192
    compression_threshold: int = 6000

    # Obsidian / Memory
    vault_path: Path = Field(default=Path("./vault"))
    memory_snapshots_enabled: bool = True
    memory_max_notes_in_context: int = 5

    # Flouwy app path
    flouwy_path: Path = Field(default=Path("C:/Users/MarcusMoraes/Documents/GitHub/flowly"))

    # MCP / Integrações externas
    github_token: str = ""
    brave_api_key: str = ""

    # Prompt caching (Anthropic beta)
    prompt_caching_enabled: bool = True

    # n8n
    n8n_base_url: str = "http://localhost:5678"
    n8n_api_key: str = ""

    # Logging
    log_level: str = "INFO"
    log_format: str = "rich"

    @property
    def vault_dir(self) -> Path:
        return self.vault_path.resolve()

    @property
    def flouwy_dir(self) -> Path:
        return self.flouwy_path.resolve()

    @property
    def has_github_mcp(self) -> bool:
        return bool(self.github_token)

    @property
    def has_brave_mcp(self) -> bool:
        return bool(self.brave_api_key)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
