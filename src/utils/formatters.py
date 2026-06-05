"""Formatadores para exibição de resultados no terminal."""

from __future__ import annotations

import json
from typing import Any

from ..schemas.agent import AgentResponse, ExecutionSnapshot


def format_response(response: AgentResponse) -> str:
    """Formata AgentResponse para exibição legível."""
    lines = [
        f"┌─ {response.agent_role.value.upper()} AGENT",
        f"│  Status: {response.status}",
        f"│  Task: {response.task_id}",
        f"│  Tokens: {response.tokens_used}",
        f"│",
        f"│  Summary:",
        f"│  {response.summary}",
    ]

    if response.decisions:
        lines.append("│")
        lines.append("│  Decisões registradas:")
        for d in response.decisions[:3]:
            if isinstance(d, dict):
                lines.append(f"│  • {d.get('title', 'Decisão')}")

    if response.follow_up_tasks:
        lines.append("│")
        lines.append("│  Follow-ups sugeridos:")
        for t in response.follow_up_tasks[:3]:
            lines.append(f"│  → {t}")

    lines.append("└" + "─" * 50)
    return "\n".join(lines)


def pprint_snapshot(snapshot: ExecutionSnapshot) -> str:
    """Formata ExecutionSnapshot para exibição no terminal."""
    status_icon = {"completed": "✓", "failed": "✗", "running": "⟳", "paused": "⏸"}.get(
        snapshot.status, "?"
    )
    lines = [
        f"╔══ WORKFLOW SNAPSHOT ══════════════════════════",
        f"║  {status_icon} {snapshot.workflow_name} [{snapshot.project_id}]",
        f"║  ID: {snapshot.snapshot_id}",
        f"║  Status: {snapshot.status}",
        f"║  Tokens usados: {snapshot.token_budget_used}",
        f"║",
        f"║  Steps concluídos:",
    ]

    for step in snapshot.steps_completed:
        artifact = snapshot.artifacts.get(step, {})
        agent = artifact.get("agent", "?")
        status = artifact.get("status", "?")
        lines.append(f"║   ✓ [{agent}] {step} → {status}")

    if snapshot.steps_pending:
        lines.append("║")
        lines.append("║  Steps pendentes:")
        for step in snapshot.steps_pending:
            lines.append(f"║   ○ {step}")

    if snapshot.error:
        lines.append(f"║")
        lines.append(f"║  Erro: {snapshot.error}")

    lines.append("╚" + "═" * 47)
    return "\n".join(lines)


def format_json(data: Any, indent: int = 2) -> str:
    return json.dumps(data, indent=indent, default=str, ensure_ascii=False)
