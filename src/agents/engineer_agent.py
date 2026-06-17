"""Senior Full Stack Engineer Agent."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from ..core.base_agent import BaseAgent
from ..schemas.agent import AgentContextPack, AgentResponse
from ..schemas.project import TechnicalPlan
from ..schemas.task import AgentRole

if TYPE_CHECKING:
    from ..providers.base_provider import BaseLLMProvider
    from ..tools.executor import ToolExecutor


class EngineerAgent(BaseAgent):
    role = AgentRole.ENGINEER
    name = "Senior Full Stack Engineer"
    description = "Arquitetura, stack, implementacao e trade-offs tecnicos."

    def __init__(self, provider, prompt, tool_executor=None):
        super().__init__(provider, prompt, tool_executor)

    async def execute(self, context_pack: AgentContextPack) -> AgentResponse:
        task = context_pack.task
        depth_tokens = {"short": 1024, "medium": 2048, "deep": 4096}
        max_tokens = depth_tokens.get(task.max_response_depth, 1536)

        if self.tool_executor:
            from ..tools.definitions import get_tool_definitions_for_role
            user_message = self._make_user_message_for_tools(context_pack)
            tools = get_tool_definitions_for_role(self.role)
            raw = await self._run_agentic_loop(user_message, tools, max_tokens=max_tokens)
        else:
            user_message = self._make_user_message(context_pack)
            raw = await self._call_provider(user_message, max_tokens=max_tokens)

        data = self._parse_json(raw)
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
            summary=data.get("architecture_summary", "Plano tecnico gerado.")[:200],
            tokens_used=context_pack.token_total,
            decisions=[
                {"title": t.get("decision", ""), "rationale": t.get("rationale", "")}
                for t in data.get("trade_offs", [])
                if isinstance(t, dict)
            ],
        )
