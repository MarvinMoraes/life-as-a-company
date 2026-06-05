"""Senior Full Stack Engineer Agent."""

from __future__ import annotations

import json
import uuid
from typing import TYPE_CHECKING

from ..core.base_agent import BaseAgent
from ..schemas.agent import AgentContextPack, AgentResponse
from ..schemas.project import TechnicalPlan
from ..schemas.task import AgentRole

if TYPE_CHECKING:
    from ..providers.base_provider import BaseLLMProvider


class EngineerAgent(BaseAgent):
    """Responsável por arquitetura, implementação e decisões técnicas."""

    role = AgentRole.ENGINEER
    name = "Senior Full Stack Engineer"
    description = "Arquitetura, stack, implementação e trade-offs técnicos."

    async def execute(self, context_pack: AgentContextPack) -> AgentResponse:
        task = context_pack.task
        user_message = self._make_user_message(context_pack)

        depth_tokens = {"short": 768, "medium": 1536, "deep": 3072}
        max_tokens = depth_tokens.get(task.max_response_depth, 1536)

        raw = await self._call_provider(user_message, max_tokens=max_tokens)

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = {"status": "partial", "raw_response": raw}

        # Tenta montar TechnicalPlan se dados suficientes
        technical_plan = None
        if data.get("tech_stack") and data.get("status") == "success":
            try:
                technical_plan = TechnicalPlan(
                    project_id=task.project_id,
                    prd_version=task.inputs.get("prd_version", "1.0"),
                    architecture_summary=data.get("architecture_summary", ""),
                    tech_stack=data.get("tech_stack", {}),
                    components=data.get("components", []),
                    data_models=data.get("data_models", []),
                    api_endpoints=data.get("api_endpoints", []),
                    implementation_phases=data.get("implementation_phases", []),
                    trade_offs=data.get("trade_offs", []),
                    estimated_effort=data.get("estimated_effort", "A definir"),
                    risks=data.get("risks", []),
                )
            except Exception:
                pass

        return AgentResponse(
            response_id=f"resp-{uuid.uuid4().hex[:8]}",
            task_id=task.task_id,
            agent_role=self.role,
            status=data.get("status", "success"),
            content=technical_plan.model_dump() if technical_plan else data,
            summary=data.get("architecture_summary", "Plano técnico gerado.")[:200],
            tokens_used=context_pack.token_total,
            decisions=[
                {"title": t.get("decision", ""), "rationale": t.get("rationale", "")}
                for t in data.get("trade_offs", [])
                if isinstance(t, dict)
            ],
        )
