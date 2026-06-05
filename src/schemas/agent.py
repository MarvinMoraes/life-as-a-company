"""Schemas de contratos entre agentes e snapshots de execução."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from .task import AgentRole, TaskBrief


class ContextLayer(BaseModel):
    """Uma camada de contexto — carregada seletivamente pelo Manager."""

    layer_name: str = Field(description="'global' | 'project' | 'task' | 'agent' | 'memory'")
    content: str
    token_estimate: int = 0
    source: str = ""


class AgentContextPack(BaseModel):
    """Pacote de contexto montado pelo Manager antes de invocar um agente.

    Política: incluir apenas o mínimo necessário.
    O Manager é responsável por manter token_total abaixo do limite configurado.
    """

    pack_id: str
    task: TaskBrief
    layers: list[ContextLayer] = Field(default_factory=list)
    token_total: int = 0
    token_budget: int = Field(default=4096, description="Limite máximo para esta invocação")
    assembled_at: datetime = Field(default_factory=datetime.utcnow)

    def fits_budget(self) -> bool:
        return self.token_total <= self.token_budget

    def add_layer(self, layer: ContextLayer) -> bool:
        """Adiciona camada se couber no budget. Retorna False se exceder."""
        if self.token_total + layer.token_estimate > self.token_budget:
            return False
        self.layers.append(layer)
        self.token_total += layer.token_estimate
        return True


class AgentResponse(BaseModel):
    """Resposta padronizada de qualquer agente."""

    response_id: str
    task_id: str
    agent_role: AgentRole
    status: str = Field(description="'success' | 'partial' | 'failed' | 'needs_clarification'")
    content: Any = Field(description="Payload principal — schema depende do agente")
    summary: str = Field(description="Resumo compacto para o Manager (max 100 words)")
    memory_writes: list[str] = Field(
        default_factory=list,
        description="Slugs de notas criadas/atualizadas nesta execução"
    )
    decisions: list[dict] = Field(
        default_factory=list,
        description="Decisões relevantes para registrar no vault"
    )
    tokens_used: int = 0
    follow_up_tasks: list[str] = Field(
        default_factory=list,
        description="Sugestões de tasks de follow-up para o Manager avaliar"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ExecutionSnapshot(BaseModel):
    """Snapshot de estado de uma execução completa de workflow.

    Salvo no vault para recuperação futura sem reexecutar.
    """

    snapshot_id: str
    workflow_name: str
    project_id: str
    status: str = Field(description="'running' | 'completed' | 'failed' | 'paused'")
    current_step: str = ""
    steps_completed: list[str] = Field(default_factory=list)
    steps_pending: list[str] = Field(default_factory=list)
    artifacts: dict[str, Any] = Field(
        default_factory=dict,
        description="Artefatos produzidos: {nome_artifact: conteúdo_resumido}"
    )
    token_budget_used: int = 0
    token_budget_total: int = 0
    error: Optional[str] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
