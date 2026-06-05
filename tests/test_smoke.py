"""Smoke tests de integração — end-to-end com MockProvider."""

import pytest
from pathlib import Path

from src.orchestrator.manager import Orchestrator
from src.providers.mock_provider import MockLLMProvider
from src.schemas.task import AgentRole


@pytest.fixture
def orchestrator(tmp_path):
    vault = tmp_path / "vault"
    vault.mkdir()
    provider = MockLLMProvider(latency_ms=0)
    return Orchestrator(vault_path=vault, provider=provider)


@pytest.mark.asyncio
async def test_orchestrator_initializes(orchestrator):
    """Todos os 5 agentes devem estar registrados."""
    agents = orchestrator.registry.list_agents()
    assert len(agents) == 5
    roles = {a["role"] for a in agents}
    assert roles == {"manager", "engineer", "product", "marketing", "qa"}


@pytest.mark.asyncio
async def test_run_single_task(orchestrator):
    """Manager deve processar uma tarefa sem erro."""
    response = await orchestrator.run_task(
        role=AgentRole.MANAGER,
        objective="Planejar o projeto X",
        project_id="test-project",
        depth="short",
    )
    assert response.status in ("success", "partial")
    assert response.agent_role == AgentRole.MANAGER
    assert response.task_id


@pytest.mark.asyncio
async def test_run_product_task(orchestrator):
    response = await orchestrator.run_task(
        role=AgentRole.PRODUCT,
        objective="Criar PRD para app de finanças pessoais",
        project_id="fintrack",
        depth="medium",
    )
    assert response.status in ("success", "partial")
    assert response.agent_role == AgentRole.PRODUCT


@pytest.mark.asyncio
async def test_run_engineer_task(orchestrator):
    response = await orchestrator.run_task(
        role=AgentRole.ENGINEER,
        objective="Definir arquitetura do backend",
        project_id="fintrack",
        depth="medium",
    )
    assert response.agent_role == AgentRole.ENGINEER


@pytest.mark.asyncio
async def test_run_qa_task(orchestrator):
    response = await orchestrator.run_task(
        role=AgentRole.QA,
        objective="Revisar PRD v1.0",
        project_id="fintrack",
        inputs={"artifact_name": "PRD v1.0"},
        depth="short",
    )
    assert response.agent_role == AgentRole.QA


@pytest.mark.asyncio
async def test_idea_to_prd_workflow(orchestrator):
    """Workflow completo idea-to-prd com mock."""
    from src.workflows.idea_to_prd import run_idea_to_prd

    snapshot = await run_idea_to_prd(
        orchestrator=orchestrator,
        project_id="smoke-test",
        raw_idea="App para gestão de checklists de viagem",
        target_audience="Viajantes frequentes",
    )

    assert snapshot.workflow_name == "idea-to-prd"
    assert snapshot.project_id == "smoke-test"
    assert snapshot.status in ("completed", "failed")
    assert len(snapshot.steps_completed) > 0


@pytest.mark.asyncio
async def test_snapshot_saved_to_vault(orchestrator, tmp_path):
    """Snapshot deve ser salvo no vault após workflow."""
    from src.workflows.idea_to_prd import run_idea_to_prd

    snapshot = await run_idea_to_prd(
        orchestrator=orchestrator,
        project_id="vault-test",
        raw_idea="Plataforma de cursos online",
    )

    vault = orchestrator.vault_path
    snapshot_files = list(vault.rglob("snap-*.md"))
    assert len(snapshot_files) >= 1


@pytest.mark.asyncio
async def test_token_budget_respected(orchestrator):
    """Context pack deve respeitar o budget de tokens."""
    response = await orchestrator.run_task(
        role=AgentRole.MANAGER,
        objective="Tarefa com budget mínimo",
        project_id="budget-test",
        token_budget=500,
        depth="short",
    )
    assert response.tokens_used <= 500 + 100  # pequena margem de erro
