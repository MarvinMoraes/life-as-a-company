"""Workflow: Flouwy Sprint

Executa um ciclo completo de feature ou bugfix no app Flouwy:
  Manager (triage) -> Product (spec) -> Engineer (implement) -> QA (lint/build)

O Engineer usa tools reais: list_files, read_file, write_file no repo flowly.
O QA usa run_command para verificar lint e build.
"""

from __future__ import annotations

from ..orchestrator.manager import Orchestrator
from ..schemas.agent import ExecutionSnapshot


async def run_flouwy_sprint(
    orchestrator: Orchestrator,
    feature_or_bug: str,
    sprint_type: str = "feature",
    project_id: str = "flouwy",
) -> ExecutionSnapshot:
    """Executa um sprint de feature ou bugfix no Flouwy.

    Args:
        orchestrator: Instância configurada com tools habilitadas.
        feature_or_bug: Descrição da feature ou bug a resolver.
        sprint_type: "feature" ou "bug".
        project_id: ID do projeto no vault (default: flouwy).
    """
    type_label = "feature" if sprint_type == "feature" else "bugfix"
    context = f"Sprint {type_label}: {feature_or_bug}\nApp: Flouwy (Next.js 16, React 19, Supabase, TailwindCSS 4)"

    steps = [
        {
            "name": "manager_triage",
            "agent": "manager",
            "objective": f"Analisar e priorizar {type_label}: {feature_or_bug[:100]}",
            "context_summary": context,
            "expected_output": "JSON com immediate_action, plan (max 3 steps), context_summary",
            "acceptance_criteria": [
                "Identificar qual parte do codebase será afetada",
                "Plano com responsabilidades claras por agente",
            ],
            "memory_hints": [f"{project_id}-spec", f"{project_id}-prd"],
            "depth": "short",
        },
        {
            "name": "product_spec_update",
            "agent": "product",
            "objective": f"Atualizar spec do Flouwy com a {type_label}: {feature_or_bug[:80]}",
            "context_summary": context,
            "expected_output": "JSON com features atualizadas ou acceptance_criteria para a feature",
            "acceptance_criteria": [
                "Definir acceptance criteria claros para o Engineer",
                "Atualizar spec no vault se necessário",
            ],
            "depth": "short",
        },
        {
            "name": "engineer_implement",
            "agent": "engineer",
            "objective": f"Implementar '{feature_or_bug[:80]}' no codebase Flouwy",
            "context_summary": (
                f"{context}\n\n"
                "Estrutura do app: src/app/ (App Router Next.js), src/components/ (React), "
                "src/lib/ (utils, supabase), src/components/flowly/ (componentes custom)."
            ),
            "expected_output": "JSON com arquivos criados/modificados, sumário da implementação",
            "acceptance_criteria": [
                "Código TypeScript válido",
                "Componentes no diretório correto (src/components/ ou src/app/)",
                "Sem quebrar imports existentes",
                "Usar Tailwind CSS para styling",
            ],
            "inputs": {
                "flouwy_stack": "Next.js 16, React 19, Supabase, TailwindCSS 4, shadcn/ui",
                "key_dirs": ["src/app", "src/components/flowly", "src/lib"],
            },
            "depth": "deep",
        },
        {
            "name": "qa_verify",
            "agent": "qa",
            "objective": "Verificar implementação: lint e build devem passar sem erros",
            "context_summary": context,
            "expected_output": "JSON com verdict, findings da execução dos comandos",
            "acceptance_criteria": [
                "npm run lint deve retornar exit 0",
                "npm run build deve compilar com sucesso",
                "Reportar qualquer erro encontrado com recomendação de fix",
            ],
            "depth": "medium",
        },
    ]

    return await orchestrator.run_workflow(
        workflow_name=f"flouwy-sprint-{sprint_type}",
        project_id=project_id,
        steps=steps,
    )
