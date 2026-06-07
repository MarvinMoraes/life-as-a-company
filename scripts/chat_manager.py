"""Chat interativo com o Manager Agent da SaaS Factory."""

from __future__ import annotations

import argparse
import asyncio
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

DEFAULT_VAULT = Path("C:/Users/MarcusMoraes/Documents/laac")


def _render(data: dict, summary: str) -> str:
    """Converte a resposta JSON do Manager em texto legível."""
    if data.get("status") == "partial" and "raw_response" in data:
        return data["raw_response"]

    parts: list[str] = []

    if obj := data.get("objective_understood"):
        parts.append(f"Entendi: {obj}")

    if action := data.get("immediate_action"):
        parts.append(f"\nAção imediata: {action}")

    if plan := data.get("plan"):
        parts.append("\nPlano:")
        for step in plan:
            if isinstance(step, dict):
                agent = step.get("agent", "?")
                task = step.get("task", step.get("objective", ""))
                num = step.get("step", "•")
                parts.append(f"  {num}. [{agent}] {task}")

    if decisions := data.get("decisions"):
        parts.append("\nDecisões:")
        for d in decisions:
            title = d.get("title", str(d)) if isinstance(d, dict) else str(d)
            parts.append(f"  • {title}")

    return "\n".join(parts) if parts else summary


def _load_vault_context(vault: Path, project_id: str) -> str:
    """Carrega contexto relevante do vault para o projeto."""
    context_parts: list[str] = []

    # Pastas onde procurar arquivos do projeto
    search_paths = [
        vault / "Projects" / project_id,
        vault / "PRDs" / project_id,
        vault / "Decisions" / project_id,
    ]

    for folder in search_paths:
        if folder.exists():
            for md_file in sorted(folder.glob("*.md")):
                try:
                    content = md_file.read_text(encoding="utf-8")
                    # Inclui só as primeiras 100 linhas de cada arquivo
                    lines = content.splitlines()[:100]
                    context_parts.append(
                        f"\n--- {md_file.name} ---\n" + "\n".join(lines)
                    )
                except Exception:
                    pass

    if not context_parts:
        return f"Projeto '{project_id}' — sem notas no vault ainda."

    return (
        f"Contexto do projeto '{project_id}' carregado do vault Obsidian "
        f"({vault}):\n" + "\n".join(context_parts)
    )


async def main() -> None:
    parser = argparse.ArgumentParser(description="Chat com o Manager Agent")
    parser.add_argument(
        "--project", "-p",
        default="flouwy",
        help="ID do projeto (nome da pasta no vault). Default: flouwy",
    )
    parser.add_argument(
        "--vault", "-v",
        default=str(DEFAULT_VAULT),
        help=f"Caminho do vault Obsidian. Default: {DEFAULT_VAULT}",
    )
    args = parser.parse_args()

    vault_path = Path(args.vault)
    project_id = args.project

    from src.config.settings import get_settings
    from src.providers.claude_provider import ClaudeLLMProvider
    from src.prompts.loader import PromptLoader
    from src.agents.manager_agent import ManagerAgent
    from src.schemas.task import AgentRole, TaskBrief
    from src.schemas.agent import AgentContextPack, ContextLayer

    settings = get_settings()

    if not settings.anthropic_api_key:
        print("[Erro] ANTHROPIC_API_KEY não encontrada no .env")
        sys.exit(1)

    provider = ClaudeLLMProvider(api_key=settings.anthropic_api_key)
    prompt = PromptLoader.load(AgentRole.MANAGER)
    manager = ManagerAgent(provider=provider, prompt=prompt)

    # Carrega contexto do vault no início da sessão
    vault_context = _load_vault_context(vault_path, project_id)
    vault_loaded = "sem notas" not in vault_context

    print("=" * 60)
    print(f"  SaaS Factory — Manager Agent")
    print(f"  Projeto: {project_id}")
    print(f"  Vault:   {vault_path}")
    print(f"  Contexto: {'✓ carregado' if vault_loaded else '⚠ sem notas ainda'}")
    print("  Digite 'sair' para encerrar")
    print("=" * 60)
    print()

    context_summary = vault_context

    while True:
        try:
            user_input = input("Você: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nEncerrando.")
            break

        if not user_input:
            continue

        if user_input.lower() in ("sair", "exit", "quit"):
            print("Manager: Até logo!")
            break

        task = TaskBrief(
            task_id=f"chat-{uuid.uuid4().hex[:8]}",
            project_id=project_id,
            assigned_to=AgentRole.MANAGER,
            objective=user_input,
            context_summary=context_summary,
            expected_output_format="JSON com status, objective_understood, plan, immediate_action, context_summary",
            acceptance_criteria=["Responder ao usuário de forma clara e acionável"],
            max_response_depth="medium",
        )

        pack = AgentContextPack(
            pack_id=f"pack-{uuid.uuid4().hex[:8]}",
            task=task,
            token_budget=2048,
        )
        pack.add_layer(ContextLayer(
            layer_name="context",
            content=context_summary,
            token_estimate=len(context_summary) // 4,
            source="vault_obsidian",
        ))

        try:
            print("Manager: ", end="", flush=True)
            response = await manager.execute(pack)
            print(_render(response.content, response.summary))

            if new_ctx := response.content.get("context_summary"):
                context_summary = new_ctx

        except Exception as e:  # noqa: BLE001
            print(f"[Erro ao chamar o Manager] {e}")

        print()


if __name__ == "__main__":
    asyncio.run(main())
