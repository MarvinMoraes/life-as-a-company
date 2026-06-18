"""Factory CLI — interface multi-agente com Rich display."""

from __future__ import annotations

import asyncio
import sys
import uuid
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
load_dotenv()

import typer
from rich.columns import Columns
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme

from src.events import AgentEvent, EventBus, EventType

app = typer.Typer(add_completion=False)
console = Console(theme=Theme({
    "manager":   "bold blue",
    "engineer":  "bold green",
    "product":   "bold yellow",
    "qa":        "bold red",
    "marketing": "bold magenta",
    "tool":      "dim cyan",
    "result":    "dim white",
    "system":    "dim grey50",
}))

ROLE_STYLE = {
    "manager":   "blue",
    "engineer":  "green",
    "product":   "yellow",
    "qa":        "red",
    "marketing": "magenta",
}

ROLE_EMOJI = {
    "manager":   "[MGR]",
    "engineer":  "[ENG]",
    "product":   "[PRD]",
    "qa":        "[QA ]",
    "marketing": "[MKT]",
}


class CLIDisplay:
    """Gerencia o display Rich em tempo real."""

    def __init__(self) -> None:
        self._log: list[Text] = []
        self._live: Optional[Live] = None
        self._current_agent: str = "—"
        self._current_tool: str = ""
        self._status: str = "Pronto"

    def handle_event(self, event: AgentEvent) -> None:
        role = event.agent_role
        style = ROLE_STYLE.get(role, "white")
        tag = ROLE_EMOJI.get(role, f"[{role[:3].upper()}]")

        if event.event_type == EventType.AGENT_START:
            self._current_agent = role
            self._current_tool = ""
            self._status = f"{tag} executando..."
            obj = event.data.get("objective", "")[:70]
            line = Text.assemble(
                Text(f"{tag} ", style=style),
                Text("START  ", style="bold"),
                Text(obj, style="white"),
            )
        elif event.event_type == EventType.AGENT_END:
            self._current_tool = ""
            self._status = f"{tag} finalizado"
            summ = event.data.get("summary", "")[:70]
            line = Text.assemble(
                Text(f"{tag} ", style=style),
                Text("END    ", style="bold"),
                Text(summ, style="dim white"),
            )
        elif event.event_type == EventType.TOOL_CALL:
            tool = event.data.get("tool", "")
            self._current_tool = tool
            inp = str(event.data.get("input", ""))[:60]
            line = Text.assemble(
                Text(f"{tag} ", style=style),
                Text(f"TOOL   {tool}", style="cyan"),
                Text(f"  {inp}", style="dim"),
            )
        elif event.event_type == EventType.TOOL_RESULT:
            tool = event.data.get("tool", "")
            res = event.data.get("result", "")[:80]
            line = Text.assemble(
                Text(f"{tag} ", style=style),
                Text(f"RESULT {tool}", style="dim cyan"),
                Text(f"  {res}", style="dim white"),
            )
        elif event.event_type == EventType.DELEGATION:
            target = event.data.get("target_role", "")
            target_style = ROLE_STYLE.get(target, "white")
            target_tag = ROLE_EMOJI.get(target, target)
            line = Text.assemble(
                Text(f"{tag} ", style=style),
                Text("DELEGA ", style="bold"),
                Text(f"→ {target_tag}", style=target_style),
            )
        elif event.event_type == EventType.WORKFLOW_STEP:
            step = event.data.get("step_name", "")
            line = Text.assemble(
                Text("[ WORKFLOW ] ", style="bold white"),
                Text(f"step: {step}", style="white"),
            )
        elif event.event_type == EventType.ERROR:
            err = event.data.get("error", "")[:100]
            line = Text.assemble(
                Text(f"{tag} ", style=style),
                Text("ERROR  ", style="bold red"),
                Text(err, style="red"),
            )
        else:
            msg = str(event.data)[:100]
            line = Text.assemble(Text(f"{tag} ", style=style), Text(msg, style="dim"))

        self._log.append(line)
        if len(self._log) > 100:
            self._log = self._log[-100:]

        if self._live:
            self._live.update(self._build_panel())

    def _build_panel(self) -> Panel:
        lines = self._log[-30:] if len(self._log) > 30 else self._log
        content = Text("\n").join(lines) if lines else Text("Aguardando eventos...", style="dim")
        title = f"[bold]SaaS Factory[/bold]  |  agente: [{ROLE_STYLE.get(self._current_agent, 'white')}]{self._current_agent}[/]"
        if self._current_tool:
            title += f"  |  tool: [cyan]{self._current_tool}[/]"
        return Panel(content, title=title, border_style="bright_black", padding=(0, 1))

    def print_line(self, text: str, style: str = "white") -> None:
        line = Text(text, style=style)
        self._log.append(line)
        if self._live:
            self._live.update(self._build_panel())
        else:
            console.print(line)


