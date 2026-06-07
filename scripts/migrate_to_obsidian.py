"""Migra toda a base de conhecimento da SaaS Factory para o vault Obsidian."""

import asyncio
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()


async def migrate():
    from src.config import get_settings
    from src.memory.memory_manager import MemoryManager
    from src.obsidian.writer import ObsidianWriter
    from src.schemas.memory import MemoryNote, MemoryType

    settings = get_settings()
    vault = settings.vault_dir
    repo = Path(__file__).parent.parent
    manager = MemoryManager(vault)
    writer = ObsidianWriter(vault)
    written = []

    print(f"Vault destino: {vault}\n")

    # ── 1. _system e Templates ──────────────────────────────────
    for folder in ["_system", "Templates"]:
        src = repo / "vault" / folder
        dst = vault / folder
        if src.exists():
            shutil.copytree(src, dst, dirs_exist_ok=True)
            count = len(list(src.rglob("*.md")))
            written.append(f"[copy]     {folder}/ — {count} arquivos")

    # ── 2. Prompts dos agentes → Agents/ ───────────────────────
    for f in sorted((repo / "src" / "prompts").glob("*.md")):
        content = f.read_text(encoding="utf-8")
        note = MemoryNote(
            slug=f"prompt-{f.stem}",
            title=f"Prompt: {f.stem.replace('-', ' ').title()} Agent",
            type=MemoryType.AGENT_LOG,
            tags=["prompt", "agent", f.stem],
            content=content,
            summary=f"System prompt do {f.stem} agent — papel, responsabilidades, formato de saida.",
        )
        path = await manager.save_note(note)
        written.append(f"[agent]    {path.name}")

    # ── 3. Docs técnicos → _system/ ────────────────────────────
    for f in sorted((repo / "docs").glob("*.md")):
        content = f.read_text(encoding="utf-8")
        note = MemoryNote(
            slug=f"doc-{f.stem}",
            title=f.stem.replace("-", " ").title(),
            type=MemoryType.SCRATCH,
            tags=["docs", "factory", "reference"],
            content=content,
            summary=f"Documentacao tecnica: {f.stem}",
        )
        path = await writer.write(note)
        written.append(f"[docs]     {path.name}")

    # ── 4. Exemplo TaskFlow — nota de projeto ──────────────────
    project_note_src = (
        repo / "examples" / "taskflow_saas" / "vault"
        / "Projects" / "taskflow-saas" / "taskflow-saas-project.md"
    )
    if project_note_src.exists():
        proj_dir = vault / "Projects" / "taskflow-saas"
        proj_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(project_note_src, proj_dir / "taskflow-saas-project.md")
        written.append("[example]  taskflow-saas-project.md")

    # ── 5. PRD como nota estruturada ───────────────────────────
    prd_path = repo / "examples" / "taskflow_saas" / "artifacts" / "prd_v1.json"
    if prd_path.exists():
        data = json.loads(prd_path.read_text(encoding="utf-8"))

        features_md = "\n\n".join(
            f"### {f['name']} `{f['priority'].upper()}`\n{f['description']}\n"
            + "\n".join(f"- [ ] {ac}" for ac in f.get("acceptance_criteria", []))
            for f in data.get("features", [])
        )
        out_of_scope = "\n".join(f"- {s}" for s in data.get("out_of_scope", []))
        metrics = "\n".join(f"- {s}" for s in data.get("success_metrics", []))
        risks = "\n".join(f"- {s}" for s in data.get("risks", []))

        content = "\n\n".join([
            f"## Resumo Executivo\n{data['executive_summary']}",
            f"## Problema\n{data['problem']}",
            f"## Solucao\n{data['solution']}",
            f"## Proposta de Valor\n{data['value_proposition']}",
            f"## Features\n{features_md}",
            f"## Fora do Escopo\n{out_of_scope}",
            f"## Metricas de Sucesso\n{metrics}",
            f"## Riscos\n{risks}",
        ])

        note = MemoryNote(
            slug="taskflow-saas-prd-v1",
            title="PRD: TaskFlow SaaS v1.0",
            type=MemoryType.PRD,
            project_id="taskflow-saas",
            tags=["prd", "taskflow-saas", "approved"],
            content=content,
            summary="PRD v1.0 aprovado: gestao inteligente de tarefas para times remotos. 4 features MVP.",
            links=["taskflow-saas-project", "taskflow-saas-tech-plan-v1"],
        )
        path = await manager.save_note(note)
        written.append(f"[example]  {path.name}")

    # ── 6. Technical Plan como nota estruturada ────────────────
    tech_path = repo / "examples" / "taskflow_saas" / "artifacts" / "technical_plan_v1.json"
    if tech_path.exists():
        data = json.loads(tech_path.read_text(encoding="utf-8"))

        stack_md = "\n".join(f"- **{k}**: {v}" for k, v in data["tech_stack"].items())
        phases_md = "\n\n".join(
            f"### Fase {p['phase']}: {p['name']}\n{p['scope']} ({p['effort']})"
            for p in data["implementation_phases"]
        )
        tradeoffs_md = "\n\n".join(
            f"**{t['decision']}**: escolhido `{t['chosen']}` (rejeitado: {t['rejected']})\n> {t['rationale']}"
            for t in data["trade_offs"]
        )
        risks = "\n".join(f"- {r}" for r in data["risks"])

        content = "\n\n".join([
            f"## Arquitetura\n{data['architecture_summary']}",
            f"## Stack\n{stack_md}",
            f"## Fases de Implementacao\n{phases_md}",
            f"## Trade-offs\n{tradeoffs_md}",
            f"## Riscos\n{risks}",
            f"## Esforco Estimado\n{data['estimated_effort']}",
        ])

        note = MemoryNote(
            slug="taskflow-saas-tech-plan-v1",
            title="Technical Plan: TaskFlow SaaS v1.0",
            type=MemoryType.PROJECT,
            project_id="taskflow-saas",
            tags=["technical-plan", "taskflow-saas", "fastapi", "nextjs"],
            content=content,
            summary="Stack: FastAPI + PostgreSQL + Next.js. Engine heuristica. Deploy Railway. 6 semanas.",
            links=["taskflow-saas-prd-v1", "taskflow-saas-project"],
        )
        path = await manager.save_note(note)
        written.append(f"[example]  {path.name}")

    # ── 7. README da factory ───────────────────────────────────
    readme = repo / "README.md"
    note = MemoryNote(
        slug="saas-factory-readme",
        title="SaaS Factory — Guia Completo",
        type=MemoryType.SCRATCH,
        tags=["factory", "guide", "reference"],
        content=readme.read_text(encoding="utf-8"),
        summary="Guia completo: agentes, workflows, CLI, Claude API, Obsidian.",
    )
    path = await manager.save_note(note)
    written.append(f"[readme]   {path.name}")

    # ── Resultado ──────────────────────────────────────────────
    print(f"{'─' * 55}")
    for item in written:
        print(f"  {item}")
    print(f"{'─' * 55}")
    print(f"  Total: {len(written)} itens → {vault}")


if __name__ == "__main__":
    asyncio.run(migrate())
