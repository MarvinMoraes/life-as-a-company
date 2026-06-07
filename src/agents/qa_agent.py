"""Quality Assurance Agent — revisão e aprovação de artefatos."""

from __future__ import annotations

import json
import uuid
from typing import TYPE_CHECKING

from ..core.base_agent import BaseAgent
from ..schemas.agent import AgentContextPack, AgentResponse
from ..schemas.task import AgentRole, QAEvaluation, QAFinding, QAVerdict

if TYPE_CHECKING:
    from ..providers.base_provider import BaseLLMProvider


class QAAgent(BaseAgent):
    """Revisa artefatos e emite veredictos com achados categorizados."""

    role = AgentRole.QA
    name = "Quality Assurance"
    description = "Revisão de artefatos, aderência ao PRD, veredictos e achados."

    async def execute(self, context_pack: AgentContextPack) -> AgentResponse:
        task = context_pack.task
        user_message = self._make_user_message(context_pack)

        depth_tokens = {"short": 1024, "medium": 2048, "deep": 4096}
        max_tokens = depth_tokens.get(task.max_response_depth, 1024)

        raw = await self._call_provider(user_message, max_tokens=max_tokens)

        data = self._parse_json(raw)
        if "verdict" not in data:
            data["verdict"] = "needs_revision"

        # Monta QAEvaluation estruturado
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
        summary = f"QA: {data.get('verdict', 'needs_revision')} (score: {data.get('score', '?')}). {data.get('summary', '')}"[:200]

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
