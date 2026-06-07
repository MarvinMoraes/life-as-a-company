"""Chat interativo com o Manager Agent da SaaS Factory."""

from __future__ import annotations

import asyncio
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()


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


async def main() -> None:
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

    print("=" * 60)
    print("  SaaS Factory — Manager Agent")
    print("  Digite 'sair' para encerrar")
    print("=" * 60)
    print()

    context_summary = "Início da sessão. Sem histórico anterior."
    project_id = "laac"

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
            source="conversation_history",
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
