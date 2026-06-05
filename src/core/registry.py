"""Registry de agentes — descoberta e instanciação centralizada."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from ..schemas.task import AgentRole

if TYPE_CHECKING:
    from .base_agent import BaseAgent
    from ..providers.base_provider import BaseLLMProvider

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Mantém referências para instâncias de agentes.

    Uso:
        registry = AgentRegistry(provider)
        registry.register(ManagerAgent(provider, prompt))
        agent = registry.get(AgentRole.MANAGER)
    """

    def __init__(self, provider: "BaseLLMProvider") -> None:
        self.provider = provider
        self._agents: dict[AgentRole, "BaseAgent"] = {}

    def register(self, agent: "BaseAgent") -> None:
        if agent.role in self._agents:
            logger.warning("Agente '%s' já registrado — substituindo.", agent.role.value)
        self._agents[agent.role] = agent
        logger.info("Agente registrado: %s (%s)", agent.name, agent.role.value)

    def get(self, role: AgentRole) -> "BaseAgent":
        if role not in self._agents:
            raise KeyError(f"Agente para role '{role.value}' não registrado.")
        return self._agents[role]

    def list_agents(self) -> list[dict]:
        return [
            {"role": r.value, "name": a.name, "description": a.description}
            for r, a in self._agents.items()
        ]

    def all_roles_registered(self) -> bool:
        return all(role in self._agents for role in AgentRole)