# ---------------------------------------------------------------------------
# Modos de operação
# ---------------------------------------------------------------------------

async def _run_chat(
    display: CLIDisplay,
    project: str,
    vault: str,
    live: Live,
) -> None:
    from src.config.settings import get_settings
    from src.providers.claude_provider import ClaudeLLMProvider
    from src.orchestrator.manager import Orchestrator
    from src.schemas.agent import AgentContextPack, ContextLayer
    from src.schemas.task import AgentRole, TaskBrief

    settings = get_settings()
    if not settings.anthropic_api_key:
        display.print_line("[Erro] ANTHROPIC_API_KEY nao encontrada no .env", "bold red")
        return

    provider = ClaudeLLMProvider(
        api_key=settings.anthropic_api_key,
        prompt_caching=settings.prompt_caching_enabled,
    )
    orch = Orchestrator(
        vault_path=vault or str(settings.vault_dir),
        provider=provider,
        enable_tools=True,
    )
    manager = orch.registry.get(AgentRole.MANAGER)

    display.print_line(f"Projeto: {project} | Vault: {vault or settings.vault_dir}", "dim")
    display.print_line("Digite 'sair' para encerrar.", "dim")

    context_summary = f"Projeto: {project}"

    while True:
        live.stop()
        try:
            user_input = input("\nVoce: ").strip()
        except (KeyboardInterrupt, EOFError):
            break
        finally:
            live.start()

        if not user_input:
            continue
        if user_input.lower() in ("sair", "exit", "quit"):
            break

        from src.events import AgentEvent, EventBus, EventType as ET
        EventBus.global_bus().emit(AgentEvent(ET.AGENT_START, "manager", {"objective": user_input}))

        task = TaskBrief(
            task_id=f"chat-{uuid.uuid4().hex[:8]}",
            project_id=project,
            assigned_to=AgentRole.MANAGER,
            objective=user_input,
            context_summary=context_summary,
            expected_output_format="JSON com status, objective_understood, plan, immediate_action",
            acceptance_criteria=["Responder de forma clara e acionavel"],
            max_response_depth="medium",
        )
        pack = AgentContextPack(
            pack_id=f"pack-{uuid.uuid4().hex[:8]}",
            task=task,
            token_budget=8192,
        )
        pack.add_layer(ContextLayer(
            layer_name="context",
            content=context_summary,
            token_estimate=len(context_summary) // 4,
            source="session",
        ))

        try:
            response = await manager.execute(pack)
            EventBus.global_bus().emit(AgentEvent(ET.AGENT_END, "manager", {"summary": response.summary}))

            live.stop()
            console.print()
            console.rule("[bold blue]Manager[/bold blue]")
            console.print(f"[white]{response.summary}[/white]")

            data = response.content
            if plan := data.get("plan"):
                console.print("\n[bold]Plano:[/bold]")
                for step in plan:
                    if isinstance(step, dict):
                        agent = step.get("agent", "?")
                        task_desc = step.get("task", step.get("objective", ""))
                        num = step.get("step", "•")
                        style = ROLE_STYLE.get(agent, "white")
                        console.print(f"  {num}. [{style}][{agent}][/{style}] {task_desc}")
            console.print()
            live.start()

            if new_ctx := data.get("context_summary"):
                context_summary = new_ctx

        except Exception as e:
            EventBus.global_bus().emit(AgentEvent(EventType.ERROR, "manager", {"error": str(e)}))
            live.stop()
            console.print(f"[red][Erro] {e}[/red]")
            live.start()


