"""Workflow D: Project Audit

Fluxo: Manager → QA → Product → Engineer → Manager (síntese)

Resultado: Relatório de auditoria completo do projeto
"""

from __future__ import annotations

from ..orchestrator.manager import Orchestrator
from ..schemas.agent import ExecutionSnapshot


async def run_project_audit(
    orchestrator: Orchestrator,
    project_id: str,
    audit_scope: str = "full",
) -> ExecutionSnapshot:
    """Auditoria completa do estado atual de um projeto.

    Args:
        orchestrator: Instância do Orchestrator.
        project_id: ID do projeto a auditar.
        audit_scope: "full" | "technical" | "product" — escopo da auditoria.
    """
    context = f"Auditoria do projeto '{project_id}'. Escopo: {audit_scope}."

    steps = [
        {
            "name": "manager_audit_setup",
            "agent": "manager",
            "objective": f"Preparar auditoria de '{project_id}': definir escopo, recuperar contexto",
            "context_summary": context,
            "memory_hints": [f"{project_id}-project", f"{project_id}-prd"],
            "depth": "short",
            "expected_output": "Escopo de auditoria e checklist de verificação",
        },
        {
            "name": "qa_full_audit",
            "agent": "qa",
            "objective": "Auditar todos os artefatos do projeto: PRD, plano técnico, plano de marketing",
            "context_summary": context,
            "inputs": {
                "artifact_name": f"Full Audit — {project_id}",
                "audit_scope": audit_scope,
            },
            "depth": "deep",
            "acceptance_criteria": [
                "Avaliação de completude do PRD",
                "Avaliação de coerência técnica",
                "Identificação de dívida técnica ou de produto",
            ],
            "expected_output": "Relatório de auditoria completo",
        },
        {
            "name": "product_audit_gaps",
            "agent": "product",
            "objective": "Identificar gaps de produto: features prometidas x entregues, backlog vencido",
            "context_summary": context,
            "depth": "medium",
            "expected_output": "Lista de gaps de produto e recomendações",
        },
        {
            "name": "engineer_tech_debt",
            "agent": "engineer",
            "objective": "Avaliar dívida técnica, riscos de escalabilidade e segurança",
            "context_summary": context,
            "depth": "medium",
            "expected_output": "Inventário de dívida técnica e roadmap de refatoração",
        },
        {
            "name": "manager_audit_report",
            "agent": "manager",
            "objective": "Sintetizar auditoria em relatório executivo com prioridades de ação",
            "context_summary": "Síntese da auditoria completa do projeto.",
            "depth": "medium",
            "expected_output": "Relatório executivo de auditoria com plano de ação priorizado",
        },
    ]

    return await orchestrator.run_workflow(
        workflow_name="project-audit",
        project_id=project_id,
        steps=steps,
    )
