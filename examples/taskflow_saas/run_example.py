"""Exemplo ponta a ponta: TaskFlow SaaS

TaskFlow é um SaaS fictício de gestão de tarefas para times remotos.
Este script demonstra todos os workflows da SaaS Factory.

Execução:
    python -m examples.taskflow_saas.run_example

Ou com provider real:
    DEFAULT_PROVIDER=claude python -m examples.taskflow_saas.run_example
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

# Adiciona raiz ao path para imports relativos funcionarem
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.orchestrator.manager import Orchestrator
from src.providers.factory import get_provider
from src.utils.formatters import format_response, pprint_snapshot
from src.workflows.idea_to_prd import run_idea_to_prd
from src.workflows.project_audit import run_project_audit

PROJECT_ID = "taskflow-saas"

RAW_IDEA = """
Quero criar um SaaS de gestão de tarefas especialmente voltado para times remotos
de 5 a 50 pessoas. O grande diferencial é que ele aprende com os padrões de trabalho
do time e sugere automaticamente quem deve fazer cada tarefa, baseado em histórico,
habilidades declaradas e disponibilidade. Times pequenos perdem muito tempo em
reuniões de alinhamento e distribuição de tarefas — quero eliminar isso.
"""

USER_FEEDBACK = """
Adoramos o produto, mas precisamos de:
1. Integração com Slack — notificações de novas tarefas direto no canal
2. Relatório semanal automático por email
3. App mobile — a maioria do time usa o celular para checar tarefas
O processo de onboarding está confuso, principalmente o setup inicial das habilidades do time.
"""


async def main():
    print("\n" + "=" * 60)
    print("  SaaS Factory — Exemplo: TaskFlow SaaS")
    print("=" * 60 + "\n")

    # Inicializa o Orchestrator com vault local de exemplo
    vault_path = Path(__file__).parent / "vault"
    vault_path.mkdir(exist_ok=True)

    provider = get_provider()  # usa DEFAULT_PROVIDER do .env (padrão: mock)
    orchestrator = Orchestrator(vault_path=vault_path, provider=provider)

    print(f"Provider: {provider.provider_name}")
    print(f"Vault: {vault_path}\n")

    # ── Workflow A: Idea → PRD ──────────────────────────────────
    print("[ WORKFLOW A ] Idea -> PRD")
    print("-" * 40)

    snapshot_a = await run_idea_to_prd(
        orchestrator=orchestrator,
        project_id=PROJECT_ID,
        raw_idea=RAW_IDEA,
        target_audience="Times remotos de 5-50 pessoas, startups e PMEs",
    )
    print(pprint_snapshot(snapshot_a))

    # Salva resultado para referência
    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)
    (results_dir / "workflow_a_snapshot.json").write_text(
        json.dumps(snapshot_a.model_dump(), indent=2, default=str),
        encoding="utf-8",
    )

    # ── Workflow D: Project Audit ───────────────────────────────
    print("\n[ WORKFLOW D ] Project Audit")
    print("-" * 40)

    snapshot_d = await run_project_audit(
        orchestrator=orchestrator,
        project_id=PROJECT_ID,
        audit_scope="full",
    )
    print(pprint_snapshot(snapshot_d))

    (results_dir / "workflow_d_snapshot.json").write_text(
        json.dumps(snapshot_d.model_dump(), indent=2, default=str),
        encoding="utf-8",
    )

    # ── Resumo Final ────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  Execução completa")
    print(f"  Workflows rodados: 2")
    print(f"  Tokens totais: {snapshot_a.token_budget_used + snapshot_d.token_budget_used}")
    print(f"  Vault: {vault_path}")
    print(f"  Resultados: {results_dir}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