async def _run_workflow(
    display: CLIDisplay,
    workflow_name: str,
    project: str,
    vault: str,
    live: Live,
    feature: str = "",
    sprint_type: str = "",
) -> None:
    from src.config.settings import get_settings
    from src.providers.claude_provider import ClaudeLLMProvider
    from src.orchestrator.manager import Orchestrator

    settings = get_settings()
    if not settings.anthropic_api_key:
        display.print_line("[Erro] ANTHROPIC_API_KEY nao encontrada.", "bold red")
        return

    provider = ClaudeLLMProvider(
        api_key=settings.anthropic_api_key,
        prompt_caching=settings.prompt_caching_enabled,
    )
    orch = Orchestrator(
        vault_path=vault or str(settings.vault_dir),
        provider=provider,
        enable_tools=True,
    )

    live.stop()
    if workflow_name == "flouwy-sprint":
        from src.workflows.flouwy_sprint import run_flouwy_sprint
        if not feature:
            feature = input("Descreva a feature ou bug: ").strip()
        if not sprint_type:
            sprint_type_input = input("Tipo [feature/bug] (default: feature): ").strip() or "feature"
            sprint_type = "bug" if sprint_type_input.startswith("b") else "feature"
    else:
        console.print(f"[red]Workflow desconhecido: {workflow_name}[/red]")
        console.print("Disponíveis: flouwy-sprint, idea-to-prd, prd-to-build, product-improvement, project-audit")
        return
    live.start()

    display.print_line(f"Iniciando workflow: {workflow_name}", "bold white")

    try:
        if workflow_name == "flouwy-sprint":
            snapshot = await run_flouwy_sprint(orch, feature, sprint_type, project)
        else:
            snapshot = None

        if snapshot:
            live.stop()
            console.print()
            console.rule("[bold]Resultado do Workflow[/bold]")
            status_style = "green" if snapshot.status == "completed" else "red"
            console.print(f"Status: [{status_style}]{snapshot.status}[/{status_style}]")
            console.print(f"Steps concluidos: {', '.join(snapshot.steps_completed)}")
            console.print(f"Tokens usados: {snapshot.token_budget_used}")
            if snapshot.error:
                console.print(f"[red]Erro: {snapshot.error}[/red]")
            console.print()

    except Exception as e:
        live.stop()
        console.print(f"[red][Erro no workflow] {e}[/red]")
        import traceback
        traceback.print_exc()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

@app.command()
def main(
    mode: str = typer.Option("chat", "--mode", "-m", help="chat | workflow | agent"),
    project: str = typer.Option("flouwy", "--project", "-p", help="ID do projeto no vault"),
    workflow: str = typer.Option("flouwy-sprint", "--workflow", "-w", help="Nome do workflow"),
    vault: str = typer.Option("", "--vault", "-v", help="Caminho do vault Obsidian"),
    feature: str = typer.Option("", "--feature", "-f", help="Feature/bug para flouwy-sprint (evita input interativo)"),
    sprint_type: str = typer.Option("feature", "--sprint-type", help="feature | bug"),
) -> None:
    """SaaS Factory — CLI multi-agente com display em tempo real."""
    display = CLIDisplay()
    EventBus.global_bus().subscribe(display.handle_event)

    console.print()
    console.print(Panel(
        f"[bold]SaaS Factory[/bold] | modo: [cyan]{mode}[/cyan] | projeto: [yellow]{project}[/yellow]",
        border_style="bright_blue",
        padding=(0, 2),
    ))
    console.print()

    initial_panel = display._build_panel()

    with Live(initial_panel, console=console, refresh_per_second=8) as live:
        display._live = live
        if mode == "chat":
            asyncio.run(_run_chat(display, project, vault, live))
        elif mode == "workflow":
            asyncio.run(_run_workflow(display, workflow, project, vault, live, feature, sprint_type))
        else:
            display.print_line(f"Modo desconhecido: {mode}. Use: chat | workflow", "red")


if __name__ == "__main__":
    app()
