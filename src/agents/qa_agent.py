"""Quality Assurance Agent."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from ..core.base_agent import BaseAgent
from ..schemas.agent import AgentContextPack, AgentResponse
from ..schemas.task import AgentRole, QAEvaluation, QAFinding, QAVerdict

if TYPE_CHECKING:
    from ..providers.base_provider import BaseLLMProvider
    from ..tools.executor import ToolExecutor


class QAAgent(BaseAgent):
    role = AgentRole.QA
    name = "Quality Assurance"
    description = "Revisao de artefatos, aderencia ao PRD, veredictos e achados."

    def __init__(self, provider, prompt, tool_executor=None):
        super().__init__(provider, prompt, tool_executor)

    async def execute(self, context_pack: AgentContextPack) -> AgentResponse:
        task = context_pack.task
        depth_tokens = {"short": 1024, "medium": 2048, "deep": 4096}
        max_tokens = depth_tokens.get(task.max_response_depth, 1024)

        if self.tool_executor:
            from ..tools.definitions import get_tool_definitions_for_role
            user_message = self._make_user_message_for_tools(context_pack)
            tools = get_tool_definitions_for_role(self.role)
            raw = await self._run_agentic_loop(user_message, tools, max_tokens=max_tokens)
        else:
            user_message = self._make_user_message(context_pack)
            raw = await self._call_provider(user_message, max_tokens=max_tokens)

        data = self._parse_json(raw)
        if "verdict" not in data:
            data["verdict"] = "needs_revision"

        evaluation = None
        if data.get("verdict"):
            try:
                findings = [
                    QAFinding(
                        severity=f.get("severity", "info"),
                        category=f.get("category", "general"),
                        description=f.get("description", ""),
                        recommendation=f.get("recommendation", ""),
                    )
                    for f in data.get("findings", [])
                    if isinstance(f, dict)
                ]
                verdict_map = {
                    "approved": QAVerdict.APPROVED,
                    "approved_with_notes": QAVerdict.APPROVED_WITH_NOTES,
                    "needs_revision": QAVerdict.NEEDS_REVISION,
                    "rejected": QAVerdict.REJECTED,
                }
                verdict = verdict_map.get(data.get("verdict", ""), QAVerdict.NEEDS_REVISION)
                evaluation = QAEvaluation(
                    evaluation_id=f"qa-{uuid.uuid4().hex[:8]}",
                    project_id=task.project_id,
                    task_id=task.task_id,
                    artifact_evaluated=task.inputs.get("artifact_name", "artifact"),
                    verdict=verdict,
                    score=float(data.get("score", 5.0)),
                    summary=data.get("summary", ""),
                    findings=findings,
                    prd_adherence=data.get("prd_adherence"),
                    missing_acceptance_criteria=data.get("missing_acceptance_criteria", []),
                )
            except Exception:
                pass

        is_approved = data.get("verdict", "").startswith("approved")
        verdict_str = data.get("verdict", "needs_revision")
        score_str = data.get("score", "?")
        summary = f"QA: {verdict_str} (score: {score_str})."[:200]

        return AgentResponse(
            response_id=f"resp-{uuid.uuid4().hex[:8]}",
            task_id=task.task_id,
            agent_role=self.role,
            status=data.get("status", "success"),
            content=evaluation.model_dump() if evaluation else data,
            summary=summary,
            tokens_used=context_pack.token_total,
            follow_up_tasks=[] if is_approved else ["revise_artifact"],
        )
