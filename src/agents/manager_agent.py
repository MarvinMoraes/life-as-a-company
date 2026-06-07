"""Manager / Orchestrator Agent — guardião de contexto e coordenação."""

from __future__ import annotations

import json
import logging
import uuid
from typing import TYPE_CHECKING

from ..core.base_agent import BaseAgent
from ..schemas.agent import AgentContextPack, AgentResponse
from ..schemas.task import AgentRole

if TYPE_CHECKING:
    from ..providers.base_provider import BaseLLMProvider

logger = logging.getLogger(__name__)


class ManagerAgent(BaseAgent):
    """Orquestra todos os agentes e garante economia de contexto."""

    role = AgentRole.MANAGER
    name = "Manager / Orchestrator"
    description = "Interpreta objetivos, delega tarefas, controla contexto e consolida resultados."

    def __init__(self, provider: "BaseLLMProvider", prompt: str) -> None:
        super().__init__(provider, prompt)

    async def execute(self, context_pack: AgentContextPack) -> AgentResponse:
        task = context_pack.task
        user_message = self._make_user_message(context_pack)

        # Profundidade de resposta → mapeia para max_tokens
        depth_tokens = {"short": 1024, "medium": 2048, "deep": 4096}
        max_tokens = depth_tokens.get(task.max_response_depth, 1024)

        raw = await self._call_provider(user_message, max_tokens=max_tokens)

        data = self._parse_json(raw)

        # Normaliza listas que Claude pode retornar como objetos em vez de strings
        memory_writes = [
            v if isinstance(v, str) else str(v.get("slug", v.get("type", str(v))))
            for v in data.get("memory_writes", [])
        ]
        decisions = [
            v if isinstance(v, dict) else {"title": str(v), "rationale": ""}
            for v in data.get("decisions", [])
        ]

        return AgentResponse(
            response_id=f"resp-{uuid.uuid4().hex[:8]}",
            task_id=task.task_id,
            agent_role=self.role,
            status=data.get("status", "success"),
            content=data,
            summary=data.get("context_summary") or data.get("immediate_action") or data.get("summary", "Manager processou a tarefa."),
            memory_writes=memory_writes,
            decisions=decisions,
            tokens_used=context_pack.token_total,
            follow_up_tasks=[
                step.get("task", step.get("objective", "")) for step in data.get("plan", [])
                if isinstance(step, dict)
            ],
        )

    async def plan_workflow(self, raw_objective: str, project_id: str) -> dict:
        """Interpreta objetivo bruto e retorna plano de ação."""
        from ..schemas.task import TaskBrief
        task = TaskBrief(
            task_id=f"plan-{uuid.uuid4().hex[:8]}",
            project_id=project_id,
            assigned_to=self.role,
            objective=f"Analisar e planejar: {raw_objective}",
            context_summary="Objetivo inicial do usuário. Sem histórico anterior.",
            expected_output_format="JSON com plan, immediate_action e context_summary",
            acceptance_criteria=["Plano com pelo menos 2 steps", "Agente correto para cada step"],
            max_response_depth="medium",
        )

        from ..schemas.agent import AgentContextPack, ContextLayer
        pack = AgentContextPack(
            pack_id=f"pack-{uuid.uuid4().hex[:8]}",
            task=task,
            token_budget=2048,
        )
        pack.add_layer(ContextLayer(
            layer_name="task",
            content=f"Objetivo: {raw_objective}",
            token_estimate=len(raw_objective) // 4,
            source="user_input",
        ))

        response = await self.execute(pack)
        return response.content
