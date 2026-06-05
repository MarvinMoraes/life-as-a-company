"""Carregamento de prompts de sistema a partir de arquivos markdown."""

from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path

from ..schemas.task import AgentRole

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).parent

ROLE_TO_FILE: dict[AgentRole, str] = {
    AgentRole.MANAGER: "manager.md",
    AgentRole.ENGINEER: "engineer.md",
    AgentRole.PRODUCT: "product.md",
    AgentRole.MARKETING: "marketing.md",
    AgentRole.QA: "qa.md",
}


class PromptLoader:
    """Carrega e cacheia prompts de sistema dos agentes."""

    @staticmethod
    @lru_cache(maxsize=10)
    def load(role: AgentRole) -> str:
        """Carrega prompt de um agente por role. Cacheado após primeira leitura."""
        filename = ROLE_TO_FILE.get(role)
        if not filename:
            raise ValueError(f"Sem prompt definido para role '{role.value}'.")

        path = PROMPTS_DIR / filename
        if not path.exists():
            raise FileNotFoundError(f"Arquivo de prompt não encontrado: {path}")

        content = path.read_text(encoding="utf-8")
        logger.debug("Prompt carregado: %s (%d chars)", role.value, len(content))
        return content

    @staticmethod
    def load_all() -> dict[AgentRole, str]:
        """Carrega todos os prompts disponíveis."""
        return {role: PromptLoader.load(role) for role in AgentRole}

    @staticmethod
    def reload(role: AgentRole) -> str:
        """Força reload do cache para um role específico."""
        PromptLoader.load.cache_clear()
        return PromptLoader.load(role)
