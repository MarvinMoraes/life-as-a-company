"""Marketing & Ads Strategist Agent."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from ..core.base_agent import BaseAgent
from ..schemas.agent import AgentContextPack, AgentResponse
from ..schemas.project import MarketingPlan
from ..schemas.task import AgentRole

if TYPE_CHECKING:
    from ..providers.base_provider import BaseLLMProvider
    from ..tools.executor import ToolExecutor


class MarketingAgent(BaseAgent):
    role = AgentRole.MARKETING
    name = "Marketing & Ads Strategist"
    description = "Pesquisa de mercado, posicionamento, canais de aquisicao e go-to-market."

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
        marketing_plan = None
        if data.get("positioning_statement") and data.get("status") == "success":
            try:
                marketing_plan = MarketingPlan(
                    project_id=task.project_id,
                    market_size=data.get("market_size", "A pesquisar"),
                    target_segment=data.get("target_segment", ""),
                    competitors=data.get("competitors", []),
                    positioning_statement=data.get("positioning_statement", ""),
                    unique_value_proposition=data.get("positioning_statement", ""),
                    messaging=data.get("messaging", {}),
                    acquisition_channels=data.get("acquisition_channels", []),
                    launch_phases=data.get("launch_phases", []),
                    gtm_strategy=data.get("gtm_strategy", ""),
                    kpis=data.get("kpis", []),
                )
            except Exception:
                pass

        return AgentResponse(
            response_id=f"resp-{uuid.uuid4().hex[:8]}",
            task_id=task.task_id,
            agent_role=self.role,
            status=data.get("status", "success"),
            content=marketing_plan.model_dump() if marketing_plan else data,
            summary=data.get("positioning_statement", "Plano de marketing gerado.")[:200],
            tokens_used=context_pack.token_total,
            follow_up_tasks=["qa_review_marketing"],
        )
