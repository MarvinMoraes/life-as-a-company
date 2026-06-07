"""Roda workflow idea-to-prd com Claude e salva no vault Obsidian."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()


RAW_IDEA = """
SaaS de gestao pessoal integrada focado em bem-estar e crescimento pessoal.
Combina saude (habitos, sono, hidratacao, exercicio, nutricao) com rendimento pessoal
(objetivos, produtividade, foco, aprendizado). Sistema de gamificacao com pontos,
niveis, conquistas e streaks para manter consistencia. Relatorios diarios de
performance, resumo semanal e analise mensal com insights e tendencias.
O usuario acompanha sua evolucao em ambas as dimensoes — corpo e mente —
em um unico lugar, de forma visual e motivadora.
"""

TARGET_AUDIENCE = """
Pessoas entre 20-40 anos que querem melhorar qualidade de vida de forma integrada,
profissionais que sentem que saude e produtividade estao desconectadas,
entusiastas de self-improvement que usam apps isolados para cada coisa.
"""

PROJECT_ID = "vitalflow"


async def main():
    from src.orchestrator.manager import Orchestrator
    from src.workflows.idea_to_prd import run_idea_to_prd
    from src.utils.formatters import pprint_snapshot

    print("=" * 60)
    print("  SaaS Factory — Workflow: Idea -> PRD")
    print(f"  Projeto: {PROJECT_ID}")
    print(f"  Provider: Claude API (claude-sonnet-4-6)")
    print("=" * 60)
    print()

    orch = Orchestrator(vault_path="C:/Users/MarcusMoraes/Documents/laac")

    print("[1/5] Manager: analisando objetivo...")
    print("[2/5] Product Strategist: discovery + PRD...")
    print("[3/5] Marketing Strategist: mercado + posicionamento...")
    print("[4/5] QA: revisando artefatos...")
    print("[5/5] Manager: consolidando resultado...")
    print()

    snapshot = await run_idea_to_prd(
        orchestrator=orch,
        project_id=PROJECT_ID,
        raw_idea=RAW_IDEA,
        target_audience=TARGET_AUDIENCE,
    )

    print(pprint_snapshot(snapshot))

    # Mostra resumos dos artefatos gerados
    print("\nArtefatos gerados:")
    for step, artifact in snapshot.artifacts.items():
        print(f"  {step}: {artifact.get('summary', '')[:120]}")


if __name__ == "__main__":
    asyncio.run(main())
