"""Workflow C: Product Improvement

Fluxo: Feedback do usuário → Manager → Product + Marketing → Engineer → QA

Resultado: PRD atualizado + plano de features + revisão técnica
"""

from __future__ import annotations

from ..orchestrator.manager import Orchestrator
from ..schemas.agent import ExecutionSnapshot


async def run_product_improvement(
    orchestrator: Orchestrator,
    project_id: str,
    user_feedback: str,
    current_version: str = "1.0",
) -> ExecutionSnapshot:
    """Processa feedback de usuários e transforma em melhoria de produto.

    Args:
        orchestrator: Instância do Orchestrator.
        project_id: ID do projeto.
        user_feedback: Feedback bruto dos usuários.
        current_version: Versão atual do produto.
    """
    context = (
        f"Feedback recebido (v{current_version}):\n{user_feedback[:500]}\n\n"
        f"Projeto: {project_id}"
    )

    steps = [
        {
            "name": "manager_feedback_triage",
            "agent": "manager",
            "objective": f"Triagem de feedback: identificar padrões, priorizar melhorias para {project_id}",
            "context_summary": context,
            "depth": "short",
            "expected_output": "Classificação do feedback e priorização inicial",
        },
        {
            "name": "product_improvement_prd",
            "agent": "product",
            "objective": "Analisar feedback e propor melhorias no PRD — novas features, ajustes de escopo",
            "context_summary": context,
            "inputs": {
                "user_feedback": user_feedback,
                "current_version": current_version,
            },
            "depth": "medium",
            "acceptance_criteria": [
                "Features propostas priorizadas com racional",
                "Impacto no escopo atual documentado",
                "Riscos de escopo identificados",
            ],
            "expected_output": "Delta de PRD com novas features e ajustes",
        },
        {
            "name": "marketing_feedback_insights",
            "agent": "marketing",
            "objective": "Extrair insights de marketing do feedback — mensagens que ressoam, posicionamento",
            "context_summary": context,
            "inputs": {"user_feedback": user_feedback},
            "depth": "short",
            "expected_output": "Insights de marketing e ajustes de posicionamento",
        },
        {
            "name": "engineer_impact_assessment",
            "agent": "engineer",
            "objective": "Avaliar impacto técnico das melhorias propostas — esforço, riscos, sequência",
            "context_summary": context,
            "inputs": {"current_version": current_version},
            "depth": "medium",
            "expected_output": "Análise de impacto técnico e estimativa de esforço",
        },
        {
            "name": "qa_improvement_review",
            "agent": "qa",
            "objective": "Revisar proposta de melhoria — consistência entre produto, marketing e técnico",
            "context_summary": "Revisão do pacote de melhoria do produto.",
            "inputs": {"artifact_name": f"Product Improvement v{current_version}+1"},
            "depth": "medium",
            "expected_output": "QA report do pacote de melhoria",
        },
    ]

    return await orchestrator.run_workflow(
        workflow_name="product-improvement",
        project_id=project_id,
        steps=steps,
    )
