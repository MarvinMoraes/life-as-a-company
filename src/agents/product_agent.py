"""Product Strategist Agent."""

from __future__ import annotations

import json
import uuid
from typing import TYPE_CHECKING

from ..core.base_agent import BaseAgent
from ..schemas.agent import AgentContextPack, AgentResponse
from ..schemas.project import PRD, UserPersona
from ..schemas.task import AgentRole

if TYPE_CHECKING:
    from ..providers.base_provider import BaseLLMProvider


class ProductAgent(BaseAgent):
    """Discovery, PRD e roadmap de produto."""

    role = AgentRole.PRODUCT
    name = "Product Strategist"
    description = "Discovery, personas, proposta de valor, PRD e roadmap."

    async def execute(self, context_pack: AgentContextPack) -> AgentResponse:
        task = context_pack.task
        user_message = self._make_user_message(context_pack)

        depth_tokens = {"short": 768, "medium": 2048, "deep": 4096}
        max_tokens = depth_tokens.get(task.max_response_depth, 2048)

        raw = await self._call_provider(user_message, max_tokens=max_tokens)

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = {"status": "partial", "raw_response": raw}

        # Tenta construir PRD estruturado
        prd = None
        if data.get("features") and data.get("status") == "success":
            try:
                personas = [
                    UserPersona(
                        name=p.get("name", "Persona"),
                        role=p.get("role", ""),
                        pains=p.get("pains", []),
                        gains=p.get("gains", []),
                        jtbd=p.get("jtbd", ""),
                    )
                    for p in data.get("personas", [])
                ]
                prd = PRD(
                    project_id=task.project_id,
                    title=task.inputs.get("project_name", task.project_id),
                    executive_summary=data.get("value_proposition", "")[:300],
                    problem=data.get("problem", ""),
                    solution=data.get("solution", data.get("value_proposition", "")),
                    personas=personas,
                    value_proposition=data.get("value_proposition", ""),
                    features=data.get("features", []),
                    out_of_scope=data.get("out_of_scope", []),
                    success_metrics=data.get("success_metrics", []),
                    risks=data.get("risks", []),
                    roadmap_phases=data.get("roadmap_phases", []),
                )
            except Exception:
                pass

        summary = data.get("value_proposition", "PRD gerado.")[:200]

        return AgentResponse(
            response_id=f"resp-{uuid.uuid4().hex[:8]}",
            task_id=task.task_id,
            agent_role=self.role,
            status=data.get("status", "success"),
            content=prd.model_dump() if prd else data,
            summary=summary,
            tokens_used=context_pack.token_total,
            follow_up_tasks=["technical_planning", "marketing_research"],
        )
