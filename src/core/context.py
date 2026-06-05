"""Governança de contexto — monta AgentContextPacks com economia de tokens."""

from __future__ import annotations

import logging
import uuid
from typing import TYPE_CHECKING

from ..schemas.agent import AgentContextPack, ContextLayer
from ..schemas.task import TaskBrief

if TYPE_CHECKING:
    from ..memory.memory_manager import MemoryManager

logger = logging.getLogger(__name__)

# Tamanhos máximos por camada (em tokens estimados)
LAYER_BUDGETS = {
    "global": 300,
    "project": 500,
    "task": 400,
    "agent": 200,
    "memory": 600,
}


class ContextGovernor:
    """Monta AgentContextPack de forma disciplinada, respeitando token budgets.

    Ordem de prioridade das camadas:
    1. task   — objetivo imediato (sempre incluído)
    2. agent  — papel e política do agente
    3. project — visão, PRD vigente, status
    4. memory — notas relevantes recuperadas seletivamente
    5. global — princípios e convenções gerais (incluído se sobrar budget)
    """

    GLOBAL_CONTEXT = """# Factory Principles
- Cada agente tem responsabilidade única e outputs estruturados.
- Respostas devem ser objetivas: nada de floreios ou repetição de contexto recebido.
- Decisões importantes devem ser registradas no vault.
- Qualidade > velocidade. QA é a última linha de defesa.
- Contexto é recurso escasso — não desperdice tokens."""

    def __init__(
        self,
        memory_manager: "MemoryManager",
        default_budget: int = 4096,
    ) -> None:
        self.memory = memory_manager
        self.default_budget = default_budget

    async def assemble(
        self,
        task: TaskBrief,
        agent_role_description: str,
        project_summary: str = "",
        token_budget: int | None = None,
    ) -> AgentContextPack:
        """Monta um context pack mínimo para a tarefa."""
        budget = token_budget or self.default_budget
        pack = AgentContextPack(
            pack_id=f"pack-{uuid.uuid4().hex[:8]}",
            task=task,
            token_budget=budget,
        )

        # Camada 1: Task (sempre incluída, já está no pack via TaskBrief)
        task_layer = ContextLayer(
            layer_name="task",
            content=self._format_task(task),
            token_estimate=self._estimate(task.context_summary),
            source="task_brief",
        )
        pack.add_layer(task_layer)

        # Camada 2: Agent identity
        agent_layer = ContextLayer(
            layer_name="agent",
            content=agent_role_description,
            token_estimate=self._estimate(agent_role_description),
            source="agent_definition",
        )
        pack.add_layer(agent_layer)

        # Camada 3: Project summary
        if project_summary:
            proj_layer = ContextLayer(
                layer_name="project",
                content=project_summary,
                token_estimate=self._estimate(project_summary),
                source="project_context",
            )
            pack.add_layer(proj_layer)

        # Camada 4: Memory retrieval (notas relevantes do vault)
        if task.memory_hints:
            memory_content = await self._retrieve_memory(task.memory_hints, task.project_id)
            if memory_content:
                mem_layer = ContextLayer(
                    layer_name="memory",
                    content=memory_content,
                    token_estimate=self._estimate(memory_content),
                    source="obsidian_vault",
                )
                pack.add_layer(mem_layer)

        # Camada 5: Global context (inclui se couber)
        global_layer = ContextLayer(
            layer_name="global",
            content=self.GLOBAL_CONTEXT,
            token_estimate=self._estimate(self.GLOBAL_CONTEXT),
            source="factory_config",
        )
        pack.add_layer(global_layer)  # add_layer retorna False silenciosamente se não couber

        logger.debug(
            "ContextPack montado: %d tokens / %d budget (%d camadas)",
            pack.token_total, budget, len(pack.layers)
        )
        return pack

    async def _retrieve_memory(self, hints: list[str], project_id: str | None) -> str:
        """Recupera e concatena notas relevantes do vault."""
        notes = []
        for slug in hints:
            note = await self.memory.get_note(slug)
            if note:
                notes.append(f"### [{slug}]\n{note.summary or note.content[:400]}")
        return "\n\n".join(notes)

    @staticmethod
    def _format_task(task: TaskBrief) -> str:
        return (
            f"**Objetivo:** {task.objective}\n"
            f"**Contexto:** {task.context_summary}\n"
            f"**Profundidade:** {task.max_response_depth}"
        )

    @staticmethod
    def _estimate(text: str) -> int:
        """Estimativa rápida de tokens: ~4 chars por token."""
        return max(1, len(text) // 4)
