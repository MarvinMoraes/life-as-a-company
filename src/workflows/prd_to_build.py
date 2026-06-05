"""Workflow B: PRD → Build

Fluxo: PRD aprovado → Manager → Engineer → QA → Manager (consolida)

Resultado: Plano técnico aprovado + ExecutionSnapshot
"""

from __future__ import annotations

from ..orchestrator.manager import Orchestrator
from ..schemas.agent import ExecutionSnapshot
from ..schemas.project import PRD


async def run_prd_to_build(
    orchestrator: Orchestrator,
    project_id: str,
    prd: PRD,
) -> ExecutionSnapshot:
    """Transforma um PRD aprovado em plano técnico revisado pelo QA.

    Args:
        orchestrator: Instância do Orchestrator.
        project_id: ID do projeto.
        prd: PRD aprovado (saída do workflow idea_to_prd).
    """
    prd_summary = (
        f"**Produto:** {prd.title}\n"
        f"**Problema:** {prd.problem[:200]}\n"
        f"**Solução:** {prd.solution[:200]}\n"
        f"**Features MVP:** {', '.join(f.get('name', '') for f in prd.features[:5])}\n"
        f"**Out-of-scope:** {', '.join(prd.out_of_scope[:3])}"
    )

    steps = [
        {
            "name": "manager_tech_brief",
            "agent": "manager",
            "objective": "Preparar brief técnico a partir do PRD aprovado",
            "context_summary": prd_summary,
            "depth": "short",
            "expected_output": "Brief técnico com escopo de arquitetura",
        },
        {
            "name": "engineer_architecture",
            "agent": "engineer",
            "objective": "Definir arquitetura completa, stack e plano de implementação baseado no PRD",
            "context_summary": prd_summary,
            "inputs": {
                "prd_version": prd.version,
                "features": [f.get("name") for f in prd.features],
                "personas": [p.name for p in prd.personas],
            },
            "depth": "deep",
            "acceptance_criteria": [
                "Stack justificada para cada camada",
                "Pelo menos 2 fases de implementação",
                "Data models para entidades principais",
                "Trade-offs documentados",
            ],
            "expected_output": "TechnicalPlan completo em JSON",
        },
        {
            "name": "qa_technical_review",
            "agent": "qa",
            "objective": "Revisar plano técnico — aderência ao PRD, riscos, gaps de arquitetura",
            "context_summary": prd_summary,
            "inputs": {
                "artifact_name": "TechnicalPlan v1.0",
                "prd_features": [f.get("name") for f in prd.features],
            },
            "depth": "medium",
            "acceptance_criteria": [
                "Verificar cobertura das features do PRD na arquitetura",
                "Identificar riscos técnicos não mitigados",
            ],
            "expected_output": "QA report do plano técnico",
        },
        {
            "name": "manager_build_summary",
            "agent": "manager",
            "objective": "Consolidar plano técnico aprovado e preparar kickoff de desenvolvimento",
            "context_summary": "Consolidar resultados do workflow prd-to-build.",
            "depth": "short",
            "expected_output": "Resumo de kickoff com próximos passos concretos",
        },
    ]

    return await orchestrator.run_workflow(
        workflow_name="prd-to-build",
        project_id=project_id,
        steps=steps,
    )
