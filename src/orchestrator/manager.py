"""Orchestrator — núcleo de coordenação da SaaS Factory."""

from __future__ import annotations

import logging
import uuid
from pathlib import Path
from typing import Any

from ..agents import EngineerAgent, ManagerAgent, MarketingAgent, ProductAgent, QAAgent
from ..core.context import ContextGovernor
from ..core.registry import AgentRegistry
from ..memory.memory_manager import MemoryManager
from ..prompts.loader import PromptLoader
from ..providers.base_provider import BaseLLMProvider
from ..providers.factory import get_provider
from ..schemas.agent import AgentResponse, ExecutionSnapshot
from ..schemas.memory import DecisionRecord, MemoryNote, MemoryType
from ..schemas.task import AgentRole, TaskBrief

logger = logging.getLogger(__name__)


class Orchestrator:
    """Ponto central de coordenação da fábrica.

    Responsabilidades:
    - Instanciar e registrar os 5 agentes
    - Montar context packs eficientes
    - Delegar tarefas ao agente correto
    - Consolidar resultados
    - Persistir memória no vault
    """

    def __init__(
        self,
        vault_path: Path | str = "./vault",
        provider: BaseLLMProvider | None = None,
    ) -> None:
        self.vault_path = Path(vault_path).resolve()
        self.provider = provider or get_provider()
        self.memory = MemoryManager(self.vault_path)
        self.governor = ContextGovernor(self.memory)
        self.registry = AgentRegistry(self.provider)
        self._setup_agents()
        logger.info("Orchestrator inicializado. Vault: %s", self.vault_path)

    def _setup_agents(self) -> None:
        """Instancia e registra todos os agentes."""
        prompts = PromptLoader.load_all()
        self.registry.register(ManagerAgent(self.provider, prompts[AgentRole.MANAGER]))
        self.registry.register(EngineerAgent(self.provider, prompts[AgentRole.ENGINEER]))
        self.registry.register(ProductAgent(self.provider, prompts[AgentRole.PRODUCT]))
        self.registry.register(MarketingAgent(self.provider, prompts[AgentRole.MARKETING]))
        self.registry.register(QAAgent(self.provider, prompts[AgentRole.QA]))
        logger.info("Agentes registrados: %s", [a["name"] for a in self.registry.list_agents()])

    async def run_task(
        self,
        role: AgentRole,
        objective: str,
        project_id: str,
        context_summary: str = "",
        inputs: dict | None = None,
        expected_output: str = "JSON estruturado",
        acceptance_criteria: list[str] | None = None,
        memory_hints: list[str] | None = None,
        depth: str = "medium",
        token_budget: int | None = None,
    ) -> AgentResponse:
        """Executa uma tarefa em um agente específico.

        Monta o context pack mínimo, invoca o agente e persiste memória.
        """
        task = TaskBrief(
            task_id=f"task-{uuid.uuid4().hex[:8]}",
            project_id=project_id,
            assigned_to=role,
            objective=objective,
            context_summary=context_summary or f"Projeto: {project_id}",
            inputs=inputs or {},
            expected_output_format=expected_output,
            acceptance_criteria=acceptance_criteria or [],
            memory_hints=memory_hints or [],
            max_response_depth=depth,
        )

        agent = self.registry.get(role)
        context_pack = await self.governor.assemble(
            task=task,
            agent_role_description=f"Role: {agent.name}\n{agent.description}",
            project_summary=context_summary,
            token_budget=token_budget,
        )

        logger.info("Invocando %s para tarefa '%s' [%d tokens]", agent.name, task.task_id, context_pack.token_total)
        response = await agent.execute(context_pack)

        # Persiste decisões no vault
        await self._persist_decisions(response, project_id)

        return response

    async def run_workflow(
        self,
        workflow_name: str,
        project_id: str,
        steps: list[dict[str, Any]],
    ) -> ExecutionSnapshot:
        """Executa uma sequência de steps e retorna snapshot do resultado."""
        snapshot = ExecutionSnapshot(
            snapshot_id=f"snap-{uuid.uuid4().hex[:8]}",
            workflow_name=workflow_name,
            project_id=project_id,
            status="running",
            steps_pending=[s.get("name", f"step-{i}") for i, s in enumerate(steps)],
        )

        results: dict[str, Any] = {}

        for step in steps:
            step_name = step.get("name", f"step-{len(snapshot.steps_completed)}")
            logger.info("Workflow '%s' → step '%s'", workflow_name, step_name)

            snapshot.current_step = step_name

            # Injeta resultados de steps anteriores como inputs
            step_inputs = step.get("inputs", {})
            step_inputs["_previous_results"] = {
                k: str(v)[:500] for k, v in results.items()  # resumo compacto
            }

            response = await self.run_task(
                role=AgentRole(step["agent"]),
                objective=step["objective"],
                project_id=project_id,
                context_summary=step.get("context_summary", ""),
                inputs=step_inputs,
                expected_output=step.get("expected_output", "JSON estruturado"),
                acceptance_criteria=step.get("acceptance_criteria", []),
                memory_hints=step.get("memory_hints", []),
                depth=step.get("depth", "medium"),
            )

            results[step_name] = response.content
            snapshot.steps_completed.append(step_name)
            if step_name in snapshot.steps_pending:
                snapshot.steps_pending.remove(step_name)

            # Salva artefato resumido no snapshot
            snapshot.artifacts[step_name] = {
                "agent": step["agent"],
                "status": response.status,
                "summary": response.summary,
            }
            snapshot.token_budget_used += response.tokens_used

            if response.status == "failed":
                snapshot.status = "failed"
                snapshot.error = f"Step '{step_name}' falhou."
                break

        if not snapshot.steps_pending:
            snapshot.status = "completed"

        # Salva snapshot no vault
        await self._save_snapshot(snapshot)
        return snapshot

    async def _persist_decisions(self, response: AgentResponse, project_id: str) -> None:
        """Salva decisões da resposta como DecisionRecords no vault."""
        for i, decision in enumerate(response.decisions or []):
            if not isinstance(decision, dict):
                continue
            record = DecisionRecord(
                decision_id=f"ADR-{response.response_id[-4:]}-{i:02d}",
                project_id=project_id,
                title=decision.get("title", "Decisão sem título"),
                decision=decision.get("title", ""),
                rationale=decision.get("rationale", ""),
                context=f"Task: {response.task_id}",
                made_by=response.agent_role.value,
            )
            await self.memory.save_decision(record)

    async def _save_snapshot(self, snapshot: ExecutionSnapshot) -> None:
        """Salva execution snapshot como nota no vault."""
        import json
        from datetime import datetime
        note = MemoryNote(
            slug=snapshot.snapshot_id,
            title=f"Snapshot: {snapshot.workflow_name} [{snapshot.project_id}]",
            type=MemoryType.SNAPSHOT,
            project_id=snapshot.project_id,
            tags=["snapshot", snapshot.workflow_name, snapshot.status],
            content=(
                f"**Workflow:** {snapshot.workflow_name}\n"
                f"**Status:** {snapshot.status}\n"
                f"**Steps:** {', '.join(snapshot.steps_completed)}\n"
                f"**Tokens usados:** {snapshot.token_budget_used}\n\n"
                f"## Artefatos\n```json\n{json.dumps(snapshot.artifacts, indent=2, default=str)}\n```"
            ),
            summary=(
                f"{snapshot.workflow_name} [{snapshot.status}] — "
                f"{len(snapshot.steps_completed)} steps, {snapshot.token_budget_used} tokens"
            ),
        )
        await self.memory.save_note(note)
        logger.info("Snapshot salvo: %s", snapshot.snapshot_id)
