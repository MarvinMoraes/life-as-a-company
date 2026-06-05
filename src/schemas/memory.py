"""Schemas de memória e registro de decisões."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class MemoryType(str, Enum):
    PROJECT = "project"
    DECISION = "decision"
    PRD = "prd"
    RESEARCH = "research"
    MARKETING = "marketing"
    QA = "qa"
    SNAPSHOT = "snapshot"
    AGENT_LOG = "agent_log"
    SCRATCH = "scratch"


class MemoryNote(BaseModel):
    """Representação de uma nota no vault Obsidian."""

    slug: str = Field(description="Nome do arquivo sem extensão, kebab-case")
    title: str
    type: MemoryType
    project_id: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    content: str = Field(description="Corpo da nota em Markdown")
    summary: str = Field(
        default="",
        description="Resumo compacto para incluir em context packs (max 150 tokens)"
    )
    links: list[str] = Field(
        default_factory=list,
        description="Slugs de notas relacionadas [[link]]"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def to_frontmatter_dict(self) -> dict:
        return {
            "slug": self.slug,
            "title": self.title,
            "type": self.type.value,
            "project_id": self.project_id,
            "tags": self.tags,
            "summary": self.summary,
            "created": self.created_at.strftime("%Y-%m-%d"),
            "updated": self.updated_at.strftime("%Y-%m-%d"),
        }


class DecisionRecord(BaseModel):
    """ADR leve — Architecture/Product Decision Record."""

    decision_id: str = Field(description="Prefixo + número, ex: ADR-001")
    project_id: Optional[str] = None
    title: str
    status: str = Field(default="accepted", description="'proposed' | 'accepted' | 'deprecated'")
    context: str = Field(description="Situação que levou à decisão")
    decision: str = Field(description="O que foi decidido")
    rationale: str = Field(description="Por que essa opção foi escolhida")
    alternatives_considered: list[str] = Field(default_factory=list)
    consequences: list[str] = Field(
        default_factory=list,
        description="Consequências positivas e negativas conhecidas"
    )
    made_by: str = Field(description="'manager' | 'product' | 'engineer' | 'user'")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def to_markdown(self) -> str:
        alts = "\n".join(f"- {a}" for a in self.alternatives_considered) or "N/A"
        cons = "\n".join(f"- {c}" for c in self.consequences) or "N/A"
        return f"""# {self.decision_id}: {self.title}

**Status:** {self.status}
**Decisor:** {self.made_by}
**Data:** {self.created_at.strftime("%Y-%m-%d")}

## Contexto
{self.context}

## Decisão
{self.decision}

## Racional
{self.rationale}

## Alternativas Consideradas
{alts}

## Consequências
{cons}
"""
