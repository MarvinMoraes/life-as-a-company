"""Schemas de tarefas e avaliação de qualidade."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class AgentRole(str, Enum):
    MANAGER = "manager"
    ENGINEER = "engineer"
    PRODUCT = "product"
    MARKETING = "marketing"
    QA = "qa"


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    DONE = "done"
    REJECTED = "rejected"


class TaskBrief(BaseModel):
    """Contexto mínimo enviado pelo Manager a um agente específico.

    Princípio: conter APENAS o que o agente precisa para executar esta tarefa.
    Contexto adicional é carregado sob demanda via MemoryRetrieval.
    """

    task_id: str
    project_id: str
    assigned_to: AgentRole
    objective: str = Field(description="Uma frase clara: o que precisa ser feito")
    context_summary: str = Field(
        description="Resumo compacto do contexto relevante (max 500 tokens)"
    )
    inputs: dict = Field(
        default_factory=dict,
        description="Dados de entrada necessários para a tarefa"
    )
    expected_output_format: str = Field(
        description="Descreve o formato esperado da saída"
    )
    acceptance_criteria: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    depends_on: list[str] = Field(
        default_factory=list,
        description="IDs de tasks anteriores cujo output é insumo"
    )
    memory_hints: list[str] = Field(
        default_factory=list,
        description="Slugs de notas do vault relevantes para esta tarefa"
    )
    max_response_depth: str = Field(
        default="medium",
        description="'short' | 'medium' | 'deep' — controla verbosidade da resposta"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: TaskStatus = TaskStatus.PENDING


class QAFinding(BaseModel):
    severity: str = Field(description="'critical' | 'major' | 'minor' | 'info'")
    category: str = Field(description="Ex: 'missing_feature', 'tech_risk', 'doc_gap'")
    description: str
    recommendation: str
    artifact_ref: Optional[str] = None


class QAVerdict(str, Enum):
    APPROVED = "approved"
    APPROVED_WITH_NOTES = "approved_with_notes"
    NEEDS_REVISION = "needs_revision"
    REJECTED = "rejected"


class QAEvaluation(BaseModel):
    """Relatório de avaliação produzido pelo QA Agent."""

    evaluation_id: str
    project_id: str
    task_id: str
    artifact_evaluated: str = Field(description="O que foi avaliado: PRD, TechnicalPlan, etc.")
    verdict: QAVerdict
    score: float = Field(ge=0, le=10, description="Score de qualidade 0-10")
    summary: str = Field(description="Resumo executivo da avaliação (max 200 words)")
    findings: list[QAFinding] = Field(default_factory=list)
    prd_adherence: Optional[float] = Field(
        default=None, ge=0, le=100,
        description="% de aderência ao PRD, se aplicável"
    )
    missing_acceptance_criteria: list[str] = Field(default_factory=list)
    approved_artifacts: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
