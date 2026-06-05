"""Classe base abstrata para todos os agentes da fábrica."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from ..schemas.agent import AgentContextPack, AgentResponse
from ..schemas.task import AgentRole

if TYPE_CHECKING:
    from ..providers.base_provider import BaseLLMProvider

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Contrato que todo agente deve implementar.

    Cada agente tem papel único, prompt próprio e política de memória.
    Agentes não conhecem uns aos outros — comunicam via Manager.
    """

    role: AgentRole
    name: str
    description: str

    def __init__(self, provider: "BaseLLMProvider", prompt: str) -> None:
        self.provider = provider
        self.system_prompt = prompt
        self._logger = logging.getLogger(f"agent.{self.role.value}")

    @abstractmethod
    async def execute(self, context_pack: AgentContextPack) -> AgentResponse:
        """Executa a tarefa descrita no context_pack e retorna uma AgentResponse."""
        ...

    def build_system_prompt(self, extra_context: str = "") -> str:
        """Monta o prompt de sistema com contexto adicional, se houver."""
        if not extra_context:
            return self.system_prompt
        return f"{self.system_prompt}\n\n---\n## Contexto Adicional\n{extra_context}"

    def _format_context_pack(self, pack: AgentContextPack) -> str:
        """Formata o context pack em texto para envio ao LLM."""
        sections = []
        for layer in pack.layers:
            sections.append(f"### [{layer.layer_name.upper()}]\n{layer.content}")
        return "\n\n".join(sections)

    def _make_user_message(self, pack: AgentContextPack) -> str:
        context_text = self._format_context_pack(pack)
        task = pack.task
        return (
            f"## Tarefa: {task.objective}\n\n"
            f"**Projeto:** {task.project_id}\n"
            f"**Profundidade esperada:** {task.max_response_depth}\n"
            f"**Formato de saída esperado:** {task.expected_output_format}\n\n"
            f"### Critérios de Aceite\n"
            + "\n".join(f"- {c}" for c in task.acceptance_criteria)
            + (f"\n\n### Contexto\n{context_text}" if context_text else "")
        )

    async def _call_provider(self, user_message: str, max_tokens: int = 2048) -> str:
        """Chama o provider LLM com o prompt de sistema do agente."""
        self._logger.debug("Chamando provider [%s] max_tokens=%d", self.provider.__class__.__name__, max_tokens)
        return await self.provider.complete(
            system=self.system_prompt,
            user=user_message,
            max_tokens=max_tokens,
        )
