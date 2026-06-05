"""CLI da SaaS Factory — interface de linha de comando com Typer."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

app = typer.Typer(
    name="factory",
    help="SaaS Factory — fábrica de SaaS agêntica multiagente",
    rich_markup_mode="rich",
)
console = Console()


def _get_orchestrator(vault: str, provider: str):
    from .orchestrator.manager import Orchestrator
    from .providers.factory import get_provider
    prov = get_provider(provider)
    return Orchestrator(vault_path=vault, provider=prov)


@app.command()
def idea(
    idea_text: str = typer.Argument(..., help="Descreva sua ideia de SaaS"),
    project_id: str = typer.Option(..., "--project", "-p", help="ID do projeto (kebab-case)"),
    audience: str = typer.Option("", "--audience", "-a", help="Público-alvo inicial"),
    vault: str = typer.Option("./vault", "--vault", "-v", help="Caminho do vault Obsidian"),
    provider: str = typer.Option("mock", "--provider", help="LLM provider: mock | claude | openai"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Salvar resultado em JSON"),
):
    """Workflow A: Ideia → PRD (idea-to-prd)"""
    async def _run():
        from .workflows.idea_to_prd import run_idea_to_prd
        orch = _get_orchestrator(vault, provider)
        console.print(Panel(f"[bold cyan]Workflow: Idea → PRD[/]\nProjeto: {project_id}", expand=False))
        snapshot = await run_idea_to_prd(orch, project_id, idea_text, audience)
        from .utils.formatters import pprint_snapshot
        console.print(pprint_snapshot(snapshot))
        if output:
            output.write_text(json.dumps(snapshot.model_dump(), indent=2, default=str))
            console.print(f"[green]Resultado salvo em: {output}[/]")

    asyncio.run(_run())


@app.command()
def build(
    project_id: str = typer.Argument(..., help="ID do projeto"),
    prd_file: Path = typer.Option(..., "--prd", help="Arquivo JSON com o PRD"),
    vault: str = typer.Option("./vault", "--vault", "-v"),
    provider: str = typer.Option("mock", "--provider"),
):
    """Workflow B: PRD → Build (plano técnico)"""
    async def _run():
        from .schemas.project import PRD
        from .workflows.prd_to_build import run_prd_to_build
        prd = PRD.model_validate_json(prd_file.read_text())
        orch = _get_orchestrator(vault, provider)
        console.print(Panel(f"[bold yellow]Workflow: PRD → Build[/]\nProjeto: {project_id}", expand=False))
        snapshot = await run_prd_to_build(orch, project_id, prd)
        from .utils.formatters import pprint_snapshot
        console.print(pprint_snapshot(snapshot))

    asyncio.run(_run())


@app.command()
def audit(
    project_id: str = typer.Argument(..., help="ID do projeto a auditar"),
    scope: str = typer.Option("full", "--scope", help="full | technical | product"),
    vault: str = typer.Option("./vault", "--vault", "-v"),
    provider: str = typer.Option("mock", "--provider"),
):
    """Workflow D: Project Audit"""
    async def _run():
        from .workflows.project_audit import run_project_audit
        orch = _get_orchestrator(vault, provider)
        console.print(Panel(f"[bold red]Workflow: Project Audit[/]\nProjeto: {project_id}", expand=False))
        snapshot = await run_project_audit(orch, project_id, scope)
        from .utils.formatters import pprint_snapshot
        console.print(pprint_snapshot(snapshot))

    asyncio.run(_run())


@app.command()
def agents():
    """Lista todos os agentes registrados e suas responsabilidades."""
    from .orchestrator.manager import Orchestrator
    from .providers.factory import get_provider
    orch = Orchestrator(provider=get_provider("mock"))
    table_data = orch.registry.list_agents()
    for agent in table_data:
        console.print(Panel(
            f"[bold]{agent['name']}[/]\n{agent['description']}",
            title=f"[cyan]{agent['role']}[/]",
            expand=False,
        ))


if __name__ == "__main__":
    app()
