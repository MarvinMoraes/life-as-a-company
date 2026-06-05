"""Workflow A: Idea → PRD

Fluxo: User → Manager → Product → Marketing → Manager (consolida)

Resultado: PRD aprovado + visão de mercado + ExecutionSnapshot no vault
"""

from __future__ import annotations

from ..orchestrator.manager import Orchestrator
from ..schemas.agent import ExecutionSnapshot


async def run_idea_to_prd(
    orchestrator: Orchestrator,
    project_id: str,
    raw_idea: str,
    target_audience: str = "",
) -> ExecutionSnapshot:
    """Transforma uma ideia bruta em PRD aprovado.

    Args:
        orchestrator: Instância do Orchestrator configurado.
        project_id: Identificador do projeto (kebab-case).
        raw_idea: Descrição da ideia como o usuário a descreveu.
        target_audience: Público-alvo inicial (opcional).
    """
    context = f"Ideia: {raw_idea}" + (f"\nPúblico-alvo inicial: {target_audience}" if target_audience else "")

    steps = [
        {
            "name": "manager_plan",
            "agent": "manager",
            "objective": f"Analisar ideia e planejar discovery para: {raw_idea[:100]}",
            "context_summary": context,
            "depth": "short",
            "expected_output": "Plano de ação e perguntas de discovery",
        },
        {
            "name": "product_discovery",
            "agent": "product",
            "objective": "Realizar discovery completo e gerar PRD v1.0",
            "context_summary": context,
            "inputs": {
                "raw_idea": raw_idea,
                "target_audience": target_audience,
                "project_name": project_id,
            },
            "depth": "deep",
            "acceptance_criteria": [
                "PRD com pelo menos 3 features priorizadas",
                "Pelo menos 1 persona definida",
                "Out-of-scope explícito",
                "Critérios de aceite testáveis",
            ],
            "expected_output": "PRD completo em JSON",
        },
        {
            "name": "marketing_research",
            "agent": "marketing",
            "objective": "Pesquisar mercado e definir posicionamento inicial",
            "context_summary": context,
            "inputs": {"raw_idea": raw_idea, "target_audience": target_audience},
            "depth": "medium",
            "acceptance_criteria": [
                "Pelo menos 2 concorrentes identificados",
                "Posicionamento claro",
                "3 canais de aquisição hipotéticos",
            ],
            "expected_output": "Análise de mercado e posicionamento",
        },
        {
            "name": "qa_prd_review",
            "agent": "qa",
            "objective": "Revisar PRD e análise de mercado — verificar completude e consistência",
            "context_summary": "Revisar artefatos gerados pelo Product e Marketing.",
            "inputs": {"artifact_name": "PRD v1.0 + Market Analysis"},
            "depth": "medium",
            "acceptance_criteria": [
                "Verificar se PRD tem critérios de aceite testáveis",
                "Verificar alinhamento entre personas do PRD e segmento de marketing",
            ],
            "expected_output": "QA report com veredicto",
        },
        {
            "name": "manager_consolidate",
            "agent": "manager",
            "objective": "Consolidar PRD, análise de mercado e relatório QA em resumo executivo",
            "context_summary": "Consolidar resultados do workflow idea-to-prd.",
            "depth": "short",
            "expected_output": "Resumo executivo e próximos passos",
        },
    ]

    return await orchestrator.run_workflow(
        workflow_name="idea-to-prd",
        project_id=project_id,
        steps=steps,
    )
