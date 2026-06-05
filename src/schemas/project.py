"""Schemas de projeto: do brief ao plano técnico e de marketing."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ProjectStatus(str, Enum):
    IDEATION = "ideation"
    DISCOVERY = "discovery"
    PLANNING = "planning"
    BUILDING = "building"
    REVIEWING = "reviewing"
    SHIPPED = "shipped"
    PAUSED = "paused"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ProjectBrief(BaseModel):
    """Entrada inicial do usuário — intenção bruta transformada em brief estruturado."""

    id: str = Field(description="Slug único: kebab-case, ex: taskflow-saas")
    name: str
    raw_idea: str = Field(description="Ideia como o usuário descreveu, sem processamento")
    problem_statement: Optional[str] = None
    target_audience: Optional[str] = None
    success_criteria: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    priority: Priority = Priority.MEDIUM
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: ProjectStatus = ProjectStatus.IDEATION


class UserPersona(BaseModel):
    name: str
    role: str
    pains: list[str]
    gains: list[str]
    jtbd: str = Field(description="Job-to-be-done principal")


class PRDSection(BaseModel):
    title: str
    content: str


class PRD(BaseModel):
    """Product Requirements Document — contrato entre produto e engenharia."""

    project_id: str
    version: str = "1.0"
    title: str
    executive_summary: str = Field(description="Max 3 frases: problema, solução, impacto")
    problem: str
    solution: str
    personas: list[UserPersona] = Field(default_factory=list)
    value_proposition: str
    features: list[dict] = Field(
        default_factory=list,
        description="Lista de {name, description, priority, acceptance_criteria}"
    )
    out_of_scope: list[str] = Field(default_factory=list)
    success_metrics: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    roadmap_phases: list[dict] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    approved: bool = False


class TechnicalPlan(BaseModel):
    """Plano técnico gerado pelo Engineer Agent."""

    project_id: str
    prd_version: str
    architecture_summary: str
    tech_stack: dict[str, str] = Field(
        description="Camada → tecnologia, ex: {'backend': 'FastAPI', 'db': 'PostgreSQL'}"
    )
    components: list[dict] = Field(
        default_factory=list,
        description="Lista de {name, responsibility, interfaces}"
    )
    data_models: list[dict] = Field(default_factory=list)
    api_endpoints: list[dict] = Field(default_factory=list)
    infrastructure: dict = Field(default_factory=dict)
    implementation_phases: list[dict] = Field(default_factory=list)
    trade_offs: list[dict] = Field(
        default_factory=list,
        description="Lista de {decision, chosen, rejected, rationale}"
    )
    estimated_effort: str = Field(description="Ex: '3 sprints de 2 semanas'")
    risks: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class MarketingPlan(BaseModel):
    """Plano de marketing e go-to-market gerado pelo Marketing Agent."""

    project_id: str
    market_size: str
    target_segment: str
    competitors: list[dict] = Field(
        default_factory=list,
        description="Lista de {name, strengths, weaknesses, positioning}"
    )
    positioning_statement: str
    unique_value_proposition: str
    messaging: dict[str, str] = Field(
        description="Canal → mensagem principal"
    )
    acquisition_channels: list[dict] = Field(
        default_factory=list,
        description="Lista de {channel, hypothesis, estimated_cac, priority}"
    )
    launch_phases: list[dict] = Field(default_factory=list)
    gtm_strategy: str
    kpis: list[str] = Field(default_factory=list)
    budget_hypothesis: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
