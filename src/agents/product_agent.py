"""Product Strategist Agent."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from ..core.base_agent import BaseAgent
from ..schemas.agent import AgentContextPack, AgentResponse
from ..schemas.project import PRD, UserPersona
from ..schemas.task import AgentRole

if TYPE_CHECKING:
    from ..providers.base_provider import BaseLLMProvider
    from ..tools.executor import ToolExecutor


class ProductAgent(BaseAgent):
    role = AgentRole.PRODUCT
    name = "Product Strategist"
    description = "Discovery, personas, proposta de valor, PRD e roadmap."

    def __init__(self, provider, prompt, tool_executor=None):
        super().__init__(provider, prompt, tool_executor)

    async def execute(self, context_pack: AgentContextPack) -> AgentResponse:
        task = context_pack.task
        depth_tokens = {"short": 1024, "medium": 3000, "deep": 6000}
        max_tokens = depth_tokens.get(task.max_response_depth, 2048)

        if self.tool_executor:
            from ..tools.definitions import get_tool_definitions_for_role
            user_message = self._make_user_message_for_tools(context_pack)
            tools = get_tool_definitions_for_role(self.role)
            raw = await self._run_agentic_loop(user_message, tools, max_tokens=max_tokens)
        else:
            user_message = self._make_user_message(context_pack)
            raw = await self._call_provider(user_message, max_tokens=max_tokens)

        data = self._parse_json(raw)
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

        return AgentResponse(
            response_id=f"resp-{uuid.uuid4().hex[:8]}",
            task_id=task.task_id,
            agent_role=self.role,
            status=data.get("status", "success"),
            content=prd.model_dump() if prd else data,
            summary=data.get("value_proposition", "PRD gerado.")[:200],
            tokens_used=context_pack.token_total,
            follow_up_tasks=["technical_planning", "marketing_research"],
        )
