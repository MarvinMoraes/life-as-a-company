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
    - Instanciar e registrar os 5 agentes (com tools quando configurado)
    - Montar context packs eficientes
    - Delegar tarefas ao agente correto
    - Consolidar resultados
    - Persistir memória no vault
    """

    def __init__(
        self,
        vault_path: Path | str = "./vault",
        provider: BaseLLMProvider | None = None,
        enable_tools: bool | None = None,
        mcp_adapters: dict | None = None,
    ) -> None:
        self.vault_path = Path(vault_path).resolve()
        self.provider = provider or get_provider()
        # Auto-detect: desativa tools se o provider não as suporta (ex: mock)
        if enable_tools is None:
            enable_tools = getattr(self.provider, "provider_name", "") not in ("mock", "base")
        self.enable_tools = enable_tools
        self.mcp_adapters = mcp_adapters or {}
        self.memory = MemoryManager(self.vault_path)
        self.governor = ContextGovernor(self.memory)
        self.registry = AgentRegistry(self.provider)
        self._setup_agents()
        logger.info("Orchestrator inicializado. Vault: %s | tools=%s", self.vault_path, enable_tools)

    def _provider_for_role(self, role: AgentRole) -> BaseLLMProvider:
        """Seleciona o provider/modelo correto para cada papel.

        Manager usa Opus 4.8 (orquestração/planejamento), execução usa
        Sonnet 5, agentes mais simples usam Haiku 4.5 — configurável no .env.
        Providers sem `for_model` (mock) usam o modelo único.
        """
        if not hasattr(self.provider, "for_model"):
            return self.provider
        from ..config.settings import get_settings
        model = get_settings().model_for_role(role.value)
        return self.provider.for_model(model)

    def _setup_agents(self) -> None:
        """Instancia e registra todos os agentes, com tools quando disponíveis."""
        from ..config.settings import get_settings
        from ..tools.executor import ToolExecutor
        from ..tools.mcp_adapter import get_adapter_for_tool

        prompts = PromptLoader.load_all()

        def _provider(role: AgentRole) -> BaseLLMProvider:
            return self._provider_for_role(role)

        if not self.enable_tools:
            # Modo legado: sem tools (para testes com mock provider)
            self.registry.register(ManagerAgent(_provider(AgentRole.MANAGER), prompts[AgentRole.MANAGER]))
            self.registry.register(EngineerAgent(_provider(AgentRole.ENGINEER), prompts[AgentRole.ENGINEER]))
            self.registry.register(ProductAgent(_provider(AgentRole.PRODUCT), prompts[AgentRole.PRODUCT]))
            self.registry.register(MarketingAgent(_provider(AgentRole.MARKETING), prompts[AgentRole.MARKETING]))
            self.registry.register(QAAgent(_provider(AgentRole.QA), prompts[AgentRole.QA]))
            logger.info("Agentes registrados (sem tools): %s", [a["name"] for a in self.registry.list_agents()])
            return

        settings = get_settings()

        # Closure: Manager delega para outros agentes via esta função
        # Sem import circular — ToolExecutor recebe apenas Callable
        async def _agent_caller(role: str, objective: str, context: str) -> dict:
            response = await self.run_task(
                role=AgentRole(role),
                objective=objective,
                project_id="__delegation__",
                context_summary=context,
                depth="medium",
            )
            return {"summary": response.summary, "content": str(response.content)[:500]}

        def _make_mcp_adapter_for_role(role: AgentRole):
            """Retorna um MCP adapter composto se houver adapters para o role."""
            if not self.mcp_adapters:
                return None
            return _CompositeMCPAdapter(self.mcp_adapters)

        def _make_executor(role: AgentRole, with_delegation: bool = False) -> ToolExecutor:
            return ToolExecutor(
                vault_path=self.vault_path,
                flouwy_path=settings.flouwy_dir,
                role=role,
                agent_caller=_agent_caller if with_delegation else None,
                mcp_adapter=_make_mcp_adapter_for_role(role),
            )

        self.registry.register(ManagerAgent(
            _provider(AgentRole.MANAGER),
            prompts[AgentRole.MANAGER],
            tool_executor=_make_executor(AgentRole.MANAGER, with_delegation=True),
            agent_caller=_agent_caller,
        ))
        self.registry.register(EngineerAgent(
            _provider(AgentRole.ENGINEER), prompts[AgentRole.ENGINEER],
            tool_executor=_make_executor(AgentRole.ENGINEER),
        ))
        self.registry.register(ProductAgent(
            _provider(AgentRole.PRODUCT), prompts[AgentRole.PRODUCT],
            tool_executor=_make_executor(AgentRole.PRODUCT),
        ))
        self.registry.register(MarketingAgent(
            _provider(AgentRole.MARKETING), prompts[AgentRole.MARKETING],
            tool_executor=_make_executor(AgentRole.MARKETING),
        ))
        self.registry.register(QAAgent(
            _provider(AgentRole.QA), prompts[AgentRole.QA],
            tool_executor=_make_executor(AgentRole.QA),
        ))
        models = {
            a.role.value: getattr(a.provider, "model", "?")
            for a in self.registry._agents.values()
        }
        logger.info("Agentes registrados (com tools) — modelos por papel: %s", models)

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


class _CompositeMCPAdapter:
    """Agrupa múltiplos MCPToolAdapters e roteia por nome de tool."""

    def __init__(self, adapters: dict) -> None:
        self._adapters = adapters

    async def call_tool(self, tool_name: str, tool_input: dict) -> str:
        from ..tools.mcp_adapter import get_adapter_for_tool
        adapter = get_adapter_for_tool(tool_name, self._adapters)
        if adapter:
            return await adapter.call_tool(tool_name, tool_input)
        return f"ERROR: Nenhum MCP adapter disponível para tool '{tool_name}'"
